[![Build Status](https://jenkins.cognicept.systems/buildStatus/icon?job=cognicept-shell-pipeline)](https://jenkins.cognicept.systems/job/cognicept-shell-pipeline/)


# COGNICEPT SHELL #

This is a shell utility to manage Cognicept tools.

  * [Installation](#installation)
    + [Dependencies](#dependencies)
    + [Package installation](#package-installation)
  * [Usage](#usage)
    + [Commands](#commands)
  * [Building](#building)
    + [Tests](#tests)
    + [Build](#build)
    + [Upload](#upload)
  * [Contribution](#contribution)
  * [Version history](#version-history)

## Installation

### Dependencies

You need:

* Python 3 (NOTE: should be python 3.8 for dependecies)
* Python 3 PIP
* `openssh-server` : (Optional) in order to enable terminal function for Kriya

Install:

```
sudo apt-get install python3 python3-pip
```

### Package Installation

To install the package locally, run:

```
pip3 install -e <path-to-the-repo>
```

To install from Python Package Index (PyPI), run:

```
pip3 install cognicept-shell
```

To verify installation, try to run

```
cognicept -h
```

If you get `cognicept: command not found` error, make sure that `~/.local/bin/` is in your `$PATH`. You could run this:

```
export PATH=$PATH:/home/$USER/.local/bin/
```
and add it to your `.bashrc` file.

### Autocomplete

To set-up autcomplete when using the cognicept shell, run:

```
cognicept config --autocomplete
```
Restart the terminal and autocomplete should be functioning

This will setup python argcomplete globally and may affect other packages. If argcomplete has been setup globally for other project, this setup is not required.

This command essentially calls the function `activate-global-python-argcomplete`

More information about this can be found in https://pypi.org/project/argcomplete/#activating-global-completion

## Usage

For details on usage, use

```
cognicept -h
```

### Commands

#### `config`: Configure Cognicept tools

`cognicept-shell` and Cognicept agents are configured in `runtime.env` file typically placed in `~/.cognicept/runtime.env`. The file defines the docker environment used by the Cognicept agents. 

This command allows to inspect and modify the configuration file. You can use parameter `--path` to modify the path to the Cognicept config directory.

To print full configuration, run:

```
cognicept config --read
```

To add new configuration parameter (or modify single value), run:

```
cognicept config --add
```

Variables used by `cognicept-shell`:

* `COGNICEPT_ACCESS_KEY`
* `COGNICEPT_API_URI`
* `COGNICEPT_USER_API_URI`
* `COG_AGENT_CONTAINERS`
* `COG_AGENT_IMAGES`
* `COG_EXTRA_IMAGES` : images to pull from Cognicept and general docker image repositories
* `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`: temporary AWS credentials modified by `keyrotate` and needed for `update`
* `COG_ENABLE_SSH`
* `COG_ENABLE_SSH_KEY_AUTH`
* `COG_ENABLE_AUTOMATIC_SSH`
* `COG_SSH_DEFAULT_USER`

To setup `ssh` access from `remote_intervention_agent` to the host machine, run:

```
cognicept config --ssh
```

It will generate ssh keys in `~/.cognicept/ssh/` and configures `COG_ENABLE_SSH`, `COG_ENABLE_SSH_KEY_AUTH`, `COG_ENABLE_AUTOMATIC_SSH`, `COG_SSH_DEFAULT_USER` according to the user preferences. If `COG_ENABLE_AUTOMATIC_SSH` is enabled, public key is copied into `~/.ssh/authorized_hosts`; `sudo` access is requested to perform this action.


To setup autocomplete from cognicept shell, run:
```
cognicept config --auto
```

#### `status`: Get status of Cognicept agents

```
cognicept status
```
Prints status of agents and other containers managed by `cognicept-shell`. Possible values:

* "ONLINE": Everything fine
* "CONTAINER NOT FOUND": Agent/container is not initiated
* "OFFLINE": Container stopped
* "Error": Error accessing API
* "ERROR": Detected error, needs inspection
* "NOT INITIALIZED": Agent is in init state
* "STALE": Agent didn't update within last minute   

#### `version`: Display Cognicept Shell and Container version

```
cognicept version
```
Prints the version of current cognicept shell and other containers version


#### `update`: Update Cognicept tools

Updates images for agents and tools specified in `COG_AGENT_IMAGES` and `COG_EXTRA_IMAGES` config variables. It requires temporary credentials to be valid. If the available disk space is less than 3 GB, the update will not proceed. This check ensures that there is sufficient space for the update to run successfully. For updates to take effect, containers need to be restarted with `restart` command.


To run update in detached mode:
```
cognicept update -d
```
In detached mode, printing of update statuses in muted. Update is run in a seperate process. Update will continue to run even if terminal session is closed.

To update docker images in environment variable `COGNICEPT_EXTRA_IMAGES`
```
cognicept update --image <docker-images-repo>
```

To override the disk space check before pulling images:
```
cognicept update -s
```
the disk space check will be bypassed, and the update will proceed regardless of the available disk space

By default, `cognicept update` doe not update the config, to update the config run 

```
cognicept update --configuration
```

This will update the configs wihout updating the agents

#### `lastevent`: Display last event log reported by Cognicept agent

Displays last event saved by `cgs_diagnostics_agent` from `~/.cognicept/logs`.

#### `start`/`stop`/`restart`: start/stop/restart cognicept agents

These commands are used to start/stop/restart containers specified in `COG_AGENT_CONTAINERS`/`COG_AGENT_IMAGES`. Certain container names are reserved for Cognicept agents and are preconfigured:

* `cgs_diagnostics_agent`
* `remote_intervention_agent`
* `kriya_watchdog`
* `cgs_diagnostics_ecs_api`
* `cgs_diagnostics_streamer_api`
* `cgs_bagger_server`
* `health_aggregator`
* `diagnostics_aggregator`
* `kopilot`
* `smartplus_sound`
* `map_manager`
* `computer_health_metrics`
* `slamtec_adapter`
* `cam_capture`

Any agent name or image type can be put in the list as long as default command for the image is specified. All containers are started in `host` network mode.

Following are examples for using `start`. `stop` follows same API as `start`. `restart` first calls `stop` and then `stop` .

To start all listed agents `COG_AGENT_CONTAINERS` don't specify any argument:

```
cognicept start
```

To start all agents:

```
cognicept start --agents
```

To start specific agents:

```
cognicept start remote_intervention_agent cgs_diagnostics_agent
```

To run restart in detached mode:

```
cognicept restart -d
```

Detached mode is particularly useful for restarting a cognicept agent remotely. 
In detached mode, progress of restart will not printed. 

To restart and clearing logs
```
cognicept restart --prune
```

#### `keyrotate`: Rotate Cognicept cloud keys

Updates temporary AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) using `COGNICEPT_ACCESS_KEY` from `COGNICEPT_API_URI`. The validity of the credentials is 12 hours. Internet access with HTTPS allowed is needed.

#### `record`: Manage rosbag recording session to start/stop/pause/resume/get status/record all topics

These commands are used to start/stop/pause/resume/get status/record all topics in a rosbag. All the operations are done by running an `exec` command inside the `cgs_bagger_server` container. All bags are typically placed in the `bags` folder of the Cognicept configuration directory: `~/.cognicept/bags/`

To start start a recording session list all topics to be recorded separated by a space and with their `/` prefix:

```
cognicept record --start /odom /cmd_vel /rosout_agg /tf /tf_static
```

To record ALL topics use `--all`:

**NOTE:** rosbags tend to become quite big quite fast especially if there are camera topics. If there is less than 1 GB disk space, the recording self terminates.

```
cognicept record --all
```

To stop a recording session:

```
cognicept record --stop
```

Alternatively, the latest bag recording can be stopped and automatically pushed to the Cognicept cloud with a single command by providing `autopush` value:

```
cognicept record --stop autopush
```

To pause a recording session:

```
cognicept record --pause
```

To resume a recording session:

```
cognicept record --resume
```

To get the status of the current recording:

```
cognicept record --status
```

Status can be `Ready`, `Started`, `Stopped`, `Paused` and `Resumed`.

**NOTE:** A note on the retry mechanisms built in to improve reliability. If the retry mechanism fails, both `cognicept record --start` and `cognicept record --all` will automatically restart the `cgs_bagger_server`. A new recording session needs to be started if this happens. All other commands will just inform that the retry has failed since these are not essential operations for bag recording.

#### `push`: Push data to Cognicept cloud

These commands are used to push data on to the Cognicept cloud.

To push a bag file, specify the name of the bag file:

```
cognicept push --bag sample_recording.bag
```
**NOTE:** Only bags in the dedicated Cognicept configuration `bags` directory, usually `~/.cognicept/bags`, will be detected and uploaded. Bag files in any other location need to be moved to this directory before upload. Bag files generated using the `cognicept record` feature will be automatically placed in the Cognicept configuration `bags` directory.

As a shorthand, you can push the latest bag file recording by not specifying any argument. This will automatically look for the latest bag file by create time and upload it:
```
cognicept push --bag
```

#### `init`: Initiates the runtime.env file with values from the COGNICEPT_USER_API_URI
To initiate a runtime.env file, specify the robot id and organisation id and then provide credentials when prompted

```
cognicept init --robot_id sample_robot --org_id sample_org
Username: sample_username
Password: sample_password (masked)
```

### **Docker-Compose** 
is supported in version `1.6` for cognicept-shell command below:
```
cognicept update/version/start/stop/restart
```

To make it work, you should added an enviroment variable `COG_COMPOSE_FILE` in `~/.cognicept/runtime.env` and specific the file directory of the docker-compose.yaml file, eg
```
COG_COMPOSE_FILE=~/.cognicept/docker-compose.yaml
```

Sample of `docker-compose` file:
```yaml
version: "3.9"
services:
  service_name:
    container_name: service_name
    network_mode: "host"
    restart: unless-stopped
    env_file:
    - ${HOME}/.cognicept/runtime.env
    image: image_repo
    command: python3 example.py
```
Sample response after running `cognicept version`

```Shell
Cognicept Shell Version 1.6.0
+------------------------------+-----------+----------------+
| Container Name               | Version   | Version Tags   |
|------------------------------+-----------+----------------|
| remote_intervention_agent    | latest    | latest         |
| kriya_watchdog               | latest    | latest         |
| cgs_diagnostics_ecs_api      | dev       | latest         |
| cgs_diagnostics_streamer_api | dev       | latest         |
| cgs_diagnostics_agent        | dev       | latest         |
| service_name                 |           |                |
+------------------------------+-----------+----------------+
Runtime enviroment file directory: ~/.cognicept/
```


### `autoupdater`: to pull the auto update server and start the services

`cognicept autoupdater --pull`  update the OTA server to latest version
`cognicept autoupdater --setup` Copy service file, setup and start the systemd service

## Building


### Tests

 (RECOMMENDED) **build and run the tests in Docker** by running the commands below:

To test in Ubuntu 20.04 `bash run_tests_ubuntu_20.sh`

To test in Ubuntu 22.04 `bash run_tests_ubuntu_22.sh`

Alternatively, you can **test locally**

`cognicept-shell` is using `pytest` as the test framework. Make sure you install manually:

```
pip3 install pytest pytest-cov cli_test_helpers mock
```

To run tests, execute:

```bash
# Run tests natively.
pytest --cov=cogniceptshell tests
```

Output will look like this:

```
user@computer:~/Desktop/repo/cognicept-shell$ bash run_tests_ubuntu_22.sh
=========================================================== test session starts ============================================================
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /
plugins: mock-3.14.0
collected 151 items                                                                                                                        

tests/functional/test_config.py .........s.....                                                                                      [  9%]
tests/functional/test_disk_space.py .                                                                                                [ 10%]
tests/functional/test_push.py ..........                                                                                             [ 17%]
tests/functional/test_record.py ..........                                                                                           [ 23%]
tests/unit/test_config.py ......................                                                                                     [ 38%]
tests/unit/test_event_log.py ....                                                                                                    [ 41%]
tests/unit/test_get_disk_space.py .                                                                                                  [ 41%]
tests/unit/test_keyrotate.py ...                                                                                                     [ 43%]
tests/unit/test_lifecycle.py ...........................                                                                             [ 61%]
tests/unit/test_ota_deployment.py .................................                                                                  [ 83%]
tests/unit/test_populate_config_files.py ....                                                                                        [ 86%]
tests/unit/test_pull_config_templates.py ...                                                                                         [ 88%]
tests/unit/test_robot_api_registrar.py ...............                                                                               [ 98%]
tests/unit/test_version_update.py ...                                                                                                [100%]

=============================================== 150 passed, 1 skipped, 2 warnings in 41.33s ================================================


```

### Build

To build the PyPI package, run:

```
python3 setup.py sdist bdist_wheel
```

This will generate the build files. 

### Upload

To upload the dev package, run:

```
python3 -m twine upload --repository testpypi dist/* --verbose
```

To upload the prod package, run:

```
python3 -m twine upload dist/* --verbose
```

## Contribution

Please follow [the successful branching model](https://nvie.com/posts/a-successful-git-branching-model/). The naming of branches follows:

* Feature branch: /feature/name-of-the-feature
* Bug fix branch: /fix/name-of-the-bug
* Release branch: /release/name-of-the-release


## Version history

* 1.8.0 [19/09/2024]
  * Update Lock File Check: Added functionality for Cognicept update to check for the update lock file before executing the update process, ensuring  that no updates are performed while a mission is in progress.
  * Agent Disabling via Config File: Added support for disabling agents using an `enabled` key in the agent configuration file. When set to true, the specified agent will not load in the Cognicept shell.
  * Migration to Compose-Style YAML Configuration: Added support for full migration to a compose-style YAML file-based agent configuration while maintaining backward compatibility with older configurations.
  * Enhanced Logging: Included the agent name in log messages and improved overall logging during the update process for better monitoring and debugging.
  * Template Pulling Extension: Extended the Cognicept update functionality to pull templates during updates, ensuring the latest configurations are always available.
  * OTA Support: Introduced main functionalities to support Over-The-Air (OTA) updates, enabling seamless remote software updates.

* 1.7.6 [01/07/2024]
  * Load devices option from docker-compose
  * Set privileged mode false by default

* 1.7.5 [26/06/2024]
  * Fix mounting issues for external devices

* 1.7.4 [18/06/2024]
  * Fix API overwrite bug
  * Allow updates to proceed when fetching robot config fails

* 1.7.3 [12/06/2024]
  * Enable pulling robot properties from cloud during cognicept init and cognicept update
  * Fix for detached cognicept restart failing to restart agents specified in docker-compose.yaml on command terminal disconnection.
  * Exception handling for missing image tag

* 1.7.2[23/04/2024]
  * Fix pip dependency version issues
  * Fix region name parameter issue
  * 1.7.1[24/11/2023]
  * Bug Fixed - templates directory blocking cognicept restart
  * cognicept prune to support only in attached mode


* 1.7.1[24/11/2023]
  * Bug Fixed - templates directory blocking cognicept restart
  * cognicept prune to support only in attached mode

* 1.7.0[25/10/2023]
  * `cognicept update` check for remaining disk space (in root directory) before pulling each image
  * `cognicept update -s` overrides check for disk space before pulling images
  * `cognicept update` will update the success or failure to S+ event logs
  * `cognicept version` will display the latest version of the docker images
  * `cognicept restart` by default is restarting in detached mode
  * `cognicept restart` -a to restart in attached mode
  * `cognicept init` support --robot_code and --org_code
  * new `cognicept move` feature


* 1.6.1[22/5/2023]
  * `cognicept update` prompts the user before upgrading the cognicept-shell version
  * `cognicept update -y` will upgrade cognicept-shell directly
  * Fixed `cognicept init` bug for non-existing robot_id and org_id
  * Added exception handling to capture HTTP status codes in shell
  * Changed cognicept version update message to reflect the latest version
  * Added install_requires for `websocket-client`, `paramiko` dependencies
  * Added docker-compose error handling exception

* 1.6 [12/5/2023]
  * `cognicept update/version/start/stop/restart` support of docker-compose with enviroment variable `COG_COMPOSE_FILE`
  * `cognicept restart --prune` for clearing logs
  * `cognicept update --image` to update docker images in environment variable `COGNICEPT_EXTRA_IMAGES`
  * `cognicept update` will prompts msgs for users about the specific errors faced when trying to run `cognicept update`
  * added camera_capture

* 1.5 [23/9/2022]
    * Auto update shell on `cognicept update`
    * Allow container specific updates
    * Add support for kopilot, smartplus_sound_server, map_manager, kriya's friends
    * Audio config for sound devices
    * Backup runtime config before updating
* 1.4 [16/12/2021]
    * 2FA modification for `init` command
    * Add `version` command to display agent version
    * Add support for health_monitoring_aggregator
* 1.3 [21/10/2021]
    * Autocomplete for basic commands and agent names
* 1.2 [29/6/2021]
    * Revamp credentials for AWS
    * Added robot init command
    * Revamped CI/CD
    * Added detached update/restart
    * Removed datadog integration
    * Added kriya watchdog run configuration
    * Added handling of the docker permission error 
    * Added run configuration to support bunch reporting
* 1.1 []
    * Limit agent logs to 5MB

* 1.0.3 []
    * Change for cognicept update command to fetch cloud credentials from cognicept backend

* 1.0 [15/12/2020]
    * Added `start` command
    * Start/Stop/Restart agents separately as parameter of command
    * Migrated to new credential management using `COGNICEPT_ACCESS_KEY` 
    * Added `keyrotate` command
    * Added unit and functional tests
    * Added `record` and `push` commands for management of rosbags
    * Added support for Python 3.5
    * Added `lastevent` command to read last event 
    * Added ssh configuration for `remote_intervention_agent`

* 0.1 [10/6/2020]
    * First version of the CLI utility able to configure, restart, and update agents 
