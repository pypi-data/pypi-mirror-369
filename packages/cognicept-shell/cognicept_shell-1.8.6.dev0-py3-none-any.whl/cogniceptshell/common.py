# Copyright 2020 Cognicept Systems
# Author: Swarooph Seshadri (swarooph@cognicept.systems)
# --> common utilities for the cognicept shell goes here.

import uuid
import http
import enum
import boto3
import docker
import requests
import datetime


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LogLevel(enum.IntEnum):
    INFO = 1
    SUCCESS = 2
    WARNING = 4
    ERROR = 16

def generate_progress_bar(iteration, total, decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
        Parameters:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    output = "|" + bar + "| " + percent + "%"
    return output

class DockerPermissionError():
    identifier_string = "Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied'))"
    suggestion = "Error while fetching server API version, Your current user might not have permissions to access the resources. If docker is newly installed try:\n " \
                 "          sudo usermod -aG docker $USER\n" \
                 "Followed by rebooting your system."



def permission_safe_docker_call(func, *args, **kwargs):
    """
    Run a function while catching for docker permissions related exceptions.

            Parameters:
                    func: function to be executed
                    args: list of positional arguments for executing func
                    kwargs: Mapping of keyword arguments for executing func
            Returns:
                    result: None if failed, else returns result for function call
    """
    try:
        result = func(*args,**kwargs)
    except docker.errors.DockerException as docker_exception:
        if str(docker_exception) == DockerPermissionError.identifier_string:
            print(DockerPermissionError.suggestion)
            return None
        else:
            raise docker_exception
    return result


def is_agent_active(agent_name):
    try:
        docker_client = docker.from_env()
        streamer_api = docker_client.containers.get(agent_name)
        if streamer_api.attrs["State"]["Status"] != "running":
            return False
    except:
        return False

    return True


def post_event_log(args, message, level=LogLevel.INFO, compounding=False, create_ticket=False):
    """
    Posts the given message to the event log
    """

    if level == LogLevel.ERROR:
        print(bcolors.FAIL + message + bcolors.ENDC)
    elif level == LogLevel.WARNING:
        print(bcolors.WARNING + message + bcolors.ENDC)
    elif level == LogLevel.SUCCESS:
        print(bcolors.OKGREEN + message + bcolors.ENDC)
    else:
        print(bcolors.OKBLUE + message + bcolors.ENDC)

    if not is_agent_active("cgs_diagnostics_streamer_api"):
        return None

    payload = {
        "agent_id": "",
        "compounding": compounding,
        "create_ticket": create_ticket,
        "description": "Null",
        "error_code": "Null",
        "event_id": "",
        "level": level,
        "message": message,
        "module": "Updater",
        "property_id": "",
        "resolution": "Null",
        "robot_id": "",
        "source": "auto_updater",
        "timestamp": ""
    }

    env_val = args.config.config
    event_log_api = env_val['AGENT_POST_API'] + "/agentstream/put-record"
    payload['agent_id'] = env_val['AGENT_ID']
    payload['robot_id'] = env_val['ROBOT_CODE']
    payload['property_id'] = env_val['SITE_CODE']
    payload['event_id'] = str(uuid.uuid4())
    payload['timestamp'] = datetime.datetime.utcnow().isoformat()

    try:
        response = requests.post(event_log_api, json=payload, timeout=5)
        if response.status_code == http.HTTPStatus.OK:
            return payload
        else:
            print(f" {bcolors.WARNING} Failed to post message to event logs {bcolors.ENDC}")
            return None
    except Exception as ex:
        print(f"{bcolors.WARNING} Failed to post message to event logs: {ex} {bcolors.ENDC}")
        return None

def create_boto3_client(resource_type, config, region="ap-southeast-1"):
    """
    Creates a boto3 client for specified resource

    Paramters:

    resource_type (string): Type of resource  that the client will access
    config: The credentials for AWS

    Returns:
    The boto3 client
    """

    try:

        creds = ['AWS_SESSION_TOKEN', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_creds = [cred for cred in creds if cred not in config]
        if not missing_creds:
            client = boto3.client(resource_type,
                                  aws_session_token=config["AWS_SESSION_TOKEN"],
                                  aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
            return client
        else:
            print(bcolors.FAIL + f"Error creating boto3 client: missing credentials {missing_creds}" + bcolors.ENDC)
            return None
        
    except Exception as ex:
        print(bcolors.FAIL + f"Error creating boto3 client: {ex}" + bcolors.ENDC)
        return None


def get_user_confirmation(message: str) -> bool:
    """
    Get user confirmation for an action.

    Args:
        message: The confirmation message to display

    Returns:
        bool: True if user confirms, False otherwise
    """
    print(bcolors.WARNING + message + bcolors.ENDC)

    while True:
        response = input("Do you want to proceed? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print(bcolors.WARNING + "Please enter 'y' or 'n'" + bcolors.ENDC)



def log_message(msg, level: LogLevel):

    if level == LogLevel.ERROR:
        print(bcolors.FAIL + msg + bcolors.ENDC)
    elif level == LogLevel.WARNING:
        print(bcolors.WARNING + msg + bcolors.ENDC)
    elif level == LogLevel.SUCCESS:
        print(bcolors.OKGREEN + msg + bcolors.ENDC)
    else:
        print(bcolors.OKBLUE + msg + bcolors.ENDC)

