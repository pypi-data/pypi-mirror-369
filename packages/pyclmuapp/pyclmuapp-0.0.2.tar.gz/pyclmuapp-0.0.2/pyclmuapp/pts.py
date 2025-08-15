import os
import re
import json
from pyclmuapp.clmu import *
from datetime import datetime
from pyclmuapp.container import clumapp

class pts_clmu(clumapp):
    
    def __init__(self,
                 pwd = os.path.join(os.getcwd(), "workdir"),
                 input_path: str = "inputfolder",
                 output_path: str = "outputfolder",
                 log_path: str = "logfolder",
                 scripts_path: str = "scriptsfolder",
                 container_type: str = "docker") -> None:
        
        super().__init__(pwd=pwd, input_path=input_path, 
                         output_path=output_path, log_path=log_path, scripts_path=scripts_path, 
                         container_type=container_type)

        with open(os.path.join(os.path.dirname(__file__), "config/config_man.json"), 'r') as f:
            self.caseconfig = json.load(f)

        
    def _clmu(self, caseconfig: Union[str, dict, pd.DataFrame, pd.Series]) -> cesm_run:
        """
        create a cesm_run object.

        Args:
            caseconfig (Union[str, dict, pd.DataFrame, pd.Series]): The configuration of the case to be built.
        Returns:
            cesm_run: The object for running CLMU-App.
        """
        self.clmu_run = cesm_run(
                            CASESCRIPT_local = self.input_path, 
                            CASEROOT_local = self.log_path,
                            DOUT_S_ROOT = self.output_path,
                            caseconfig=caseconfig)
        
        return self.clmu_run
    
    def _read_surfin(self, caseconfig: Union[str, dict, pd.DataFrame, pd.Series] = "None") -> str:
        """
        Read the surface input file. read the lnd_in after the case was built.
        
        Args:
            caseconfig (Union[str, dict, pd.DataFrame, pd.Series], optional): The configuration of the case to be built. The default is "None".
                "None" means the default configuration is used.
        Returns:
            filename (str): The path to the surface input file.
        """
        if caseconfig == "None":
            caseconfig = self.caseconfig
        else:
            self.caseconfig = getconfig(caseconfig)
            caseconfig = self.caseconfig
        #filename = self.log_path + "/" + caseconfig["case_name"] + "/run/lnd_in"
        filename = self.scripts_path + "/" + caseconfig["case_name"] + "/CaseDocs/lnd_in"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    if 'fsurdat' in line:
                        parts = line.split()
                        self.fsurdat_path = parts[parts.index('fsurdat') + 2].replace('\'', '')
                        break
        else:
            print(f"File '{filename}' does not exist.")
            raise ValueError
        return self.fsurdat_path
    
    def _case_run_(self, 
                task: str, 
                caseconfig: Union[str, dict, pd.DataFrame, pd.Series] = "None",
                iflog: bool = True,
                password: str = "None",
                cmdlogfile: str = "dockercmd.log"
                ) -> None:
        """
        Run a CTSM case using the docker container.

        Args:
            task (str): The type of the case to be built.
                        build: Build the case.
                        revise: Revise the case.
                        submit: Submit the case.
            caseconfig (Union[str, dict, pd.DataFrame, pd.Series], optional): The configuration of the case to be built. The default is "None".
                "None" means the default configuration is used.
            iflog (bool, optional): If log is needed. The default is True.
        """
        if caseconfig == "None":
            caseconfig = self.caseconfig
        else:
            self.caseconfig = getconfig(caseconfig)
            caseconfig = self.caseconfig
        _biuld = self._clmu(caseconfig)
        case_script = "{scripts_path}/{case_name}_{task}.sh"
        script = _biuld.create_case(scriptpath=os.path.join(os.path.dirname(__file__),"./scripts/PTS_{task}.sh".format(task=task)))
        with open(case_script.format(scripts_path=self.scripts_path,
                            case_name=caseconfig["case_name"],
                            task=task),
                'w'
                ) as f:
            f.write(script)
        self.docker(cmd="chmod",
                    password=password,
                    cmdlogfile=cmdlogfile,
                    dockersript=case_script.\
                                format(scripts_path="/p/scripts", 
                                    case_name=caseconfig["case_name"],
                                    task=task),
                    iflog=iflog
                    )
        self.docker(cmd="exec",
                    password=password,
                    cmdlogfile=cmdlogfile,
                    dockersript=case_script.\
                                format(scripts_path="/p/scripts", 
                                    case_name=caseconfig["case_name"],
                                    task=task),
                    iflog=iflog
                    )
    
    def run(self, 
            caseconfig: Union[str, dict, pd.DataFrame, pd.Series] = "None",
            ouptname: str = "_clm.nc",
            iflog: bool = True,
            password: str = "None",
            cmdlogfile: str = "dockercmd.log"
            ) -> list:
        """
        Run workflow for a case of CLMU-App.

        Args:
            caseconfig (Union[str, dict, pd.DataFrame, pd.Series], optional): The configuration of the case to be built. The default is "None". "None" means the default configuration is used.
            ouptname (str, optional): The name of the output file. The default is "_clm.nc".
            iflog (bool, optional): If log is needed. The default is True.
            password (str, optional): The password for the sudo command. The default is "None".
            cmdlogfile (str, optional): The name of the log file. The default is "dockercmd.log".
        Returns:
            savename_list (list[str]): The list of the saved output files names.
        """
        if caseconfig == "None":
            caseconfig = self.caseconfig
        else:
            self.caseconfig = getconfig(caseconfig)
            caseconfig = self.caseconfig
        self.case_name = caseconfig["case_name"]
        # build the case
        self._case_run_("build", caseconfig, iflog)
        ## read the surface input file
        if self.fsurdat_path is None:
            self.fsurdat_path = self._read_surfin(caseconfig=caseconfig)
        #self.fsurdat_path = self._read_surfin(caseconfig=caseconfig)
        caseconfig['fsurdat'] = self.fsurdat_path
        caseconfig['local_fsurdat'] = self.fsurdat_path.replace(
            "/p/scratch/CESMDATAROOT/inputdata",
            self.input_path)
        # revise the case
        self._case_run_("revise", caseconfig, iflog, password, cmdlogfile)
        # submit the case
        self._case_run_("submit", caseconfig, iflog, password, cmdlogfile)
        # save the result
        i = 0
        savename_list = []
        #if self.container_type == "docker":
        #    op_path = os.path.join(self.output_path, 'lnd/hist')
        #else:
        #    op_path = os.path.join(self.output_path, 'lnd/hist')
        op_path = self.output_path
        for filename in os.listdir(op_path):
            if 'clm2' in filename:
                savename = op_path + '/' + caseconfig["case_name"] +f'_hist{i}_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+ouptname
                os.rename(op_path + '/' +filename, savename)
                savename_list.append(savename)
                self.save_name = savename
                i += 1
        return savename_list
    
    def modify_surf(self, 
                var: str,
                action: Union[dict, float, np.ndarray],
                numurbl: int = None,
                caseconfig: Union[str, dict, pd.DataFrame, pd.Series] = "None"
                ) -> dict:
        """
        Modify the surface input file.

        Args:
            var (str): The variable to be modified.
            action (Union[dict, float, np.ndarray]): The action to be taken. 
                - if action is a float, the action will be added to the variable.
                - if action is a dict, the key is the variable name, the value is the action.
                - if action is a np.ndarray, the variable will be replaced by the action.
            numurbl (int, optional): The number of urban land units. Defaults to None. 
                The type of urban, 0 is TBD, 1 is HD, 2 is MD.
            caseconfig (Union[str, dict, pd.DataFrame, pd.Series]): The configuration of the case to be built.
        """
        if caseconfig == "None":
            caseconfig = self.caseconfig
        else:
            self.caseconfig = getconfig(caseconfig)
            caseconfig = self.caseconfig
        
        #if self.fsurdat_path is None:
        #    self.fsurdat_path = self._read_surfin(caseconfig=caseconfig)
        self.fsurdat_path = self._read_surfin(caseconfig=caseconfig)
        caseconfig['fsurdat'] = self.fsurdat_path
        caseconfig['local_fsurdat'] = self.fsurdat_path.replace(
            "/p/scratch/CESMDATAROOT/inputdata",
            self.input_path)
        caseconfig['local_fsurdat_org'] = re.sub(r'_modified_.*\.nc', '.nc', caseconfig['local_fsurdat'])
        caseconfig['local_fsurdat'] = caseconfig['local_fsurdat_org'].replace('.nc', '_modified_{}.nc'.format(caseconfig['case_name']))
        #caseconfig['local_fsurdat_org'] = caseconfig['local_fsurdat'].replace('_modified_{}.nc'.format(caseconfig['case_name']), '.nc')
        #caseconfig['local_fsurdat'] = caseconfig['local_fsurdat_org'].replace('.nc', '_modified_{}.nc'.format(caseconfig['case_name']))
        copy_file_if_not_exists2(caseconfig['local_fsurdat_org'], 
                                caseconfig['local_fsurdat'],
                                caseconfig['case_lon'],
                                caseconfig['case_lat'],)
                
        # modify the surface input file
        self._clmu(caseconfig=caseconfig).modify_surf(var=var,
                                                    action=action,
                                                    numurbl=numurbl)
        caseconfig['fsurdat'] = re.sub(r'_modified_.*\.nc', '.nc', caseconfig['fsurdat']).\
                                replace('.nc', '_modified_{}.nc'.format(caseconfig['case_name']))
        #caseconfig['fsurdat'] = caseconfig['fsurdat'].\
        #                        replace('_modified_{}.nc'.format(caseconfig['case_name']),'').\
        #                        replace('.nc', '_modified_{}.nc'.format(caseconfig['case_name']))
        caseconfig['revise_fsurdat'] = "True"
        self.fsurdat_path = caseconfig['fsurdat']
        self.caseconfig = caseconfig
        print(f"The surface input file has been modified. The modified file is {caseconfig['fsurdat']}.")
        return caseconfig
    
    def modify_forcing(self, 
                var: str,
                action: str, 
                forcing_location: str = "forcing location",
                caseconfig: Union[str, dict, pd.DataFrame, pd.Series] = "None"
                ) -> dict:
        """
        Modify the forcing input file.

        Args:
            var (str): The variable to be modified.
            action (str): The action to be taken.
            param_location (str): The location of the parameter to be modified.
            caseconfig (Union[str, dict, pd.DataFrame, pd.Series]): The configuration of the case to be built.
        """
        if caseconfig == "None":
            caseconfig = self.caseconfig
        else:
            self.caseconfig = getconfig(caseconfig)
            caseconfig = self.caseconfig
        
        # build the case
        self._clmu(caseconfig=caseconfig).modify_forcing(var=var,
                                                    action=action,
                                                    forcing_location=forcing_location)
    def nc_view(self, ds : str = "None"):
        """
        View the netcdf file. The netcdf file should be in the DOUT_S_ROOT folder. 

        Args:
            ds (xarray.Dataset): The xarray dataset. 
        
        """
        # Read the netcdf file
        if ds == "None":
            if self.save_name is None:
                print("The netcdf file does not exist. Please use ds parameter to specify the netcdf file.")
                raise ValueError
            else:
                filepath = self.save_name
        else:
            filepath = ds
        ds = xr.open_dataset(filepath)
        ds['time'] = ds['time'].dt.round('min')
        return ds                                                                  




    



