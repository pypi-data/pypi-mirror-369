#! /bin/bash
# This script is used to create a new case with a user-defined dataset
# Junjie YU, 2024-03-13, Manchester

# --------------------------------Input of ENV variables--------------------------------
# ! note:  export the path of plumber and the input data beafore running this scripts
# export plumber=/p/scratch/CESMDATAROOT/inputdata/Urban-PLUMBER
# export CASESRPITS=/p/project/clm5.0/cime/scripts
# platform: UoM csf3; Linux; MacOS.
# * How to use? bash plumber.sh -h for help

# --------------------------------ENV--------------------------------
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
export OMPI_ALLOW_RUN_AS_ROOT=1
export CASESRPITS=/p/project/clm5.0/cime/scripts 
export USER=root 
export PROJECT=/p/project
export SCRATCH=/p/scratch 
export CESMDATAROOT=/p/scratch/CESMDATAROOT 
export CSMDATA=/p/scratch/CESMDATAROOT/inputdata 
export CASESCRIPT=/p/project/clm5.0/cime/scripts
usage() {
    echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --ATMDOM_FILE <ATMDOM_FILE>  The domain file of the atmosphere"
      echo "  --SURF <SURF>  The surface dataset"
      echo "  --FORCING_FILE <FORCING_FILE>  The forcing file"
      echo "  --case_name <case_name>  The name of the case"
      echo "  --RUN_STARTDATE <RUN_STARTDATE>  The start date of the run"
      echo "  --STOP_OPTION <STOP_OPTION>  The stop option"
      echo "  --STOP_N <STOP_N>  The stop number"
      echo "  --CLIMATE_VAR <CLIMATE_VAR>  The climate variable"
      echo "  --START <START>  The start year"
      echo "  --END <END>  The end year"
      exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
         --ATMDOM_FILE)
            ATMDOM_FILE=$2
            shift 2
            ;;
         --SURF)
            SURF=$2
            shift 2
            ;;
         --FORCING_FILE)
            FORCING_FILE=$2
            shift 2
            ;;
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
         --CLIMATE_VAR)
            CLIMATE_VAR=$2
            shift 2
            ;;
         --START)
            START=$2
            shift 2
            ;;
         --END)
            END=$2
            shift 2
            ;;
         --RUN_TYPE)
            RUN_TYPE=$2
            shift 2
            ;;
         --RUN_REFCASE)
            RUN_REFCASE=$2
            shift 2
            ;;
         --RUN_REFDATE)
            RUN_REFDATE=$2
            shift 2
            ;;
        *)
            usage
            ;;
    esac
done


# Set the environment variables
# --------------------------------Input--------------------------------
export ctsm_input=/p/scratch/CESMDATAROOT/inputdata
export ATMDOM_PATH=${ctsm_input}/usp
#export ATMDOM_FILE=domain.lnd.domain.lnd.1x1_${GRIDNAME}_noocean.nc_domain.ocn_noocean.nc.210525.nc
export FORCING_PATH=${ctsm_input}/usp
export SURF=${ctsm_input}/usp/${SURF}
#export FORCING_FILE=CTSM_DATM_${GRIDNAME}_${FORCING_DATE}.nc
# --------------------------------Input--------------------------------

# --------------------------------Setting--------------------------------
# Create a new case
cd ${CASESRPITS}
if [ -d ${case_name} ]; then
   echo "The case ${case_name} already exists."
   cd ${case_name}
else
   ./create_newcase --case ${case_name} --res CLM_USRDAT --compset 2000_DATM%1PT_CLM50%SP_SICE_SOCN_SROF_SGLC_SWAV --run-unsupported
   cd ${case_name}
   echo "domainfile='$ATMDOM_PATH/$ATMDOM_FILE'" >> user_nl_datm
   #echo "fatmlndfrc='$ATMDOM_PATH/$ATMDOM_FILE'" >> user_nl_clm
   echo "fsurdat='$SURF'" >> user_nl_clm
   echo "hist_avgflag_pertape='A'" >> user_nl_clm
   echo "hist_nhtfrq=1" >> user_nl_clm
   echo "hist_mfilt=1000000" >> user_nl_clm
   #echo "hist_empty_htapes = .true." >> user_nl_clm
   variables=$CLIMATE_VAR
   formatted_variables=$(echo $variables | sed "s/\([^,]\+\)/'\1'/g")
   echo $formatted_variables
   echo "hist_fincl1=$formatted_variables" >> user_nl_clm
   #echo "hist_fincl1=$CLIMATE_VAR" >> user_nl_clm
   #echo "hist_dov2xy=.false." >> user_nl_clm
   #echo "hist_type1d_pertape='LAND'" >> user_nl_clm
   cp ${ctsm_input}/usp/SourceMods/src.clm/* ${case_name}/SourceMods/src.clm/


   ./xmlchange DATM_MODE=CLM1PT



   # Set up the case
   ./xmlchange NTASKS=1
   ./xmlchange CALENDAR=GREGORIAN # or NOLEAP
   #./xmlchange CLM_USRDAT_NAME=${GRIDNAME}
   ./xmlchange LND_DOMAIN_FILE=${ATMDOM_FILE}
   ./xmlchange LND_DOMAIN_PATH=${ATMDOM_PATH}
   ./xmlchange ATM_DOMAIN_FILE=${ATMDOM_FILE}
   ./xmlchange ATM_DOMAIN_PATH=${ATMDOM_PATH}
   ./xmlchange DATM_CLMNCEP_YR_START=${START}
   ./xmlchange DATM_CLMNCEP_YR_END=${END}
   ./xmlchange DATM_CLMNCEP_YR_ALIGN=${START}
   #./xmlchange DIN_LOC_ROOT_CLMFORC=${FORCING}
   ./case.setup
   ./case.build

fi

#./preview_namelists
# Modify the DATA namelist
# ref: https://www2.cesm.ucar.edu/models/cesm1.2/data8/doc/x310.html

new_text="fsurdat='${SURF}'"
echo ${new_text}
sed -i "1s|.*|${new_text}|" user_nl_clm
variables=$CLIMATE_VAR
formatted_variables=$(echo $variables | sed "s/\([^,]\+\)/'\1'/g")
echo $formatted_variables
echo "hist_fincl1=$formatted_variables" >> user_nl_clm

./xmlchange LND_DOMAIN_FILE=${ATMDOM_FILE}
./xmlchange LND_DOMAIN_PATH=${ATMDOM_PATH}
./xmlchange ATM_DOMAIN_FILE=${ATMDOM_FILE}
./xmlchange ATM_DOMAIN_PATH=${ATMDOM_PATH}
#./xmlchange DATM_CLMNCEP_YR_START=${START}
#./xmlchange DATM_CLMNCEP_YR_END=${START}
#./xmlchange DATM_CLMNCEP_YR_ALIGN=${START}

cat <<EOF > user_datm.streams.txt.CLM1PT.CLM_USRDAT
<?xml version="1.0"?>
<file id="stream" version="1.0">
<dataSource>
   GENERIC
</dataSource>
<domainInfo>
  <variableNames>
     time    time
        xc      lon
        yc      lat
        area    area
        mask    mask
  </variableNames>
  <filePath>
     $ATMDOM_PATH
  </filePath>
  <fileNames>
     $ATMDOM_FILE
  </fileNames>
</domainInfo>
<fieldInfo>
   <variableNames>
     Zbot     z
        Prectmms precn
        Wind     wind
        LWdown   lwdn
        PSurf    pbot
        Qair     shum
        Tair     tbot
        SWdown   swdn
   </variableNames>
   <filePath>
    $FORCING_PATH
   </filePath>
   <fileNames>
    $FORCING_FILE
   </fileNames>
   <offset>
      0
   </offset>
</fieldInfo>
</file>
EOF

# Modify the DATM namelist

./xmlchange RUN_STARTDATE=${RUN_STARTDATE}
./xmlchange STOP_OPTION=${STOP_OPTION}
./xmlchange STOP_N=${STOP_N}

echo "RUN_TYPE=${RUN_TYPE}"
if [ "${RUN_TYPE}" = "coldstart" ];
then
   echo "--------------coldstart-----------------"
    ./xmlchange CLM_FORCE_COLDSTART=on
fi

if [ "${RUN_TYPE}" = "branch" ];
then
   # Set up the case of restart
   echo "----------------branch-----------------"
   #export RUN_REFDIR=/p/scratch/CESMDATAROOT/CaseOutputs/${RUN_REFCASE}/run
   export RUN_REFDIR=/p/scratch/CESMDATAROOT/Archive/rest/${RUN_REFDATE}-00000
   ./xmlchange RUN_TYPE=branch
   ./xmlchange RUN_REFDIR=${RUN_REFDIR}
   ./xmlchange RUN_REFDATE=${RUN_REFDATE}
   ./xmlchange RUN_REFTOD=00000
   ./xmlchange GET_REFCASE=TRUE
   ./xmlchange RUN_REFCASE=${RUN_REFCASE}
fi

./preview_namelists

./case.submit