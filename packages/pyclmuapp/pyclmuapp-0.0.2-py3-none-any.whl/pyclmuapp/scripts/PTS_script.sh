#!/bin/bash

# Junjie Yu, 2023-11-24, Manchester, UK
# This script is used to create a CESM case with the PTS mode on.

export USER=root
source ~/.bashrc

cd ${CASESCRIPT} # scripts folder


#!/bin/bash

if [ -d "${case_name}" ]; then
    cd ${case_name}
else
    ./create_newcase --case ${case_name} --res ${resolution} --compset ${compset} --run-unsupported
    cd ${case_name}

    ./xmlchange PTS_MODE=TRUE,PTS_LAT=${case_lat},PTS_LON=${case_lon}
    ./xmlchange RUN_STARTDATE=${RUN_STARTDATE}
    ./xmlchange DATM_CLMNCEP_YR_START=${DATM_CLMNCEP_YR_START}
    ./xmlchange DATM_CLMNCEP_YR_END=${DATM_CLMNCEP_YR_END}
    ./xmlchange STOP_OPTION='${STOP_OPTION}'
    ./xmlchange STOP_N=${case_length}
    ./xmlchange NTASKS=1
    ./xmlchange CLM_FORCE_COLDSTART=on

    # Set up the case
    ./case.setup

    # Modify the user_nl_clm file
    #echo "hist_avgflag_pertape='${hist_avgflag_pertape}'" >> user_nl_clm
    #echo "hist_nhtfrq=${hist_nhtfrq}" >> user_nl_clm
    #echo "hist_mfilt=${hist_mfilt}" >> user_nl_clm
    #
    #if [ "${output_murban}" = "True" ]; then
    #    echo "hist_empty_htapes = .true." >> user_nl_clm
    #    echo "hist_fincl1=${mu_urban}" >> user_nl_clm
    #    echo "hist_dov2xy=.false." >> user_nl_clm
    #    echo "hist_type1d_pertape='LAND'" >> user_nl_clm
    #fi
    #
    #echo "hist_empty_htapes = .true." >> user_nl_clm
    #echo "hist_fincl1='TREFMNAV','TREFMXAV'" >> user_nl_clm
    #
    #echo "hist_dov2xy=.false." >> user_nl_clm
    #echo "hist_type1d_pertape='LAND'" >> user_nl_clm

    # Modify the CLM namelist
    echo "hist_empty_htapes=.true." >> user_nl_clm_jj
    variables=$hist_type
    formatted_variables=$(echo $variables | sed "s/\([^,]\+\)/'\1'/g")
    hist_type1d_pertape=$formatted_variables
    IFS=',' read -ra hist_array <<< "$hist_type1d_pertape"

    length=${#hist_array[@]}

    hist_nhtfrq_l="${hist_nhtfrq},"
    for (( i=1; i<=length; i++ ))
    do
        new_hist_nhtfrq+=${hist_nhtfrq_l}
    done

    hist_mfilt_l="${hist_mfilt},"
    for (( i=1; i<=length; i++ ))
    do
        new_hist_mfilt+=${hist_mfilt_l}
    done

    new_hist_dov2xy=$(printf '.false.,'%.0s $(seq 1 $length))
    new_hist_nhtfrq=${new_hist_nhtfrq%,}
    new_hist_mfilt=${new_hist_mfilt%,}
    new_hist_dov2xy=${new_hist_dov2xy%,}

    echo "hist_nhtfrq=${new_hist_nhtfrq}" >> user_nl_clm_jj
    echo "hist_mfilt=${new_hist_mfilt}" >> user_nl_clm_jj
    echo "hist_dov2xy=${new_hist_dov2xy}" >> user_nl_clm_jj
    echo "hist_type1d_pertape=${hist_type1d_pertape}" >> user_nl_clm_jj


    if [ $length -eq 1 ]; then
        echo "hist_fincl1='FSA', 'FIRA', 'URBAN_HEAT', 'WASTEHEAT', 'EFLX_LH_TOT', 'FSH', 'FGR', 'URBAN_AC', 'RAIN', 'SNOW', 'QVEGT', 'QVEGE', 'QSOIL', 'QOVER', 'QH2OSFC', 'QDRAI', 'QDRAI_PERCH', 'SOILLIQ', 'SOILICE', 'H2OSNO', 'HIA','SWBGT','WBT', 'HUMIDEX', 'TWS', 'TRAFFICFLUX', 'TBUILD', 'COSZEN', 'ZWT', 'QFLX_EVAP_TOT', 'RH2M','TG','TSKIN','TBOT','FIRE','FLDS','FSDS','FSR','FGEV','TSOI','ERRSOI','SABV','SABG','FSDSVD','FSDSND','FSDSVI','FSDSNI','FSRVD','FSRND','FSRVI','FSRNI','TSA','FCTR','FCEV','QBOT','Q2M','H2OSOI','SWup','LWup','Rnet','Qh','Qle','Qstor','Qtau','Wind','Qair','Tair','PSurf','Rainf','SWdown','LWdown','SoilAlpha_U','TBUILD','TWS','TRAFFICFLUX','COSZEN'" >> user_nl_clm_jj

    elif [ $length -eq 2 ]; then
        echo "hist_fincl1='FSA', 'FIRA', 'URBAN_HEAT', 'WASTEHEAT', 'EFLX_LH_TOT', 'FSH', 'FGR', 'URBAN_AC', 'RAIN', 'SNOW', 'QVEGT', 'QVEGE', 'QSOIL', 'QOVER', 'QH2OSFC', 'QDRAI', 'QDRAI_PERCH', 'SOILLIQ', 'SOILICE', 'H2OSNO', 'HIA','SWBGT','WBT', 'HUMIDEX', 'TWS', 'TRAFFICFLUX', 'TBUILD', 'COSZEN', 'ZWT', 'QFLX_EVAP_TOT', 'RH2M','TG','TSKIN','TBOT','FIRE','FLDS','FSDS','FSR','FGEV','TSOI','ERRSOI','SABV','SABG','FSDSVD','FSDSND','FSDSVI','FSDSNI','FSRVD','FSRND','FSRVI','FSRNI','TSA','FCTR','FCEV','QBOT','Q2M','H2OSOI','SWup','LWup','Rnet','Qh','Qle','Qstor','Qtau','Wind','Qair','Tair','PSurf','Rainf','SWdown','LWdown','SoilAlpha_U','TBUILD','TWS','TRAFFICFLUX','COSZEN'" >> user_nl_clm_jj
        echo "hist_fincl2='FSA', 'FIRA', 'URBAN_HEAT', 'WASTEHEAT', 'EFLX_LH_TOT', 'FSH', 'FGR', 'URBAN_AC', 'RAIN', 'SNOW', 'QVEGT', 'QVEGE', 'QSOIL', 'QOVER', 'QH2OSFC', 'QDRAI', 'QDRAI_PERCH', 'SOILLIQ', 'SOILICE', 'H2OSNO', 'HIA','SWBGT','WBT', 'HUMIDEX', 'TWS', 'TRAFFICFLUX', 'TBUILD', 'COSZEN', 'ZWT', 'QFLX_EVAP_TOT', 'RH2M','TG','TSKIN','TBOT','FIRE','FLDS','FSDS','FSR','FGEV','TSOI','ERRSOI','SABV','SABG','FSDSVD','FSDSND','FSDSVI','FSDSNI','FSRVD','FSRND','FSRVI','FSRNI','TSA','FCTR','FCEV','QBOT','Q2M','H2OSOI','SWup','LWup','Rnet','Qh','Qle','Qstor','Qtau','Wind','Qair','Tair','PSurf','Rainf','SWdown','LWdown','SoilAlpha_U','TBUILD','TWS','TRAFFICFLUX','COSZEN'" >> user_nl_clm_jj

    else
        echo "hist_fincl1='FSA', 'FIRA', 'URBAN_HEAT', 'WASTEHEAT', 'EFLX_LH_TOT', 'FSH', 'FGR', 'URBAN_AC', 'RAIN', 'SNOW', 'QVEGT', 'QVEGE', 'QSOIL', 'QOVER', 'QH2OSFC', 'QDRAI', 'QDRAI_PERCH', 'SOILLIQ', 'SOILICE', 'H2OSNO', 'HIA','SWBGT','WBT', 'HUMIDEX', 'TWS', 'TRAFFICFLUX', 'TBUILD', 'COSZEN', 'ZWT', 'QFLX_EVAP_TOT', 'RH2M','TG','TSKIN','TBOT','FIRE','FLDS','FSDS','FSR','FGEV','TSOI','ERRSOI','SABV','SABG','FSDSVD','FSDSND','FSDSVI','FSDSNI','FSRVD','FSRND','FSRVI','FSRNI','TSA','FCTR','FCEV','QBOT','Q2M','H2OSOI','SWup','LWup','Rnet','Qh','Qle','Qstor','Qtau','Wind','Qair','Tair','PSurf','Rainf','SWdown','LWdown','SoilAlpha_U','TBUILD','TWS','TRAFFICFLUX','COSZEN'" >> user_nl_clm_jj
        echo "hist_fincl2='FSA', 'FIRA', 'URBAN_HEAT', 'WASTEHEAT', 'EFLX_LH_TOT', 'FSH', 'FGR', 'URBAN_AC', 'RAIN', 'SNOW', 'QVEGT', 'QVEGE', 'QSOIL', 'QOVER', 'QH2OSFC', 'QDRAI', 'QDRAI_PERCH', 'SOILLIQ', 'SOILICE', 'H2OSNO', 'HIA','SWBGT','WBT', 'HUMIDEX', 'TWS', 'TRAFFICFLUX', 'TBUILD', 'COSZEN', 'ZWT', 'QFLX_EVAP_TOT', 'RH2M','TG','TSKIN','TBOT','FIRE','FLDS','FSDS','FSR','FGEV','TSOI','ERRSOI','SABV','SABG','FSDSVD','FSDSND','FSDSVI','FSDSNI','FSRVD','FSRND','FSRVI','FSRNI','TSA','FCTR','FCEV','QBOT','Q2M','H2OSOI','SWup','LWup','Rnet','Qh','Qle','Qstor','Qtau','Wind','Qair','Tair','PSurf','Rainf','SWdown','LWdown','SoilAlpha_U','TBUILD','TWS','TRAFFICFLUX','COSZEN'" >> user_nl_clm_jj
        echo "hist_fincl3='FSA', 'FIRA', 'URBAN_HEAT', 'WASTEHEAT', 'EFLX_LH_TOT', 'FSH', 'FGR', 'URBAN_AC', 'RAIN', 'SNOW', 'QVEGT', 'QVEGE', 'QSOIL', 'QOVER', 'QH2OSFC', 'QDRAI', 'QDRAI_PERCH', 'SOILLIQ', 'SOILICE', 'H2OSNO', 'HIA','SWBGT','WBT', 'HUMIDEX', 'TWS', 'TRAFFICFLUX', 'TBUILD', 'COSZEN', 'ZWT', 'QFLX_EVAP_TOT', 'RH2M','TG','TSKIN','TBOT','FIRE','FLDS','FSDS','FSR','FGEV','TSOI','ERRSOI','SABV','SABG','FSDSVD','FSDSND','FSDSVI','FSDSNI','FSRVD','FSRND','FSRVI','FSRNI','TSA','FCTR','FCEV','QBOT','Q2M','H2OSOI','SWup','LWup','Rnet','Qh','Qle','Qstor','Qtau','Wind','Qair','Tair','PSurf','Rainf','SWdown','LWdown','SoilAlpha_U','TBUILD','TWS','TRAFFICFLUX','COSZEN'" >> user_nl_clm_jj
    fi

    cp user_nl_clm_jj user_nl_clm
    rm user_nl_clm_jj

    echo "fsurdat='${fsurdat}'" >> user_nl_clm

    # Set up the case
    ./case.build
fi

./xmlchange PTS_MODE=TRUE,PTS_LAT=${case_lat},PTS_LON=${case_lon}
./xmlchange RUN_STARTDATE=${RUN_STARTDATE}
./xmlchange STOP_OPTION='${STOP_OPTION}'
./xmlchange STOP_N=${case_length}
./xmlchange NTASKS=1
./xmlchange CLM_FORCE_COLDSTART=on
./preview_namelists
# Submit the case
./case.submit