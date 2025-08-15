#!/bin/bash

# Junjie Yu, 2023-11-24, Manchester, UK
# This script is used to create a CESM case with the PTS mode on.

export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
export OMPI_ALLOW_RUN_AS_ROOT=1
export CASESRPITS=/p/project/clm5.0/cime/scripts 
export USER=root 
export PROJECT=/p/project
export SCRATCH=/p/scratch 
export CESMDATAROOT=/p/scratch/CESMDATAROOT 
export CSMDATA=/p/scratch/CESMDATAROOT/inputdata 
export CASESCRIPT=/p/project/clm5.0/cime/scripts
source ~/.bashrc

cd ${CASESCRIPT} # scripts folder




usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --case_name <case_name>  The name of the case"
    echo "  --RUN_STARTDATE <RUN_STARTDATE>  The start date of the run"
    echo "  --STOP_OPTION <STOP_OPTION>  The stop option"
    echo "  --STOP_N <STOP_N>  The stop number"
    echo "  --DATM_CLMNCEP_YR_START <DATM_CLMNCEP_YR_START>  The start year of the forcing data"
    echo "  --DATM_CLMNCEP_YR_END <DATM_CLMNCEP_YR_END>  The end year of the forcing data"
    echo "  --case_lat <case_lat>  The latitude of the single point"
    echo "  --case_lon <case_lon>  The longitude of the single point"
    echo "  --hist_avgflag_pertape <hist_avgflag_pertape>  The average flag per tape"
    echo "  --hist_nhtfrq <hist_nhtfrq>  The history file frequency"
    echo "  --hist_mfilt <hist_mfilt>  The history file filter"
    echo "  --output_murban <output_murban>  The output flag for murban"
    echo "  --mu_urban <mu_urban>  The murban variable"
    echo "  --fsurdat <fsurdat>  The surface dataset"
    echo "  --case_length <case_length>  The length of the case"
    exit 1

}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --case_name)
            case_name=$2
            shift 2
            ;;
        --RUN_STARTDATE)
            RUN_STARTDATE=$2
            shift 2
            ;;
        --STOP_OPTION)
            STOP_OPTION=$2
            shift 2
            ;;
        --STOP_N)
            STOP_N=$2
            shift 2
            ;;
        --DATM_CLMNCEP_YR_START)
            DATM_CLMNCEP_YR_START=$2
            shift 2
            ;;
        --DATM_CLMNCEP_YR_END)
            DATM_CLMNCEP_YR_END=$2
            shift 2
            ;;
        --case_lat)
            case_lat=$2
            shift 2
            ;;
        --case_lon)
            case_lon=$2
            shift 2
            ;;
        --hist_avgflag_pertape)
            hist_avgflag_pertape=$2
            shift 2
            ;;
        --hist_nhtfrq)
            hist_nhtfrq=$2
            shift 2
            ;;
        --hist_mfilt)   
            hist_mfilt=$2
            shift 2
            ;;
        --output_murban)
            output_murban=$2
            shift 2
            ;;
        --mu_urban)
            mu_urban=$2
            shift 2
            ;;
        --fsurdat)
            fsurdat=$2
            shift 2
            ;;
        --case_length)
            case_length=$2
            shift 2
            ;;
        *)
            usage
            ;;
    esac
done

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

cd ..
if [ -d ${CASE} ]; then
    cd ${CASE}

    ./xmlchange PTS_MODE=TRUE,PTS_LAT=${case_lat},PTS_LON=${case_lon}
    ./xmlchange RUN_STARTDATE=${RUN_STARTDATE}
    ./xmlchange DATM_CLMNCEP_YR_START=${DATM_CLMNCEP_YR_START}
    ./xmlchange DATM_CLMNCEP_YR_END=${DATM_CLMNCEP_YR_END}
    ./xmlchange STOP_OPTION='${STOP_OPTION}'
    ./xmlchange STOP_N=${case_length}
    ./xmlchange NTASKS=1
    ./xmlchange CLM_FORCE_COLDSTART=on

    # Modify the user_nl_clm file
    echo "hist_avgflag_pertape='${hist_avgflag_pertape}'" >> user_nl_clm
    echo "hist_nhtfrq=${hist_nhtfrq}" >> user_nl_clm
    echo "hist_mfilt=${hist_mfilt}" >> user_nl_clm

    if [ "${output_murban}" = "True" ]; then
        echo "hist_empty_htapes = .true." >> user_nl_clm
        echo "hist_fincl1=${mu_urban}" >> user_nl_clm
        echo "hist_dov2xy=.false." >> user_nl_clm
        echo "hist_type1d_pertape='LAND'" >> user_nl_clm
    fi

    if [ "${output_murban}" = "False" ]; then
        echo "hist_fincl1=${mu_urban}" >> user_nl_clm
    fi

    echo "fsurdat='${fsurdat}'" >> user_nl_clm

    ./preview_namelists

else
    echo "The case folder [${CASE}] does not exist. Please create the case first."
fi

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