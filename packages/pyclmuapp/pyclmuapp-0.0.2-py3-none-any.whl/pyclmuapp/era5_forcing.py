import cdsapi
import os
import xarray as xr
import numpy as np
from typing import Union
import tempfile
import zipfile
import shutil

variable=[
            '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
            '2m_temperature', 'surface_pressure', 'surface_solar_radiation_downwards',
            'surface_thermal_radiation_downwards', 'total_precipitation', 'forecast_surface_roughness'
            ]

era5_var_dict = {
    '10m_u_component_of_wind': 'u10',
    '10m_v_component_of_wind': 'v10',
    '2m_dewpoint_temperature': 'd2m',
    '2m_temperature': 't2m',
    'surface_pressure': 'sp',
    'surface_solar_radiation_downwards': 'ssrd',
    'surface_thermal_radiation_downwards': 'strd',
    'total_precipitation': 'tp',
    'forecast_surface_roughness': 'fsr'
}

def era5_download(year, month,lat, lon, 
                  outputfolder='./data'):

    """
    This function `era5_download` is designed to download ERA5 reanalysis data for 
    a specific year, month, pressure level, latitude, and longitude. 
    It uses the `cdsapi` library to retrieve the data from the Copernicus Climate Data Store (CDS) API.

    Args:
        year (int): The year of the data to download.
        month (str): The month of the data to download.
        lat (float): The latitude of the data to download.
        lon (float): The longitude of the data to download.
        outputfolder (str): The folder to save the downloaded data to.
        
    Returns:
        pres (str): The path to the downloaded pressure level data.
        single (str): The path to the downloaded single level data.
    
    """
    
    c = cdsapi.Client()
    
    #months_str = "-".join([str(i).zfill(2) for i in months])
    months_str = str(month).zfill(2)
    single = os.path.join(outputfolder, f'era5_single_{year}_{months_str}_{lat}_{lon}.zip')
    single_nc = os.path.join(outputfolder, f'era5_single_{year}_{months_str}_{lat}_{lon}.nc')
    if os.path.exists(single_nc):
        print(f'file exists: {single_nc}')
    else:
        print(f'download: {single}')
        os.makedirs(outputfolder, exist_ok=True)
        c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': ["reanalysis"],
            "download_format": "zip",
            'data_format': 'netcdf',
            'variable': variable,
            'year': [str(year)],
            'month': [str(month).zfill(2)],
            #'month': [str(i).zfill(2) for i in months],
            'day': [str(i).zfill(2) for i in range(1, 32)],
            'time': [str(i).zfill(2)+':00' for i in range(24)],
            'area': [
                lat+0.25, lon-0.25, lat-0.25, lon+0.25,
            ],
        },
        single)

        with zipfile.ZipFile(single, 'r') as zip_ref:
            os.makedirs(f'{outputfolder}/single_temp', exist_ok=True)
            zip_ref.extractall(f'{outputfolder}/single_temp')
            ds_ls = []
            for file in zip_ref.namelist():
                if file.endswith('.nc'):
                    single_ds = f'{outputfolder}/single_temp/{file}'
                    ds = xr.open_dataset(single_ds)
                    ds_ls.append(ds)
                    
            single_ds = xr.merge(ds_ls)
            
            single_ds = single_ds.rename({'valid_time': 'time'})
            single_ds = single_ds.drop_vars(['expver','number'])
            single_ds.to_netcdf(single_nc)
            
        shutil.rmtree(f'{outputfolder}/single_temp')
        os.remove(single)        
                
    return single_nc


def arco_era5_to_forcing(start_year, end_year, 
                start_month, end_month,
                lat, lon, zbot,outputfile,lapse_rate=0.006):

    """
    Converts ERA5 data to forcing data for a specified time period and location using a lapse rate.

    Args:
        start_year (int): The beginning year for the data extraction process. Specifies the starting year for the time period from which data will be extracted.
        end_year (int): Specifies the ending year for the data range you want to process. Used to indicate the last year for which the data will be processed.
        start_month (int): Represents the starting month for which you want to retrieve data. Specifies the beginning month of the time period for which you want to extract ERA5 data.
        end_month (int): Represents the ending month for which you want to process data. Specifies the end month of the time period for which you are retrieving or processing data.
        lat (float): Latitude of the location for which the data is being processed.
        lon (float): Longitude of the location for which the ERA5 data will be extracted.
        zbot (float): Likely refers to the bottom level of the atmosphere or the height above the surface at which the atmospheric data is being extracted. Represents the altitude or depth at which the atmospheric variables are measured or calculated.
        outputfile (str): The name of the file where the output data will be saved or written to. This file will contain the processed data based on the input parameters provided to the function.
        lapse_rate (float, optional): Represents the lapse rate used for calculating temperature at different altitudes. The lapse rate is the rate at which atmospheric temperature decreases with an increase in altitude. Defaults to 0.
    """
    
    ar_full_37_1h = xr.open_zarr(
                    'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3',
                    chunks=None,
                    storage_options=dict(token='anon'),)
    single = ar_full_37_1h[variable]\
            .sel(time=slice(f'{start_year}-{start_month}', f'{end_year}-{end_month}'))\
            .sel(longitude=lon, latitude=lat, method='nearest')
            
    with tempfile.NamedTemporaryFile() as temp_file:
        single.to_netcdf(temp_file.name)
        single = xr.open_dataset(temp_file.name)
        for var in era5_var_dict:
            single = single.rename({var: era5_var_dict[var]})
        forcing = era5_to_forcing(single, lat, lon, zbot, outputfile, lapse_rate=lapse_rate)


def check_era5(era5: Union[str, xr.Dataset],
               lat: float, lon: float):
    """
    The `check_era5` function is a helper function that takes in a variable `era5`, 
    latitude `lat`, and longitude `lon`. It checks the type of the `era5` variable and based on its type, 
    it opens the dataset if it's a file path or uses it directly if it's already an xarray Dataset.

    Args:
        era5 (Union[str, xr.Dataset]): The ERA5 data.
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.
    
    Returns:
        xarray.Dataset: The ERA5 data for the location.
    """
    if isinstance(era5, str):
        if os.path.isfile(era5):
            forcing = xr.open_dataset(era5)
            
        elif os.path.isdir(era5):
            for root, dirs, files in os.walk(era5):
                for file in files:
                    forcing_ls = []
                    if file.endswith(".nc"):
                        _forcing = xr.open_dataset(os.path.join(root, file))
                        forcing_ls.append(_forcing)
            forcing = xr.concat(forcing_ls, dim='time').sortby('time')
    
    elif isinstance(era5, xr.Dataset):
        forcing = era5
    else:
        raise ValueError("The era5 should be a xarray dataset or a file path.")
    
    if forcing.latitude.values.shape:
        
        if forcing.longitude.values.shape:
            forcing = forcing.sel(latitude=lat,longitude=lon,method='nearest')
        else:
            forcing = forcing.sel(latitude=lat,method='nearest')
    
    elif forcing.longitude.values.shape:
        forcing = forcing.sel(longitude=lon,method='nearest')
    
    return forcing


def era5_to_forcing(
                    single: Union[str, xr.Dataset], 
                    lat: float, lon: float, 
                    zbot: int = 30,
                    outputfile: str = './forcing.nc',
                    lapse_rate: int = 0.006
                    ):
    
    """
    "The function `era5_to_forcing` takes in two xarray Datasets `pres` and `single`, latitude `lat`, longitude `lon`, 
    and an optional `pressure` parameter with a default value of 950."
    
    Args:
        single (xarray.Dataset, str): The single level data.
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.
        zbot (int, float): The bottom level of the forcing data.
        outputfile (str): The path to save the forcing data.
        lapse_rate (int, float): The lapse rate of the forcing data. default is 0.006, from Pritchard et al. (GRL, 35, 2008) of CTSM 

    Returns:
        xarray.Dataset: The forcing data.
    """
    
    # Check the type of the input data
    single = check_era5(single, lat, lon)
    
    #-------------------Constants-------------------
    SHR_CONST_BOLTZ   = 1.38065e-23  # Boltzmann's constant ~ J/K/molecule
    SHR_CONST_AVOGAD  = 6.02214e26   # Avogadro's number ~ molecules/kmole
    SHR_CONST_RGAS    = SHR_CONST_AVOGAD*SHR_CONST_BOLTZ       # Universal gas constant ~ J/K/kmole
    SHR_CONST_MWDAIR  = 28.966       # molecular weight dry air ~ kg/kmole
    SHR_CONST_MWWV    = 18.016       # molecular weight water vapor
    SHR_CONST_RDAIR   = SHR_CONST_RGAS/SHR_CONST_MWDAIR        # Dry air gas constant     ~ J/K/kg
    SHR_CONST_G       = 9.80616      # acceleration of gravity ~ m/s^2

    rair              = SHR_CONST_RDAIR
    grav              = SHR_CONST_G
    # Pritchard et al. (GRL, 35, 2008) use 0.006
    #lapse_rate = 0.006 # https://github.com/ESCOMP/CTSM/blob/a9433779f0ae499d60ad118d2ec331628f0eaaa8/bld/namelist_files/namelist_defaults_ctsm.xml#L197
    
    
    # costants for saturation vapor pressure for Qair
    a0 =  6.11213476
    a1 =  0.444007856
    a2 =  0.143064234e-01
    a3 =  0.264461437e-03
    a4 =  0.305903558e-05
    a5 =  0.196237241e-07
    a6 =  0.892344772e-10
    a7 = -0.373208410e-12
    a8 =  0.209339997e-15

    c0 =  6.11123516
    c1 =  0.503109514
    c2 =  0.188369801e-01
    c3 =  0.420547422e-03
    c4 =  0.614396778e-05
    c5 =  0.602780717e-07
    c6 =  0.387940929e-09
    c7 =  0.149436277e-11
    c8 =  0.262655803e-14
    # -------------------Constants-------------------
    
    #tbot_c = tbot_g-lapse_rate*(hsurf_c-hsurf_g)
    #Hbot  = rair*0.5*(tbot_g+tbot_c)/grav
    #pbot_c = pbot_g*np.exp(-(hsurf_c-hsurf_g)/Hbot)
    
    single['Tair'] = single['t2m']/1.0
    single['Tair'] = single['Tair'] - lapse_rate * (zbot - 2.0)
    single['Tair'].attrs['units'] = 'K'
    single['Tair'].attrs['long_name'] = 'Air temperature'
    
    Hbot = rair * single['Tair'] / grav
    single['PSurf'] = single['sp']/1.0
    single['PSurf'] = single['PSurf'] * np.exp(-(zbot - 2.0) / Hbot)
    single['PSurf'].attrs['units'] = 'Pa'
    single['PSurf'].attrs['long_name'] = 'Surface pressure at 950 hPa'

    single['Wind'] = (single['u10']**2 + single['v10']**2)**0.5
    # ref: https://doi.org/10.5194/essd-14-5157-2022
    single['Wind'] = single['Wind'] * (np.log(zbot / single['fsr']) / np.log(10 / single['fsr']))
    #single['Wind'] = single['Wind'] * (xr.ufuncs.log(2 / single['fsr']) / xr.ufuncs.log(10 / single['fsr']))
    single['Wind'] = single['Wind'].assign_attrs(units='m/s')
    single['Wind'] = single['Wind'].assign_attrs(long_name='Wind speed')

    # ref1: https://github.com/ESCOMP/CTSM/blob/75b34d2d8770461e3e28cee973a39f1737de091d/doc/source/tech_note/Land-Only_Mode/CLM50_Tech_Note_Land-Only_Mode.rst#L113
    # ref2: https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
    # ref3: https://github.com/ESCOMP/CTSM/blob/75b34d2d8770461e3e28cee973a39f1737de091d/src/biogeophys/QSatMod.F90
    # Reference:  Polynomial approximations from:
    #             Piotr J. Flatau, et al.,1992:  Polynomial fits to saturation
    #             vapor pressure.  Journal of Applied Meteorology, 31, 1507-1513.
    lapse_rate_dew = 1.8/1000 # ref: https://commons.erau.edu/cgi/viewcontent.cgi?article=1374&context=ijaaa
    # DPLR of moist air at temperature of 20oC (293 K) and dew point of 12oC(285 K) has RH of approximately 60%. 
    # DP-depression D is 8oC (8 K). Using Eq. (38), whileneglecting specific humidity contribution, 
    # DPLR yields about 0.546 K/1,000 ft (1.8 K/km). Thisis valid result as measured DPLRs are normally in the range 1.6-2.0 K/km or 0.50 to 0.6 K/1,000ft.
    # for simple, we use lapse_rate_dew = 1.8/1000, which is the middle of the range.
    # pdf is in src/CLMU_literatures/On Atmospheric Lapse Rates.pdf
    single['d2m'] = single['d2m'] - 273.15 - lapse_rate_dew * (zbot - 2.0)
    # es_water
    single['es_water'] = a0 + single['d2m']*(a1 + single['d2m']*(a2 + single['d2m']*(a3 + single['d2m']*(a4 
            + single['d2m']*(a5 + single['d2m']*(a6 + single['d2m']*(a7 + single['d2m']*a8)))))))
    single['es_water'] = single['es_water'] * 100
    # es_ice
    single['es_ice'] = c0 + single['d2m']*(c1 + single['d2m']*(c2 + single['d2m']*(c3 + single['d2m']*(c4 
            + single['d2m']*(c5 + single['d2m']*(c6 + single['d2m']*(c7 + single['d2m']*c8)))))))
    single['es_ice'] = single['es_ice'] * 100   
    # es 
    single['es'] = xr.where(single['d2m'] >= 0, single['es_water'],single['es_ice'])
    # Qair
    single['Qair'] = 0.622 * single['es'] / (single['PSurf'] - (1 - 0.622) * single['es'])
    single['Qair'] = single['Qair'].where(single['Qair'] > 0, 1e-16)
    single['Qair'].attrs['units'] = 'kg/kg'
    single['Qair'].attrs['long_name'] = 'Specific humidity'
    
    single['Zbot'] = single['sp'] /1.0
    single['Zbot'].values = np.ones(single['Zbot'].shape) * zbot
    single['Zbot'].attrs['units'] = 'm'
    single['Zbot'].attrs['long_name'] = 'Geopotential height'
    
    single['SWdown'] = single['ssrd']/ 3600 
    single['SWdown'] = single['SWdown'].where(single['SWdown'] > 0, 1e-16)
    single['SWdown'].attrs['units'] = 'W/m^2'
    single['SWdown'].attrs['long_name'] = 'Surface solar radiation downwards'
    single['LWdown'] = single['strd']/ 3600 
    single['LWdown'] = single['LWdown'].where(single['LWdown'] > 0, 1e-16)
    single['LWdown'].attrs['units'] = 'W/m^2'
    single['LWdown'].attrs['long_name'] = 'Surface thermal radiation downwards'
    
    single['Prectmms'] = single['tp'] * 1000 / 3600
    single['Prectmms'] = single['Prectmms'].where(single['Prectmms'] > 0, 1e-16)
    single['Prectmms'].attrs['units'] = 'mm/s'
    single['Prectmms'].attrs['long_name'] = 'Total precipitation'
    for var in ['PSurf', 'Qair', 'Wind', 'Tair', 'Zbot', 'SWdown', 'LWdown', 'Prectmms']:
        single[var] = single[var].assign_attrs(_FillValue=1.e36)
    single['x'] = 1
    single['y'] = 1
    single = single.assign_coords(x=1,y=1)
    for var in single.data_vars:
        single[var] = single[var].expand_dims('x',axis=1).expand_dims('y',axis=1)
        
    del single['latitude'], single['longitude'], single['d2m'], \
        single['sp'], single['ssrd'], single['strd'], single['tp'], \
        single['u10'], single['v10'], single['fsr'], \
        single['t2m'], single['es_water'], single['es_ice'], single['es']
    
    #single.to_netcdf(outputfile)
    return single