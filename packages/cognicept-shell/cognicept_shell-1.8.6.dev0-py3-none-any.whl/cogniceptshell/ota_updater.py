
import os
import re
import shutil
import zipfile
import subprocess
from cogniceptshell.common import create_boto3_client, post_event_log, LogLevel


class OTAUpdater:

    def populate_home_in_service_file(self, args, ota_server_service_file):
        try:
            with open(ota_server_service_file, "r") as service_file:
                service_file_data = service_file.read()
            service_file_data = re.sub(r'\${(HOME)}', os.path.expanduser("~"), service_file_data)
            with open(ota_server_service_file, "w") as service_file:
                service_file.write(service_file_data)  
            return True  
        except Exception as ex:
            print(f"Failed to populate service file: {ex}")
            return False        

    def populate_user_in_service_file(self, args, ota_server_service_file):
        try:
            with open(ota_server_service_file, "r") as service_file:
                service_file_data = service_file.read()
            service_file_data = re.sub(r'\${(USER)}', os.getlogin(), service_file_data)
            with open(ota_server_service_file, "w") as service_file:
                service_file.write(service_file_data)  
            return True  
        except Exception as ex:
            print(f"Failed to populate service file: {ex}")
            return False          

    def copy_service_file(self, ota_server_service_file):
        try:
            subprocess.check_call(["sudo", "cp", ota_server_service_file, "/etc/systemd/system"])
            return True
        except subprocess.CalledProcessError as ex:
            return False

    def reload_services(self):
        try:
            subprocess.check_call(["sudo", "systemctl", "daemon-reload"])
            return True
        except subprocess.CalledProcessError as ex:
            return False

    def enable_service(self):
        try: 
            subprocess.check_call(["sudo", "systemctl", "enable", "auto_update_server"])
            return True
        except subprocess.CalledProcessError as ex:
            return False

    def start_service(self):
        try:
            subprocess.check_call(["sudo", "systemctl", "restart", "auto_update_server"])
            return True
        except subprocess.CalledProcessError as ex:
            return False

    def disable_service(self):
        try:
            subprocess.check_call(["sudo", "systemctl", "disable", "auto_update_server"])
            return True
        except subprocess.CalledProcessError as ex:
            return False        

    def stop_service(self):
        try:
            subprocess.check_call(["sudo", "systemctl", "stop", "auto_update_server"])
            return True
        except subprocess.CalledProcessError as ex:
            return False
       
    def remove_ota_zip(self, ota_server_zip_file):
        if os.path.isfile(ota_server_zip_file):
            try:
                os.remove(ota_server_zip_file)
                return True
            except Exception as ex:
                return False

    def remove_ota_folder(self, ota_server_path):
        if os.path.isdir(ota_server_path):
            try:
                shutil.rmtree(ota_server_path)
                return True
            except Exception as ex:
                return False

    def remove_service_file(self, service_file):
        if os.path.isfile(service_file):
            try:
                subprocess.check_call(["sudo", "rm", service_file])
                return True
            except Exception as ex:
                return False

    def download_ota_server(self,args):

        # Check for ~/.cognicept folder
        ota_base = os.path.expanduser(args.path)
        if not os.path.isdir(os.path.expanduser(ota_base)):
            post_event_log(args, 
                        f"Cannot update ota server: {ota_base} does not exist",
                        LogLevel.ERROR)
            return False

        ota_server_bucket = "kabam-sg-ota-server"
        s3_client = create_boto3_client("s3", args.config.config)

        s3_objects = s3_client.list_objects_v2(Bucket=ota_server_bucket).get('Contents')
        if s3_objects is None:
            post_event_log(args, 
                        "Could not update ota server: Empty response", LogLevel.ERROR)
            return False

        ota_server_object_name = "auto_update_server.zip"
        ota_server_local_zip_path = os.path.join(ota_base, ota_server_object_name)
        if os.path.isfile(ota_server_local_zip_path):
            os.remove(ota_server_local_zip_path)
        if any(object["Key"] == ota_server_object_name for object in s3_objects):
            s3_client.download_file(ota_server_bucket, ota_server_object_name, ota_server_local_zip_path)

        
        if not os.path.isfile(ota_server_local_zip_path):
            post_event_log(args,
                        f"Could not update ota server: file not found at {ota_server_local_zip_path}",
                        LogLevel.ERROR)
            return False

        ota_server_path = os.path.join(ota_base, "auto_update_server")
        if os.path.isdir(ota_server_path):
            shutil.rmtree(ota_server_path)
        with zipfile.ZipFile(ota_server_local_zip_path, "r") as ota_server_compressed:
            ota_server_compressed.extractall(path=ota_base)

        post_event_log(args, "Installing pip requirements", LogLevel.INFO)
        subprocess.check_call(["pip", "install", "-r", os.path.join(ota_server_path, "requirements.txt")])

        post_event_log(args, "OTA server updated successfully", LogLevel.SUCCESS)
        return True


    def create_ota_lock_folder(self, lock_folder_path):

        try:
            os.mkdir(lock_folder_path)
            return True
        except:
            return False


    def setup_ota_server(self,args):

        # Check for ~/.cognicept folder
        ota_base = os.path.expanduser(args.path)
        if not os.path.isdir(os.path.expanduser(ota_base)):
            post_event_log(args, 
                        f"Cannot setup ota server: {ota_base} does not exist", LogLevel.ERROR)
            return False

        # Check for ota lock folder
        ota_lock_folder = os.path.join(ota_base,"ota")
        if not os.path.isdir(ota_lock_folder):
            if not self.create_ota_lock_folder(ota_lock_folder):
                post_event_log(args, "Could not setup ota lock folder", LogLevel.ERROR)
                return False

        ota_server_bucket = "kabam-sg-ota-server"
        s3_client = create_boto3_client("s3", args.config.config)

        s3_objects = s3_client.list_objects_v2(Bucket=ota_server_bucket).get('Contents')
        if s3_objects is None:
            post_event_log(args, "Could not setup ota service: Empty response", LogLevel.ERROR)
            return False

        ota_server_object_name = "auto_update_server.service"
        ota_server_service_file = os.path.join(ota_base, ota_server_object_name)
        if any(object["Key"] == ota_server_object_name for object in s3_objects):
            s3_client.download_file(ota_server_bucket, ota_server_object_name, ota_server_service_file)

        if not os.path.isfile(ota_server_service_file):
            post_event_log(args, "Could not setup ota service: service file not found", LogLevel.ERROR)
            return False

        # Fill value of the HOME variable
        if not self.populate_home_in_service_file(args, ota_server_service_file):
            post_event_log(args, "Could not setup ota server: Failed to populate HOME in service file", LogLevel.ERROR)
            return False
        
        if not self.populate_user_in_service_file(args, ota_server_service_file):
            post_event_log(args, "Could not setup ota server: Failed to populate USER in service file", LogLevel.ERROR)
            return False

        post_event_log(args,"Root privilage is required to copy service file to `/etc/systemd/system and start the service \nPlease input root password if prompted", LogLevel.WARNING)
        
        post_event_log(args, "Copying service file to system")
        if not self.copy_service_file(ota_server_service_file):
            post_event_log(args, f"Could not setup ota service: Failed to copy service file", LogLevel.ERROR)
            return False
         
        post_event_log(args, "Reloading services", LogLevel.INFO)
        if not self.reload_services():
            post_event_log(args, f"Could not setup ota service: Failed to reload services", LogLevel.ERROR)
            return False

        post_event_log(args, "Enabling ota service")   
        if not self.enable_service():
            post_event_log(args, f"Could not setup ota service: Failed to enable service", LogLevel.ERROR)
            return False

        post_event_log(args, "Starting ota service")
        if not self.start_service():
            post_event_log(args, f"Could not setup ota service: Failed to start service", LogLevel.ERROR)
            return False

        
        post_event_log(args, "Sucessfully started the ota server", LogLevel.SUCCESS)
        return True

    def disable_ota(self, args):
        
        ota_base = os.path.expanduser(args.path)
        ota_server_path = os.path.join(ota_base, "auto_update_server")
        ota_server_zip_file = ota_server_path + ".zip"

        post_event_log(args, "Root permission is required for disabling the OTA agent, please input sudo passowrd if prompted", LogLevel.WARNING) 
        
        post_event_log(args, "Disabling ota service")
        if not self.disable_service():
            post_event_log(args, f"Could not disable ota service", LogLevel.ERROR)
            return False
        
        post_event_log(args, "Stopping ota service")
        if not self.stop_service():
            post_event_log(args, f"Could not stop ota service", LogLevel.ERROR)
            return False

        post_event_log(args, "Removing ota zip file")
        if not self.remove_ota_zip(ota_server_zip_file):
            post_event_log(args, "Could not remove ota zip file", LogLevel.ERROR)
            return False
        
        post_event_log(args, "Removing ota server")
        if not self.remove_ota_folder(ota_server_path):
            post_event_log(args, f"Could not remove ota server source", LogLevel.ERROR)
            return False

        service_file = "/etc/systemd/system/auto_update_server.service"
        post_event_log(args, f"Removing service file from: {service_file}", LogLevel.WARNING)
        if not self.remove_service_file(service_file):
            post_event_log(args, f"Failed to delete service file", LogLevel.ERROR)
            return False
        
        post_event_log(args, "Successfully disabled and removed OTA server", LogLevel.SUCCESS)
        return True
