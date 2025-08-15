import os
import json
from pyclmuapp.clmu import *
from datetime import datetime
#from pyclmuapp.config.scripts import *
from typing import Union
class clumapp:

    """
    The class for running CLMU-App.

    Args:
        pwd (str): The path to the working directory. The default is "wokdir".
        input_path (str): The path to the folder for the input of CLMU-App.
        output_path (str): The path to the folder for the output of CLMU-App.
        log_path (str): The path to the folder for the log of CLMU-App.
        scripts_path (str): The path to the folder for the scripts of CLMU-App.
        container_type (str): The type of the container for CLMU-App. The supported types are:
            - docker: The docker container.
            - singularity: The singularity container.

    Attributes:
        - input_path (str): The path to the folder for the input of CLMU-App.
        - output_path (str): The path to the folder for the output of CLMU-App.
        - log_path (str): The path to the folder for the log of CLMU-App.
        - image_name (str): The name of the image for CLMU-App.
        - container_name (str): The name of the container for CLMU-App.
        - caseconfig (dict): The configuration of the case to be built.
        - fsurdat_path (str): The path to the surface input file.
        - save_name (str): The name of the output file.
        - caseconfig (dict): The configuration of the case to be built.
        - clmu_run (cesm_run): The object for running CLMU-App.

    """

    def __init__(self, 
                 pwd = os.path.join(os.getcwd(), 'workdir'),
                 input_path: str = "inputfolder",
                 output_path: str = "outputfolder",
                 log_path: str = "logfolder",
                 scripts_path: str = "scriptsfolder",
                 container_type: str = "docker"
                 ):
        """
        
        Args:
            pwd (str): The path to the working directory. The default is pwd+"workdir".
            input_path (str): The path to the folder for the input of CLMU-App.
            output_path (str): The path to the folder for the output of CLMU-App.
            log_path (str): The path to the folder for the log of CLMU-App.
        
        """
        #self.input_path = pwd + "/" + self.create_folder(input_path)

        #self.output_path = pwd + "/" + self.create_folder(output_path)
        #self.log_path = pwd + "/" +  self.create_folder(log_path)
        #self.scripts_path = pwd + "/" + self.create_folder(scripts_path)
        if pwd is not None:
            os.makedirs(pwd, exist_ok=True)
            self.pwd = pwd
            self.input_path = os.path.join(pwd, self.create_folder(os.path.join(pwd, input_path)))
            self.output_path = os.path.join(pwd, self.create_folder(os.path.join(pwd, output_path)))
            self.log_path = os.path.join(pwd, self.create_folder(os.path.join(pwd, log_path)))
            self.scripts_path = os.path.join(pwd, self.create_folder(os.path.join(pwd, scripts_path)))
        else:
            self.input_path = input_path
            self.output_path = output_path
            self.log_path = log_path
            self.scripts_path = scripts_path
        self.fsurdat_path = None
        # CLMU-App run
        self.image_name = "envdes/clmu-app:1.1"
        self.container_name = "myclmu"
        self.container_type = container_type

        if container_type == "docker":
            self.container_name = "myclmu"
        elif container_type == "singularity":
            self.container_name = os.path.join(os.getcwd(), "clmu-app_1.1.sif")
            #os.environ["SINGULARITY_BINDPATH"] = scripts_cmd['singularity'].format(
            #    input_path=self.input_path,
            #    output_path=self.output_path,
            #    log_path=self.log_path,
            #    scripts_path=self.scripts_path
            #)
            if not os.path.join(os.path.expanduser('~'), '.cime'):
                shutil.copytree(os.path.join(os.path.dirname(__file__), 'config/cime_config'),
                            os.path.join(os.path.expanduser('~'), '.cime'))
        elif container_type == "docker_in":
            self.container_name = "myclmu"
        else:
            raise ValueError(f"Container type '{container_type}' is not supported.")

    def create_folder(self, folder_path) -> str:

        """
        Create folders for the scripts ,input, output and log of CLMU-App if it does not exist.
        
        Args:
            folder_path (str): The path to the folder to be created.
        
        Returns:
            folder_path (str): The path to the folder created.
        """
        os.makedirs(folder_path, exist_ok=True)

        #try:
        #    os.makedirs(folder_path) 
        #    #print(f"Folder '{folder_path}' created successfully!")
        #except FileExistsError:
        #    print(f"Folder '{folder_path}' already exists.")

        return folder_path


    def docker(self,
               cmd: str = "run",
               iflog : bool = True,
               password: str = "None",
               cmdlogfile: str = None,
               dockersript: str = "docker.sh",
               ) -> None:

        """
        Run the docker command.

        Args:
            cmd (str): The docker command to be run. The supported commands are:
                - pull: Pull the docker image.
                - chmod: Change the mode of a file.
                - run: create a docker container.
                - exec: Execute the docker command.
            iflog (bool, optional): If log is needed. The default is True.
            password (str, optional): The password for the sudo command. The default is "None".
            cmdlogfile (str, optional): The name of the log file. The default is "dockercmd.log".
            dockersript (str, optional): The name of the docker script. The default is "docker.sh".
        """
        
        if cmdlogfile is None:
            cmdlogfile = os.path.join(self.pwd, "dockercmd.log")

        if self.container_type == "docker":
            if self.image_name == "envdes/clmu-app:1.1":
                with open(os.path.join(os.path.dirname(__file__),'./config/ini_docker_1.1.json')) as f:
                    config = json.load(f)
            else:
                with open(os.path.join(os.path.dirname(__file__),'./config/ini_docker.json')) as f:
                    config = json.load(f)
        elif self.container_type == "singularity":
            if self.image_name == "envdes/clmu-app:1.1":
                with open(os.path.join(os.path.dirname(__file__),'./config/ini_sing_1.1.json')) as f:
                    config = json.load(f)
            else:
                with open(os.path.join(os.path.dirname(__file__),'./config/ini_sing.json')) as f:
                    config = json.load(f)
        elif self.container_type == "docker_in":
            with open(os.path.join(os.path.dirname(__file__),'./config/ini_docker_in.json')) as f:
                config = json.load(f)


        if cmd in config.keys():

            if password != "None":
                command = "sudo -S " + config[cmd]
            else:
                command = config[cmd]
                
            if os.name == 'nt':
                command = command.replace("'", '"')

            command = command.format(
                image_name=self.image_name,
                container_name=self.container_name,
                input_path=self.input_path,
                output_path=self.output_path,
                log_path=self.log_path,
                scripts_path=self.scripts_path,
                command=dockersript
            )
            
            #print(f"Running the docker command: '{command}'")
            run_command(command=command,
                        password=password,
                        logname=cmdlogfile,
                        iflog=iflog
                        )
        else:
            print(f"Command '{cmd}' is not supported.")
            raise ValueError

    def case_scripts(self, mode: str = "usp") -> None:

        """
        Copy the scripts to the input folder.

        Args:
            mode (str): The mode of the scripts. The supported modes are:
        """

        # Copy the user_single_point.sh to the input folder
        if mode == "usp":
            destination_path = 'usp/usp.sh'
            self.script_path = os.path.join(self.input_path, destination_path)
        elif mode == "pts":
            destination_path = 'scripts/pts.sh'
            self.script_path = os.path.join(self.scripts_path, destination_path)

        else:
            raise ValueError (f"The {mode} is not supported.")
        
        if os.path.exists(self.script_path):
            pass
            #print(f"The {self.script_path} already exists.")
        else:
            if self.image_name == "envdes/clmu-app:1.1" and mode == "usp":
                shutil.copy(os.path.join(os.path.dirname(__file__), f'scripts/{mode}_1.1.sh'), 
                    self.script_path)
            else:
                shutil.copy(os.path.join(os.path.dirname(__file__), f'scripts/{mode}.sh'), 
                        self.script_path)
        # CMD used to run the CLMU-App
        if self.image_name == "envdes/clmu-app:1.1":
            from pyclmuapp.config.scripts2 import scripts_cmd
        else:
            from pyclmuapp.config.scripts import scripts_cmd
            
        self.command=scripts_cmd[mode]

    def case_clean(self, case_name : str = None) -> None:
        """
        Clean the case artifacts.
        Args:
            case_name (str): The name of the case to be cleaned.
        """

        if case_name is None:
            case_name = self.case_name
        # Remove the input, output and log folders

        #shutil.rmtree(os.path.join(self.scripts_path, case_name))
        #shutil.rmtree(os.path.join(self.log_path, case_name))
        
        self.docker(cmd="usp-exec",
                    dockersript=f"rm -rf /p/scripts/{case_name}",
                    iflog=False)
        self.docker(cmd="usp-exec",
                    dockersript=f"rm -rf /p/scratch/CESMDATAROOT/CaseOutputs/{case_name}",
                    iflog=False)
        
        if os.path.exists(os.path.join(self.input_path, 'usp')):
            shutil.rmtree(os.path.join(self.input_path, 'usp'))
