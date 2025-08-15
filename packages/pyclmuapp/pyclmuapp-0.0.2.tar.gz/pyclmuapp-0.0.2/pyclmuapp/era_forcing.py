import cdsapi
import xarray as xr
import numpy as np
from typing import Union
import zipfile
import re
from datetime import datetime
import os


def download_era5_land_data(lat: float, lon: float, start_date: str, end_date: str, output_file: str = None):
    
    """
    Downloads ERA5 land data for a specific latitude and longitude within a given date range.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        start_date (str): Start date for data retrieval in 'YYYY-MM-DD' format.
        end_date (str): End date for data retrieval in 'YYYY-MM-DD' format.
        output_file (str, optional): Path to save the downloaded data. If not provided,
                                      a default name will be generated based on the parameters.
    """
    
    dataset = "reanalysis-era5-land-timeseries"
    
    lat = round(float(lat), 1)
    lon = round(float(lon), 1)
    
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("Latitude must be between -90 and 90, and longitude must be between -180 and 180.")
    
    if not (start_date and end_date):
        raise ValueError("Start date and end date must be provided.")
    
    request = {
        "variable": [
            "2m_dewpoint_temperature",
            "2m_temperature",
            "surface_pressure",
            "total_precipitation",
            "surface_solar_radiation_downwards",
            "10m_v_component_of_wind",
            "10m_u_component_of_wind",
        ],
        "location": {"longitude": lon, "latitude": lat},
        "date": [f"{start_date}/{end_date}"],
        "data_format": "netcdf"
    }
    
    client = cdsapi.Client()
    output_file = output_file or f"era5_land_{lat}_{lon}_{start_date}_{end_date}.zip"
    client.retrieve(dataset, request).download(output_file)
    return output_file

def get_nc_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        # 获取压缩包内的第一个文件名
        file_name = z.namelist()
        # 打开并读取 CSV 文件
        xr_ls = []
        for name in file_name:
            if name.endswith('.nc'):
                _xr = xr.open_dataset(z.open(name))
                xr_ls.append(_xr)
        # 合并所有的 xarray 数据集
        if xr_ls:
            ds = xr.merge(xr_ls)
    return ds

def era5s_to_forcing(
                    single: Union[str, xr.Dataset], 
                    zbot: int = 30,
                    outputfile: str = './forcing.nc',
                    lapse_rate: int = 0.006
                    ):
    
    """
    "The function `era5s_to_forcing` takes in two xarray Datasets `pres` and `single`, latitude `lat`, longitude `lon`, 
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
    
    if isinstance(single, str):
        single = xr.open_dataset(single)
        
    single = single.rename({'valid_time': 'time'})
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
    # ref: https://www.bilibili.com/opus/963995230578671683
    # ref: https://www.calculatoratoz.com/en/wind-speed-at-standard-10-m-reference-level-calculator/Calc-23764
    # ref: https://baike.baidu.com/item/%E9%A3%8E%E5%88%87%E5%8F%98%E6%8C%87%E6%95%B0/5192431
    single['Wind'] = single['Wind'] * (zbot / 10.0)**(1/7)  # Convert to wind
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
    
    # es == ea in this case, as we calculate the es using d2m
    single['eair'] = 1.24 * (single['es']/100 / single['t2m']) ** (1/7) # ref: W Brutsaert - Water resources research, 1975
    single['LWdown'] = single['eair'] * (single['t2m'] ** 4) * 5.67e-8 # ref : W Brutsaert - Water resources research, 1975
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
        single['sp'], single['ssrd'], single['tp'], \
        single['u10'], single['v10'], \
        single['t2m'], single['es_water'], single['es_ice'], single['es'], single['eair']
    
    single.to_netcdf(outputfile)
    return single


def is_within(existing_file, start_date, end_date):
    pattern = r"era5_land_.*_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.zip"
    match = re.match(pattern, existing_file)
    if match:
        existing_start = datetime.strptime(match.group(1), "%Y-%m-%d")
        existing_end = datetime.strptime(match.group(2), "%Y-%m-%d")
        new_start = datetime.strptime(start_date, "%Y-%m-%d")
        new_end = datetime.strptime(end_date, "%Y-%m-%d")
        return existing_start <= new_start and existing_end >= new_end
    return False


def workflow_era5s_to_forcing(
                    lat: float, lon: float, start_date: str, end_date: str, # for download_era5_land_data
                    zbot: int = 30,
                    outputfile: str = './forcing.nc',
                    lapse_rate: int = 0.006
                    ):
    """
    A workflow function to download ERA5 land data and convert it to forcing data.
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        start_date (str): Start date for data retrieval in 'YYYY-MM-DD' format.
        end_date (str): End date for data retrieval in 'YYYY-MM-DD' format.
        zbot (int, float): The bottom level of the forcing data.
        outputfile (str): The path to save the forcing data.
        lapse_rate (int, float): The lapse rate of the forcing data. default is 0.006, from Pritchard et al. (GRL, 35, 2008) of CTSM
    Returns:
        xarray.Dataset: The forcing data.
        ds (xarray.Dataset): The dataset containing the downloaded ERA5 land data.
    """
    lat = round(float(lat), 1)
    lon = round(float(lon), 1)
    
    # Check if the file already exists and is within the date range
    found = False
    for fname in os.listdir("."):
        if fname.startswith(f"era5_land_{lat}_{lon}_") and fname.endswith(".zip"):
            if is_within(fname, start_date, end_date):
                print(f"Data for {lat}, {lon}, {start_date} to {end_date} already downloaded in file {fname}.")
                found = True
                zip_path = fname
                break

    if not found:
        print(f"Downloading data for {lat}, {lon}, {start_date} to {end_date}...")
        zip_path = f"era5_land_{lat}_{lon}_{start_date}_{end_date}.zip"
        download_era5_land_data(lat, lon, start_date, end_date, output_file=zip_path)
        
        
    ds = get_nc_from_zip(zip_path)
    forcing_data = era5s_to_forcing(ds, zbot=zbot, outputfile=outputfile, lapse_rate=lapse_rate)
    os.remove(zip_path)
    return outputfile, ds

if __name__ == "__main__":
    # Example usage
    lat = 52.6
    lon = -2.0
    start_date = "2020-01-01"
    end_date = "2020-01-31"
    zbot = 30
    outputfile = "forcing.nc"
    
    forcing_file = workflow_era5s_to_forcing(lat, lon, start_date, end_date, zbot=zbot, outputfile=outputfile)
    print(f"Forcing data saved to {forcing_file}")