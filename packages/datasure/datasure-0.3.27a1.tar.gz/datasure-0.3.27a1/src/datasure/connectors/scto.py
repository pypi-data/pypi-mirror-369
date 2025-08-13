import contextlib
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
import polars as pl
import pysurveycto
import requests
import streamlit as st
from pydantic import BaseModel, Field, field_validator

from datasure.utils import duckdb_get_table, duckdb_save_table, get_cache_path

# --- Configuration and Models --- #


class FormType(str, Enum):
    """Enum for form types."""

    REGULAR = "regular"
    SERVER_DATASET = "server_dataset"


class MediaType(str, Enum):
    """Enum for media types."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    COMMENTS = "comments"
    TEXT_AUDIT = "text audit"
    AUDIO_AUDIT = "audio audit"
    SENSOR_STREAM = "sensor stream"


@dataclass
class SurveyCTOConfig:
    """Configuration for SurveyCTO operations."""

    max_retries: int = 3
    timeout: int = 30
    chunk_size: int = 1000
    default_date: datetime = datetime(2024, 1, 1, 13, 40, 40)


class ProjectID(BaseModel):
    """Model for project ID with validation."""

    project_id: str = Field(..., min_length=8, max_length=8)

    @field_validator("project_id")
    def validate_project_id(cls, v):
        """Validate project ID format."""
        if not re.fullmatch(r"^[a-z0-9]{8}$", v):
            raise ValueError("Project ID must be alphanumeric and 8 characters long")
        return v


class ServerCredentials(BaseModel):
    """Model for server credentials with validation."""

    server: str = Field(..., min_length=2, max_length=64)
    user: str = Field(..., min_length=4, max_length=128)
    password: str = Field(..., min_length=1)

    @field_validator("server")
    def validate_server(cls, v):
        """Validate server name format."""
        if not re.fullmatch(r"^[a-z][a-z0-9]{1,63}", v):
            raise ValueError("Invalid SurveyCTO server name format")
        return v

    @field_validator("user")
    def validate_user(cls, v):
        """Validate user email format."""
        if not re.fullmatch(
            r"^[A-Za-z0-9\._\-\+%]+@[A-Za-z0-9\.\-]+\.[A-Z|a-z]{2,7}$", v
        ):
            raise ValueError("Invalid email format for SurveyCTO user")
        return v


class FormConfig(BaseModel):
    """Model for form configuration."""

    alias: str = Field(..., min_length=1, max_length=64)
    form_id: str = Field(..., min_length=1, max_length=64)
    server: str = Field(..., min_length=2, max_length=64)
    private_key: str | None = None
    save_to: str | None = None
    attachments: bool = False
    refresh: bool = True


# --- Exceptions --- #


class SurveyCTOError(Exception):
    """Base exception for SurveyCTO operations."""

    pass


class ConnectionError(SurveyCTOError):
    """Exception for connection errors."""

    pass


class ValidationError(SurveyCTOError):
    """Exception for validation errors."""

    pass


# --- Core Classes --- #


class CacheManager:
    """Manages caching operations for SurveyCTO data."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)

    def get_server_cache(self) -> dict:
        """Get cached server credentials."""
        try:
            cache_file = get_cache_path(self.project_id, "settings", "scto.json")
            if cache_file.exists():
                return json.loads(cache_file.read_text())
            else:
                return {}
        except Exception as e:
            self.logger.warning(f"Failed to read cache: {e}")
            return {}

    def save_server_cache(self, credentials: ServerCredentials) -> None:
        """Save server credentials to cache."""
        cache_file = get_cache_path(self.project_id, "settings", "scto.json")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(credentials.json())

    def get_existing_data(self, file_path: str) -> tuple[pd.DataFrame, datetime]:
        """Load existing data and return with latest submission date."""
        try:
            if not Path(file_path).exists():
                return pd.DataFrame(), SurveyCTOConfig.default_date

            data = pd.read_csv(file_path)
            if data.empty or "SubmissionDate" not in data.columns:
                return data, SurveyCTOConfig.default_date

            data["SubmissionDate"] = pd.to_datetime(data["SubmissionDate"])
            return data, data["SubmissionDate"].max()

        except Exception as e:
            self.logger.warning(f"Failed to load existing data: {e}")
            return pd.DataFrame(), SurveyCTOConfig.default_date


class DataProcessor:
    """Handles data processing and type conversion."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_repeat_fields(self, questions: pd.DataFrame) -> list[str]:
        """Extract repeat field names from form definition."""
        fields = questions[["type", "name"]].copy()
        repeat_fields = []
        begin_count = 0
        end_count = 0

        for _, row in fields.iterrows():
            if row["type"] == "begin repeat":
                begin_count += 1
            elif row["type"] == "end repeat":
                end_count += 1
            elif (
                begin_count > end_count
                and len(str(row["name"])) > 1
                and row["type"] not in ["begin group", "end group"]
            ):
                repeat_fields.append(row["name"])

        return repeat_fields

    def get_repeat_columns(self, field: str, data_cols: list[str]) -> list[str]:
        """Get all columns that belong to a repeat group."""
        pattern = rf"\b{re.escape(field)}_[0-9]+_{{,1}}[0-9]*_{{,1}}[0-9]*\b"
        return [col for col in data_cols if re.fullmatch(pattern, col)] or [field]

    def convert_data_types(
        self, data: pd.DataFrame, questions: pd.DataFrame
    ) -> pd.DataFrame:
        """Convert data types based on form definition."""
        # Convert standard datetime columns
        datetime_cols = ["CompletionDate", "SubmissionDate", "starttime", "endtime"]
        for col in datetime_cols:
            if col in data.columns:
                with contextlib.suppress(ValueError, TypeError):
                    data[col] = pd.to_datetime(data[col], format="mixed")

        # Convert standard numeric columns
        numeric_cols = ["duration", "formdef_version"]
        for col in numeric_cols:
            if col in data.columns:
                with contextlib.suppress(ValueError, TypeError):
                    data[col] = pd.to_numeric(data[col])

        # Process fields based on form definition
        repeat_fields = self.get_repeat_fields(questions)
        data_cols = list(data.columns)

        for _, row in questions[["type", "name"]].iterrows():
            field_name = row["name"]
            field_type = row["type"]

            # Get columns for this field (including repeat columns)
            if field_name in repeat_fields:
                cols = self.get_repeat_columns(field_name, data_cols)
            else:
                cols = [field_name]

            cols = [col for col in cols if col in data.columns]

            # Apply type conversions
            for col in cols:
                try:
                    if field_type in ["date", "datetime", "time"]:
                        data[col] = pd.to_datetime(data[col], errors="coerce")
                    elif field_type in ["integer", "decimal"]:
                        data[col] = pd.to_numeric(data[col], errors="coerce")
                    elif field_type == "note":
                        data.drop(columns=[col], inplace=True)
                except Exception as e:
                    self.logger.warning(f"Failed to convert column {col}: {e}")

        return data


class MediaDownloader:
    """Handles media file downloads."""

    def __init__(self, scto_client, config: SurveyCTOConfig):
        self.scto_client = scto_client
        self.config = config
        self.logger = logging.getLogger(__name__)

    def download_media_files(
        self,
        media_fields: list[str],
        data: pd.DataFrame,
        media_folder: Path,
        encryption_key: str | None = None,
    ) -> None:
        """Download all media files for the given data."""
        media_folder.mkdir(parents=True, exist_ok=True)

        for field in media_fields:
            self._download_field_media(field, data, media_folder, encryption_key)

    def _download_field_media(
        self,
        field: str,
        data: pd.DataFrame,
        media_folder: Path,
        encryption_key: str | None,
    ) -> None:
        """Download media files for a specific field."""
        processor = DataProcessor()
        cols = processor.get_repeat_columns(field, list(data.columns))

        for col in cols:
            media_data = data[data[col].notna()][["KEY", col]].reset_index()

            if len(media_data) > 0:
                progress_bar = st.progress(0, text=f"Downloading {col} media files...")

                for idx, row in media_data.iterrows():
                    try:
                        self._download_single_file(
                            row[col], row["KEY"], col, media_folder, encryption_key
                        )
                        progress_bar.progress(
                            (idx + 1) / len(media_data),
                            text=f"Downloading {col}... {idx + 1}/{len(media_data)}",
                        )
                    except Exception:
                        self.logger.exception(
                            f"Failed to download {col} for {row['KEY']}"
                        )

    def _download_single_file(
        self,
        url: str,
        submission_key: str,
        field_name: str,
        media_folder: Path,
        encryption_key: str | None,
    ) -> None:
        """Download a single media file."""
        file_ext = Path(url).suffix or ".csv"
        clean_key = submission_key.replace("uuid:", "")
        filename = f"{field_name}_{clean_key}{file_ext}"

        media_content = self.scto_client.get_attachment(url, key=encryption_key)
        (media_folder / filename).write_bytes(media_content)


class SurveyCTOClient:
    """Main client for SurveyCTO operations."""

    def __init__(self, project_id: str, config: SurveyCTOConfig | None = None):
        self.project_id = project_id
        self.config = config or SurveyCTOConfig()
        self.cache_manager = CacheManager(project_id)
        self.data_processor = DataProcessor()
        self.logger = logging.getLogger(__name__)
        self._scto_client = None

    def connect(
        self, credentials: ServerCredentials, validate_permissions: bool = True
    ) -> dict[str, any]:
        """
        Establish connection to SurveyCTO server and validate credentials.

        Args:
            credentials: Server credentials to use for connection
            validate_permissions: Whether to validate permissions by listing forms

        Returns
        -------
            Dict containing connection info and available form

        Raises
        ------
            ConnectionError: If connection or validation fails
        """
        connection_info = {
            "server": credentials.server,
            "connected": False,
            "forms_count": 0,
            "forms_list": [],
            "validation_attempted": validate_permissions,
        }

        try:
            # Create SurveyCTO client object
            self._scto_client = pysurveycto.SurveyCTOObject(
                credentials.server, credentials.user, credentials.password
            )

            if validate_permissions:
                # Validate credentials by making an API call
                try:
                    with st.spinner(
                        f"Validating connection to {credentials.server}..."
                    ):
                        server_response = self._scto_client.list_forms()
                        # extract form list with titles
                        forms_list = [
                            (
                                form.get("id", "no id"),
                                form.get("title", "No title"),
                                form.get("encrypted", False),
                            )
                            for form in server_response
                        ]

                        server_forms_count = len(forms_list)

                    connection_info.update(
                        {
                            "connected": True,
                            "forms_count": server_forms_count,
                            "forms_list": forms_list,
                        }
                    )

                    self.logger.info(
                        f"Successfully connected to {credentials.server}. Found {server_forms_count} forms."
                    )

                    # Save credentials only after successful validation
                    self.cache_manager.save_server_cache(credentials)

                    # Show success message with details
                    if len(forms_list) > 0:
                        st.success(
                            f"✅ Connection to server '{credentials.server}' successful!."
                        )

                    else:
                        st.warning(
                            f"⚠️ Connection successful, but no forms found on server '{credentials.server}'."
                        )

                except requests.exceptions.HTTPError as http_err:
                    self._handle_http_error(http_err, credentials.server)

                except requests.exceptions.ConnectionError:
                    self._scto_client = None
                    raise ConnectionError(  # noqa: B904
                        f"🔌 Cannot connect to server '{credentials.server}'. "
                        f"Please check your internet connection and verify the server name."
                    )

                except requests.exceptions.Timeout:
                    self._scto_client = None
                    raise ConnectionError(  # noqa: B904
                        f"⏱️ Connection timeout to server '{credentials.server}'. "
                        f"The server may be slow or unavailable. Please try again."
                    )

                except Exception as validation_err:
                    self._scto_client = None
                    self.logger.exception(f"Validation error: {validation_err}")  # noqa: TRY401
                    raise ConnectionError(
                        f"❌ Failed to validate credentials: {validation_err}"
                    ) from validation_err
            else:
                # Skip validation, just create connection
                connection_info["connected"] = True
                self.cache_manager.save_server_cache(credentials)
                st.success(
                    f"✅ Connection created for server '{credentials.server}' (validation skipped)."
                )

        except Exception as e:
            # Handle SurveyCTO object creation errors
            self._scto_client = None
            self.logger.exception("Connection creation error")

            if "Invalid server name" in str(e):
                raise ConnectionError(  # noqa: B904
                    f"🏷️ Invalid server name '{credentials.server}'. "
                    f"Server names should contain only lowercase letters and numbers."
                )
            else:
                raise ConnectionError(f"❌ Failed to create connection: {e}")  # noqa: B904

        return connection_info

    def _handle_http_error(
        self, http_err: requests.exceptions.HTTPError, server_name: str
    ) -> None:
        """Handle specific HTTP errors with user-friendly messages."""
        self._scto_client = None

        if hasattr(http_err, "response") and http_err.response is not None:
            status_code = http_err.response.status_code

            error_messages = {
                401: "🔐 Invalid credentials. Please check your username and password.",
                403: "🚫 Access forbidden. Your account may not have permission to access this server.",
                404: f"🔍 Server '{server_name}' not found. Please verify the server name.",
                429: "⏱️ Too many requests. Please wait a moment and try again.",
                500: "🔧 Server error. The SurveyCTO server is experiencing issues. Please try again later.",
                502: "🌐 Bad gateway. There may be a network issue. Please try again.",
                503: "⚠️ Service unavailable. The server is temporarily down. Please try again later.",
            }

            error_msg = error_messages.get(
                status_code,
                f"❌ Server error (HTTP {status_code}). Please try again later.",
            )

            self.logger.error(
                f"HTTP {status_code} error for server {server_name}: {http_err}"
            )
            raise ConnectionError(error_msg)
        else:
            raise ConnectionError(f"❌ Authentication failed: {http_err}")

    def get_form_definition(self, form_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Get form definition (questions and choices)."""
        if not self._scto_client:
            raise ConnectionError("Not connected to server")

        try:
            form_def = self._scto_client.get_form_definition(form_id)

        except Exception as e:
            raise SurveyCTOError(f"Failed to get form definition: {e}")  # noqa: B904

        questions = pd.DataFrame(
            form_def["fieldsRowsAndColumns"][1:],
            columns=form_def["fieldsRowsAndColumns"][0],
        )

        choices = pd.DataFrame(
            form_def["choicesRowsAndColumns"][1:],
            columns=form_def["choicesRowsAndColumns"][0],
        )

        return questions, choices

    def import_data(self, form_config: FormConfig) -> int:
        """Import data from SurveyCTO form."""
        if not self._scto_client:
            # Try to reconnect using cached credentials
            cache = self.cache_manager.get_server_cache()
            if cache:
                credentials = ServerCredentials(**cache)
                self.connect(credentials)
            else:
                raise ConnectionError("Not connected to server")

        try:
            # Try server dataset first
            return self._import_server_dataset(form_config)
        except:
            # Fall back to regular form
            return self._import_regular_form(form_config)

    def _import_server_dataset(self, form_config: FormConfig) -> int:
        """Import from server dataset."""
        data_csv = self._scto_client.get_server_dataset(form_config.form_id)
        data = pl.read_csv(data_csv.encode())

        # Save to DuckDB
        duckdb_save_table(self.project_id, data, alias=form_config.alias, db_name="raw")

        return len(data)

    def _import_regular_form(self, form_config: FormConfig) -> int:
        """Import from regular form with incremental updates."""
        # Load existing data
        existing_data, last_date = (
            self.cache_manager.get_existing_data(form_config.save_to)
            if form_config.save_to
            else (pd.DataFrame(), self.config.default_date)
        )

        if not form_config.refresh:
            return 0

        # Get new data
        new_data_json = self._scto_client.get_form_data(
            form_id=form_config.form_id,
            format="json",
            oldest_completion_date=last_date,
            key=form_config.private_key,
        )

        new_data = pd.DataFrame(new_data_json)
        new_count = len(new_data)

        # Combine data
        if not existing_data.empty:
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_data = new_data

        # Process data types
        questions, _ = self.get_form_definition(form_config.form_id)
        questions = questions[questions.get("disabled", "") != "yes"]
        combined_data = self.data_processor.convert_data_types(combined_data, questions)

        # Download media if requested
        if form_config.attachments and form_config.save_to:
            self._download_attachments(questions, new_data, form_config)

        # Save data
        if form_config.save_to:
            combined_data.to_csv(form_config.save_to, index=False)

        # Save to DuckDB
        duckdb_save_table(
            self.project_id, combined_data, alias=form_config.alias, db_name="raw"
        )

        return new_count

    def _download_attachments(
        self, questions: pd.DataFrame, data: pd.DataFrame, form_config: FormConfig
    ) -> None:
        """Download media attachments."""
        media_types = {e.value for e in MediaType}
        media_fields = questions[questions["type"].isin(media_types)]["name"].tolist()

        if media_fields:
            media_folder = Path(form_config.save_to).parent / "media"

            downloader = MediaDownloader(self._scto_client, self.config)
            downloader.download_media_files(
                media_fields, data, media_folder, form_config.private_key
            )


# --- Streamlit UI Components --- #


class SurveyCTOUI:
    """Streamlit UI components for SurveyCTO integration."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = SurveyCTOClient(project_id)
        self.logger = logging.getLogger(__name__)

    def _get_logo_path(self) -> str:
        """Get path to SurveyCTO logo."""
        assets_dir = Path(__file__).parent.parent / "assets"
        image_path = assets_dir / "SurveyCTO-Logo-CMYK.png"
        return str(image_path)

    def _get_server_list(self) -> list[str]:
        """Get list of available servers."""
        cache = self.client.cache_manager.get_server_cache()
        return (
            cache.get("server", [])
            if isinstance(cache.get("server"), list)
            else [cache.get("server", "")]
        )

    def _get_forms_info(self) -> dict[str, any]:
        """Get connection info for the current server."""
        cache = self.client.cache_manager.get_server_cache()
        connection_info = self.client.connect(
            ServerCredentials(
                server=cache.get("server", ""),
                user=cache.get("user", ""),
                password=cache.get("password", ""),
            ),
            validate_permissions=True,
        )
        return {
            "connected": connection_info["connected"],
            "forms_count": connection_info["forms_count"],
            "forms_list": connection_info["forms_list"],
        }

    def render_login_form(self) -> None:
        """Render server login form."""
        with st.container(border=True):
            st.image(self._get_logo_path(), width=200)
            st.markdown("*Server Details:*")

            server = st.text_input("Server name*", help="e.g., 'myserver'")
            email = st.text_input("Email address*", help="Your SurveyCTO account email")
            password = st.text_input("Password*", type="password")

            st.markdown("**required*")

            if st.button("Connect to server", type="primary", use_container_width=True):
                try:
                    credentials = ServerCredentials(
                        server=server, user=email, password=password
                    )
                    self.client.connect(credentials)
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    def render_form_config(
        self, edit_mode: bool = False, defaults: dict | None = None
    ) -> None:
        """Render form configuration interface with form selection."""
        defaults = defaults or {}

        with st.container(border=True):
            logo_path = self._get_logo_path()
            if logo_path and Path(logo_path).exists():
                st.image(logo_path, width=200)
            else:
                st.markdown("### SurveyCTO Form Configuration")

            alias = st.text_input("Alias*", help="Unique identifier for this form")

            # Server selection
            server_list = self._get_server_list()
            if not server_list:
                st.warning(
                    "No SurveyCTO servers configured. Please connect to a server first."
                )
                return

            server = st.selectbox("Server*", options=server_list)

            # Form selection with dynamic loading
            forms_info = self._get_forms_info()
            # concat form id and form names to create options
            form_options = [
                form[0] + " (" + form[1] + ")" for form in forms_info["forms_list"]
            ]

            # Show form selection dropdown
            default_index = None
            if edit_mode and defaults.get("form_id"):
                # Try to find the default form in the list
                for i, (fid, _) in enumerate(form_options):
                    if fid == defaults.get("form_id"):
                        default_index = i
                        break

            selected_form = st.selectbox(
                "Form*",
                options=form_options,
                index=default_index,
                help="Select a form from the available forms on the server",
            )

            # Show form details in an expander
            if selected_form:
                # split selected form into id and title
                selected_form_split = re.match(r"^(.*?) \((.*)\)$", selected_form)
                form_id = (
                    selected_form_split.group(1)
                    if selected_form_split
                    else selected_form
                )
                form_title = (
                    selected_form_split.group(2) if selected_form_split else "No title"
                )

                # get selected form index from form_options
                form_index = form_options.index(selected_form)
                encrypted = (
                    forms_info["forms_list"][form_index][2]
                    if len(forms_info["forms_list"]) > form_index
                    else False
                )

                with st.expander("📋 Form Details", expanded=False):
                    st.write(f"**Form ID:** {form_id}")
                    st.write(f"**Title:** {form_title}")
                    st.write(f"**Encrypted:** {'Yes' if encrypted else 'No'}")
            else:
                encrypted = False

            # Rest of the form fields
            encryption_key_file = st.text_input(
                "Encryption Key",
                value=defaults.get("key", ""),
                type="password",
                disabled=not encrypted,
                help="Enter encryption key if the form is encrypted (optional)",
            )

            if encrypted and not encryption_key_file:
                st.warning(
                    "Encryption key is required for encrypted forms. Only published fields will be downloaded."
                )

            # validate encryption key is a valid file path
            if encryption_key_file and not os.path.exists(str(encryption_key_file)):
                st.error("Encryption key must be a valid file path to a key file.")
                return

            # validate file has extension.pem
            if encryption_key_file and not encryption_key_file.endswith(".pem"):
                st.error("Encryption key file must have a .pem extension.")
                return

            save_file = st.text_input(
                "Save as",
                value=defaults.get("saveas", ""),
                disabled=not selected_form,
                help="File path to save the data (e.g., data/survey.csv)",
            )

            # check that save file is a valid file path
            if save_file and os.path.exists(str(save_file)):
                save_path = Path(str(save_file)).parent
                if not save_path.exists():
                    st.error(
                        f"Save directory '{save_path}' does not exist. Please create it first."
                    )
                    return

            attachments = st.checkbox(
                "Download attachments",
                value=defaults.get("attachments", False),
                disabled=not selected_form,
                help="Download media files (images, audio, etc.)",
            )

            st.markdown("**required*")

            if st.button(
                "Add Form",
                type="primary",
                use_container_width=True,
                disabled=not selected_form,
            ):
                if not alias:
                    st.error("Please enter an alias for the form.")
                    return

                if not form_id:
                    st.error("Please select or enter a form ID.")
                    return

                try:
                    self._add_form_to_project(
                        FormConfig(
                            alias=alias,
                            form_id=form_id,
                            server=server,
                            private_key=str(encryption_key_file) or None,
                            save_to=str(save_file) or None,
                            attachments=attachments,
                        )
                    )
                    st.success("Form added successfully")
                    st.rerun()  # Refresh the page to clear the form
                except Exception as e:
                    st.error(f"Failed to add form: {e}")

    def _get_form_options(self, server: str) -> list[tuple[str, str]] | None:
        """
        Get list of available forms for the selected server.

        Returns
        -------
            List of tuples (form_id, form_title) or None if connection failed
        """
        try:
            # Check if we have a connection for this server
            if not self._ensure_server_connection(server):
                return None

            with st.spinner(f"Loading forms from {server}..."):
                # Get list of forms
                forms = self._scto_client.list_forms()

                form_options = []
                for form in forms:
                    try:
                        # Get form definition to extract title
                        form_def = self._scto_client.get_form_definition(form)

                        # Extract title from form definition
                        title = self._extract_form_title(form_def, form)
                        form_options.append((form, title))

                    except Exception as e:
                        # If we can't get the title, just use the form ID
                        self.logger.warning(f"Could not get title for form {form}: {e}")
                        form_options.append((form, "Title unavailable"))

                # Sort by form ID for consistency
                form_options.sort(key=lambda x: x[0])
                return form_options

        except Exception as e:
            self.logger.exception(f"Failed to load forms for server {server}")
            st.error(f"Failed to load forms: {e}")
            return None

    def _extract_form_title(self, form_def: dict, form_id: str) -> str:
        """
        Extract form title from form definition.

        Args:
            form_def: Form definition dictionary from SurveyCTO
            form_id: Form ID as fallback

        Returns
        -------
            Form title or form_id if title not found
        """
        try:
            # Try to get title from settings
            if "settings" in form_def:
                settings = form_def["settings"]
                if isinstance(settings, list) and len(settings) > 1:
                    # Settings is usually a list where first row is headers
                    headers = settings[0] if settings else []
                    data = settings[1] if len(settings) > 1 else []

                    # Look for title in common field names
                    title_fields = ["form_title", "title", "form_name", "name"]
                    for field in title_fields:
                        if field in headers:
                            index = headers.index(field)
                            if index < len(data) and data[index]:
                                return str(data[index])

            # Try to get title from survey sheet
            if "fieldsRowsAndColumns" in form_def:
                fields = form_def["fieldsRowsAndColumns"]
                if len(fields) > 1:
                    headers = fields[0]
                    # Look for a title field in the first few rows
                    for i in range(1, min(5, len(fields))):
                        row = fields[i]
                        if len(row) > 1 and "title" in str(row).lower():
                            # This is a heuristic - might need adjustment
                            continue
            else:
                # If no title found, return form_id
                return form_id

        except Exception as e:
            self.logger.warning(f"Error extracting title for form {form_id}: {e}")
            return form_id

    def _ensure_server_connection(self, server: str) -> bool:
        """
        Ensure we have a valid connection to the specified server.

        Returns
        -------
            True if connection is valid, False otherwise
        """
        try:
            # Check if we already have a connection
            if self._scto_client is not None:
                # Verify it's for the right server by testing a simple call
                try:
                    self._scto_client.list_forms()
                    return True  # noqa: TRY300
                except:
                    # Connection is stale, clear it
                    self._scto_client = None

            # Try to reconnect using cached credentials
            cached_credentials = self.cache_manager.get_server_cache()
            if cached_credentials and cached_credentials.get("server") == server:
                credentials = ServerCredentials(**cached_credentials)
                self.connect(credentials)
                return self._scto_client is not None
            else:
                return False

        except Exception:
            self.logger.exception(f"Failed to ensure connection to {server}")
            return False

    def _get_server_list(self) -> list[str]:
        """Get list of available servers from cache."""
        try:
            cache = self.client.cache_manager.get_server_cache()

            # Handle both single server and multiple servers
            if isinstance(cache, dict):
                server = cache.get("server", "")
                if server:
                    return [server]

            else:
                return []

        except Exception as e:
            self.logger.warning(f"Failed to get server list: {e}")
            return []

    def _add_form_to_project(self, form_config: FormConfig) -> None:
        """Add form configuration to project."""
        # Check for duplicate alias
        import_log = duckdb_get_table(
            self.project_id, alias="import_log", db_name="logs"
        )
        if form_config.alias in import_log.get_column("alias").to_list():
            raise ValidationError(f"Alias '{form_config.alias}' already exists")

        # Add to import log
        new_entry = {
            "refresh": True,
            "load": True,
            "source": "SurveyCTO",
            "alias": form_config.alias,
            "filename": "",
            "sheet_name": "",
            "server": form_config.server,
            "form_id": form_config.form_id,
            "private_key": form_config.private_key,
            "save_to": form_config.save_to,
            "attachments": form_config.attachments,
        }

        updated_log = pl.concat([import_log, pl.DataFrame([new_entry])], how="vertical")
        duckdb_save_table(
            self.project_id, updated_log, alias="import_log", db_name="logs"
        )


# --- Main Functions --- #


def download_forms(project_id: str, form_configs: list[FormConfig]) -> None:
    """Download data for multiple forms with progress tracking."""
    if not form_configs:
        st.warning("No forms selected for download")
        return

    client = SurveyCTOClient(project_id)
    progress_bar = st.progress(0, text="Downloading from SurveyCTO...")

    for i, form_config in enumerate(form_configs):
        try:
            new_count = client.import_data(form_config)
            st.write(
                f"{i + 1}/{len(form_configs)}: Downloaded {new_count} new records for {form_config.alias}"
            )
        except Exception as e:
            st.error(f"Failed to download {form_config.alias}: {e}")
        finally:
            progress_bar.progress(
                (i + 1) / len(form_configs),
                text=f"Progress: {i + 1}/{len(form_configs)}",
            )

    st.success("Download complete")
