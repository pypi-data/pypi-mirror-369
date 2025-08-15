# coding=utf8
# Copyright 2023 Cognicept Systems
# Author: Kenneth Chow (kenneth.chow@kabam.ai)
# --> RobotActions class handles on demand custom robot actions on cognicept-shell

import getpass
import json
import requests
import jwt
import io 
import base64
from cogniceptshell.common import bcolors
from cogniceptshell.configuration import Configuration
from cogniceptshell.agent_life_cycle import AgentLifeCycle

class RobotActions:
    """
    A class to manage robot
    ...

    Parameters
    ----------
    None

    Methods
    -------
    login(username, password):
        API call to login the user to smart+

    get_organization(org_id, headers):
        API call to retrieve organization details

    get_robot(robot_id, org_id, headers):
        API call to retrieve robot details
    
    create_robot(robot_details, headers):
        API call to create robot

    get_robot_missions(robot_id, headers):
        API call to retrieve missions associated with robot_id
    
    get_mission_instances(mission_id, headers):
        API call to retrieve instances associated with mission_id
    
    create_mission(mission_details, headers):
        API call to create mission
    
    create_waypoint(waypoint_details, headers):
        API call to create waypoint

    get_map(map_id, headers):
        API call to retrieve map 

    create_map(map_details, headers):
        API call to create map

    get_schedules(schedule_id, headers):
        API call to retrieve schedule

    create_schedule(schedule_details, headers):
        API call to create schedule

    get_property_by_id(property_id, headers):
        API call to retrieve property by property_id

    get_property_by_filter(filters, headers):
        API call to retrieve property by filters

    create_property(property_details, headers):
        API call to create property

    switch_org(org_id, headers):
        API call to switch organizations

    rollback(created_data, headers):
        Deletes any created data if an error occurs 
    
    """

    def login(self, username, password):
        login_base_uri = self.api_uri + "user/login"
        login_resp = requests.post(login_base_uri, json={"username": str(username), "password": str(password)}, timeout=5)
        if json.loads(login_resp.content.decode()).get('message', '') == "Username and password combination not valid":
            print(bcolors.FAIL + "Error in logging in: Wrong credentials" + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(login_resp.content.decode())['access_token']

    def mfa_verfication(self, auth_key, headers):
        mfa_verification_base_uri = self.api_uri + "user/mfa/verify"
        otp_trial = 3
        loop = True
        while loop:
            if otp_trial == 0:
                key = auth_key
                loop = False
            else:
                otp = getpass.getpass('OTP from Authenticator: ')
                x = requests.post(mfa_verification_base_uri, headers=headers, json={'otp': otp})
                if 'access_token' not in x.json():
                    print('Invalid OTP! Please try again...')
                else:
                    key = x.json()["access_token"]
                    loop = False
            otp_trial -= 1
        return key
    
    def get_organization_by_id(self, org_id, headers):
        org_base_uri = self.api_uri + "organization/"
        get_org_uri = org_base_uri + '?filter={{"organization_id":"{org_id}"}}'.format(org_id=org_id)
        get_org_resp = requests.get(get_org_uri, headers=headers, timeout=5)
        json_resp = json.loads(get_org_resp.content.decode())
        if get_org_resp.status_code != 200 or (isinstance(json_resp.get('data', ''), dict) and 'psycopg2.errors' in json_resp['data'].get('Message', '')):
             print(bcolors.FAIL + "Error in getting organization {org_id}".format(org_id=org_id) + bcolors.ENDC)
             raise SystemExit(1)
        elif len(json.loads(get_org_resp.content.decode())['data']) == 0:
             print(bcolors.FAIL + "No such organization {org_id}".format(org_id=org_id) + bcolors.ENDC)
             raise SystemExit(1)
        return json.loads(get_org_resp.content.decode())['data'][0]
    
    def get_organization_by_org_code(self, org_code, headers):
        org_base_uri = self.api_uri + "organization/"
        get_org_uri = org_base_uri + '?filter={{"organization_code":"{org_code}"}}'.format(org_code=org_code)
        get_org_resp = requests.get(get_org_uri, headers=headers, timeout=5)
        if get_org_resp.status_code != 200:
             print(bcolors.FAIL + "Error in getting organization" + bcolors.ENDC)
             raise SystemExit(1)
        elif len(json.loads(get_org_resp.content.decode())['data']) == 0:
             print(bcolors.FAIL + "No such organization {org_code}".format(org_code=org_code) + bcolors.ENDC)
             raise SystemExit(1)           
        return json.loads(get_org_resp.content.decode())['data'][0]

    def get_robot_by_id(self, robot_id, org_id, headers):
        get_robot_uri = self.api_uri + "robot/organization?robot_id={robot_id}&organization_id={org_id}".format(robot_id=robot_id, org_id=org_id)
        get_robot_resp = requests.get(get_robot_uri, headers=headers, timeout=5)
        if get_robot_resp.status_code != 200:
            print(bcolors.FAIL + "Error in retrieving robot" + bcolors.ENDC)
            raise SystemExit(1)
        elif len(get_robot_resp.content.decode()) == 0 or json.loads(get_robot_resp.content.decode()).get('message', '') == 'Bad request. Invalid input':
            print(bcolors.FAIL + "No such robot {robot_id} in organization {org_id}".format(robot_id=robot_id, org_id=org_id) + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_robot_resp.content.decode())

    def get_robot_by_code(self, robot_code, org_code, headers):
        get_robot_uri = self.api_uri + "robot/organization_code?robot_code={robot_code}&organization_code={org_code}".format(robot_code=robot_code, org_code=org_code)
        get_robot_resp = requests.get(get_robot_uri, headers=headers, timeout=5)
        if get_robot_resp.status_code != 200:
             print(bcolors.FAIL + "Error in retrieving robot. Message: {err}".format(err=json.loads(get_robot_resp.content.decode()).get('message', '')) + bcolors.ENDC)
             raise SystemExit(1)
        elif len(json.loads(get_robot_resp.content.decode())) == 0 or json.loads(get_robot_resp.content.decode()).get('message', '') == 'Bad request. Invalid input':
            print(bcolors.FAIL + "No such robot {robot_code} in organization {org_code}".format(robot_code=robot_code, org_code=org_code) + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_robot_resp.content.decode())

    def create_robot(self, robot_details, headers):
        create_robot_uri = self.api_uri + "robot/"
        create_robot_resp = requests.post(create_robot_uri, json=robot_details, headers=headers, timeout=5)
        if create_robot_resp.status_code != 200:
             raise Exception(bcolors.FAIL + "Error in creating robot" + bcolors.ENDC)
        return json.loads(create_robot_resp.content.decode())['robot_id']

    def delete_robot(self, robot_id, organization_id, headers):
        delete_robot_uri = self.api_uri + "robot/organization"
        delete_robot_resp = requests.delete(delete_robot_uri, params={"robot_id": "{robot_id}".format(robot_id=robot_id), "organization_id": "{organization_id}".format(organization_id=organization_id)}, headers=headers, timeout=5)
        if delete_robot_resp.status_code != 200:
             print(bcolors.FAIL + "Error in deleting robot {robot_id}. Please manually delete it".format(robot_id=robot_id) + bcolors.ENDC)
             return None
        return json.loads(delete_robot_resp.content.decode()).get('message', None)

    def get_robot_missions(self, robot_id, headers):
        mission_base_uri = self.api_uri + "mission/"
        get_mission_uri = mission_base_uri + '?filter={{"robot_id": "{robot_id}"}}'.format(robot_id=robot_id)
        get_mission_resp = requests.get(get_mission_uri, headers=headers, timeout=5)
        if get_mission_resp.status_code != 200:
             print(bcolors.FAIL + "Error in retrieving missions" + bcolors.ENDC)
             raise SystemExit(1)
        mission_list = json.loads(get_mission_resp.content.decode())['data']
        return mission_list
    
    def create_mission(self, mission_details, headers, tries=0):
        create_mission_uri = self.api_uri + "mission/"
        create_mission_resp = requests.post(create_mission_uri, json=mission_details, headers=headers, timeout=5)
        if create_mission_resp.status_code != 200:
            if 'UniqueViolation' in json.loads(create_mission_resp.content.decode())['message'] and tries < 50: 
                return self.create_mission(mission_details, headers, tries)
            else:
                raise Exception(bcolors.FAIL + "Error in creating mission" + bcolors.ENDC)
        return json.loads(create_mission_resp.content.decode())['mission_id']
    
    def delete_mission(self, mission_id, headers):
        delete_mission_uri = self.api_uri + "mission/{mission_id}".format(mission_id=mission_id)
        delete_mission_resp = requests.delete(delete_mission_uri, headers=headers, timeout=5)
        if delete_mission_resp.status_code != 200:
            print(bcolors.FAIL + "Failed to delete mission {mission_id}. Please manually delete it".format(mission_id=mission_id) + bcolors.ENDC)
            return None
        else:
            print("successfully deleted mission {mission_id}".format(mission_id=mission_id))
            return json.loads(delete_mission_resp.content.decode()).get('mission_id', None)
    
    def get_mission_instances(self, mission_id, headers):
        mission_instance_base_uri = self.api_uri + "mission-instance/"
        get_mission_instance_uri = mission_instance_base_uri + '?filter={{"mission_id": "{mission_id}"}}'.format(mission_id=mission_id)
        get_mission_instance_resp = requests.get(get_mission_instance_uri, headers=headers, timeout=5)
        if get_mission_instance_resp.status_code != 200:
            print(bcolors.FAIL + "Error retrieving mission instance" + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_mission_instance_resp.content.decode())['data']

    def create_mission_instance(self, mission_instance_details, headers):
        create_mission_instance_uri = self.api_uri + "mission-instance/"
        create_mission_instance_resp = requests.post(create_mission_instance_uri, json=mission_instance_details, headers=headers)
        if create_mission_instance_resp.status_code != 200:
            raise Exception(bcolors.FAIL + "Error in creating mission instance" + bcolors.ENDC)
        return json.loads(create_mission_instance_resp.content.decode())['mission_instance_id']

    def delete_mission_instance(self, mission_instance_id, headers):
        delete_mission_instance_uri = self.api_uri + "mission-instance/" + str(mission_instance_id)
        delete_mission_instance_resp = requests.delete(delete_mission_instance_uri, headers=headers, timeout=5)
        if delete_mission_instance_resp.status_code != 200:
            print(bcolors.FAIL + "Failed to delete mission_instance {mission_instance_id}. Please manually delete it".format(mission_instance_id=mission_instance_id) + bcolors.ENDC)
        else:
            print("successfully deleted mission_instance {mission_instance_id}".format(mission_instance_id=mission_instance_id))
    
    def get_waypoints_from_map_id(self, map_id, headers):
        waypoint_base_uri = self.api_uri + "waypoint/"
        get_waypoint_uri = waypoint_base_uri + '?filter={{"map_id": "{map_id}"}}'.format(map_id=map_id)
        get_waypoint_resp = requests.get(get_waypoint_uri, headers=headers, timeout=5)
        if get_waypoint_resp.status_code != 200:
            print(bcolors.FAIL + "Error retrieving waypoint" + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_waypoint_resp.content.decode())['data']

    def create_waypoint(self, waypoint_details, headers):
        waypoint_base_uri = self.api_uri + "waypoint/"
        create_waypoint_uri = waypoint_base_uri
        create_waypoint_resp = requests.post(create_waypoint_uri, json=waypoint_details, headers=headers, timeout=5)
        if create_waypoint_resp.status_code != 200:
            raise Exception(bcolors.FAIL + "Error in creating waypoint" + bcolors.ENDC)
        return json.loads(create_waypoint_resp.content.decode())['waypoint_id']
    
    def delete_waypoint(self, waypoint_id, headers):
        delete_waypoint_uri = self.api_uri + "waypoint/"
        delete_waypoint_uri += str(waypoint_id)
        delete_waypoint_resp = requests.delete(delete_waypoint_uri, headers=headers, timeout=5)
        if delete_waypoint_resp.status_code != 200:
            print(bcolors.FAIL + "Failed to delete waypoint {waypoint_id}. Please manually delete it".format(waypoint_id=waypoint_id) + bcolors.ENDC)
        else:
            print("successfully deleted waypoint {waypoint_id}".format(waypoint_id=waypoint_id))
    
    def get_map_image(self, map_id, headers):
        map_base_uri = self.api_uri + "map/"
        get_map_uri = map_base_uri + "{map_id}".format(map_id=map_id)
        get_map_resp = requests.get(get_map_uri, headers=headers, timeout=5)
        if get_map_resp.status_code != 200:
            print(bcolors.FAIL + "Error retrieving map {map_id}".format(map_id=map_id) + bcolors.ENDC)
            raise SystemExit(1)
        try:
            image_file = io.BytesIO(get_map_resp.content)
            image_data = image_file.read()
            b64_string = base64.b64encode(image_data).decode('utf-8')
        except Exception as err:
            print("Failed to decode image file")
            raise SystemExit(1)
        
        return b64_string
    
    def get_maps_from_robot_id(self, robot_id, headers):
        map_base_uri = self.api_uri + "map/"
        get_map_uri = map_base_uri + '?filter={{"robot_id":"{robot_id}"}}'.format(robot_id=robot_id)
        get_map_resp = requests.get(get_map_uri, headers=headers, timeout=5)
        if get_map_resp.status_code != 200:
            print(bcolors.FAIL + "Error retrieving maps associated to robot {robot_id}".format(robot_id=robot_id) + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_map_resp.content.decode())['data']
    
    def create_map(self, map_details, headers):
        create_map_uri = self.api_uri + "map/"
        create_map_resp = requests.post(create_map_uri, json=map_details, headers=headers, timeout=5)
        if create_map_resp.status_code != 200:
            raise Exception(bcolors.FAIL + "Error in creating map" + bcolors.ENDC)
        return json.loads(create_map_resp.content.decode())['map_id']

    def delete_map(self, map_id, headers):
        delete_map_uri = self.api_uri + "map/"
        delete_map_uri += str(map_id)
        delete_map_resp = requests.delete(delete_map_uri, headers=headers, timeout=5)
        if delete_map_resp.status_code != 200:
            print(bcolors.FAIL + "Failed to delete map {map_id}. Please manually delete it".format(map_id=map_id) + bcolors.ENDC)
            return None
        else:
            print("successfully deleted map {map_id}".format(map_id=map_id))
            return json.loads(delete_map_resp.content.decode()).get('map_id', None)

    def get_schedules(self, schedule_id, headers):
        schedule_base_uri = self.api_uri + "schedule/"
        get_schedule_uri = schedule_base_uri + 'metadata/{schedule_id}'.format(schedule_id=schedule_id)
        get_schedule_resp = requests.get(get_schedule_uri, headers=headers, timeout=5)
        if get_schedule_resp.status_code != 200:
            print(bcolors.FAIL + "Error in retrieving schedule {schedule_id}".format(schedule_id=schedule_id) + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_schedule_resp.content.decode())
    
    def create_schedule(self, schedule_details, headers):
        create_schedule_uri = self.api_uri + "schedule/"
        create_schedule_resp = requests.post(create_schedule_uri, json=schedule_details, headers=headers, timeout=5)
        if create_schedule_resp.status_code != 200:
            raise Exception(bcolors.FAIL + "Error in creating schedule. Error: {err}".format(err=json.loads(create_schedule_resp.content.decode()).get('message', '')) + bcolors.ENDC)
        return json.loads(create_schedule_resp.content.decode())['schedule_id']
    
    def delete_schedule(self, schedule_id, headers):
        delete_schedule_uri = self.api_uri + "schedule/" + str(schedule_id)
        delete_schedule_resp = requests.delete(delete_schedule_uri, headers=headers, timeout=5)
        if delete_schedule_resp.status_code != 200:
            print(bcolors.FAIL + "Failed to delete schedule {schedule_id}. Please manually delete it".format(schedule_id=schedule_id) + bcolors.ENDC)
            return None
        else:
            print("successfully deleted schedule {schedule_id}".format(schedule_id=schedule_id))
            return json.loads(delete_schedule_resp.content.decode()).get('schedule_id', None)
    
    def get_property_by_id(self, property_id, headers):
        property_base_uri = self.api_uri + "property/"
        get_property_uri = property_base_uri + "{property_id}".format(property_id=property_id)
        get_property_resp = requests.get(get_property_uri, headers=headers, timeout=5)
        if get_property_resp.status_code != 200:
            print(bcolors.FAIL + "Error in retrieving property {property_id} of robot".format(property_id=property_id) + bcolors.ENDC)
            raise SystemExit(1)
        return json.loads(get_property_resp.content.decode())
    
    def get_property_by_filter(self, filters, headers):
        property_base_uri = self.api_uri + "property/"
        filter_string = '?filter={'
        index = 0
        for key, value in filters.items():
            filter_string += '"{key}": "{value}"'.format(key=key, value=value)
            if index != len(filters) - 1:
                filter_string += ', '
            index += 1
        filter_string += '}'
        
        get_property_uri = property_base_uri + filter_string
        get_property_resp = requests.get(get_property_uri, headers=headers, timeout=5)
        if get_property_resp.status_code != 200:
            print(bcolors.FAIL + "Error in retrieving property of robot" + bcolors.ENDC)
            raise SystemExit(1)
        get_property_data = json.loads(get_property_resp.content.decode())['data']
        return get_property_data
    
    def create_property(self, property_details, headers):
        property_base_uri = self.api_uri + "property/"
        create_property_resp = requests.post(property_base_uri, json=property_details, headers=headers, timeout=5)
        if create_property_resp.status_code != 200: 
            raise Exception(bcolors.FAIL + "Error in creating property for new organization. Error: {err}"
                            .format(err=json.loads(create_property_resp.content.decode()).get('message', None)) + bcolors.ENDC)
        return json.loads(create_property_resp.content.decode())['property_id'] 

    def delete_property(self, property_id, headers):
        delete_property_uri = self.api_uri + "property/{property_id}".format(property_id=property_id)
        delete_property_resp = requests.delete(delete_property_uri, headers=headers, timeout=5)
        if delete_property_resp.status_code != 200:
            print(bcolors.FAIL + "Failed to delete property {property_id}. Please manually delete it".format(property_id=property_id) + bcolors.ENDC)
            return None
        else:
            print("successfully deleted property {property_id}".format(property_id=property_id))
            return json.loads(delete_property_resp.content.decode()).get('property_id', None)
        
    def get_robot_config(self, org_id, robot_id, headers):
        get_config_uri = self.api_uri + f'robot_config/config/{org_id}/{robot_id}'
        get_config_resp = requests.get(get_config_uri, headers=headers, timeout=5)
        if get_config_resp.status_code != 200:
            print(get_config_resp.content)
            print(bcolors.FAIL + "Failed to fetch new robot config file" + bcolors.ENDC)
            return None
        return json.loads(get_config_resp.content.decode())

    def switch_org(self, org_id, headers):
        switch_org_uri = self.api_uri + "user/switch_org"
        switch_org_payload = {
             'organization_id': org_id,
             "blacklist": True
        }   
        switch_org_resp = requests.post(switch_org_uri, json=switch_org_payload, headers=headers, timeout=5)
        if switch_org_resp.status_code != 200:
            print(bcolors.FAIL + "Error in switching organization" + bcolors.ENDC)
            raise SystemExit(1)
        new_access_token = json.loads(switch_org_resp.content.decode())['access_token']
        return new_access_token
    
    def rollback(self, created_data, headers):
        for key, value in created_data.items():
            if key == 'property_id':
                self.delete_property(value, headers)
            if key == 'robot':
                if value.get('robot_id', None):
                    self.delete_robot(robot_id=value.get('robot_id'), organization_id=value.get('organization_id', ''), headers=headers)
            if key == 'missions':
                for mission_id in value:
                    self.delete_mission(mission_id, headers=headers)
            if key == 'waypoints':
                for waypoint_id in value:
                    self.delete_waypoint(waypoint_id, headers=headers)
            if key == 'schedules':
                for schedule_id in value:
                    self.delete_schedule(schedule_id, headers=headers)
            if key == 'maps':
                for map_id in value:
                    if map_id:
                        self.delete_map(map_id, headers=headers)
            if key == 'mission_instances':
                for mission_instance_id in value:
                    self.delete_mission_instance(mission_instance_id, headers=headers)

