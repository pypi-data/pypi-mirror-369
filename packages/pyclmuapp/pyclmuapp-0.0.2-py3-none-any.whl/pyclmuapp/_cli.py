# encoding: utf-8
# Author: Junjie Yu, 2024-5-18
# Description: CLI for pyclmuapp

# pyclmuapp/cli.py

import argparse
from pyclmuapp import usp_clmu
from pyclmuapp.clmu import get_forcing
import numpy as np
import shutil
import os
from . import __version__

class CaseInsensitiveArgumentParser(argparse.ArgumentParser):
    """
    define a case-insensitive argument parser
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_option_tuples(self, option_string):
        """
        get the option tuples
        """
        option_string = option_string.lower()  # make option_string case-insensitive
        return super()._get_option_tuples(option_string)

def get_pypars(gr_l: dict = None):
    #parser = argparse.ArgumentParser(description='A sample command line tool for pyclmuapp.',
    #                                prog='pyclmuapp',
    #                                prefix_chars='-',
    #                                epilog='For any qusetion, contact yjj1997@live.cn',)
    parser = CaseInsensitiveArgumentParser(description='pyclmuapp command line tool.',
                                            prog='pyclmuapp',
                                            prefix_chars='-',
                                            epilog='For any question, contact yjj1997@live.cn',)

    parser.add_argument('--version', '-v', action='version', version=f'%(prog)s {__version__}. Author: Junjie Yu. Email: yjj1997@live.cn')

    parser.add_argument('--init', 
                        type=bool,
                        help='Init pyclmuapp, default is False',
                        default=False)

    # add arguments for container part
    parser.add_argument('--pwd', 
                        type=str, 
                        help='Param for usp and script. Current working directory, default is pwd, can be none. If is not none, the the input_path, output_path, log_path, scripts_path will be used in pwd or be created. If none, the input_path, output_path, log_path, scripts_path should be provided.', 
                        default=os.getcwd())

    parser.add_argument('--container_type',
                        type=str, 
                        help='Param for usp and script. Container type, default is docker, can be singularity', 
                        default='docker')

    parser.add_argument('--input_path',
                        type=str, 
                        help='Param for usp and script. CTSM input path, default is None. The path will be binded to "inputdata" in container',
                        default=None)

    parser.add_argument('--output_path', 
                        type=str,
                        help='Param for usp and script. CTSM output path, default is None. The path will be binded to "Archive" in container',
                        default=None)

    parser.add_argument('--log_path', 
                        type=str,
                        help='Param for usp and script. CTSM log path, default is None. The path will be binded to "CaseOutputs" in container',
                        default=None)

    parser.add_argument('--scripts_path', 
                        type=str,
                        help='Param for usp and script. CTSM scripts path, default is None. The path will be binded to "/p/scripts" in container',
                        default=None)

    # add arguments for pyclmuapp part
    parser.add_argument('--pyclmuapp_mode', 
                        type=str,
                        help='pyclmuapp mode, default is usp, can be script, pts, get_forcing, get_surfdata',
                        default='usp')

    parser.add_argument('--has_container', 
                        type=bool,
                        help='Param for usp and script. Has container, default is True',
                        default=True)

    #--------------------- add arguments for usp_clmu part---------------------
    parser.add_argument('--usr_domain', 
                        type=str,
                        help='Param for usp. User domain file, default is None',
                        default=None)

    parser.add_argument('--usr_forcing', 
                        type=str,
                        help='Param for usp. User forcing file, default is None',
                        default=None)

    parser.add_argument('--usr_surfdata', 
                        type=str,
                        help='Param for usp. User surface data file, default is None',
                        default=None)

    parser.add_argument('--output_prefix', 
                        type=str,
                        help='Param for usp. Output file name prefix, default is _clm.nc, is used to generate the output file of pyclmuapp',
                        default="_clm.nc")

    parser.add_argument('--case_name', 
                        type=str,
                        help='Param for usp. Case name, default is usp_case',
                        default="usp_case")

    parser.add_argument('--run_startdate',
                        type=str,
                        help='Param for usp. Start date, default is None')
    
    parser.add_argument('--start_tod',
                        type=str,
                        help='Param for usp. Start time of the day, default is 00000',
                        default='00000')

    parser.add_argument('--stop_option',
                        type=str,
                        help='Param for usp. Stop option, default is ndays, can be nyears, nmonths, ndays',
                        default='ndays')

    parser.add_argument('--stop_n',
                        type=str,
                        help='Param for usp. Stop number, default is 1',
                        default='1')

    parser.add_argument('--run_type', 
                        type=str,
                        help='Param for usp. Run type, default is coldstart, can be branch',
                        default='coldstart')

    parser.add_argument('--run_refcase',
                        type=str,
                        help='Param for usp. Reference case, default is None',
                        default="None")

    parser.add_argument('--run_refdate',
                        type=str,
                        help='Param for usp. Reference date, default is None',
                        default="None")
    
    parser.add_argument('--run_reftod',
                        type=str,
                        help='Param for usp. Reference time of the day, default is 00000. Need to be provided when the RUN_TYPE is "branch".',
                        default="00000")
    
    parser.add_argument('--urban_hac',
                        type=str,
                        help='The flag to turn on the urban HAC. The default is "ON". valid_values="OFF,ON,ON_WASTEHEAT"',
                        default='ON')

    parser.add_argument('--iflog', 
                        type=bool,
                        help='Param for usp and script. If log, default is True',
                        default=True)

    parser.add_argument('--logfile', 
                        type=str,
                        help='Param for usp and script. Log file, default is pyclmuapp.log',
                        default='pyclmuapp.log')

    parser.add_argument('--hist_type',
                        type=str,
                        help='Param for usp. ouput type. Can be GRID, LAND, COLS, default is GRID',
                        default='GRID')
    
    parser.add_argument('--hist_nhtfrq',
                        type=int,
                        help='Param for usp. History file frequency, default is 1 (ouput each time step)',
                        default=1)
    
    parser.add_argument('--hist_mfilt',
                        type=int,
                        help='Param for usp. each history file will include mfilt time steps, default is 1000000000',
                        default=1000000000)

    parser.add_argument('--clean', 
                        type=str,
                        help='Param for usp. Clean, default is False',
                        default=False)
    
    def parse_list_float(value):
        return list(map(float, value.split(',')))
    
    def parse_list_str(value):
        return list(map(str, value.split(',')))

    parser.add_argument('--surf_var',
                        type=parse_list_str,
                        help="Param for usp. Surface variable, default is None. Can be one/some (use ','(withou space to seperate each)) of 'CANYON_HWR', 'HT_ROOF','THICK_ROOF','THICK_WALL','WTLUNIT_ROOF',\
'WTROAD_PERV','WIND_HGT_CANYON','NLEV_IMPROAD',\
'TK_ROOF','TK_WALL','TK_IMPROAD','CV_ROOF','CV_WALL','CV_IMPROAD',\
'EM_IMPROAD','EM_PERROAD','EM_ROOF','EM_WALL',\
'ALB_IMPROAD_DIR','ALB_IMPROAD_DIF','ALB_PERROAD_DIR','ALB_PERROAD_DIF',\
'ALB_ROOF_DIR','ALB_ROOF_DIF','ALB_WALL_DIR','ALB_WALL_DIF','T_BUILDING_MIN'",
                        default=None)
    
    parser.add_argument('--surf_action',
                        type=parse_list_float,
                        help='Param for usp. Surface action, default is None. The number is same as surf_var with "," seperated (not ", ")',
                        default=0)
    
    parser.add_argument('--forcing_var',
                        type=parse_list_str,
                        help="'Param for usp. Forcing variable, default is None. Can be one/some (use ','(withou space to seperate each)) of 'Prectmms','Wind','LWdown','PSurf','Qair','Tair','SWdown'",
                        default=None)

    parser.add_argument('--forcing_action',
                        type=parse_list_float,
                        help='Param for usp. Forcing action, default is None. The number is same as forcing_var with "," seperated (not ", ")',
                        default=0)

    #--------------------- add arguments for script part---------------------
    parser.add_argument('--script', 
                        type=str,
                        help='Param for script. Script file in container, default is None',
                        default=None)

    #--------------------- add arguments for mksurfdata part---------------------
    parser.add_argument('--urbsurf', 
                        type=str,
                        help='Param for get_surfdata. Urban surface data file, default is None. Here to download the urban surface data file: https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/lnd/clm2/rawdata/mksrf_urban_0.05x0.05_simyr2000.c120601.nc',
                        default=None)

    parser.add_argument('--soildata', 
                        type=str,
                        help='Param for get_surfdata. Soil data file, default is None. Here to download the soil data file: https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/lnd/clm2/rawdata/mksrf_soitex.10level.c010119.nc',
                        default=None)

    parser.add_argument('--pct_urban',
                        type=parse_list_float,
                        help='Param for get_surfdata. Percentage of urban land use in each density class, sum should be 100, default is [0,0,100.0]',
                        default=[0, 0, 100.0])

    # shared with get_surfdata and get_forcing
    parser.add_argument('--lat',
                        type=float,
                        help='Param for get_surfdata and get_forcing. Latitude of the urban area, default is None',
                        default=None)
    parser.add_argument('--lon',
                        type=float,
                        help='Param for get_surfdata and get_forcing. Longitude of the urban area, default is None',
                        default=None)
    parser.add_argument('--outputname',
                        type=str,
                        help='Param for get_surfdata. Output file name, default is surfdata.nc',
                        default='surfdata.nc')

    #--------------------- add arguments for get_forcing part---------------------
    parser.add_argument('--zbot',
                        type=int,
                        help='Param for get_forcing. zbot, default is 30 meters',
                        default=30)

    parser.add_argument('--start_year',
                        type=int,
                        help='Param for get_forcing. Start year, default is 2012',
                        default=2012)
    
    parser.add_argument('--end_year',
                        type=int,
                        help='Param for get_forcing. End year, default is 2012',
                        default=2012)
    parser.add_argument('--start_month',
                        type=int,
                        help='Param for get_forcing. Start month, default is 1',
                        default=1)
    parser.add_argument('--end_month',
                        type=int,
                        help='Param for get_forcing. End month, default is 12',
                        default=12)
    parser.add_argument('--source',
                        type=str,
                        help='Param for get_forcing. Source, default is cds, can be arco_era5',
                        default='cds')

    return parser.parse_args(gr_l) if gr_l is not None else parser.parse_args()

def check_file(file):
    """
    Args:
        file (_type_): check if the file exists
    """
    if file is None:
        raise ValueError(f"{file} should be provided")
    if not os.path.exists(file):
        raise ValueError(f"{file} does not exist")
        
def file_in_directory(file_name, directory):
    """
    check if the file exists in the directory
    
    Args:
        file_name (_type_): the file name
        directory (_type_): the directory

    """
    for dirpath, dirnames, filenames in os.walk(directory):
        if file_name in filenames:
            return True
        else:
            return False

def main():
    
    # get the arguments
    args = get_pypars()
    print(args)
    
    #####################################  INIT  pyclmuapp #####################################
    if args.container_type == "docker":
        container_type = "docker"
    elif args.container_type == "singularity":
        container_type = "singularity"
    else:
        raise ValueError("The container type should be docker or singularity")

    if args.pyclmuapp_mode in ["usp", "script"]:
        if args.pwd is None or args.pwd == "None" or args.pwd == "none":
            check_file(args.input_path)
            check_file(args.output_path)
            check_file(args.log_path)
            check_file(args.scripts_path)

            usp = usp_clmu(
            pwd=None,
            input_path=args.input_path,
            output_path=args.output_path,
            log_path=args.log_path,
            scripts_path = args.scripts_path,
            container_type=container_type)

        else:
            pwd = os.path.join(args.pwd, 'workdir')
            usp = usp_clmu(pwd=pwd, container_type=container_type)

        if args.has_container:
            usp.docker('pull', iflog=False)
            
            #if args.container_type == "docker":
            #    usp.docker('run', iflog=False)
            #
        else:
            print("Will use the existing container")
        
    if args.init:
        print("The pyclmuapp is initialized.")
    else:

        ##################################### pyclmuapp: USP mode #####################################
        if args.pyclmuapp_mode == "usp":
            _main_usp(args, usp)
            
        elif args.pyclmuapp_mode == "script":
            _main_script(args, usp)
            
        elif args.pyclmuapp_mode == "pts":
            print("The pts mode is not supported yet in cmd line tool")
            print("Please use the usp mode or refer to docs for creating your pts case using python")

        elif args.pyclmuapp_mode == "get_forcing":
            _main_create_forcing(args)

        elif args.pyclmuapp_mode == "get_surfdata":
            _main_create_surfdata(args)

        else:
            raise ValueError("The pyclmuapp_mode should be usp, script, pts, get_forcing or get_surfdata")

def _main_script(args, usp):
    check_file(args.script)

    script = args.script.split("/")[-1]

    print("The script is: ", args.script.split)

    if os.path.exists(os.path.join(usp.scripts_path, script)):
        print(f"The {script} already exists.")
    else:
        shutil.copy(args.script, os.path.join(usp.scripts_path, script))

    script = os.path.join("/p/scripts", script)

    usp.docker(cmd="chomd", script=script, iflog=False)
    # use the "file.log" to record the log
    usp.docker(cmd="exec", cmdlogfile=args.logfile, script=script, iflog=args.iflog)


def _main_usp(args, usp):
    if not args.has_container:
        usp.docker('run', iflog=False)

    if args.usr_surfdata is None:
        usp.check_surf()
    else:
        check_file(args.usr_surfdata)
        usp.check_surf(usr_surfdata=args.usr_surfdata)


    if args.usr_forcing is None:
        usp.check_forcing()
    else:
        check_file(args.usr_forcing)
        usp.check_forcing(usr_forcing=args.usr_forcing)
    
    # do this after check_surf
    # because the surfdata should be provided to read the domain file
    if args.usr_domain is None:
        print("The domain file is not provided")
        usp.check_domain()
    else:
        check_file(args.usr_domain)
        usp.check_domain(usr_domain=args.usr_domain)
    
    ouput = usp.run(
            output_prefix=args.output_prefix,
            case_name=args.case_name,
            RUN_STARTDATE=args.run_startdate,
            START_TOD=args.start_tod,
            STOP_OPTION=args.stop_option,
            STOP_N=args.stop_n,
            RUN_TYPE=args.run_type,
            RUN_REFCASE=args.run_refcase,
            RUN_REFDATE=args.run_refdate,
            RUN_REFTOD=args.run_reftod,
            urban_hac=args.urban_hac,
            #var_add=args.var_add,
            hist_type=args.hist_type,
            hist_nhtfrq=args.hist_nhtfrq,
            hist_mfilt=args.hist_mfilt,
            iflog=args.iflog,
            logfile=args.logfile,
        )
    # modify the surface data
    sur_mod = False
    ouput_modify_s = None
    if isinstance(args.surf_var, list) and isinstance(args.surf_action, list):
        if len(args.surf_var) != len(args.surf_action):
            raise ValueError("The length of surf_var and surf_action should be the same")

        if not np.any(np.isin(np.array(args.surf_var), [""])):
            print(args.surf_var, args.surf_action)
            action_s = {k: float(v) for k, v in zip(args.surf_var, args.surf_action)}
            action_sr = {k: -float(v) for k, v in zip(args.surf_var, args.surf_action)}
            usp.modify_surf(action=action_s,mode="add")
            sur_mod = True

            ouput_modify_s = usp.run(
                output_prefix=args.output_prefix,
                case_name=args.case_name,
                RUN_STARTDATE=args.run_startdate,
                START_TOD=args.start_tod,
                STOP_OPTION=args.stop_option,
                STOP_N=args.stop_n,
                RUN_TYPE=args.run_type,
                RUN_REFCASE=args.run_refcase,
                RUN_REFDATE=args.run_refdate,
                RUN_REFTOD=args.run_reftod,
                urban_hac=args.urban_hac,
                #var_add=args.var_add,
                hist_type=args.hist_type,
                hist_nhtfrq=args.hist_nhtfrq,
                hist_mfilt=args.hist_mfilt,
                iflog=args.iflog,
                logfile=args.logfile,
            )
            # recover the surfdata
            usp.modify_surf(action=action_sr,mode="add")

    # modify the forcing data
    forcing_mod = False
    ouput_modify_f = None
    if isinstance(args.forcing_var, list) and isinstance(args.forcing_action, list):

        if len(args.forcing_var) != len(args.forcing_action):
            raise ValueError("The length of forcing_var and forcing_action should be the same")

        if not np.any(np.isin(np.array(args.forcing_var), [""])):
            print(args.forcing_var, args.forcing_action)
            action_f = {k: float(v) for k, v in zip(args.forcing_var, args.forcing_action)}
            action_fr = {k: -float(v) for k, v in zip(args.forcing_var, args.forcing_action)}
            usp.modify_forcing(action=action_f,mode="add")
            forcing_mod = True

            ouput_modify_f = usp.run(
                    output_prefix=args.output_prefix,
                    case_name=args.case_name,
                    RUN_STARTDATE=args.run_startdate,
                    START_TOD=args.start_tod,
                    STOP_OPTION=args.stop_option,
                    STOP_N=args.stop_n,
                    RUN_TYPE=args.run_type,
                    RUN_REFCASE=args.run_refcase,
                    RUN_REFDATE=args.run_refdate,
                    RUN_REFTOD=args.run_reftod,
                    urban_hac=args.urban_hac,
                    #var_add=args.var_add,
                    hist_type=args.hist_type,
                    hist_nhtfrq=args.hist_nhtfrq,
                    hist_mfilt=args.hist_mfilt,
                    iflog=args.iflog,
                    logfile=args.logfile,
                )

            # recover the forcing data
            usp.modify_forcing(action=action_fr,mode="add")

    ouput_modify_sf = False
    if sur_mod and forcing_mod:

        # modify the forcing data and surfdata
        usp.modify_surf(action=action_s,mode="add")
        usp.modify_forcing(action=action_f,mode="add")
        ouput_modify_sf = usp.run(
                output_prefix=args.output_prefix,
                case_name=args.case_name,
                RUN_STARTDATE=args.run_startdate,
                START_TOD=args.start_tod,
                STOP_OPTION=args.stop_option,
                STOP_N=args.stop_n,
                RUN_TYPE=args.run_type,
                RUN_REFCASE=args.run_refcase,
                RUN_REFDATE=args.run_refdate,
                RUN_REFTOD=args.run_reftod,
                urban_hac=args.urban_hac,
                #var_add=args.var_add,
                hist_type=args.hist_type,
                hist_nhtfrq=args.hist_nhtfrq,
                hist_mfilt=args.hist_mfilt,
                iflog=args.iflog,
                logfile=args.logfile,
            )
        # recover the forcing data and surfdata
        usp.modify_forcing(action=action_fr,mode="add")
        usp.modify_surf(action=action_sr,mode="add")

    if args.clean == True:
        print("Clean the case")
        usp.case_clean()
        usp.clean_usp()

    # output the result
    output_dict = {"original": ouput}
    if ouput_modify_f:
        output_dict["modify_forcing"] = ouput_modify_f
    if ouput_modify_s:
        output_dict["modify_surf"] = ouput_modify_s
    if ouput_modify_sf:
        output_dict["modify_surf_forcing"] = ouput_modify_sf

    with open(args.logfile, "a") as f:
        f.write(f"The case is: {args.case_name}\n")
        f.write(f"The output file is: {output_dict}\n")

    print("The case is: ", args.case_name)
    print("The log file is: ", args.logfile)
    print("The output file is: ", output_dict)

    return output_dict

#def _main_create_forcing(args):
#    import xarray as xr
#    from pyclmuapp.clmu import get_clmuapp_frocing
#    
#    era5_list = []
#    
#    check_file(args.era5_path)
#    if args.lat is None or args.lon is None:
#        raise ValueError("The latitude and longitude should be provided")
#    for file in os.listdir(args.era5_path):
#        ds = xr.open_dataset(os.path.join(args.era5_path, file))
#        era5_list.append(ds)
#    era5 = xr.concat(era5_list, dim='time')
#    era5 = era5.sortby('time')
#    
#    forcing = get_clmuapp_frocing(era5=era5, 
#                          lat = args.lat,
#                          lon = args.lon,
#                          outputname=args.outputname)
#    
#    print("The forcing data is created successfully. The file is: ", args.outputname)
#    
#    return os.path.join(os.getcwd(), args.outputname)
    
def _main_create_forcing(args):
    get_forcing(
        start_year=args.start_year,
        end_year=args.end_year,
        start_month=args.start_month,
        end_month=args.end_month,
        lat=args.lat,
        lon=args.lon,
        zbot=args.zbot,
        source=args.source,
    )
    
def _main_create_surfdata(args):
        
    import xarray as xr
    from pyclmuapp import get_urban_params

    check_file(args.urbsurf)
    check_file(args.soildata)
    if args.lat is None or args.lon is None:
        raise ValueError("The latitude and longitude should be provided")
    urb = xr.open_dataset(args.urbsurf)
    soil = xr.open_dataset(args.soildata)
    urban = get_urban_params(
        urban_ds=urb,
        soil_ds=soil,
        template=os.path.join(os.path.dirname(__file__), 'usp/surfdata.nc'),
        lat=args.lat,
        lon=args.lon,
        PTC_URBAN=args.pct_urban,
        outputname=args.outputname,
    )
    print("The urban surface data is created successfully. The file is: ", args.outputname)
    return os.path.join(os.getcwd(), args.outputname)
    #https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/lnd/clm2/rawdata/mksrf_urban_0.05x0.05_simyr2000.c120601.nc