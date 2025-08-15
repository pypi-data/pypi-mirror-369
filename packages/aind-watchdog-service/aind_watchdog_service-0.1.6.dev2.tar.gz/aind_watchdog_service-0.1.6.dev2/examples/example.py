from aind_watchdog_service.models import ManifestConfig


# Create manifest
manifest = ManifestConfig(
    subject_id="726087",
    acquisition_datetime="2024-06-18 10:34:32.749880",
    schedule_time="03:00:00",
    transfer_endpoint="http://aind-data-transfer-service-dev/api/v1/submit_jobs",
    platform="multiplane-ophys",
    mount="ophys",
    s3_bucket="private",
    project_name="Learning mFISH-V1omFISH",
    modalities={
        "behavior": [
            r"\\W10SV109650002\mvr\data\1374103167_Behavior_20240618T103420.mp4"
        ],
        "ophys": [r"D:\scanimage_ophys\data\1374103167\1374103167_averaged_depth.tiff"],
    },
    schemas=[
        "C:/ProgramData/aind/rig.json",
        r"D:\scanimage_ophys\data\1374103167\session.json",
        r"D:\scanimage_ophys\data\1374103167\data_description.json",
    ],
    processor_full_name="Chris P. Bacon",
    destination=r"//allen/aind/scratch/2p-working-group/data-uploads",
    capsule_id="private",
)


manifest.write_standard_file(".")
