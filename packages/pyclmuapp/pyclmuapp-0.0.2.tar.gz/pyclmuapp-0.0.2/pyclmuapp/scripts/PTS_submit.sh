#!/bin/bash

# Junjie Yu, 2023-11-24, Manchester, UK
# This script is used to create a CESM case with the PTS mode on.

export USER=root
source ~/.bashrc

cd ${CASESCRIPT} # scripts folder
CASE=/p/scripts/${case_name}

if [ -d ${CASE} ]; then
    cd ${CASE}

    ./xmlchange PTS_MODE=TRUE,PTS_LAT=${case_lat},PTS_LON=${case_lon}
    ./xmlchange RUN_STARTDATE=${RUN_STARTDATE}
    ./xmlchange STOP_OPTION='${STOP_OPTION}'
    ./xmlchange STOP_N=${case_length}
    ./xmlchange DATM_CLMNCEP_YR_START=${DATM_CLMNCEP_YR_START}
    ./xmlchange DATM_CLMNCEP_YR_END=${DATM_CLMNCEP_YR_END}
    ./xmlchange NTASKS=1
    ./xmlchange CLM_FORCE_COLDSTART=on
    ./preview_namelists
    # Submit the case
    ./case.submit

else
    echo "The case folder [${CASE}] does not exist. Please create the case first."
fi