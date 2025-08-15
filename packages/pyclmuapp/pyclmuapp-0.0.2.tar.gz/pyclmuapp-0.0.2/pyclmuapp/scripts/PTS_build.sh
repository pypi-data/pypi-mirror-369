#!/bin/bash

# Junjie Yu, 2023-11-24, Manchester, UK
# This script is used to create a CESM case with the PTS mode on.

export USER=root
source ~/.bashrc

cd ${CASESCRIPT} # scripts folder

CASE=/p/scripts/${case_name}

if [ -d ${CASE} ]; then
    cd ${CASE}
else
    ./create_newcase --case ${CASE} --res ${resolution} --compset ${compset} --run-unsupported
    cd ${CASE}

    ./xmlchange NTASKS=1
    ./xmlchange CLM_FORCE_COLDSTART=on

    # Set up the case
    ./case.setup
    ./case.build
fi