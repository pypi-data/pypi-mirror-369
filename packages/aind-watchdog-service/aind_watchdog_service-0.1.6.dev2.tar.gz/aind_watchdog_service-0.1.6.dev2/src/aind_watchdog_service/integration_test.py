import argparse
import datetime
import os
import subprocess
from pathlib import Path, PurePosixPath
from datetime import datetime as dt
from typing import Optional
import yaml

from mpetk.mpeconfig import source_configuration
from mpetk.mpeconfig.python_3.mpeconfig import get_platform_paths

from aind_watchdog_service.models.manifest_config import (
    ManifestConfig,
    make_standard_transfer_args,
)


def make_large_random_file(path: Path, size_mb: int = 50):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as file:
        file.write(os.urandom(size_mb * 1_000_000))


def make_dummy_data(folder: Path) -> tuple[dict[str, list[Path]], list[Path]]:
    """Make some files to be copied, both data (by modality) and metadata"""
    modalities = {
        "behavior": ["test.txt", "test2.txt"],
        "behavior-videos": ["test.txt", "test2.txt", {"directory": ["test.txt"]}],
    }
    for modality, files in modalities.items():
        files_actual = []
        for item in files:
            if isinstance(item, dict):
                for dir, filenames in item.items():
                    path = folder / modality / dir
                    path.mkdir(parents=True, exist_ok=True)
                    for filename in filenames:
                        path_file = path / filename
                        if not path_file.exists():
                            make_large_random_file(path_file)
                    files_actual.append(str(path))
            else:
                path = folder / modality / item
                if not path.exists():
                    make_large_random_file(path)
                files_actual.append(str(path))
        modalities[modality] = files_actual  # replace with resolved path

    metadata_files = [folder / "session.json"]
    for path in metadata_files:
        make_large_random_file(path)

    return modalities, metadata_files


def make_manifest(
    data_by_modality: dict[str, list[Path]],
    metadata: list[Path],
    destination: str,
    transfer_endpoint: str,
    extra_identifying_info: dict,
    name_prefix: str = "test",
    **kwargs,
):

    now = dt.now()

    manifest = ManifestConfig(
        name=name_prefix + "_" + now.strftime("%Y-%m-%d_%H-%M-%S"),
        platform="multiplane-ophys",
        processor_full_name="User Name",
        subject_id=614173,  # test mouse
        acquisition_datetime=now,
        # schedule_time=now
        s3_bucket="private",
        destination=destination,
        # capsule_id='',
        # mount=self.config["mount"],
        modalities=data_by_modality,
        schemas=[str(path) for path in metadata],
        project_name="Dynamic Routing",
        transfer_endpoint=transfer_endpoint,
        extra_identifying_info=extra_identifying_info,
        **kwargs,
    )

    return manifest


def run_test(
    test_data_dir: Optional[Path] = None,
    destination: str = r"\\allen\aind\scratch\SIPE\test_watchdog",
    transfer_endpoint: str = "http://aind-data-transfer-service-dev/api/v2/submit_jobs",
):

    watchdog_config = source_configuration(
        "aind_watchdog_service",
        send_start_log=False,
        fetch_logging_config=False,
    )

    manifest_directory = Path(watchdog_config["flag_dir"])

    if test_data_dir is None:
        log_dir, config_dir = get_platform_paths(watchdog_config, "aind_watchdog_service")
        test_data_dir = Path(log_dir).parent / "test_data"
        more_test_data_dir = Path(log_dir).parent / "more_test_data"
    test_data_dir = test_data_dir.resolve()
    more_test_data_dir = test_data_dir.resolve()

    # Generate some test data
    data_by_modality, metadata = make_dummy_data(test_data_dir)
    print(f"Data created at {test_data_dir}")

    manifest = make_manifest(
        data_by_modality,
        metadata,
        destination,
        transfer_endpoint,
        {
            "datetime": dt.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "test_type": "Basic Integration Test",
        },
    )
    path = manifest.write_standard_file(manifest_directory)

    print(f"Manifest created at {path}")

    # Generate some more test data
    data_by_modality, metadata = make_dummy_data(more_test_data_dir)
    manifest2 = make_manifest(
        data_by_modality,
        metadata,
        destination,
        transfer_endpoint,
        {
            "datetime": dt.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "test_type": "Integration Test with transfer_service_args and delete",
        },
        name_prefix="test_transfer_service_args",
        checksum_mode_override="no_check",
    )
    manifest2.delete_modalities_source_after_success = True
    submit_request = make_standard_transfer_args(manifest2)
    manifest2.transfer_service_args = submit_request
    path = manifest2.write_standard_file(manifest_directory)

    print(f"Manifest created at {path}")


if __name__ == "__main__":
    run_test()
