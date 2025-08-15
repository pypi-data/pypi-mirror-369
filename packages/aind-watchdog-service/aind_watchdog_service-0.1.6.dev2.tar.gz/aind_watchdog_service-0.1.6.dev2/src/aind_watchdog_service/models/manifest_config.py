"""Job configs for VAST staging or executing a custom script"""

from datetime import datetime, time
from functools import cached_property
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Literal, Optional
import os
import warnings
import yaml
import json

from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.platforms import Platform
from aind_data_schema_models.data_name_patterns import build_data_name
from aind_data_transfer_service.models.core import (
    SubmitJobRequestV2,
    Task,
    UploadJobConfigsV2,
)

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    SerializeAsAny,
    field_serializer,
    field_validator,
    model_validator,
    computed_field,
    PlainSerializer,
)
from typing_extensions import Annotated, Self


class ManifestConfig(BaseModel):
    """Job configs for data transfer to VAST"""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    name: Optional[str] = Field(
        None,
        description="If not provided, gets generated to match CO asset",
        title="Manifest name",
    )
    processor_full_name: str = Field(
        ..., description="User who processed the data", title="Processor name"
    )
    subject_id: int = Field(..., description="Subject ID", title="Subject ID")
    acquisition_datetime: datetime = Field(
        description="Acquisition datetime",
        title="Acquisition datetime",
    )
    schedule_time: Optional[time] = Field(
        default=None,
        description="Transfer time to schedule copy and upload. If None defaults to trigger the transfer immediately",  # noqa
        title="APScheduler transfer time",
    )
    force_cloud_sync: bool = Field(
        default=False,
        description="Overwrite data in AWS",
        title="Force cloud sync",
    )
    transfer_endpoint: Optional[str] = Field(
        default="http://aind-data-transfer-service/api/v2/submit_jobs",
        description="Transfer endpoint for data transfer",
        title="Transfer endpoint",
    )
    platform: str = Field(description="Platform type", title="Platform type")
    capsule_id: Optional[str] = Field(
        default=None, description="Capsule ID of pipeline to run", title="Capsule"
    )
    mount: Optional[str] = Field(
        default=None, description="Mount point for pipeline run", title="Mount point"
    )
    s3_bucket: Literal["private", "open", "default"] = Field(
        default="private", description="s3 endpoint", title="S3 endpoint"
    )
    project_name: str = Field(..., description="Project name", title="Project name")
    destination: str = Field(
        ...,
        description="Remote directory on VAST where to copy the data to.",
        title="Destination directory",
        examples=[r"\\allen\aind\scratch\test"],
    )
    modalities: Dict[str, List[str]] = Field(
        default={},
        description="list of ModalityFile objects containing modality names and associated files or directories",  # noqa
        title="modality files",
    )
    schemas: List[str] = Field(
        default=[],
        description="Where schema files to be uploaded are saved",
        title="Schema directory",
    )
    script: Dict[str, List[str]] = Field(
        default={},
        description="Set of commands to run in subprocess. - DEPRECATED - NONFUNCTIONAL",
        title="Commands",
    )
    transfer_service_args: Optional[SerializeAsAny[SubmitJobRequestV2]] = Field(
        default=None,
        description="Arguments to pass to data-transfer-service",
        title="Transfer service args",
    )

    transfer_service_job_type: str = Field(
        "default",
        description="Job type to pass to data-transfer-service",
        title="Transfer service job type",
    )

    delete_modalities_source_after_success: bool = False

    extra_identifying_info: Optional[dict] = None

    checksum_mode_override: Optional[Literal["no_check", "file_size", "crc32"]] = Field(
        None,
        description="If present, overrides the checksum mode in the watchdog app config",
        title="Checksum mode override",
    )

    @field_validator("name", mode="before")
    @classmethod
    def name_set_warning(cls, value):
        if value is not None:
            warnings.warn(
                "Manually setting name is discouraged, leave it as None and it will be generated",
            )
        return value

    @model_validator(mode="after")
    def set_name(self) -> Self:
        """Construct name"""
        if self.name is None:
            self.name = build_data_name(
                f"{self.platform}_{self.subject_id}",
                self.acquisition_datetime,
            )
        return self

    @field_validator("destination", mode="after")
    @classmethod
    def validate_destination_path(cls, value: str) -> str:
        """Converts path string to posix"""
        return cls._path_to_posix(value)

    @field_validator("schemas", mode="after")
    @classmethod
    def validate_schema_paths(cls, value: List[str]) -> List[str]:
        """Converts path strings to posix"""
        return [cls._path_to_posix(path) for path in value]

    @field_validator("modalities", mode="after")
    @classmethod
    def validate_modality_paths(cls, value: Dict[Any, List[str]]) -> Dict[Any, List[str]]:
        """Converts modality path strings to posix and check for existence"""

        output: dict[str, list[str]] = {}
        for modality, paths in value.items():
            output[modality] = []
            for path in paths:
                output[modality].append(cls._path_to_posix(path))

        return output

    @staticmethod
    def _path_to_posix(path: str) -> str:
        """Converts path string to posix"""
        return str(Path(path).as_posix())

    @field_validator("schedule_time", mode="before")
    @classmethod
    def normalized_scheduled_time(cls, value) -> Optional[time]:
        """Normalize scheduled time"""
        if value is None:
            return value
        else:
            if isinstance(value, datetime):
                return value.time()
            elif isinstance(value, str):
                return datetime.strptime(value, "%H:%M:%S").time()
            elif isinstance(value, time):
                return value
            else:
                raise ValueError("Invalid time format")

    @model_validator(mode="after")
    def validate_capsule(self) -> Self:
        """Validate capsule and mount"""
        if (self.capsule_id is None) ^ (self.mount is None):
            raise ValueError(
                "Both capsule and mount must be provided, or must both be None"
            )
        return self

    def write_standard_file(self, manifest_directory: Path) -> Path:
        path = Path(manifest_directory) / f"manifest_{self.name}.yml"
        json_str = self.model_dump_json(exclude_none=True)
        data = json.loads(json_str)
        with open(path, "w") as file:
            yaml.safe_dump(
                data,
                file,
                default_flow_style=False,
                sort_keys=False,
                width=float("inf"),
                allow_unicode=True,
            )
        return path


class IngestedManifest(ManifestConfig):

    name: str

    transfer_service_args: Optional[dict] = Field(
        default=None,
        description="Dump of aind_data_transfer_models.SubmitJobRequestUpload to pass to data-transfer-service",
        title="Transfer service args",
    )

    total_data_size: Optional[float] = None

    checksum_mode: Literal["no_check", "file_size", "crc32"]

    @field_validator("name", mode="before")
    @classmethod
    def name_set_warning(cls, value):
        return value  # no warning

    @staticmethod
    def _get_tree_size(path: str) -> int:
        """Return total size of files in given path and subdirs."""
        total = 0
        if os.path.isdir(path):
            for entry in os.scandir(path):
                if entry.is_dir(follow_symlinks=False):
                    total += IngestedManifest._get_tree_size(entry.path)
                else:
                    total += entry.stat(follow_symlinks=False).st_size
        else:
            total += os.path.getsize(path)
        return total

    def calculate_total_data_size(self) -> float:
        """Calculate the total size of the data in megabytes."""

        total_size = 0
        for files in self.modalities.values():
            for file in files:
                try:
                    total_size += self._get_tree_size(file)
                except:
                    return None
        total_size_mb = total_size / 1024**2  # convert to MB
        self.total_data_size = round(total_size_mb, 2)

    @property
    def log_tags(self) -> dict:
        if self.total_data_size is None:
            print("calculating data size")
            self.calculate_total_data_size()
        return {
            "name": self.name,
            "subject_id": self.subject_id,
            "project_name": self.project_name,
            "modalities": list(self.modalities.keys()),
            "data_size_mb": self.total_data_size,
            "checksum_mode": self.checksum_mode,
            "extra_identifying_info": self.extra_identifying_info,
        }


def make_standard_transfer_args(manifest: ManifestConfig) -> SubmitJobRequestV2 | None:
    """Constructs arguments for aind-data-transfer-service v2 API."""

    if len(manifest.modalities) == 0:
        return None

    modality_transformation_settings = {}
    for modality in manifest.modalities.keys():
        modality_transformation_settings[modality] = Task(
            job_settings={
                "input_source": str(
                    PurePosixPath(manifest.destination) / manifest.name / modality
                )
            }
        )

    gather_preliminary_metadata = Task(
        job_settings={
            "metadata_dir": str(PurePosixPath(manifest.destination) / manifest.name)
        }
    )

    upload_job_configs_v2 = UploadJobConfigsV2(
        job_type=manifest.transfer_service_job_type,
        project_name=manifest.project_name,
        platform=Platform.from_abbreviation(manifest.platform),
        modalities=[Modality.from_abbreviation(m) for m in manifest.modalities.keys()],
        subject_id=str(manifest.subject_id),
        acq_datetime=manifest.acquisition_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        tasks={
            "modality_transformation_settings": modality_transformation_settings,
            "gather_preliminary_metadata": gather_preliminary_metadata,
        },
    )

    submit_request_v2 = SubmitJobRequestV2(
        upload_jobs=[upload_job_configs_v2],
    )

    post_request_content = submit_request_v2
    return post_request_content


def check_for_missing_data(manifest: ManifestConfig) -> tuple[list[str], list[str]]:
    """Check for missing files in manifest"""
    missing_files = []
    for modality, paths in manifest.modalities.items():
        for path in paths:
            if not Path(path).exists():
                missing_files.append(path)

    missing_schema = [path for path in manifest.schemas if not Path(path).exists()]
    return missing_files, missing_schema
