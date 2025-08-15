# aind_watchdog_service

Since the transfer of aind_watchdog_service into SIPE's control, it now lives and builds on SIPE's gitlab, with a mirror pushing updates to AllenNeuralDynamic's github repo.

It is published to pypi via a github action that runs when a Github Release is created.

## Usage

Watchdog runs in the background, and watches a directory for newly-created yaml files containing instructions to transfer files. To use, `pip install aind-watchdog-service` and use the `aind_watchdog_service.models.ManifestConfig` object to write your manifest file in the proper format. See the examples/ folder in this repo for more details.

## Configuration

Watchdog is configured using SIPE's configuration zookeeper server. The configuration options are listed in /src/aind_watchdog_service/models/watch_config.py.

## Monitoring

Watchdog logs can be monitored from the main SIPE logserver (http://eng-logtools:8080/?channel_filter=watchdog&hide=location,count) or this [grafana dashboard](http://eng-tools/grafana/d/de377sfsa9fcwf/watchdog-service-logs?var-acquisition_age=7d&orgId=2&from=now-7d&to=now&timezone=browser&var-hostname=$__all&refresh=auto).

## Deployment
Watchdog should be deployed on a SIPE-accessible rig via the install-aind_watchdog_service.yml ansible script. This will download the app and set up a windows scheduled task to run the service. By default, the scheduled task includes a nightly restart at 11:30pm. If the task is running, the scheduler will kill the old instance and start the new one - due to how task scheduler force kills processes, the death of an old process will not generate a stop log.

When deploying on a new rig that had previously had the non-SIPE version of watchdog installed, extra care must be taken. 
- First, delete any scheduled tasks relating to watchdog. Some of these may be in a folder called "GUI Automation" or "AIND".
- Next, run `tasklist` to check if there active watchdog processes, and kill them all with repeated use of `taskkill /F /PID pid_of_the_process`.
    - One running instance of watchdog will have two processes listed by `tasklist`
- Install the new watchdog via ansible and check for a start log.
- SSH in and run a self test with `aind_watchdog_service.exe --test` (see below) and make sure you see successful logs.

## Testing
Watchdog has a bundled test function that will create some dummy data on the rig and create a manifest file to transfer that data. Once  Run it with the below commands:

```
cd "C://Program Files/AIBS_MPE/aind_watchdog_service
aind_watchdog_service.exe --test
```

It will print something like the following:
```
Data created at C:\ProgramData\AIBS_MPE\aind_watchdog_service\logs\test_data
Manifest created at C:\Users\svc_mpe\Documents\aind_watchdog_service\manifest\test_manifest_2024-11-15_17-31-25.yml
```

Make sure that the running instance of watchdog picks up the manifest and completes the transfer.

## Development

After cloning the repo, watchdog can be installed from source with `pip install .[service]`, and run with `python src/aind_watchdog_service/main.py`.

