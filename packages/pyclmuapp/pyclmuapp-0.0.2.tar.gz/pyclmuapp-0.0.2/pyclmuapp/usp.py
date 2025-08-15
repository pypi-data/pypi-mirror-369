import os
from typing import Union
import shutil
import pandas as pd
import numpy as np
import xarray as xr
from pyclmuapp.clmu import *
from pyclmuapp.getcity import *
from datetime import datetime
from pyclmuapp.container import clumapp

class usp_clmu(clumapp):

    def __init__(self,
                 pwd = os.path.join(os.getcwd(), 'workdir'),
                 input_path: str = "inputfolder",
                 output_path: str = "outputfolder",
                 log_path: str = "logfolder",
                 scripts_path: str = "scriptsfolder",
                 container_type: str = "docker") -> None:
        
        super().__init__(pwd=pwd, input_path=input_path, 
                         output_path=output_path, log_path=log_path, scripts_path=scripts_path, 
                         container_type=container_type)

        if container_type == "singularity":
            shutil.copytree(os.path.join(os.path.dirname(__file__), 'config', 'cime_config'), 
                            os.path.expanduser('~/.cime'), dirs_exist_ok=True)

        self.urban_vars_dict = {
            "morphological": ["CANYON_HWR","HT_ROOF","THICK_ROOF","THICK_WALL",
                              "WTLUNIT_ROOF","WTROAD_PERV", #"WALL_TO_PLAN_AREA_RATIO", #this value needs to revise the source code
                              "WIND_HGT_CANYON","NLEV_IMPROAD"],
            "thermal": ["TK_ROOF","TK_WALL","TK_IMPROAD",
                        "CV_ROOF","CV_WALL","CV_IMPROAD"],
            "radiative": ["EM_IMPROAD","EM_PERROAD","EM_ROOF","EM_WALL",
                          "ALB_IMPROAD_DIR","ALB_IMPROAD_DIF",
                          "ALB_PERROAD_DIR","ALB_PERROAD_DIF",
                          "ALB_ROOF_DIR","ALB_ROOF_DIF",
                          "ALB_WALL_DIR","ALB_WALL_DIF"],
            "indoor":["T_BUILDING_MIN"]}
        
        self.urban_vars_list = [value for sublist in self.urban_vars_dict.values() for value in sublist]

        self.create_folder(os.path.join(self.input_path, 'usp'))
        # get the default surface data --> UK King's College London
        self.check_surf()
        
        self.domain = None
        #os.mkdir(os.path.join(self.input_path, 'usp'))

        #if os.path.exists(os.path.join(self.input_path, 'usp')):
        #    print(f"The folder {os.path.join(self.input_path, 'usp')} already exists.")
        #else:
        #    os.makedirs(os.path.join(self.input_path, 'usp'), exist_ok=True)

    def _open_nc(self, path: str, nctype: str = "surfdata"
                 ) -> xr.Dataset:
        
        """
        Open the netCDF provided by the user or the default one.

        Args:
            path (str): The path to the netCDF file.
            nctype (str): The type of the netCDF file. The default is "surfdata".
        """

        ncfile = f"usp/{nctype}.nc"

        if path is not None:
            if os.path.exists(path):
                ds = xr.open_dataset(path)
            else:
                raise FileNotFoundError(f"The data file [{path}] is not found.")
        
        else:
            path = os.path.join(os.path.dirname(__file__), ncfile)
            ds = xr.open_dataset(path)

        return ds
    

    def check_surf(self, usr_surfdata: str = None, surfata_name: str = "surfdata.nc",
                   urban_type: int = 2) -> dict:
        """
        The function to get the surface data for the urban surface parameters.

        Args:
            usr_surfdata (str): The path to the user-defined surface data file. The default is None.
            surfata_name (str): The name of the surface data file. The default is "surfdata.nc".
            urban_type (int): The type of the urban surface. The default is 2. 0 is for TBD urban, 1 is for HD urban, and 2 is for MD urban.
        Returns:
            dict: The dictionary of the surface data for the urban surface parameters.
        """

        surfdata = self._open_nc(usr_surfdata, "surfdata")

        output = {}
        for var in self.urban_vars_list:
            
            if var in self.urban_vars_dict["morphological"]:
                output[var] = {"long_name": surfdata[var].long_name,
                                "units": surfdata[var].units,
                                "value": surfdata[var].values[urban_type,0,0],
                                "type": "morphological"}
            
            elif var in self.urban_vars_dict["thermal"]:
                output[var] = {
                    "long_name": surfdata[var].long_name,
                    "units": surfdata[var].units,
                    "value": surfdata[var].values[:,urban_type,0,0].tolist(),
                    "type": "thermal"
                }
            
            elif var in self.urban_vars_dict["radiative"]:
                if var in ["EM_IMPROAD","EM_PERROAD","EM_ROOF","EM_WALL"]:
                    output[var] = {
                        "long_name": surfdata[var].long_name,
                        "units": surfdata[var].units,
                        "value": surfdata[var].values[urban_type,0,0],
                        "type": "radiative"
                    }
                else:
                    output[var] = {
                    "long_name": surfdata[var].long_name,
                    "units": surfdata[var].units,
                    "value": surfdata[var].values[:,urban_type,0,0].tolist(),
                    "type": "radiative"
                    }
            elif var in self.urban_vars_dict["indoor"]:
                output[var] = {
                    "long_name": surfdata[var].long_name,
                    "units": surfdata[var].units,
                    "value": surfdata['T_BUILDING_MIN'].values[urban_type,0,0],
                    "type": "indoor"
                }
            else:
                raise ValueError(f"The variable {var} is not in the prefined data.")
            
            self.surfdata_dict = output

        #ncfile = f"usp/{surfata_name}"
        ncfile = os.path.join('usp', surfata_name)
        ncfile_path = os.path.join(self.input_path, ncfile)
        #self.surfdata = ncfile_path.split("/")[-1]
        self.surfdata = os.path.split(ncfile_path)[-1]
        
        if os.path.exists(ncfile_path):
            os.remove(ncfile_path)
        # Save the file
        surfdata.to_netcdf(ncfile_path)
        surfdata.close()
        del surfdata
        gc.collect()

        return output
        

    def modify_surf(self, usr_surfdata: str = None,
                        action: dict = None,
                        mode: str = "replace",
                        surfata_name: str = "surfdata.nc",
                        urban_type: int = 2) -> dict:

        """
        The function to revise the surface data for the urban surface parameters.

        Args:
            usr_surfdata (str): The path to the user-defined surface data file. The default is None.
            action (dict): The dictionary of the revised surface data for the urban surface parameters. The default is None, which means no action.
            mode (str): The mode for the revision. The default is "replace".
            surfata_name (str): The name of the revised surface data file. The default is "surfdata.nc".
            urban_type (int): The type of the urban surface. The default is 2. 0 is for TBD urban, 1 is for HD urban, and 2 is for MD urban.
        Returns:
            dict: The dictionary of the revised surface data for the urban surface parameters.
        """

        #surfdata = self._open_nc(usr_surfdata, "surfdata")

        if usr_surfdata is not None:
            surfdata = self._open_nc(usr_surfdata, "surfdata")
        else:
            surfdata = self._open_nc(os.path.join(self.input_path, 'usp', self.surfdata), "surfdata")

        def _check_action(action: dict):
            
                for i in action.keys():
                    if i not in self.urban_vars_list:
                        raise ValueError(f"The variable {i} is not in the predefined data.")
                    else:
                        if isinstance(action[i], list):
                            assert len(action[i]) == len(self.surfdata_dict[i]["value"]), f"The length of the revised value for {i} is not correct. It should be {self.surfdata_dict[i]['value']}."

        if action is not None:

            if mode == "replace":
                _check_action(action)
                for var in self.urban_vars_list:
                    
                    if var in self.urban_vars_dict["morphological"]:
                        if var in action.keys():
                            surfdata[var].values[urban_type,0,0] = np.array(action[var], dtype=np.float64)
                    
                    elif var in self.urban_vars_dict["thermal"]:
                        if var in action.keys():
                            surfdata[var].values[:,urban_type,0,0] = np.array(action[var], dtype=np.float64)
                    
                    elif var in self.urban_vars_dict["radiative"]:
                        if var in action.keys():
                            if var in ["EM_IMPROAD","EM_PERROAD","EM_ROOF","EM_WALL"]:
                                surfdata[var].values[urban_type,0,0] = np.array(action[var], dtype=np.float64)
                            else:
                                surfdata[var].values[:,urban_type,0,0] = np.array(action[var], dtype=np.float64)
                    
                    elif var in self.urban_vars_dict["indoor"]:
                        if var in action.keys():
                            surfdata['T_BUILDING_MIN'].values[urban_type,0,0] = np.array(action[var], dtype=np.float64)

            elif mode == "add":
                for var in self.urban_vars_list:
                    
                    if var in self.urban_vars_dict["morphological"]:
                        if var in action.keys():
                            surfdata[var].values[urban_type,0,0] += action[var]
                    
                    elif var in self.urban_vars_dict["thermal"]:
                        if var in action.keys():
                            surfdata[var].values[:,urban_type,0,0] += action[var]
                    
                    elif var in self.urban_vars_dict["radiative"]:
                        if var in action.keys():
                            if var in ["EM_IMPROAD","EM_PERROAD","EM_ROOF","EM_WALL"]:
                                surfdata[var].values[urban_type,0,0] += action[var]
                            else:
                                surfdata[var].values[:,urban_type,0,0] += action[var]
                    
                    elif var in self.urban_vars_dict["indoor"]:
                        if var in action.keys():
                            surfdata['T_BUILDING_MIN'].values[urban_type,0,0] += action[var]

        ncfile = f"usp/{surfata_name}"
        ncfile_path = os.path.join(self.input_path, ncfile)
        #self.surfdata = ncfile_path.split("/")[-1]
        self.surfdata = os.path.split(ncfile_path)[-1]
        if os.path.exists(ncfile_path):
            os.remove(ncfile_path)
        # Save the file
        surfdata.to_netcdf(ncfile_path)
        surfdata.close()
        del surfdata
        gc.collect()

    def check_domain(self, usr_domain: str = None, 
                          #lat : float = None, 
                          #lon: float = None,
                          domain_name: str = "domain.nc") -> None:

        """
        The function to get the domain data for the urban surface parameters.

        Args:
            usr_domain (str): The path to the user-defined domain data file. The default is None, which means using the default domain data.
            domain_name (str): The name of the domain data file. The default is "domain.nc".
            
        Returns:
            dict: The dictionary of the domain data for the urban surface parameters.
        """
        
        domian_nc = self._open_nc(usr_domain, "domain")
        surfdata = self._open_nc(os.path.join(self.input_path, 'usp', self.surfdata), "surfdata")
        lat = surfdata['LATIXY'].values[0,0]
        lon = surfdata['LONGXY'].values[0,0]
        if lon < 0:
            lon = 360 + lon
        if lat > 90 or lat < -90:
            raise ValueError("The latitude should be between -90 and 90.")
        if usr_domain is None:
            if lat is not None:
                domian_nc['yc'].values[0,0] = lat
                domian_nc['yv'].values[0,0] = np.array([lat-0.05, lat-0.05, lat+0.05, lat+0.05], dtype=np.float64)
            if lon is not None:
                domian_nc['xc'].values[0,0] = lon
                domian_nc['xv'].values[0,0] = np.array([lon-0.05, lon+0.05, lon+0.05, lon-0.05], dtype=np.float64)

            latitude_longitude_coords = [
                (domian_nc['yv'].values[0,0,0], domian_nc['xv'].values[0,0,0]),
                (domian_nc['yv'].values[0,0,1], domian_nc['xv'].values[0,0,1]),
                (domian_nc['yv'].values[0,0,2], domian_nc['xv'].values[0,0,2]),
                (domian_nc['yv'].values[0,0,3], domian_nc['xv'].values[0,0,3])
            ]

            area = calculate_polygon_area(latitude_longitude_coords)
            domian_nc['area'].values[0,0] = np.array([area], dtype=np.float64)

        ncfile = f"usp/{domain_name}"
        ncfile_path = os.path.join(self.input_path, ncfile)
        #self.domain = ncfile_path.split("/")[-1]
        self.domain = os.path.split(ncfile_path)[-1]
        if os.path.exists(ncfile_path):
            os.remove(ncfile_path)
        # Save the file
        domian_nc.to_netcdf(ncfile_path)
        domian_nc.close()
        del domian_nc
        gc.collect()

    def check_forcing(self, usr_forcing: str = None) -> None:

        """
        The function to get the forcing data for the urban surface parameters.

        Args:
            usr_forcing (str): The path to the user-defined forcing data file. The default is None.
        
        """
        #self.usr_forcing_file = usr_forcing.split("/")[-1]
        self.usr_forcing_file = os.path.split(usr_forcing)[-1]
        if os.path.exists(os.path.join(self.input_path, f'usp/{self.usr_forcing_file}')):
            #print(f"The file {self.usr_forcing_file} already exists.")
            os.remove(os.path.join(self.input_path, f'usp/{self.usr_forcing_file}'))
        
        print(
                f"Copying the file {self.usr_forcing_file} to the {os.path.join(self.input_path, 'usp')}"
            )

        shutil.copy(usr_forcing, os.path.join(self.input_path, f'usp/{self.usr_forcing_file}'))
        self.forcing_file = os.path.join(self.input_path, f'usp/{self.usr_forcing_file}')

    def modify_forcing(self, usr_forcing: str = None,
                            action: dict = None,
                            mode: str = "add",
                            forcing_name: str = "forcing.nc") -> None:
        """
        The function to revise the forcing data for the urban surface parameters.

        Args:
            usr_forcing (str): The path to the user-defined forcing data file. The default is None.
            action (dict): The dictionary of the revised forcing data for the urban surface parameters. The default is None, which means no action.
            mode (str): The mode for the revision. The default is "add".
            forcing_name (str): The name of the revised forcing data file. The default is "forcing.nc".
        
        """
        if usr_forcing is not None:
            forcing = self._open_nc(usr_forcing, "forcing")
        else:
            if self.forcing_file is not None:
                forcing = self._open_nc(self.forcing_file, "forcing")
            else:
                raise ValueError("The forcing data is not provided.")
            
        if action is not None:
            if mode == "replace":
                for var in action.keys():
                    forcing[var].values = np.array(action[var], dtype=np.float64)
            elif mode == "add":
                for var in action.keys():
                    forcing[var].values += np.array(action[var], dtype=np.float64)
        
        ncfile = f"usp/{forcing_name}"
        ncfile_path = os.path.join(self.input_path, ncfile)
        if os.path.exists(ncfile_path):
            os.remove(ncfile_path)
        forcing.to_netcdf(ncfile_path)
        #self.usr_forcing_file = ncfile_path.split("/")[-1]
        self.usr_forcing_file = os.path.split(ncfile_path)[-1]

    def run(self, 
            output_prefix: str = "_clm.nc",
            case_name: str = "usp_case", 
            RUN_STARTDATE: str = "2012-08-08",
            START_TOD: str = "00000",
            STOP_OPTION: str = "ndays", 
            STOP_N: str = "10",
            ATM_DOM: str = None, 
            SURF: str = None, 
            FORCING: str = None,
            RUN_TYPE: str = "coldstart",
            RUN_REFCASE: str = "None",
            RUN_REFDATE: str = "None",
            RUN_REFTOD: str = "00000",
            password: str = "None",
            iflog: bool = True,
            logfile: str = None,
            hist_type: str = "GRID",
            hist_nhtfrq: int = 1,
            hist_mfilt: int = 1000000000,
            urban_hac: str = "ON_WASTEHEAT",
            crun_type : str = "usp") -> list:

        """
        The function to run the CLMU-App for the urban single point.

        Args:
            output_prefix (str): The output file name. The default is "_clm.nc". if the output_prefix is `none`, the output file name will not be changed.
            case_name (str): The case name. The default is "usp_case".
            RUN_STARTDATE (str): The start date of the run. The default is "2012-08-08".
            START_TOD (str): The start time of the day. The default is "00000".
            STOP_OPTION (str): The stop option. The default is "ndays".
            STOP_N (str): The number of days to run. The default is "10".
            ATM_DOM (str): The path to the domain data file. Will use the domain data provided by the user. The default is None. 
            SURF (str): The path to the surface data file. Will use the surface data provided by the user. The default is None.
            FORCING (str): The path to the forcing data file. Will use the forcing data provided by the user. The default is None.
            RUN_TYPE (str): The type of the run. The default is "coldstart". The other option is "branch".
            RUN_REFCASE (str): The reference case. The default is "None". Need to be provided when the RUN_TYPE is "branch".
            RUN_REFDATE (str): The reference date. The default is "None". Need to be provided when the RUN_TYPE is "branch".
            RUN_REFTOD (str): The reference time of the day. The default is "00000". Need to be provided when the RUN_TYPE is "branch".
            password (str): The password for the docker. The default is "None". Need to be provided when server is needed.
            iflog (bool): The flag to log the output. The default is True.
            logfile (str): The log file name. The default is pwd+"log.log".
            urban_hac (str): The flag to turn on the urban HAC. The default is "ON_WASTEHEAT". valid_values="OFF","ON","ON_WASTEHEAT".
            crun_type (str): The type of the run. The default is "usp". 

        Returns:
            list: The list of the output files names.
        """


        #def _check_command():
        #    if self.domain is None:
        #        raise ValueError("The domain data is not provided.")
        #    if self.surfdata is None:
        #        raise ValueError("The surface data is not provided.")
        #    if self.usr_forcing_file is None:
        #        raise ValueError("The forcing data is not provided.")
        #    if self.caseconfig["case_name"] is None:
        #        raise ValueError("The case name is not provided.")
        #    if self.caseconfig["FORCING_DATE"] is None:
        #        raise ValueError("The forcing date is not provided.")
        #    if self.caseconfig["RUN_STARTDATE"] is None:
        #        raise ValueError("The run start date is not provided.")
        #    if self.caseconfig["STOP_OPTION"] is None:
        #        raise ValueError("The stop option is not provided.")

        self.case_name = case_name
        case_name = f'/p/scripts/{case_name}'
        #case_name = os.path.join('/' 'p' 'scripts', case_name)

        if SURF is not None:
            #self.surfdata = SURF
            self.check_surf(usr_surfdata=SURF)
        else:
            if self.surfdata is None:
                raise ValueError("The surface data is not provided.")
            else:
                self.surfdata = self.surfdata

        if FORCING is not None:
            #self.usr_forcing_file = FORCING
            self.check_forcing(usr_forcing=FORCING)
        else:
            if self.usr_forcing_file is None:
                raise ValueError("The forcing data is not provided.")
            else:
                self.usr_forcing_file = self.usr_forcing_file
                
        if ATM_DOM is not None:
            #self.domain = ATM_DOM
            self.check_domain(usr_domain=ATM_DOM)
        else:
            if self.domain is None:
                #print("Generating the domain data.")
                self.check_domain()
            else:
                self.domain = self.domain

        self.case_scripts(mode="usp")

        # Copy the SourceMods folder to the input folder
        self.sourcemod = os.path.join(self.input_path, 'usp', 'SourceMods')
        if os.path.exists(self.sourcemod):
            pass
            #print(f"The {self.sourcemod} already exists.")
        else:
            shutil.copytree(os.path.join(os.path.dirname(__file__), 'usp', 'SourceMods'), 
                    self.sourcemod)
#        # Copy the user_single_point.sh to the input folder
#        self.usr_single_point = os.path.join(self.input_path, 'usp/usp.sh')
#        if os.path.exists(self.usr_single_point):
#            print(f"The {self.usr_single_point} already exists.")
#        else:
#            shutil.copy(os.path.join(os.path.dirname(__file__), 'scripts/usp.sh'), 
#                    self.usr_single_point)

        # Run the CLMU-App

#        self.command="""export CASESRPITS=/p/project/clm5.0/cime/scripts && \
#export USER=root && \
#export PROJECT=/p/project && \
#export SCRATCH=/p/scratch && \
#export CESMDATAROOT=/p/scratch/CESMDATAROOT && \
#export CSMDATA=/p/scratch/CESMDATAROOT/inputdata && \
#export CASESCRIPT=/p/project/clm5.0/cime/scripts && \
#export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 && \
#export OMPI_ALLOW_RUN_AS_ROOT=1 && \
#cd $CSMDATA && \
#bash usp/usp.sh --ATMDOM_FILE {ATMDOM_FILE} \
#--SURF '{SURF}' \
#--FORCING_FILE '{FORCING_FILE}' \
#--case_name {case_name} \
#--RUN_STARTDATE '{RUN_STARTDATE}' \
#--STOP_OPTION {STOP_OPTION} --STOP_N {STOP_N} --START {START} --END {END}
#"""
        run_time_str = datetime.strptime(RUN_STARTDATE, "%Y-%m-%d")
        START = run_time_str.year
        if STOP_OPTION == "ndays":
            dateparam = {'days': int(STOP_N)}
        elif STOP_OPTION == "nmonths":
            dateparam = {'months': int(STOP_N)}
        elif STOP_OPTION == "nyears":
            dateparam = {'years': int(STOP_N)}
        elif STOP_OPTION == "nsteps":
            dateparam = {'hours': int(STOP_N)/2}
        else:
            raise ValueError("The STOP_N is not correct. please use 'ndays', 'nmonths', or 'nyears'.")

        END = (run_time_str + pd.DateOffset(**dateparam)).year
        command = self.command.format(ATMDOM_FILE=self.domain,
                                        SURF=self.surfdata,
                                        FORCING_FILE=self.usr_forcing_file,
                                        case_name=case_name,
                                        RUN_STARTDATE=RUN_STARTDATE,
                                        START_TOD=START_TOD,
                                        STOP_OPTION=STOP_OPTION,
                                        STOP_N=STOP_N,
                                        START=START,
                                        END=END,
                                        RUN_TYPE=RUN_TYPE,
                                        RUN_REFCASE=RUN_REFCASE,
                                        RUN_REFDATE=RUN_REFDATE,
                                        RUN_REFTOD=RUN_REFTOD,
                                        hist_type=hist_type,
                                        hist_nhtfrq=hist_nhtfrq,
                                        hist_mfilt=hist_mfilt,
                                        urban_hac=urban_hac)

        if logfile is None:
            logfile = os.path.join(self.pwd, 'pyclmuapprun.log')

        self.docker(cmd=crun_type, iflog=iflog, 
                    password=password, cmdlogfile=logfile,
                    dockersript=command)

        savename_list = []
        i=0
        op_path = os.path.join(self.output_path, 'lnd', 'hist')
        
        if output_prefix is not None:
        
            for filename in os.listdir(op_path):
                if ((f'{os.path.split(case_name)[-1]}.clm2' in filename) and\
                    f'{RUN_STARTDATE}' in filename):
                    #savename = op_path + '/' \
                    #                + case_name.split('/')[-1] \
                    #                + f'_clm{i}_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S") \
                    #                + output_prefix
                    savename = os.path.join(op_path, (os.path.split(case_name)[-1] 
                                            + f'_clm{i}_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
                                            + output_prefix))
                    try :
                        os.rename(op_path + '/' +filename, savename)
                        savename_list.append(savename)
                        self.save_name = savename
                    except PermissionError:
                        savename_list.append(op_path + '/' +filename)
                        self.save_name = op_path + '/' +filename
                    
                    i += 1

        return savename_list
        

    def nc_view(self, ds : str = "None") -> xr.Dataset:
        """
        View the netcdf file. The netcdf file should be in the DOUT_S_ROOT folder. 

        Args:
            ds (xarray.Dataset): The xarray dataset. 
        
        Returns:
            xarray.Dataset: The xarray dataset.
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
    
    def clean_usp(self) -> None:
        """
        Clean the usp folder.
        """
        shutil.rmtree(os.path.join(self.input_path, 'usp'))
        #os.rmdir(os.path.join(self.input_path, 'usp'))