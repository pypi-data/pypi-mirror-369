# Copyright 2020 Cognicept Systems
# Author: Jakub Tomasek (jakub@cognicept.systems)
# --> AgentLifeCycle handles life cycle of Cognicept Agents
import uuid
import yaml
import time
import docker
import boto3
import getpass
import base64
import json
import os
import sys
import subprocess
import dateutil
import dotenv
import threading
import traceback
from datetime import datetime
from ping3 import ping
import re
from docker.errors import DockerException
import glob
from multiprocessing import Process, Queue
import requests
import botocore
import shutil
import psutil
import pkg_resources
from tabulate import tabulate
import ruamel.yaml
from cogniceptshell.common import bcolors
from cogniceptshell.common import generate_progress_bar
from cogniceptshell.common import permission_safe_docker_call
from cogniceptshell.common import post_event_log, LogLevel
from subprocess import DEVNULL
from docker.types import LogConfig
from typing import Dict, Callable, List, Any


class AgentLifeCycle:
    """
    A class to manage agent and Cognicept's docker container lifecycle
    ...

    Parameters
    ----------
    None

    Methods
    -------
    configure_containers(cfg):
        Loads agent configuration from `COG_AGENT_CONTAINERS` and `COG_AGENT_IMAGES`
    get_status(args):
        Prints status of docker containers listed in `COG_AGENT_CONTAINERS`.
    get_last_event(args):
        Prints last log in `~/.cognicept/agent/logs/`.
    restart(args):
        Stops and starts the containers listed in `COG_AGENT_CONTAINERS`.
    start(args):
        Starts the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, starts only containers in the list.
    stop(args):
        Stops the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, stops only containers in the list.
    update(args):
        Pulls docker images listed in `COG_AGENT_IMAGES`.
    register_container_callback(container_name, callback):
        Registers a callback function to be executed after a container is started.
    """

    # default configuration of containers and images
    _docker_compose_container_name = []
    _docker_images = {}

    # Container callbacks registry
    _container_callbacks: Dict[str, List[Callable]] = {}

    def configure_containers(object, cfg):
        """
        Loads agent configuration from `COG_AGENT_CONTAINERS`, `COG_AGENT_IMAGES` and `COG_COMPOSE_FILE`

                Parameters:
                        cfg (Configuration): Cognicept configuration
                Returns:
                        None
        """

        if("COG_AGENT_CONTAINERS" in cfg.config and "COG_AGENT_IMAGES" in cfg.config):
            print(bcolors.WARNING + " Use `COG_AGENT_CONTAINERS` and `COG_AGENT_IMAGES` is depreciated, please migrate to docker-compose.yaml" + bcolors.ENDC)
            container_names = cfg.config["COG_AGENT_CONTAINERS"].split(";")
            image_names = cfg.config["COG_AGENT_IMAGES"].split(";")
            if(len(image_names) == len(container_names)):
                object._docker_images = {}
                i = 0
                for container_name in container_names:
                    object._docker_images[container_name] = image_names[i]
                    i = i + 1
            else:
                print(
                    bcolors.WARNING + 
                    "`COG_AGENT_CONTAINERS` and `COG_AGENT_IMAGES` do not coincide. Agents specified using COG_AGENT_CONTAINERS will not be loaded" +
                    bcolors.ENDC)


        if "COG_COMPOSE_FILE" in cfg.config:
            object._compose_dir = os.path.dirname(os.path.expanduser(cfg.config["COG_COMPOSE_FILE"]))
            docker_compose_dict = cfg.get_docker_compose()

            if docker_compose_dict == {}:
                print(f"{bcolors.WARNING}Warning: No agents loaded from docker compose file - {cfg.config['COG_COMPOSE_FILE']} {bcolors.ENDC}")
            else:
                for container_name in docker_compose_dict:
                    object._docker_compose_container_name.append(container_name)
                object._docker_images.update(docker_compose_dict)

    def _get_latest_log_loc(object, args):
        """
        Retrieve path to the last log in `~/.cognicept/agent/logs/` relative to `~/.cognicept/` or `path` specified by args.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        latest_log_loc (str): path to latest log relative to `~/.cognicept/`
        """
        # get latest log location
        latest_log_loc_file_path = os.path.expanduser(
            args.path+"agent/logs/latest_log_loc.txt")
        latest_log_loc = ""
        try:
            with open(latest_log_loc_file_path) as txt_file:
                latest_log_loc_temp = txt_file.readline()
                latest_log_loc_temp = latest_log_loc_temp[:-1]
                latest_log_loc = latest_log_loc_temp.replace(
                    "/$HOME/.cognicept/", "")
                latest_log_loc = latest_log_loc.replace(".cognicept/", "")
        except:
            cgs_agent_status = bcolors.FAIL + "UNKNOWN" + bcolors.ENDC

        return latest_log_loc

    def get_status(object, args):
        """
        Prints status of docker containers listed in `COG_AGENT_CONTAINERS`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`

        """
        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False
        client = permission_docker_call_result
        # check status of cgs_agent
        # get latest log location
        latest_log_loc = object._get_latest_log_loc(args)
        # read latest status and set for display
        file_path = os.path.expanduser(
            args.path+latest_log_loc+"/logDataStatus.json")
        try:
            with open(file_path) as json_file:
                data = json.load(json_file)
                period_since_update = datetime.utcnow(
                ) - dateutil.parser.parse(data["timestamp"])
                if(period_since_update.seconds < 30 and period_since_update.seconds >= 0):
                    cgs_agent_status = bcolors.OKBLUE + \
                        data["message"].upper() + bcolors.ENDC
                else:
                    cgs_agent_status = bcolors.WARNING + "STALE" + bcolors.ENDC

        except:
            cgs_agent_status = bcolors.FAIL + "Error" + bcolors.ENDC

        container_names = list(object._docker_images.keys())
        for container_name in container_names:
            print(container_name, end=': ', flush=True)
            try:
                container = client.containers.get(container_name)
                if container.status != "running":
                    print(bcolors.WARNING + "OFFLINE" + bcolors.ENDC)
                else:
                    if(container_name == "cgs_diagnostics_agent"):
                        print(cgs_agent_status)
                    elif(container_name == "remote_intervention_agent"):
                        object._parse_remote_intervention_agent_logs(
                            container.logs(tail=50))
                    else:
                        print(bcolors.OKBLUE + "ONLINE" + bcolors.ENDC)
            except docker.errors.NotFound:
                print(bcolors.FAIL + "CONTAINER NOT FOUND" + bcolors.ENDC)

    def get_last_event(object, args):
        """
        Prints last log in `~/.cognicept/agent/logs/`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`

        """
        # get latest log location
        latest_log_loc = object._get_latest_log_loc(args)

        # read and display latest log if any
        file_path = os.path.expanduser(args.path+latest_log_loc)
        try:
            print(bcolors.OKBLUE +
                  "Looking for the latest event log..." + bcolors.ENDC)
            # should read only latest logData#.json file and not logDataStatus.json
            list_of_log_files = [fn for fn in glob.glob(file_path + "/*.json")
                                 if not os.path.basename(fn).endswith("logDataStatus.json")]
            latest_log_file = max(list_of_log_files, key=os.path.getctime)

            with open(latest_log_file) as json_file:
                data = json.load(json_file)
                print(bcolors.OKGREEN+"Latest Event Log:" + bcolors.ENDC)
                print(json.dumps(data, indent=4, sort_keys=True))
        except:
            print(bcolors.WARNING + "No event logs present." + bcolors.ENDC)

    def check_docker_image_exists(object, args):
        """
        Checks if this docker image exists.
        
                Parameters:
                        args (str): Input container names.
        """
        image_set = set()
        missing_image = set()

        # If list of agents is not specified, get all container_names
        if(not hasattr(args, 'list') or len(args.list) == 0):
            args.list = list(object._docker_images.keys())

        # Based on args.list to get image(s)
        for container_name in args.list:
            try:
                image_set.add(object._docker_images[container_name])
            except KeyError as exp:
                print(bcolors.WARNING + "Container: " + container_name + " not found. Skipping." + bcolors.ENDC)

        success_flag = True
        docker_client = permission_safe_docker_call(docker.from_env)
        for image in image_set:
            try:
                image = docker_client.images.get(image)

            except docker.errors.ImageNotFound:
                missing_image.add(image) #Track image(s) that is/are missing
                success_flag = False

        return success_flag, missing_image

    def _parse_remote_intervention_agent_logs(object, logs):
        """
        Parses logs to find status of remote intervention agent. Prints status.

                Parameters:
                        logs: container logs

        """
        logs_lines = logs.splitlines()
        # parse logs to get current status
        ri_agent_status = {}
        ri_agent_status["AGENT"] = ""
        ri_agent_status["WEBRTC"] = ""
        ri_agent_status["WEBSOCKET"] = ""

        # find latest status of the each module (agent, webrtc, websocket)
        for line in reversed(logs_lines):
            for key, value in ri_agent_status.items():
                if(value != ""):
                    continue
                matches = re.search(
                    '^.*{}:: STATUS:: (?P<status>.*).*$'.format(key), str(line))
                if(matches is not None):
                    ri_agent_status[key] = matches.groups(0)[0]
            if(ri_agent_status["AGENT"] != "" and ri_agent_status["WEBRTC"] != "" and ri_agent_status["WEBSOCKET"] != ""):
                continue

        output_text = bcolors.OKBLUE + "ONLINE" + bcolors.ENDC

        for key, value in ri_agent_status.items():
            if(value == ""):
                # if not found, it was not yet initialized
                output_text = bcolors.WARNING + "NOT INITIALIZED" + bcolors.ENDC
                break
            if(value != "OK"):
                output_text = bcolors.WARNING + key + value + bcolors.ENDC
                break
        print(output_text)

    def _detached_restart(object, args):
        """
        Runs _restart_protocol in detached mode with printing muted.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """

        if os.fork() != 0:
            return
        sys.stdout = open(os.devnull, 'w')
        result = object._restart_protocol(args)
        sys.stdout = sys.__stdout__
        return result

    def _restart_protocol(object, args):
        """
        Stops and starts the containers listed in `COG_AGENT_CONTAINERS`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        object.stop(args)
        result = object.start(args)
        return result

    def restart(object, args):
        """
        Stops and starts the containers listed in `COG_AGENT_CONTAINERS`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded in attached mode, always True in detached mode
        """
        #success_flag is a bool to check if all image(s) exist before running restart protocol
        success_flag, missing_images = object.check_docker_image_exists(args) 

        if success_flag:
            if not args.attach and not args.prune:
                result = True
                post_event_log(args,"Running restart in detached mode")
                p = Process(target=object._detached_restart, args=(args,))
                p.start()
            else:
                result = object._restart_protocol(args)
            if args.prune:
                print("Clearing logs")
                object.clear_logs(args)
                            
        else:
            result = success_flag
            print(bcolors.FAIL + "Error: The following image(s) shown below cannot be found" + bcolors.ENDC)
            print(*missing_images, sep = "\n")
        return result

    def start(object, args):
        """
        Starts the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, starts only containers in the list.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        print("Called start")
        print("Starting agents")
        result = object.run_agents(args)
        return result

    def stop(object, args):
        """
        Stops the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, stops only containers in the list.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        print("Stopping agents")
        result = object.remove_agents(args)
        return result
    
    def check_sudo_password(object, password):
        '''
        Checks if user entered password for clearing logs is correct. Runs a dummy sudo command to test input password.
        '''
        cmd = ["sudo","-kS","echo","test"]
        
        p = subprocess.run(cmd, capture_output=True, input=password, encoding="ascii")

        if "incorrect password" in str(p):
            return False
        else:
            return True
        
    def clear_logs(object, args):
        """
        Remove all unused containers, networks, images (both dangling and unreferenced). Removes all .txt logs stored in /kriya_logs
        and .json logs stored in /agents/logs
                
        """
        log_list = ["sudo","-S","-k", "rm"]
        kriya_log_count = 0
        agent_folder_list = ["sudo","-S","-k","rm","-r"]
        cognicept_dir_path = os.path.expanduser(args.path)
        kriya_logs_dir = cognicept_dir_path + "kriya_logs/"
        if os.path.exists(kriya_logs_dir):
            kriya_logs = os.listdir(kriya_logs_dir)
            for item in kriya_logs:
                if item.endswith(".txt"):
                    log_list.append(str(kriya_logs_dir + item))
                    kriya_log_count += 1

        agent_logs_dir = cognicept_dir_path + "agent/logs/"
        if os.path.exists(agent_logs_dir):
            agent_folders = os.listdir(agent_logs_dir)
            
            for folder in agent_folders:
                folder_path = agent_logs_dir + folder
                if os.path.isdir(folder_path) and folder != "bunched_logs" and folder != "unittest_logs":
                    agent_folder_list.append(str(folder_path))
                
                elif folder == "bunched_logs":
                    bunched_logs = os.listdir(folder_path)
                    bunched_log_count = len(bunched_logs)
                    for item in bunched_logs:
                        log_list.append(str(folder_path + "/" + item))
                
                elif folder == "unittest_logs":
                    unittest_logs = os.listdir(folder_path)
                    unittest_log_count = len(unittest_logs)
                    for item in unittest_logs:
                        log_list.append(str(folder_path + "/" + item))

        agent_folder_count = len(agent_folder_list)-4

        print(f'\nClear File Summary: \n-Kriya: {kriya_log_count} Logs Found \n-Agent: {agent_folder_count} Folders Found \n-Bunched: {bunched_log_count} Logs Found \n-Unittest: {unittest_log_count} Logs Found')
        if kriya_log_count + bunched_log_count + unittest_log_count + agent_folder_count == 0:
            print("No detected Logs and Files to be cleared.")
        else:
            print("Do you wish to proceed?")
            user_input = input("(Y/N)")
            if user_input.lower() == "y":
                
                attempt = 0
                success = False
                while attempt < 3 and success == False:
                    password = getpass.getpass("Enter sudo password: ")
                    success = object.check_sudo_password(password)
                    
                    if not success:
                        
                        attempt += 1
                
                if success:
                
                    if kriya_log_count > 0:
                        print("Successfully removed all kriya_folder")
                    
                    if agent_folder_count > 0:
                        clear_agent_folder = subprocess.Popen(agent_folder_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = clear_agent_folder.communicate(input=(password + '\n').encode())
                        print("Successfully removed all agent_folder")

                    if bunched_log_count > 0:
                        print("Successfully removed all bunched_logs")

                    if unittest_log_count > 0:
                        print("Successfully removed all unittest_logs")

                    clear_logs = subprocess.Popen(log_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = clear_logs.communicate(input=(password + '\n').encode())

                else:
                    print("Logs and Files not cleared, Sudo Password Incorrect.")
            else:
                print("Logs and Files not cleared")

    def status(object, args):
        object.get_status(args)
        object.status_datadog(args)
        return True

    def remove_agents(object, args):
        """
        Stops the containers listed in `args.list`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """

        # if list of agents is not specified, restart all
        if(not hasattr(args, 'list') or len(args.list) == 0):
            args.list = list(object._docker_images.keys())
        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False

        client = permission_docker_call_result
        print("STOP: ")
        flag_success = True
        for container_name in args.list:
            post_event_log(args, f"Stopping agent: {container_name}")
            print("   - " + container_name, end=': ', flush=True)
            try:
                container = client.containers.get(container_name)
                container.stop(timeout=10)
                container.remove()
                print(bcolors.OKBLUE + "DONE" + bcolors.ENDC)
                post_event_log(args, f"Stopped agent: {container_name}", LogLevel.SUCCESS)
            except docker.errors.NotFound:
                post_event_log(args, f"Agent {container_name} not found", LogLevel.ERROR)
                print(bcolors.WARNING + "NOT FOUND" + bcolors.ENDC)
                flag_success = False
            except docker.errors.APIError:
                post_event_log(args, f"Error stopping agent {container_name}", LogLevel.ERROR)
                print(bcolors.FAIL + "ERROR" + bcolors.ENDC)
                flag_success = False
        return flag_success

    def populate_config_files(object, args):
        """
        Populates robot configuration files located in the ~/path/to/templates and copies them to the ~/.cognicept output folder

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        None
        """
 
        templates_source_folder = os.path.expanduser(args.path + 'templates')
        templates_target_folder = os.path.expanduser(args.path)
        
        # Check if source and targert folders exits
        if not os.path.exists(templates_target_folder):
            raise FileNotFoundError("Specifed target folder for templates does not exist")
        elif not os.path.exists(templates_source_folder):
            print(bcolors.WARNING + "No templates folder found at specifed source location, will continue without templates" + bcolors.ENDC)             
        else:
            # Load the key-value pairs from the runtime.env file
            runtime_vars = args.config.config

            try:
                # Get the list of template files
                template_files = os.listdir(templates_source_folder)

                if not template_files:
                    print(bcolors.WARNING + "No templates found in the specifed source folder, will continue without templates" + bcolors.ENDC)
                else:
                    # Process each template file
                    for template_file_name in template_files:
                        template_file_path = os.path.join(templates_source_folder, template_file_name)
                        output_file_path = os.path.join(templates_target_folder, template_file_name)

                        # Read the template file
                        with open(template_file_path, 'r') as template_file:
                            template_content = template_file.read()

                        # Find all variables matching ${VARIABLE} and replace with corresponding value
                        pattern = r'\${([A-Za-z_][A-Za-z0-9_]*)}'
                        matches = re.findall(pattern, template_content)
                        for match in matches:
                            if match in runtime_vars:
                                value = runtime_vars[match]
                                placeholder = '${' + match + '}'
                                template_content = template_content.replace(placeholder, str(value))

                        # Save the populated config file while preserving the original format
                        if template_file_name.endswith(('.yaml', '.yml')):
                            yaml = ruamel.yaml.YAML()
                            yaml.preserve_quotes = True
                            yaml.width = 4096
                            data = yaml.load(template_content)
                            with open(output_file_path, 'w') as output_file:
                                yaml.dump(data, output_file)
                        else:
                            with open(output_file_path, 'w') as output_file:
                                output_file.write(template_content)

                    print('Config files populated and copied successfully.')
            except FileNotFoundError as e:
                print(str(e))
                raise SystemExit

            except Exception as ex:
                print(f"Unexpected {ex=}, {type(ex)=}")
                raise

    def set_agent_config(object, args):

        object._agent_run_options = {}

        # diagnostics agent/API run config
        object._agent_run_options["cgs_diagnostics_agent"] = {"command": "rosrun error_resolution_diagnoser error_resolution_diagnoser", "volumes": {
            args.config.config_path + "agent/logs/": {"bind": "/root/.cognicept/agent/logs", "mode": "rw"}}, "network_mode": "host"}
        object._agent_run_options["cgs_diagnostics_ecs_api"] = {
            "command": "/src/ecs_endpoint.py", "network_mode": "host"}
        object._agent_run_options["cgs_diagnostics_streamer_api"] = {"command": "/src/streamer_endpoint.py", "volumes": {
            args.config.config_path + "agent/logs/bunched_logs": {"bind": "/root/.cognicept/agent/logs/bunched_logs", "mode": "rw"}}, "network_mode": "host"}

        # health aggregator run config
        object._agent_run_options["health_aggregator"] = {"command": "roslaunch health_monitoring_aggregator aggregator.launch --wait", "volumes": {
            args.config.config_path + "health_config.yaml": {"bind": "/home/aggregator_ws/src/health_monitoring_aggregator/config.yml", "mode": "rw"}}, "network_mode": "host"}
        
        # diagnostics aggregator run config
        object._agent_run_options["diagnostics_aggregator"] = {"command": "roslaunch diagnostic_aggregator aggregator.launch --wait", "volumes": {
            args.config.config_path + "diag_analyzers.yaml": {"bind": "/opt/ros/noetic/share/diagnostic_aggregator/demo/pr2_analyzers.yaml", "mode": "rw"}}, "network_mode": "host"}

        # kriya run config
        object._agent_run_options["remote_intervention_agent"] = {
            "command": "", "network_mode": "host"}
        if(args.config.is_ssh_enabled()):
            object._agent_run_options["remote_intervention_agent"]["volumes"] = {
                args.config.config_path + "ssh/id_rsa": {"bind": "/root/.ssh/id_rsa", "mode": "rw"}}
        if(args.config.is_audio_enabled()):
            object._agent_run_options["remote_intervention_agent"]["devices"] = ["/dev/snd"]
        object._agent_run_options["kriya"] = object._agent_run_options["remote_intervention_agent"]
        object._agent_run_options["kriya_watchdog"] = {
            "command": "python3 /home/watchdog.py", "volumes": {
                args.config.config_path + "kriya_logs/": {"bind": "/root/logs/", "mode": "rw"},
                "/var/run/docker.sock/": {"bind": "/var/run/docker.sock/", "mode": "rw"}}}

        # kopilot run config
        object._agent_run_options["kopilot"] = {"command": "", "network_mode": "host", "volumes": {
            args.config.config_path + "kockpit.yaml": {"bind": "/root/config/kockpit.yaml", "mode": "rw"}}}

        # ROSBagger run config
        object._agent_run_options["cgs_bagger_server"] = {"command": "rosrun cognicept_rosbagger bagger_action_server.py", "volumes": {
            args.config.config_path + "bags/": {"bind": "/root/.cognicept/bags", "mode": "rw"}}, "network_mode": "host"}
        
        # Smart+ Sound Server run config
        object._agent_run_options["smartplus_sound"] = {"volumes": {
            args.config.config_path + "sounds/": {"bind": "/root/.cognicept/sounds", "mode": "rw"},
            args.config.config_path + "tts_configuration.yaml": {"bind": "/home/smartplus_sound_server_ws/src/tts/config/sample_configuration.yaml", "mode": "rw"}},
            "network_mode": "host", "devices": ["/dev/snd"]}

        # Map Manager run config
        object._agent_run_options["map_manager"] = {"volumes": {
            args.config.config_path + "slamware_maps/": {"bind": "/root/.cognicept/slamware_maps", "mode": "rw"},
            args.config.config_path + "map_server_maps/": {"bind": "/root/.cognicept/map_server_maps", "mode": "rw"},
            args.config.config_path + "building_info.json": {"bind": "/home/map_manager_ws/src/map_manager/config/sample_building_info.json", "mode": "rw"}},
            "network_mode": "host"}
        
        # Computer Health Metrics run config
        object._agent_run_options["computer_health_metrics"] = {"volumes": {
            args.config.config_path + "health_config.yaml": {"bind": "/home/health_ws/src/computer_health_metrics/config/computer_params.yml", "mode": "rw"},
            "/var/run/docker.sock/": {"bind": "/var/run/docker.sock/", "mode": "rw"}},
             "network_mode": "host"}

        # Slamware adapter run config
        object._agent_run_options["slamtec_adapter"] = {"volumes": {
            args.config.config_path + "slamware_maps/": {"bind": "/root/.cognicept/slamware_maps", "mode": "rw"}},
            "network_mode": "host"}
        
        # Camera capture run config 
        object._agent_run_options["cam_capture"] = {"volumes": {
            args.config.config_path + "inspect_images/" : {"bind": "/root/.cognicept/inspect_images/", "mode": "rw"},
            args.config.config_path + "runtime.env" : {"bind": "/root/.cognicept/runtime.env", "mode": "rw"}},
            "network_mode": "host"}
        
        # Default other config
        object._agent_run_options["other"] = {
            "command": "", "network_mode": "host"}
        

    def run_agents(object, args):
        """
        Starts the containers listed in `args.list`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        # if list of agents is not specified, restart all and run the docker-compose file
        if(not hasattr(args, 'list') or len(args.list) == 0):
            args.list = list(object._docker_images.keys())

        object.set_agent_config(args)

        # Load docker compose file
        compose_file_path = args.config.config.get("COG_COMPOSE_FILE", None)
        if compose_file_path:
            try:
                compose_dict = None
                with open(os.path.expanduser(compose_file_path)) as compose_file:
                    print(f"Loading agents from {compose_file_path}")
                    compose_dict = yaml.safe_load(compose_file)["services"]
            except Exception as ex:
                print(bcolors.FAIL + "Failed to load docker compose file: " + ex + bcolors.ENDC)

        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False
        client = permission_docker_call_result
        print("RUN: ")
        success_flag = True
        
        # Keep track of successfully started containers for callbacks
        started_containers = []
        
        for container_name in args.list:
            post_event_log(args, f"Starting agent: {container_name}")
            print("   - " + container_name, end=': ', flush=True)
            try:
                if(container_name not in object._docker_images):
                    if("COG_AGENT_CONTAINERS" in args.config.config):
                        containers = " (configured list: " + \
                            args.config.config["COG_AGENT_CONTAINERS"] + ")"
                    else:
                        containers = ""
                    print(bcolors.WARNING + "NOT FOUND" +
                          bcolors.ENDC + containers)
                    post_event_log(args, f"Agent {container_name} not found", LogLevel.ERROR)
                    success_flag = False
                    continue

                if(container_name in object._agent_run_options.keys()):
                    options = object._agent_run_options[container_name]
                else:
                    options = object._agent_run_options["other"]
                options["name"] = container_name
                options["detach"] = True
                options["environment"] = args.config.config
                try:
                    if container_name == "smartplus_sound":
                        options["environment"]["ALSA_CARD"] = options["environment"]["SOUND_DEV_OUT"]
                    elif container_name == "remote_intervention_agent":
                        options["environment"]["ALSA_CARD"] = options["environment"]["SOUND_DEV_IN"]
                except KeyError as exp:
                    print(bcolors.WARNING + 'Missing sound device configuration in runtime.' +
                        ' Might result in sound features not working as expected.' +
                        ' Explicitly define `SOUND_DEV_IN` and `SOUND_DEV_OUT` variables.' + 
                        bcolors.ENDC)
                options["restart_policy"] = {"Name": "unless-stopped"}
                options["tty"] = True
                options["log_config"] = LogConfig(
                    type=LogConfig.types.JSON, config={'max-size': '5m'})
                if "command" in options:
                    command = options.pop("command")
                else:
                    command = ""
                
                #if container name is within docker-compose service, trigger run function
                # check whether the container's image is not found
                
                if container_name in object._docker_compose_container_name:
                    compose_options = object.parse_compose(compose_dict[container_name])
                    for option in compose_options:
                        options[option] = compose_options[option]

                    client.containers.run(
                        object._docker_images[container_name], **options)
                else:
                    client.containers.run(
                        object._docker_images[container_name], command, **options)
                
                print(bcolors.OKBLUE + "DONE" + bcolors.ENDC)
                post_event_log(args, f"Started agent: {container_name}", LogLevel.SUCCESS)
                
                # Add to the list of successfully started containers
                started_containers.append(container_name)
                
            except docker.errors.ContainerError:
                print(bcolors.WARNING + "ALREADY EXISTS" +
                      bcolors.ENDC + " (run `cognicept update`)")
            except docker.errors.ImageNotFound:
                print(bcolors.WARNING + "IMAGE NOT FOUND" +
                      bcolors.ENDC + " (run `cognicept update`)")
                post_event_log(args, f"ERROR: Image not found for {container_name}", LogLevel.ERROR)
                success_flag = False
            except docker.errors.APIError as exp:
                print(exp)
                print(bcolors.FAIL + "DOCKER ERROR" + bcolors.ENDC)
                post_event_log(args, f"ERROR: Could not start {container_name}, docker error", LogLevel.ERROR)
                success_flag = False

        # Execute callbacks for successfully started
        # containers in separate threads
        object._execute_container_callbacks(started_containers, args)

        return success_flag

    def status_datadog(object, args):
        """
        Prints datadog status.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        sts = subprocess.call(
            ['sudo', 'sh', '-c', "systemctl status datadog-agent", "-p"], shell=True, stdout=DEVNULL, stderr=DEVNULL)
        if sts == 0:
            print("Health monitor status:" +
                  bcolors.OKBLUE + " ACTIVE" + bcolors.ENDC)
        elif sts == 4:
            print("Health monitor status:" +
                  bcolors.FAIL + " NOT FOUND" + bcolors.ENDC)
        else:
            print("Health monitor status:" +
                  bcolors.WARNING + " INACTIVE" + bcolors.ENDC)

    def cognicept_version_update(object,args):
        current_version = pkg_resources.require("cognicept-shell")[0].version
        package = 'cognicept-shell'
        response = requests.get(f'https://pypi.org/pypi/{package}/json')
        latest_version = response.json()['info']['version']
        if latest_version > current_version:
            if args.skip:
                user_input = 'y'
            else:
                user_input = ""
                while(user_input.lower() != "y" and user_input.lower() != "n"):
                    user_input = input(f"New Cognicept Shell version {latest_version} is available! current version is {current_version}, proceed with update (y/n) ?  ")

            if user_input.lower() == "y":
                print(f"{package} current version {current_version} - Installing Version {latest_version}")
                updation_result = os.system(f'pip3 install -q {package}=={latest_version}')
                if updation_result == 0: # Process exited with success   
                    print(f'Updating {package} to version {latest_version}:'+bcolors.OKGREEN + " SUCCESS" + bcolors.ENDC + "\n")
                else:
                    print(f'Updating {package} to version {latest_version}:'+bcolors.FAIL + " FAILED" + bcolors.ENDC + "\n")
            else:
                print(f"{package} was not updated. Current version: {current_version}")
        else:
            print(f"{package} already on latest version={latest_version}")

    def pull_image(object, args, image_name, N, i):
        """
        Pulls a Docker image and displays a progress bar.

            Parameters:
                image_name : The name of the Docker image to pull.
                N : The total number of images to pull.
                i : index
        """
        image_name_short = image_name.replace("412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/", "cognicept/")
        for status in object.docker_client.pull(image_name, stream=True, decode=True):
            if("progress" not in status):
                status["progress"] = ""
            if("status" not in status):
                status["status"] = "Error"
            terminal_size = shutil.get_terminal_size().columns
            progress = ""
            if("progressDetail" in status and "total" in status["progressDetail"]):
                progress = generate_progress_bar(
                    status["progressDetail"]["current"], status["progressDetail"]["total"], 1, 10)
                status = "[" + str(i) + "/" + str(N) + "] " + image_name_short + \
                    " - " + status["status"] + " " + progress
                if(terminal_size > 0):
                    print('{:{terminal_size}.{terminal_size}}'.format(
                        status, terminal_size=terminal_size), end="\r", flush=True)
                else:
                    print('{:{trm_sz}.{trm_sz}}'.format(
                        status, trm_sz=80), end="\r", flush=True)
        print("[" + str(i) + "/" + str(N) + "] " + image_name_short +
            " - " + bcolors.OKBLUE + "OK" + bcolors.ENDC + "\033[K")

    def get_disk_space(object):
        """
        Checks for host disk space in root directory

                Parameters:
                        None
                Returns:
                        percentage_free(float): remaining disk space in percentage format
                        free_space(String): remaining disk space in readable byte format
        """
        disk_usage = psutil.disk_usage('/')
        raw_free_space = disk_usage.free
        free_space = round(raw_free_space/(1024 * 1024 * 1024), 2) #convert bytes to gigabytes
        
        return free_space

    def update_agents(object, args):
        """
        Starts the containers listed in `args.list` for the purpose of update.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        
        agents_to_update = {}
        images = set()
        # if list of agents is not specified, update all agents
        
        if((not hasattr(args, 'list') or not args.list) and (not hasattr(args, 'image') or not args.image)):
            agents_to_update = object._docker_images
            # load extra images to update
            if("COG_EXTRA_IMAGES" in args.config.config):
                post_event_log(args, "COG_EXTRA_IMAGES is depreciated, please use YAML config", LogLevel.WARNING)
                image_names = args.config.config["COG_EXTRA_IMAGES"].split(";")
                if(len(image_names) > 0):
                    images = set(image_names)
            
            N = len(agents_to_update) + len(images)
            object.cognicept_version_update(args)
            print("Info: This may take a while depending on your connection.")
        # if list of agents is specified, update only that particular set of agents
        else: 
            agents_to_update = {}
            if args.list:
                for container_name in args.list:
                    if container_name in list(object._docker_images.keys()):
                        agents_to_update[container_name] = object._docker_images[container_name]
                    else:
                        print(f"Error: Agent {container_name} not found")
                        success_flag = False

            if args.image:
                for image_name in args.image:
                    images.add(image_name)

            N  = len(agents_to_update) + len(images)
            print("Info: Update " + str(N) + " agent_image(s).")

        for i, image in enumerate(images):
            agents_to_update[f"extra_image_{i}"] = image

        i = 0 # For indexing
        success_flag = True
        for agent_name, image_name in agents_to_update.items():
            disk_space = object.get_disk_space()
            i = i + 1
            agent_ecr_prefix = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/"
            image_name_short = image_name.replace(agent_ecr_prefix, "cognicept/")
            try:

                post_event_log(args, f"Updating agent: {agent_name}", LogLevel.INFO)
                post_event_log(args, f"Pulling {image_name_short}", LogLevel.INFO)

                if args.space: # Update image without checking for space
                    object.pull_image(args, image_name, N=N, i=i)
                    post_event_log(args, f"Pulled {image_name_short}", LogLevel.SUCCESS)
                    post_event_log(args, f"Updated agent: {agent_name}", LogLevel.SUCCESS)
                else:
                    if disk_space >= 3: # Pull image only if there is atleast 3GB of disk space available
                        object.pull_image(args, image_name, N=N, i=i)
                        post_event_log(args, f"Pulled {image_name_short}", LogLevel.SUCCESS)
                        post_event_log(args, f"Updated agent: {agent_name}", LogLevel.SUCCESS)
                    else:
                        post_event_log(args, f"ERROR: Remaining disk space not enough! Current disk space is: {disk_space} GB", LogLevel.ERROR)
                        success_flag = False

                post_event_log(args, f"Available disk space: {disk_space} GB \n", LogLevel.INFO)
            except docker.errors.NotFound:
                try:
                    object.pull_image(args, image_name,N=N, i=i)
                    
                except docker.errors.NotFound:
                    post_event_log(args, "ERROR: Image could not be found in ECR or Docker Hub", LogLevel.ERROR)
                    print(bcolors.FAIL + "Error: " + bcolors.ENDC + f"Image {image_name} can't be accessed in ECR or Docker Hub.")
                    print("[" + str(i) + "/" + str(N) + "] " + image_name +
                        " - " + bcolors.FAIL + "FAILED" + bcolors.ENDC + "\033[K")
                    post_event_log(args, f"Failed to update agent: {agent_name}", LogLevel.ERROR)
                    success_flag = False                  
                except DockerException as ex:
                    print("[" + str(i) + "/" + str(N) + "] " + image_name +
                        " - " + bcolors.FAIL + "FAILED" + bcolors.ENDC + "\033[K")
                    print(f"Error: {ex}")
                    post_event_log(args, f"Failed to update agent: {agent_name}", LogLevel.ERROR)
                    success_flag = False
                    continue  # skip the current image and continue with the next one
            except Exception as e:
                post_event_log(args, f"Failed to update agent: {agent_name}", LogLevel.ERROR)
                post_event_log(args, "Error: " + str(e), LogLevel.ERROR)
                success_flag = False
                break
            except:
                print("[" + str(i) + "/" + str(N) + "] " + image_name +
                    " - " + bcolors.FAIL + "FAILED" + bcolors.ENDC + "\033[K")
                success_flag = False

        if not success_flag:
            print("There were errors while updating some images.")

        print("Info: Run `cognicept restart` to redeploy updated agents.")

        return success_flag
    
    def _update_protocol(object, args):
        """
        Pulls docker images listed in `COG_AGENT_IMAGES`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        #Check internet connection, if cannot connect, notify user and return false
        response_time = ping('google.com')
        if response_time == False:
            print("No internet connection. Please check the internet connection and try 'cognicept update` again.")
            return False
        else:
            login_success = object._ecr_login(args)
            if login_success is False:
                print("Your login has failed due to the error mentioned above. Please try again.")
                return False
            
            if args.configuration:
                args.config.pull_config_templates(args)
                args.config.update_robot_config(args)
                args.config.save_config(args)
                object.populate_config_files(args)
                post_event_log(args, "Configs updated successfully", LogLevel.SUCCESS)
                return True

            if object.update_agents(args) is False:
                config_file_path = os.path.expanduser('~/.docker/config.json')
                if os.path.exists(config_file_path):
                    print(bcolors.WARNING + "There is a conflict in authentication file, run rm ~/.docker/config.json to remove conflicting file" + bcolors.ENDC)   
                    post_event_log(args, "ERROR: Authentication file conflict, remove ~/.docker/config.json", LogLevel.ERROR)
                    return False
                else:
                    post_event_log(args, "ERROR: Credentials may have expired, run cognicept update", LogLevel.ERROR)
                    print(bcolors.WARNING + "Your update credentials may have expired. Run `cognicept keyrotate` to refresh credentials and try `cognicept update` again." + bcolors.ENDC)
                    return False
            else:
                return True
        
    def _detached_update(object, args):
        """
        Runs the _update_protocol that pulls docker images listed in `COG_AGENT_IMAGES`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        if os.fork() != 0:
            return

        sys.stdout = open(os.devnull, 'w')

        result = object._update_protocol(args)
        # object._update_event_log(result, args)

        sys.stdout = sys.__stdout__

        return result
    
    def update(object, args, lock_file="~/.cognicept/ota/update.lock"):
        """
        Pulls docker images listed in `COG_AGENT_IMAGES`. Can be run in detached mode where printing is muted

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): Always True if run in detached mode, otherwise True if successful
        """

        if args.detach:
            result = True
            post_event_log(args, message="Running update in detached mode", level=LogLevel.INFO)
            p = Process(target=object._detached_update, args=(args,))
            p.start()
        else:
            result = object._update_protocol(args)
            # object._update_event_log(result, args)
        return result
        
    def _construct_ecr_client(object, args):
        """
        Member utility function to create ECR client `object.ecr_client` based on runtime.env credentials

                Parameters:
                        args : object holding Cognicept configuration
                Returns:
                        None      
        """
        # Get config
        local_cfg = args.config.fetch_aws_keys()
        if local_cfg == False:
            return False
        if 'SessionToken' in local_cfg:
            object.ecr_client = boto3.client(
                'ecr', region_name='ap-southeast-1',
                aws_access_key_id=local_cfg['AccessKeyId'],
                aws_secret_access_key=local_cfg['SecretAccessKey'],
                aws_session_token=local_cfg['SessionToken'])
        else:
            object.ecr_client = boto3.client(
                'ecr', region_name='ap-southeast-1',
                aws_access_key_id=local_cfg['AccessKeyId'],
                aws_secret_access_key=local_cfg['SecretAccessKey'])
        return True

    def _ecr_login(object, args):
        """
        Member utility function that is called to login to ECR

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        # Construct client
        result = object._construct_ecr_client(args)
        if result == False:
            return False
        num_retries = 3
        for trial in range(num_retries):
            try:
                # Get token
                token = object.ecr_client.get_authorization_token()
                # Parse username, password
                username, password = base64.b64decode(
                    token['authorizationData'][0]['authorizationToken']).decode().split(':')
                # Get registry
                registry = token['authorizationData'][0]['proxyEndpoint']
                # Login
                docker_call_result = permission_safe_docker_call(docker.APIClient,
                                                                 base_url='unix://var/run/docker.sock')
                if docker_call_result is None:
                    return False

                object.docker_client = docker_call_result

                object.docker_client.login(username, password,
                                           registry=registry, reauth=True)
                # Return true for successful login
                return True
            except (docker.errors.APIError, botocore.exceptions.ClientError) as e:
                # On failure, retry
                print('Attempt #' + str(trial+1) + bcolors.FAIL +
                      " FAILED" + bcolors.ENDC + "\033[K")
                error_message = str(e)
                # Wait for 1 second before retrying
                time.sleep(1.0)
        # If the loop is completed, login failed, so return false
        print(bcolors.FAIL + error_message + bcolors.ENDC)
        return False
    
    def get_image_digest(object, image_name):
        """
        Retrieves image digest of image stored in local docker repository
                
                Parameters:
                        image_name: the name of a docker image in the format: '412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/repo_name:image_tag'
                Returns:
                        image_digest: imageDigest of current docker image  
        """
        client = docker.from_env()
        try:
            image = client.images.get(image_name)
            image_info = image.attrs
            repo_digests = image_info.get('RepoDigests', [])
            if repo_digests:
                image_digest = repo_digests[0].split('@')[1]
                return image_digest
            else:
                print(f"Image '{image_name}' does not have a digest.")
                return None
        
        except docker.errors.ImageNotFound:
            print(f"Image '{image_name}' not found in the local Docker repository.")
            return None
        
        except docker.errors.APIError as e:
            print(bcolors.FAIL + f"API error occurred while retrieving the image '{image_name}': {e.explanation}" + bcolors.ENDC)
            return None
    
    def get_version_tag_from_latest(object, image_data, ecr_client):
        """
        Retrieves version tag of current image stored in local docker repository
                
                Parameters:
                        image_data: a tuple/list with the following format: [412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/repo_name, image_tag]
                Returns:
                        version_tag: version of image with latest tag   
        """
        version_tag = None
        image_uri = image_data[0]
        

        try:
            if (image_data[1] == 'latest') and ('ecr' in image_uri):
                repo_name = image_data[0].split('/')[1]
                registry_id = image_uri.split('.')[0]
                image_digest = object.get_image_digest(':'.join(image_data))
                
                try:
                    if image_digest:
                        response = ecr_client.describe_images(
                            registryId=registry_id,
                            repositoryName=repo_name,
                            imageIds=[
                                {
                                    "imageDigest":image_digest    
                                }
                            ]                 
                        )
                        image_details = response.get('imageDetails', [])
                        image_tags = image_details[0]['imageTags']
                        pattern = r'v?\d+(\.\d+)+'
                        for tag in image_tags:
                            match = re.fullmatch(pattern, tag)
                            if match:
                                version_tag = match.group()
                                break
                            else:
                                version_tag = None
                        return version_tag
                    else:
                        return None
                
                except boto3.exceptions.Boto3Error as e:
                    print(f"Error occurred while querying ECR: {e}")
                    return None
                
                except botocore.exceptions.NoCredentialsError as e:
                    return None
                
                except Exception as e:
                    print("Error: " + str(e))
                    return None
        except IndexError as e:
            print(f"Error occurred when accessing image tag: {e}")
            return None

    def get_container_versions(object, args):
        """
        Get version information for all containers.

        Parameters:
            args: populated argument namespace returned
            by `argparse.parse_args()`

        Returns:
            dict: A dictionary containing container names,
            versions, and version tags
        """
        data = {}
        images_version = []
        latest_version = []
        data['Container Name'] = list(object._docker_images.keys())
        object._construct_ecr_client(args)

        for x in data['Container Name']:
            if x in object._docker_images:
                image_data = object._docker_images[x].split(':')
                if len(image_data) > 1:
                    latest_version_data = object.get_version_tag_from_latest(
                        image_data, object.ecr_client
                    )
                    latest_version.append(latest_version_data)
                    images_version.append(image_data[1])
                    image_data = []
                else:
                    latest_version.append("unknown/latest")
                    images_version.append("unknown/latest")
            else:
                latest_version.append("unknown/latest")
                images_version.append("unknown/latest")

        data['Version'] = images_version
        data['Version Tags'] = latest_version

        return data

    def get_container_version(object, container_name, args):
        """
        Get version information for a specific container.

        Parameters:
            container_name (str): Name of the container to get version for
            args: populated argument namespace returned
            by `argparse.parse_args()`

        Returns:
            tuple: (version, version_tag) for the specified container
        """
        object._construct_ecr_client(args)

        if container_name in object._docker_images:
            image_data = object._docker_images[container_name].split(':')
            if len(image_data) > 1:
                latest_version_data = object.get_version_tag_from_latest(
                    image_data, object.ecr_client
                )
                return image_data[1], latest_version_data

        return "unknown", "unknown/latest"

    def display_version(object, args):
        """
        Display Cognicept-Shell version and docker images version

        Parameters:
            args: populated argument namespace
            returned by `argparse.parse_args()`
        """
        version = pkg_resources.require("cognicept-shell")[0].version
        data = object.get_container_versions(args)

        print("Cognicept Shell Version " + version)
        print(tabulate(data, headers='keys', tablefmt='psql'))
        print("Runtime enviroment file directory: " + args.path)

    def register_container_callback(
        object, container_name: str, callback: Callable[[Any], None]
    ) -> None:
        """
        Register a callback function to be executed after a container is started.

        Parameters:
            container_name (str): The name of the container to register the callback for
            callback (Callable): The callback function to execute
        """
        if container_name not in object._container_callbacks:
            object._container_callbacks[container_name] = []

        object._container_callbacks[container_name].append(callback)

    def _execute_container_callbacks(
        object, container_names: List[str], args: Any
    ) -> None:
        """
        Execute callbacks for the specified containers in separate threads.

        Parameters:
            container_names (List[str]):
            List of container names that were successfully started
            args: Arguments to pass to the callbacks
        """
        threads = []

        for container_name in container_names:
            if container_name in object._container_callbacks:
                for callback in object._container_callbacks[container_name]:
                    # Create and start a thread for each callback
                    thread = threading.Thread(
                        target=object._run_callback_with_error_handling,
                        args=(callback, args, container_name),
                    )
                    thread.start()
                    threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    def _run_callback_with_error_handling(
        object, callback: Callable, args: Any, container_name: str
    ) -> None:
        """
        Run a callback with error handling to prevent thread crashes.

        Parameters:
            callback (Callable): The callback function to execute
            args: Arguments to pass to the callback
            container_name (str): Name of the container for logging purposes
        """
        try:
            callback(args)
            traceback.print_exc()
        except Exception as e:
            print(
                f"{bcolors.WARNING}Error in callback for container '{container_name}': {str(e)}{bcolors.ENDC}"
            )

    def parse_compose(object, compose_agent):
        """
        Parses the docker-compose.yaml to extract the docker container configuration of the agent.
        The reason for this methods existence is due to the fact that docker compose python library attaches to the parent process
        and dies when the parent process (terminal) is closed, causing agents specified using docker-compose to not restart.

            Parameter:
                compose_agent (str): The name of the agent as specified in docker-compose.yaml
            Return:
                options (dict): A dictionary containing the container configuration for the agent
        """
        options = {}

        # Parse privileged mode
        options["privileged"] = compose_agent.get("privileged", False)

        # Parse network mode
        options["network_mode"] = compose_agent.get("network_mode", "host")

        # Parse restart polict
        options["restart_policy"] = {"Name": compose_agent.get("restart", "unless-stopped")}

        # Parse stdin
        options["stdin_open"] = compose_agent.get("stdin_open", True)

        # Parse tty
        options["tty"] = compose_agent.get("tty", True)

        # Parse env file and env variables, assumes agents will only have one env file supplied
        options["environment"] = {}
        env_file = compose_agent.get("env_file", [])
        env_vars = compose_agent.get("environment", [])
        if env_file:
            env_vals = dotenv.dotenv_values(os.path.expandvars(env_file[0]))
            options["environment"].update(env_vals)
        if env_vars:
            for var in env_vars:
                key, val = var.split("=")
                options["environment"][key] = val

        # Parse volumes
        volumes = compose_agent.get("volumes", [])
        options["volumes"] = {}
        for volume in volumes:
            assert len(volume.split(":")) == 2 or len(volume.split(":")) == 3
            if len(volume.split(":")) == 2:
                host_volume, docker_volume = volume.split(":")
                options["volumes"][os.path.expandvars(host_volume)] = {"bind": docker_volume, "mode": "rw"}
            elif len(volume.split(":")) == 3:
                host_volume, docker_volume, mode = volume.split(":")
                options["volumes"][os.path.expandvars(host_volume)] = {"bind": docker_volume, "mode": mode}

        # Parse devices
        options["devices"] = compose_agent.get("devices", [])

        # Parse command
        options["command"] = str(compose_agent.get('command', ''))

        # Parse logging
        options["log_config"] = LogConfig(
            type=LogConfig.types.JSON,
            config={"max-size": "5m", "max-file": "3"})

        return options