"""Module to run jobs on file modification"""

import json
import logging
import os
import platform
import subprocess
from pathlib import Path, PurePosixPath
import shutil
from typing import Optional
import time
import re
import crc32c

import requests

from aind_watchdog_service.models.manifest_config import (
    IngestedManifest,
    make_standard_transfer_args,
    check_for_missing_data,
)
from aind_watchdog_service.models.watch_config import WatchConfig

if platform.system() == "Windows":
    PLATFORM = "windows"
else:
    PLATFORM = "linux"


class RunJob:
    """Run job class to stage files on VAST or run a custom script
    and trigger aind-data-transfer-service
    """

    def __init__(
        self,
        src_path: str,
        config: IngestedManifest,
        watch_config: WatchConfig,
    ):
        """initialize RunJob class"""
        self.src_path = src_path
        self.config = config
        self.watch_config = watch_config

    def copy_to_vast(self) -> bool:
        """Determine platform and copy files to VAST

        Returns
        -------
        bool
            status of the copy operation
        """
        parent_directory = self.config.name
        destination = self.config.destination
        modalities = self.config.modalities
        for modality in modalities.keys():
            destination_directory = Path(destination) / parent_directory / modality
            if not destination_directory.is_dir():
                destination_directory.mkdir(parents=True)
            for file in modalities[modality]:
                if PLATFORM == "windows":
                    transfer = self.execute_windows_command(file, destination_directory)
                else:
                    transfer = self.execute_linux_command(file, destination_directory)
                if not transfer:
                    logging.error("Error copying files %s", file)
                    return False
        for schema in self.config.schemas:
            destination_directory = os.path.join(destination, parent_directory)
            if PLATFORM == "windows":
                transfer = self.execute_windows_command(schema, destination_directory)
            else:
                transfer = self.execute_linux_command(schema, destination_directory)
            if not transfer:
                logging.error("Error copying schema %s", schema)
                return False
        return True

    def run_subprocess(self, cmd: list) -> subprocess.CompletedProcess:
        """subprocess run command

        Parameters
        ----------
        cmd : list
            command to execute

        Returns
        -------
        subprocess.CompletedProcess
            subprocess completed process
        """
        logging.debug("Executing command: %s", cmd)
        subproc = subprocess.run(
            cmd, check=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        return subproc

    def get_robocopy_log_path(self) -> Optional[str]:
        """Get the robocopy log file path from watch_config.robocopy_args.

        Returns
        -------
        Optional[str]
            Path to the robocopy log file if specified, otherwise None.
        """
        args = self.watch_config.robocopy_args
        log_pattern = re.compile(r"/log\+?:(.+)")
        for arg in args:
            match = log_pattern.match(arg)
            if match:
                return match.group(1)
        return None

    def parse_robocopy_log(self, log_file_path: str) -> list:
        """Parse the robocopy log file to fetch error details for the latest run.

        Parameters
        ----------
        log_file_path : str
            Path to the robocopy log file.

        Returns
        -------
        list
            A list containing error details.
        """
        error_details = []
        error_pattern = re.compile(r"(ERROR)\s+\d+\s+\(0x[0-9A-F]+\)\s+(.+)\s+(.+)")
        start_pattern = re.compile(r"^ *Started : ")

        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()

        # Read the log file in reverse to find the latest run
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if start_pattern.match(line):
                break
            match = error_pattern.search(line)
            if match:
                error_message = " ".join(match.groups())
                additional_message = (
                    lines[i + 1].strip()
                    if i + 1 < len(lines)
                    else "No additional error message"
                )
                error_message = f"{error_message} - {additional_message}"
                # Avoid duplicate error messages for the same file when retrying
                if error_message not in error_details:
                    error_details.append(error_message)

        return error_details

    def validate_file_integrity(self, src_file: Path, dest_file: Path, extra_log_context: Optional[dict] = None) -> bool:
        """Compare source and destination files to make sure they match and nothing went wrong in the transfer.
        
        Configurable to take three different actions:
            1. Nothing, don't check anything and just trust robocopy
            2. Compare file sizes - not super robust but it is fast.
            3. Compare CRC32C checksums - more robust but slower, especially for large files.
        """
        t0 = time.time()
        
        log_dict = {
            "Checksum Mode": self.config.checksum_mode,
            "Source": src_file,
            "Destination": dest_file,
        } | self.config.log_tags
        if extra_log_context:
            log_dict.update(extra_log_context)

        logging.info({"Action": "Beginning file integrity check"} | log_dict)

        match self.config.checksum_mode:
            case "no_check":
                success = True
            case "file_size":
                src_size = src_file.stat().st_size
                dest_size = dest_file.stat().st_size
                log_dict["Source Size"] = src_size
                log_dict["Destination Size"] = dest_size
                success = src_size == dest_size
            case "crc32":
                src_checksum = self.calculate_crc32c(src_file)
                dest_checksum = self.calculate_crc32c(dest_file)
                log_dict["Source Checksum"] = src_checksum
                log_dict["Destination Checksum"] = dest_checksum
                success = src_checksum == dest_checksum

        if success:
            logging.info(
                {
                    "Action": "File integrity check passed",
                    "Duration_s": int(time.time() - t0),
                }
                | log_dict,
            )
        else:
            logging.warning(
                {
                    "Error": "File integrity check failed",
                    "Duration_s": int(time.time() - t0),
                }
                | log_dict
            )

        return success

    def calculate_crc32c(self, file_path: str) -> str:
        """Calculate the CRC32C checksum of a file with optimized handling for large files.

        Parameters
        ----------
        file_path : str
            Path to the file.

        Returns
        -------
        str
            CRC32C checksum as a hexadecimal string.
        """
        file_size = os.path.getsize(file_path)
        chunk_size = self.watch_config.checksum_parameters.chunk_size
        threshold = self.watch_config.checksum_parameters.file_size_threshold
        checksum = 0

        with open(file_path, "rb") as f:
            if file_size <= threshold:
                # For smaller files, read the entire file at once
                checksum = crc32c.crc32c(f.read())
            else:
                # For larger files, process in chunks
                while chunk := f.read(chunk_size):
                    checksum = crc32c.crc32c(chunk, checksum)

        return f"{checksum:08x}"

    def execute_windows_command(self, src: str, dest: str) -> bool:
        """copy files using windows robocopy command or shutil

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """
        if not Path(src).exists():
            logging.error(
                {
                    "Error": "Source file does not exist",
                    "File": src,
                    "Destination": dest,
                }
                | self.config.log_tags
            )
            return False

        for attempt in range(self.watch_config.checksum_parameters.max_retries):
            t0 = time.time()
            if self.watch_config.windows_copy_utility == "shutil":
                if not self.execute_shutil(src, dest):
                    return False  # No need to try validating if the copy failed
            else:
                if not self.execute_robocopy(src, dest):
                    return False

            logging.info(
                {
                    "Action": "Copy complete.",
                    "Source": src,
                    "Destination": dest,
                    "Duration_s": int(time.time() - t0),
                    "Attempt": attempt + 1,
                }
                | self.config.log_tags
            )

            if Path(src).is_dir():
                # Validate all files in the directory
                checksum_mismatch = False
                for root, _, files in os.walk(src):
                    for file in files:
                        src_file = Path(root) / file
                        dest_file = dest / Path(root).relative_to(src) / file
                        if not self.validate_file_integrity(src_file, dest_file, extra_log_context={'Attempt': attempt + 1}):
                            dest_file.unlink(missing_ok=True)  # Delete invalid file
                            checksum_mismatch = True
                            break
                    if checksum_mismatch:
                        break

                if not checksum_mismatch:
                    return True  # All files validated successfully
            else:
                dest_file = Path(dest) / Path(src).name
                if self.validate_file_integrity(Path(src), dest_file):
                    return True
                else:
                    dest_file.unlink(missing_ok=True)  # Delete invalid file

        # If we reach here, all attempts failed. Delete the destination file(s)
        if Path(dest).is_dir():
            with os.scandir(dest) as entries:
                for entry in entries:
                    if entry.is_file():
                        file_path = Path(entry.path)
                        file_path.unlink(missing_ok=True)
                    elif entry.is_dir():
                        shutil.rmtree(entry.path, ignore_errors=True)
        else:
            dest_file = Path(dest) / Path(src).name
            dest_file.unlink(missing_ok=True)

        logging.error(
            {
                "Error": "Max retries exceeded for checksum validation. Deleting all files on destination.",
                "Source": src,
                "Destination": dest,
            }
            | self.config.log_tags
        )
        return False

    def execute_shutil(self, src: str, dest: str) -> bool:
        """copy files using shutil

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """

        try:
            if Path(src).is_dir():
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy(src, dest)
            return True
        except:
            logging.exception(
                {
                    "Error": "Could not copy file",
                    "File": src,
                    "Destination": dest,
                }
                | self.config.log_tags,
                extra={"emit_exc": True},
            )
            return False

    def execute_robocopy(self, src: str, dest: str) -> bool:
        """copy files using windows robocopy command

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """
        if Path(src).is_dir():
            run = self.run_subprocess(
                ["robocopy", src, dest] + self.watch_config.robocopy_args,
            )
        else:
            # Robocopy used over xcopy for better performance
            # /j: unbuffered I/O (to speed up copy)
            # /e: copy subdirectories (includes empty subdirs), /r:5: retry 5 times
            run = self.run_subprocess(
                [
                    "robocopy",
                    str(Path(src).parent),
                    dest,
                    Path(src).name,
                ]
                + self.watch_config.robocopy_args,
            )

        # Robocopy return code documentation:
        # https://learn.microsoft.com/en-us/troubleshoot/windows-server/backup-and-storage/return-codes-used-robocopy-utility # noqa
        if run.returncode > 7:
            error_details = {
                "Error": "Could not copy file",
                "File": src,
                "Destination": dest,
                "Robocopy Return Code": run.returncode,
            }

            log_file_path = self.get_robocopy_log_path()
            if log_file_path:
                robocopy_error_details = self.parse_robocopy_log(log_file_path)
                logging.error(
                    error_details
                    | {"Robocopy Error Details": robocopy_error_details}
                    | self.config.log_tags
                )
            else:
                logging.error(error_details | self.config.log_tags)
            return False
        return True

    def execute_linux_command(self, src: str, dest: str) -> bool:
        """copy files using linux cp command

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """
        # Rsync used over cp for better performance
        # -r: recursive, -t: preserve modification times
        if not Path(src).exists():
            logging.error(
                {
                    "Error": "Source file does not exist",
                    "File": src,
                    "Destination": dest,
                }
                | self.config.log_tags
            )
            return False
        if Path(src).is_dir():
            run = self.run_subprocess(["rsync", "-r", "-t", src, dest])
        else:
            run = self.run_subprocess(["rsync", "-t", src, dest])
        if run.returncode != 0:
            logging.error(
                {
                    "Error": "Could not copy file",
                    "File": src,
                    "Destination": dest,
                    "Rsync Return Code": run.returncode,
                }
                | self.config.log_tags
            )
            return False
        return True

    def trigger_transfer_service(self) -> requests.Response:
        """Triggers aind-data-transfer-service"""
        if self.config.transfer_service_args is None:
            submit_request = make_standard_transfer_args(self.config)
            post_request_content = json.loads(
                submit_request.model_dump_json(round_trip=True)
            )
        else:
            post_request_content = self.config.transfer_service_args

        logging.info("Submitting job to aind-data-transfer-service")
        submit_job_response = requests.post(
            url=self.config.transfer_endpoint, json=post_request_content, timeout=30
        )
        return submit_job_response

    def delete_modalities_source(self):
        """Delete everything in manifest "modalities" key"""

        for modality, sources in self.config.modalities.items():
            for source in sources:
                path = Path(source)
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                except Exception as e:
                    logging.warning(
                        {
                            "Warning": "Could not remove source data",
                            "Source": path,
                            "Modality": modality,
                        }
                        | self.config.log_tags,
                        exc_info=True,
                    )

    def move_manifest_to_archive(self) -> None:
        """Move manifest file to archive"""
        archive = self.watch_config.manifest_complete
        if PLATFORM == "windows":
            copy_file = self.execute_windows_command(self.src_path, archive)
            if not copy_file:
                logging.error("Error copying manifest file %s", self.src_path)
                return
            os.remove(self.src_path)
        else:
            self.run_subprocess(["mv", self.src_path, archive])

    def run_job(self) -> None:
        """Triggers the vast transfer service

        Parameters
        ----------
        event : FileCreatedEvent
            modified event file
        """
        try:
            start_time = time.time()
            logging.info(
                {"Action": "Running job"} | self.config.log_tags,
                extra={"weblog": True},
            )

            # Check for missing data
            missing_files, missing_schema = check_for_missing_data(self.config)

            if missing_files or missing_schema:
                logging.error(
                    {
                        "Error": "Missing files when executing manifest",
                        "Missing data": missing_files,
                        "Missing schema": missing_schema,
                    }
                    | self.config.log_tags
                )
                return

            transfer = self.copy_to_vast()
            if not transfer:
                logging.error({"Error": "Could not copy to VAST"} | self.config.log_tags)
                return
            after_copy_time = time.time()
            logging.info(
                {
                    "Action": "Data copied to VAST",
                    "Duration_s": int(after_copy_time - start_time),
                }
                | self.config.log_tags
            )

            if self.config.transfer_endpoint is not None:
                response = self.trigger_transfer_service()
                if not response.status_code == 200:
                    logging.error(
                        {
                            "Error": "Could not trigger aind-data-transfer-service",
                            "Response": response.status_code,
                            "Message": response.text,
                        }
                        | self.config.log_tags
                    )
                    return
                after_post_time = time.time()
                logging.info(
                    {
                        "Action": "AIND Data Transfer Service notified",
                        "Duration_s": int(after_post_time - after_copy_time),
                    }
                    | self.config.log_tags
                )

            if self.config.delete_modalities_source_after_success:
                self.delete_modalities_source()
                logging.info(
                    {"Action": "Modality source deleted"} | self.config.log_tags,
                    extra={"weblog": True},
                )

            end_time = time.time()

            logging.info(
                {"Action": "Job complete", "Duration_s": int(end_time - start_time)}
                | self.config.log_tags,
                extra={"weblog": True},
            )
            self.move_manifest_to_archive()
        except:
            logging.exception(
                {"Error": "Job failed"} | self.config.log_tags,
                extra={"emit_exc": True},
            )
