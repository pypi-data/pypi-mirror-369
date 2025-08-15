# Junjie Yu, 2024-02-06, Mancheser UK
#------------------------------------------------------------------------------
# This script is used to run CESM2 via python

import os
import math
import subprocess
import shutil
import json
import xarray as xr
import pandas as pd
import numpy as np
from typing import Union, List, Dict
import time
import gc

# Set the path of the CESM2
class cesm_run():

    """
    This class is used to create CESM2/CTSM case. Run the CESM2/CTSM case should be done by running the generated shell script
         using terminal or python subprocess or container (docker or singularity with CESM2/CTSM installed)

    Args:
        CASESCRIPT_local (str): The path of the case script in the local machine.
        CASEROOT_local (str): The path of the case root in the local machine.
        DOUT_S_ROOT (str): The path of the output root in the local machine.
        caseconfig (Union[str, dict, pd.DataFrame, pd.Series]): The configuration of the case to be built.
         

    Attributes:
        CASESCRIPT (str): The path of the case script.
        CASEROOT (str): The path of the case root.
        DOUT_S_ROOT (str): The path of the output root.
        case_lat (float): The latitude of the case.
        case_lon (float): The longitude of the case.
        case_name (str): The name of the case.
        json_file_path (str): The path of the JSON file.
        config (dict): The configuration data.
    """

    def __init__(self, 
                #CASESCRIPT, 
                CASESCRIPT_local, 
                CASEROOT_local, 
                DOUT_S_ROOT, 
                caseconfig: Union[str, dict, pd.DataFrame, pd.Series]
                ):
        """
        Returns:
            An instance of the cesm_run class.
        """
        #self.CASESCRIPT = CASESCRIPT
        self.CASESCRIPT_local = CASESCRIPT_local
        #self.CIMEROOT = os.path.join(SRCROOT, 'cime')
        self.CASEROOT_local = CASEROOT_local
        self.DOUT_S_ROOT = DOUT_S_ROOT
        self.case_lat = 0.9
        self.case_lon = 1.25
        self.case_name = 'test'

        if isinstance(caseconfig, str):
            self.json_file_path = caseconfig
            with open(caseconfig, 'r') as f:
                self.config = json.load(f)
        if isinstance(caseconfig, dict):
            self.config = caseconfig
            self.json_file_path = None

        if isinstance(caseconfig, pd.DataFrame) or isinstance(caseconfig, pd.Series):
            self.config = caseconfig.to_dict(orient='records')[0]
            self.json_file_path = None

        self.case_lat = self.config['case_lat']
        self.case_lon = self.config['case_lon']
        self.case_name = self.config['case_name']

        if 'fsurdat' in self.config.keys():
            self.fsurdat = self.config['fsurdat']
        if 'local_fsurdat' in self.config.keys():
            self.local_fsurdat = self.config['local_fsurdat']

    # Read the config file
    def read_json_config(self) -> dict:
        """
        Read the JSON config file.

        Returns:
            config (dict): The configuration data.

        """
        with open(self.json_file_path, 'r') as f:
            config = json.load(f)

        return config

    def modify_case_config(self, scriptpaht) -> str:
        
        """
        Modify the case config file.

        Args:
            scriptpath (str): The path of the script file.

        Returns:
            script (str): The modified script file.
        """

        # read the shell script
        with open(scriptpaht, 'r') as f:
            script = f.read()
        for i in self.config.keys():
            input_sc = "${" + i + "}"
            # replace the value
            script = script.replace(input_sc, self.config[i])

        return script


    def create_case(self, scriptpath) -> str:

        """
        Create the case scripts for single point modeling.

        Args:
            filepath (str): File path of the config file.

        Returns:
            script (str): The modified script file.
        """

        script = self.modify_case_config(scriptpath)

        return script
        
    def reset_case(self, password=None) -> subprocess.CompletedProcess:

        """
        Reset the case. (delete the case folders and files)

        Args:
            password (str, optional): The password of the server. Defaults to None.
        
        Returns:
            subprocess.CompletedProcess: The result of the command.
        """
        # Remove the case
        if password == None:
            script = "rm -rf " + self.CASESCRIPT_local + "/" + self.config['case_name']
            result = subprocess.run(script, text=True, check=True, shell=True)
            script = "rm -rf " + self.CASEROOT_local + "/" + self.config['case_name']
            result = subprocess.run(script, text=True, check=True, shell=True)

        else:
            script = "sudo -S rm -rf " + self.CASESCRIPT_local + "/" + self.config['case_name']
            result = subprocess.run(script, input=password, text=True, check=True, shell=True)
            script = "sudo -S rm -rf " + self.CASEROOT_local + "/" + self.config['case_name']
            result = subprocess.run(script, input=password, text=True, check=True, shell=True)

        return result


    def nc_view(self, ds : str = "None") -> xr.Dataset:

        """
        View the netcdf file. 

        Args:
            xarray.Dataset: The xarray dataset. 
            ds (str, optional): The path of the netcdf file. Defaults to "None".
        
        Returns:
            xarray.Dataset: The xarray dataset.
        """

        # Read the netcdf file
        if ds == "None":
            filepath = self.DOUT_S_ROOT + '/lnd/hist/' + self.config['case_name'] + '.clm2.h0.' \
                        + self.config['case_start_year'] + '-' + self.config['filemonth'] + '.nc'
        else:
            filepath = ds
        ds = xr.open_dataset(filepath)

        return ds
    
    def modify_surf(self, var, action, numurbl=None) -> str:
            
        """
        Modify the surface data file.

        Args:
            var (str): The variable to be modified.
            action (float, np.ndarray, dict): The action to be taken. 
                - if action is a dict, the key is the variable name, the value is the action.
                - if action is a float, the action will be added to the variable.
                - if action is a np.ndarray, the variable will be replaced by the action.
            numurbl (int, optional): The number of urban land units. Defaults to None. 
                None means the action will be implemented to all the urban land units.
                numurbl 0 --> TBD urban, numurbl 1 --> HD urban, numurbl 2 --> MD urban

        Returns:
            str: The modified surface data file path.
        """

        # Open the file
        ds = xr.open_dataset(self.config['local_fsurdat'])
        # Modify the file
        #if float(self.config['case_lon']) < 0:
        #    case_lon = float(copy.deepcopy(self.config['case_lon'])) + 360
        #else:
        #    case_lon = float(copy.deepcopy(self.config['case_lon']))
        #llat = int((float(copy.deepcopy(self.config['case_lat']))+90)/(180/192))
        #llon = int(case_lon/1.25)
        # * Set the location of the parameter, only one location is modified
        # numurbl is the number of urban land units, here is 1, indicating HD urban
        #param_location = dict(lsmlat=llat, lsmlon=llon, numurbl=1)
        #param_location = dict(lsmlat=0, lsmlon=0, numurbl=1)
        if numurbl is None:
            param_location = dict(lsmlat=0, lsmlon=0)
        
        else:
            param_location = dict(lsmlat=0, lsmlon=0, numurbl=numurbl)


        if isinstance(action, float):
            ds[var].loc[param_location] = ds[var].loc[param_location].values + action
            #ds[var].loc[:] = ds[var].loc[:].values + action
        if isinstance(action, np.ndarray):
            ds[var].loc[param_location] = action
            #ds[var].loc[:] = action

        if isinstance(action, dict):
            #print('action is a dict')
            for i in action.keys():
                if isinstance(action[i], float) or isinstance(action[i], np.float64) or isinstance(action[i], np.float32):
                    #print('action is a float')
                    ds[i].loc[param_location] = ds[i].loc[param_location].values + action[i]
                    #ds[i].loc[:] = ds[i].values + action[i]
                    #print(param_location)
                    #print(ds[i].loc[param_location].values)
                if isinstance(action[i], np.ndarray):
                    #print('action is a ndarray')
                    ds[i].loc[param_location] = action[i]
                    #ds[i].loc[:] = action[i]
                    

        if os.path.exists(self.config['local_fsurdat']):
            # Remove the file if exists
            # this will cause the error if the file does is exist 
            # and we still want to modify the file
            # will make it can not be modified any more
            # !!!!!!! don't resvie this
            os.remove(self.config['local_fsurdat'])
        # Save the file
        ds.to_netcdf(self.config['local_fsurdat'])

        ds.close()
        del ds
        gc.collect()


    def modify_forcing(self, var, action, forcing_location) -> None:


        """
        Modify the forcing file.

        Args:
            var (str): The variable to be modified.
            action (float, np.ndarray, dict): The action to be taken.
            forcing_location (str): The location of the forcing file.
                - if action is a dict, the key is the variable name, the value is the action.
                - if action is a float, the action will be added to the variable.
                - if action is a np.ndarray, the variable will be replaced by the action.
        Returns:
            None
        """

        ds = xr.open_dataset(forcing_location)
        if isinstance(action, float) or isinstance(action, int) or isinstance(action, np.float64) or isinstance(action, np.float32):
            ds[var].loc[:] = ds[var].loc[:].values + action
        if isinstance(action, np.ndarray):
            ds[var].loc[:] = action
        if isinstance(action, dict):
            for i in action.keys():
                if isinstance(action[i], int) or isinstance(action[i], float) or isinstance(action[i], np.float64) or isinstance(action[i], np.float32):
                    ds[i].loc[:] = ds[i].loc[:].values + action[i]
                if isinstance(action[i], np.ndarray):
                    ds[i].loc[:] = action[i]

        if os.path.exists(forcing_location):
            # Remove the file if exists
            # this will cause the error if the file does is exist 
            # and we still want to modify the file
            # will make it can not be modified any more
            # !!!!!!! don't resvie this
            os.remove(forcing_location)
        # Save the file
        ds.to_netcdf(forcing_location)

    def recover_forcing(self, forcing_location, backup_location) -> None:

        """
        Recover the forcing file.

        Args:
            forcing_location (str): The location of the forcing file.
            backup_location (str): The location of the backup file.
        
        Returns:
            None
        """

        # Recover the forcing file
        shutil.copy2(backup_location, forcing_location)


def run_command(command, password="None", logname="None", iflog=True) -> None:
    """
    Run the command. There are two ways to run the command, with or without password.
    The loges will be saved in the log_ppo.txt file.

    Args:
        command (str): The command to be run.
        password (str, optional): The password of the server.
        logname (str, optional): The name of the log file. Defaults to "cmdlog.txt".
        iflog (bool, optional): If log is needed. Defaults to True.

    Returns:
        None
    """
    
    try:
        if password == "None":
            
            result = subprocess.run(command, text=True, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:    
            result = subprocess.run(command, input=password, text=True, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if iflog:
            if logname == "None":
                #print(now_time())
                if result.stdout is not None:
                    print(result.stdout)
            else:
                with open(logname, 'w') as f:
                    f.write(now_time())
                    if result.stdout is not None:
                        f.write(result.stdout)

    except subprocess.CalledProcessError as e:
        if iflog:
            if logname == "None":
                #print(now_time())
                if e.stdout is not None:
                    print(e.stdout)
                    print(e.stderr)
            else:
                with open(logname, 'w') as f:
                    f.write(now_time())
                    if e.stdout is not None:
                        f.write(e.stdout)
                        f.write(e.stderr)       


def getconfig(caseconfig: Union[str, dict, pd.DataFrame, pd.Series] = "None") -> dict:

    """
    Read the configuration of the case to be built.

    Args:
        caseconfig (Union[str, dict, pd.DataFrame, pd.Series]): The configuration of the case to be built.
    
    Returns:
        dict: The configuration data.
    """

    if isinstance(caseconfig, str):
        with open(caseconfig, 'r') as f:
            config = json.load(f)
    if isinstance(caseconfig, dict):
        config = caseconfig

    if isinstance(caseconfig, pd.DataFrame) or isinstance(caseconfig, pd.Series):
        config = caseconfig.to_dict(orient='records')[0]

    return config


def now_time():
    """
    Get the current time
    """
    return "Current time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n"

def copy_file_if_not_exists(source_path, destination_path):
    # check if the destination file exists
    if not os.path.exists(destination_path):
        # copy the file
        shutil.copy2(source_path, destination_path)
        print(f"The {source_path} has been copied to {destination_path}")

def copy_file_if_not_exists2(source_path, destination_path, lon, lat, res="1.25*0.9") -> None:

    """
    
    Copy the file if the destination file does not exist.
    
    Args:
        source_path (str): The source file path.
        destination_path (str): The destination file path.
        lon (str): The longitude of the point.
        lat (str): The latitude of the point.
        res (str): The resolution of the file. Defaults to "1.25*0.9".
    
    """


    # check if the destination file exists
    if not os.path.exists(destination_path):
        # copy the file

        ds = xr.open_dataset(source_path)

        if res == "1.25*0.9":
            if float(lon) < 0:
                lon = float(lon) + 360
            llat = int((float(lat)+90)/(180/192))
            llon = int(float(lon)/1.25)
            #paramdict = dict(lsmlat=llat, lsmlon=llon, numurbl=1)
            ds.sel(lsmlat=slice(llat, llat+2), lsmlon=slice(llon, llon+2)).to_netcdf(destination_path)

        elif res == "0.5*0.5":
            if float(lon) < 0:
                lon = float(lon) + 360
            llat = int((float(lat)+90)/(180/360))
            llon = int(float(lon)/0.5)
            #paramdict = dict(lat=llat, lon=llon)
            ds.sel(lat=slice(llat, llat+2), lon=slice(llon, llon+2)).to_netcdf(destination_path)

        else:
            print("The resolution is not supported.")
            print("Please input the lat and lon directly as lsmlat and lsmlon.")
            llat = int(lat)
            llon = int(lon)

        
        copy_file_if_not_exists(source_path, destination_path)

# This function is not used in the current version
# which is used to get the forcing data from the era5 land/single dataset
# we moved to the module era5_forcing.py
#def get_clmuapp_frocing(era5: Union[xr.Dataset, str],
#                        lat : float,
#                        lon : float,
#                        outputname : str,
#                        zbot: Union[float, int] = 2) -> xr.Dataset:
#    """
#    Args:
#        era5 (_type_): the era5 dataset, or the path of the era5 dataset
#        lat (_type_): latitude of interest point
#        lon (_type_): longitude of interest point
#        outputname (_type_): the output file name
#
#    Returns:
#        _type_: the forcing dataset
#    """
#        
#    if isinstance(era5, str):
#        if os.path.isfile(era5):
#            forcing = xr.open_dataset(era5)
#            
#        elif os.path.isdir(era5):
#            for root, dirs, files in os.walk(era5):
#                for file in files:
#                    forcing_ls = []
#                    if file.endswith(".nc"):
#                        _forcing = xr.open_dataset(os.path.join(root, file))
#                        forcing_ls.append(_forcing)
#            forcing = xr.concat(forcing_ls, dim='time').sortby('time')
#    
#    elif isinstance(era5, xr.Dataset):
#        forcing = era5
#    else:
#        raise ValueError("The era5 should be a xarray dataset or a file path.")
#    
#    if forcing.latitude.values.shape:
#        
#        if forcing.longitude.values.shape:
#            forcing = forcing.sel(latitude=lat,longitude=lon,method='nearest')
#        else:
#            forcing = forcing.sel(latitude=lat,method='nearest')
#    
#    elif forcing.longitude.values.shape:
#        forcing = forcing.sel(longitude=lon,method='nearest')
#    
#    
#    Prectmms = forcing['tp'] * 1000 / 3600
#    Prectmms = Prectmms.where(Prectmms > 0, 1e-16)
#    #forcing['Prectmms'] = forcing['tp'] * 1000 / 3600
#    forcing['Prectmms'] = Prectmms
#    forcing['Prectmms'] = forcing['Prectmms'].assign_attrs(units='mm/s')
#    forcing['Prectmms'] = forcing['Prectmms'].assign_attrs(long_name='Precipitation rate')
#    forcing['Prectmms'] = forcing['Prectmms'].assign_attrs(_FillValue=1.e36)
#
#    #forcing['SWdown'] = forcing['ssrd'] / 3600
#    SWdown = forcing['ssrd'] / 3600
#    SWdown = SWdown.where(SWdown > 0, 1e-16)
#    forcing['SWdown'] = SWdown
#    forcing['SWdown'] = forcing['SWdown'].assign_attrs(units='W/m2')
#    forcing['SWdown'] = forcing['SWdown'].assign_attrs(long_name='Downward shortwave radiation')
#    forcing['SWdown'] = forcing['SWdown'].assign_attrs(_FillValue=1.e36)
#
#    forcing['LWdown'] = forcing['strd'] / 3600 
#    forcing['LWdown'] = forcing['LWdown'].assign_attrs(units='W/m2')
#    forcing['LWdown'] = forcing['LWdown'].assign_attrs(long_name='Downward longwave radiation')
#
#    forcing['Wind'] = (forcing['u10']**2 + forcing['v10']**2)**0.5
#    # ref: https://doi.org/10.5194/essd-14-5157-2022
#    #forcing['Wind'] = forcing['Wind'] * (np.log(2 / forcing['fsr']) / np.log(10 / forcing['fsr']))
#    #forcing['Wind'] = forcing['Wind'] * (xr.ufuncs.log(2 / forcing['fsr']) / xr.ufuncs.log(10 / forcing['fsr']))
#    forcing['Wind'] = forcing['Wind'].assign_attrs(units='m/s')
#    forcing['Wind'] = forcing['Wind'].assign_attrs(long_name='Wind speed')
#    forcing['Wind'] = forcing['Wind'].assign_attrs(_FillValue=1.e36)
#
#    forcing['PSurf'] = forcing['sp'] /1.0
#    forcing['PSurf'] = forcing['PSurf'].assign_attrs(units='Pa')
#    forcing['PSurf'] = forcing['PSurf'].assign_attrs(long_name='Surface pressure')
#
#    forcing['Zbot'] = forcing['sp'] /1.0
#    forcing['Zbot'].values = np.ones(forcing['Zbot'].shape) * zbot
#    forcing['Zbot'] = forcing['Zbot'].assign_attrs(long_name='Bottom level height')
#    forcing['Zbot'] = forcing['Zbot'].assign_attrs(units='m')
#
#    forcing['Tair'] = forcing['t2m'] / 1.0
#    forcing['Tair'] = forcing['Tair'].assign_attrs(units='K')
#    forcing['Tair'] = forcing['Tair'].assign_attrs(long_name='Air temperature')
#
#    # ref1: https://github.com/ESCOMP/CTSM/blob/75b34d2d8770461e3e28cee973a39f1737de091d/doc/source/tech_note/Land-Only_Mode/CLM50_Tech_Note_Land-Only_Mode.rst#L113
#    # ref2: https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
#    # ref3: https://github.com/ESCOMP/CTSM/blob/75b34d2d8770461e3e28cee973a39f1737de091d/src/biogeophys/QSatMod.F90
#    # Reference:  Polynomial approximations from:
#    #             Piotr J. Flatau, et al.,1992:  Polynomial fits to saturation
#    #             vapor pressure.  Journal of Applied Meteorology, 31, 1507-1513.
#
#    forcing['d2m'] = forcing['d2m'] - 273.15
#    a0 =  6.11213476
#    a1 =  0.444007856
#    a2 =  0.143064234e-01
#    a3 =  0.264461437e-03
#    a4 =  0.305903558e-05
#    a5 =  0.196237241e-07
#    a6 =  0.892344772e-10
#    a7 = -0.373208410e-12
#    a8 =  0.209339997e-15
#    forcing['es_water'] = a0 + forcing['d2m']*(a1 + forcing['d2m']*(a2 + forcing['d2m']*(a3 + forcing['d2m']*(a4 
#            + forcing['d2m']*(a5 + forcing['d2m']*(a6 + forcing['d2m']*(a7 + forcing['d2m']*a8)))))))
#    forcing['es_water'] = forcing['es_water'] * 100
#    c0 =  6.11123516
#    c1 =  0.503109514
#    c2 =  0.188369801e-01
#    c3 =  0.420547422e-03
#    c4 =  0.614396778e-05
#    c5 =  0.602780717e-07
#    c6 =  0.387940929e-09
#    c7 =  0.149436277e-11
#    c8 =  0.262655803e-14
#    forcing['es_ice'] = c0 + forcing['d2m']*(c1 + forcing['d2m']*(c2 + forcing['d2m']*(c3 + forcing['d2m']*(c4 
#            + forcing['d2m']*(c5 + forcing['d2m']*(c6 + forcing['d2m']*(c7 + forcing['d2m']*c8)))))))
#    forcing['es_ice'] = forcing['es_ice'] * 100
#    forcing['es'] = xr.where(forcing['d2m'] >= 0, forcing['es_water'],forcing['es_ice'])
#    forcing['Qair'] = 0.622 * forcing['es'] / (forcing['PSurf'] - (1 - 0.622) * forcing['es'])
#    forcing['Qair'] = forcing['Qair'].assign_attrs(units='kg/kg')
#
#    del forcing['fsr']
#    del forcing['es_water']
#    del forcing['es_ice']
#    del forcing['es']
#    del forcing['ssrd']
#    del forcing['strd']
#    del forcing['tp']
#    del forcing['u10']
#    del forcing['v10']
#    del forcing['sp']
#    del forcing['t2m']
#    del forcing['d2m']
#    del forcing['longitude']
#    del forcing['latitude']
#    
#    forcing['x'] = 1
#    forcing['y'] = 1
#    forcing = forcing.assign_coords(x=1,y=1)
#    for var in forcing.data_vars:
#        forcing[var] = forcing[var].expand_dims('x',axis=1).expand_dims('y',axis=1)
#
#    if os.path.exists(outputname):
#        os.remove(outputname)
#    forcing.to_netcdf(outputname)
#    print(f"The forcing file has been saved as {outputname}")
#    return forcing



def get_urban_params(urban_ds: Union[xr.Dataset, str],
                     soil_ds: Union[xr.Dataset, str],
                     lat: float, 
                     lon: float,
                     template: Union[xr.Dataset, str] = os.path.join(os.path.dirname(__file__), "usp", "surfdata.nc"),
                     PTC_URBAN: list = [0,0,100],
                     outputname: str = "surfdata.nc"
                     ) -> xr.Dataset:
    
    """
    Get the urban parameters.
    
    Args:
        urban_ds (_type_): the urban dataset
        soil_ds (_type_): the soil dataset
        template (_type_): the template dataset
        lat (_type_): latitude of interest point
        lon (_type_): longitude of interest point
        PTC_URBAN (list, optional): The percentage of urban. Defaults to [0,0,100].
            0. TBD urban, 1. HD urban, 2. MD urban
        outputname (_type_, optional): the output file name. Defaults to "surfdata.nc".
        
    Returns:
        _type_: the modified template dataset
    """
    
    if lon > 180:
        lon = lon - 360
    
    if isinstance(urban_ds, str):
        urban_ds = xr.open_dataset(urban_ds)
    if isinstance(template, str):
        template = xr.open_dataset(template)

    urban = urban_ds.assign_coords(lat=urban_ds.LAT, lon=urban_ds.LON).sel(lat=lat, lon=lon, method='nearest')
    urban =  urban.sel(region=(urban.REGION_ID.values-1)) # to make region_id start from 0
    urban['ALB_ROOF_DIF'] = urban['ALB_ROOF'].sel(numsolar=0)
    urban['ALB_ROOF_DIR'] = urban['ALB_ROOF'].sel(numsolar=1)
    urban['ALB_WALL_DIF'] = urban['ALB_WALL'].sel(numsolar=0)
    urban['ALB_WALL_DIR'] = urban['ALB_WALL'].sel(numsolar=1)
    urban['ALB_IMPROAD_DIF'] = urban['ALB_IMPROAD'].sel(numsolar=0)
    urban['ALB_IMPROAD_DIR'] = urban['ALB_IMPROAD'].sel(numsolar=1)
    urban['ALB_PERROAD_DIF'] = urban['ALB_PERROAD'].sel(numsolar=0)
    urban['ALB_PERROAD_DIR'] = urban['ALB_PERROAD'].sel(numsolar=1)
    
    # Set the urban parameters
    for v1 in urban.variables:
        for v2 in template.variables:
            if v1 == v2:
                #print(f"Setting {v1} to {v2}")
                #print(template[v2].loc[dict(lsmlat=float(template['lsmlat'].values), lsmlon=float(template['lsmlon'].values))].shape)
                #print(urban[v1].shape)
                template[v2].loc[dict(lsmlat=float(template['lsmlat'].values), lsmlon=float(template['lsmlon'].values))] = urban[v1].values
                if v2 == 'LONGXY':
                    if template[v2].loc[dict(lsmlat=float(template['lsmlat'].values), lsmlon=float(template['lsmlon'].values))] < 0:
                        template[v2].loc[dict(lsmlat=float(template['lsmlat'].values), lsmlon=float(template['lsmlon'].values))] = template[v2].loc[dict(lsmlat=float(template['lsmlat'].values), lsmlon=float(template['lsmlon'].values))].values + 360
                template[v2] = template[v2].fillna(0)
    template['URBAN_REGION_ID'].loc[dict(lsmlat=float(template['lsmlat'].values), lsmlon=float(template['lsmlon'].values))] = urban['REGION_ID'].values
    template['PCT_URBAN'].values[:, 0, 0] = np.array(PTC_URBAN)
    
    sand, clay = get_soil_params(soil_ds, lat, lon)
    
    template['PCT_SAND'].values[:, 0, 0] = sand
    template['PCT_CLAY'].values[:, 0, 0] = clay
    
    template.to_netcdf(outputname)
                
    return  template


def get_soil_params(ds: Union [xr.Dataset, xr.DataArray, str],
                    lat: float = 51.508965,
                    lon: float = -0.118092) -> tuple:
    
    """
    Get the soil parameters.
    
    Args:
        ds (_type_): the soil dataset
        lat (_type_): latitude of interest point
        lon (_type_): longitude of interest point
    
    Returns:
        tuple: sand and clay content from the soil dataset
    """
    
    if isinstance(ds, str):
        ds = xr.open_dataset(ds)
    
    ds = ds.assign_coords(lat=ds.LAT, lon=ds.LON)

    lat_soil = lat
    lon_soil = lon

    search_range = 180/21600  # 0.008333333333333333

    while True:
        found_point = False  # flag to indicate if a suitable point is found
        for lat_offset in [0, 1 , -1]:
            for lon_offset in [0, 1, -1]:
                # calculate new latitude and longitude
                new_lat = lat_soil + lat_offset * search_range
                new_lon = lon_soil + lon_offset * search_range
                
                # select the nearest point
                dd = ds.sel(lat=new_lat, lon=new_lon, method='nearest')
                sand = dd['PCT_SAND'].sel(max_value_mapunit=int(dd['MAPUNITS'].values)).values
                clay = dd['PCT_CLAY'].sel(max_value_mapunit=int(dd['MAPUNITS'].values)).values
                
                # check if the point is suitable
                if not (np.all(sand == 0) or np.all(clay == 0)):
                    found_point = True
                    lat_soil = new_lat
                    lon_soil = new_lon
                    break  #  break the inner loop
            # break the outer loop
            if found_point:
                print(f'Found suitable point at lat: {lat_soil}, lon: {lon_soil}')
                break  # break the outer loop
        # break the while loop
        if found_point:
            print(f'Found suitable point at lat: {lat_soil}, lon: {lon_soil}')
            break  # break the while loop
        else:
            print('No suitable point found in the search range, expanding search range.')
            search_range += 180/21600  # expand the search range by 0.008333333333333333

    return sand, clay


def get_forcing(start_year, end_year, 
                start_month, end_month,
                lat, lon, zbot,
                source='cds'
                ):
    
    """
    get the forcing data from the era5 dataset
    
    Args:
        start_year (_type_): the start year
        end_year (_type_): the end year
        start_month (_type_): the start month
        end_month (_type_): the end month
        lat (_type_): latitude of interest point
        lon (_type_): longitude of interest point
        zbot (_type_): the bottom level height
        source (_type_): the source of the data, cds or arco-era5
    Returns:
        _type_: the forcing dataset
    """
    
    if source == "cds":
        from pyclmuapp.era5_forcing import era5_to_forcing, era5_download
        import xarray as xr
        era5_list = []
        # from 2002 to 2014
        years = range(start_year, end_year+1)
        # download data from January to December
        months = range(start_month, end_month+1)
        if not os.path.exists('./era5_data'):
            os.makedirs('./era5_data', exist_ok=True)
            os.makedirs('./era5_data/era5_single', exist_ok=True)
        outputfile='era5_data/era5_forcing_{lat}_{lon}_{zbot}_{year}_{month}.nc'
        for year in years:
            
            if start_year == end_year:
                months = range(start_month, end_month+1)
            elif year == end_year:
                months = range(1, end_month+1)
            elif year == start_year:
                months = range(start_month, 13)
            else:
                months = range(1, 13)
                
            for month in months:
                single = era5_download(year=year, month=month,
                                            lat=lat, lon=lon, outputfolder='./era5_data/era5_single')
                # Convert ERA5 data to CLM forcing
                forcing = era5_to_forcing(single=single, 
                                        lat=lat, lon=lon, zbot=zbot,)
                era5_list.append(forcing)
                
            #for month in months:
            #    single = era5_download(year=year, month=month,
            #                                lat=lat, lon=lon, outputfolder='./era5_data')
            #    # Convert ERA5 data to CLM forcing
            #    forcing = era5_to_forcing(single=single, 
            #                            lat=lat, lon=lon, zbot=zbot,
            #                            outputfile=outputfile.format(lat=lat, lon=lon, 
            #                                                        zbot=zbot, year=year, 
            #                                                        month=str(month).zfill(2)))
            #    ds = xr.open_dataset(outputfile.format(lat=lat, lon=lon, 
            #                                        zbot=zbot, year=year, 
            #                                        month=str(month).zfill(2)))
            #    era5_list.append(ds)
        era5 = xr.concat(era5_list, dim='time').sortby('time')
        outfile = f'era5_data/era5_forcing_{lat}_{lon}_{zbot}_{start_year}_{start_month}_{end_year}_{end_month}.nc'
        if os.path.exists(outfile):
            os.remove(outfile)
        era5.to_netcdf(outfile)
        result = os.path.join(os.getcwd(), outfile)

    if source == "arco-era5":
        if not os.path.exists('./era5_data'):
            os.makedirs('./era5_data', exist_ok=True)
        outfile = f'era5_data/arco_era5_forcing_{lat}_{lon}_{zbot}_{start_year}_{start_month}_{end_year}_{end_month}.nc'
        from pyclmuapp.era5_forcing import arco_era5_to_forcing
        if os.path.exists(outfile):
            print(f"The forcing file {outfile} already exists.")
        else:
            arco_era5_to_forcing(lat=lat, lon=lon, zbot=zbot, 
                                start_year=start_year, end_year=end_year, 
                                start_month=start_month, end_month=end_month, outputfile=outfile)
        result = os.path.join(os.getcwd(), outfile)
        
    if source == "era5-land-ts":
        from pyclmuapp.era_forcing import workflow_era5s_to_forcing
        if not os.path.exists('./era5_data'):
            os.makedirs('./era5_data', exist_ok=True)
        outfile = f'era5_data/era5_land_ts_forcing_{lat}_{lon}_{zbot}_{start_year}_{start_month}_{end_year}_{end_month}.nc'
        if os.path.exists(outfile):
            print(f"The forcing file {outfile} already exists.")
        else:
            start_date = f"{start_year}-{str(start_month).zfill(2)}-01"
            if end_month == 12:
                end_date = f"{end_year+1}-01-01"
            else:
                end_date = f"{end_year}-{str(end_month+1).zfill(2)}-01"
            outputfile = f'era5_data/era5_land_ts_forcing_{lat}_{lon}_{zbot}_{start_year}_{start_month}_{end_year}_{end_month}.nc'
            workflow_era5s_to_forcing(lat, lon, start_date, end_date, zbot=zbot, outputfile=outputfile)
        result = os.path.join(os.getcwd(), outfile)

    return result