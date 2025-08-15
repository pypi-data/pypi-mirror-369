#scripts_cmd = {
#    "pts": """export CASESRPITS=/p/project/clm5.0/cime/scripts && \
#export USER=root && \
#export PROJECT=/p/project && \
#export SCRATCH=/p/scratch && \
#export CESMDATAROOT=/p/scratch/CESMDATAROOT && \
#export CSMDATA=/p/scratch/CESMDATAROOT/inputdata && \
#export CASESCRIPT=/p/project/clm5.0/cime/scripts && \
#export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 && \
#export OMPI_ALLOW_RUN_AS_ROOT=1 && \
#bash /p/scripts/pts.sh --case_name {case_name} \
#--RUN_STARTDATE '{RUN_STARTDATE}' \
#--STOP_OPTION {STOP_OPTION} --STOP_N {STOP_N} \
#--DATM_CLMNCEP_YR_START {DATM_CLMNCEP_YR_START} \
#--DATM_CLMNCEP_YR_END {DATM_CLMNCEP_YR_END} \
#--case_lat {case_lat} --case_lon {case_lon} \
#--hist_avgflag_pertape {hist_avgflag_pertape} \
#--hist_nhtfrq {hist_nhtfrq} --hist_mfilt {hist_mfilt} \
#--output_murban {output_murban} --mu_urban {mu_urban} \
#--fsurdat {fsurdat} --case_length {case_length}
#""",
#    "usp": """export CASESRPITS=/p/project/clm5.0/cime/scripts && \
#export USER=root && \
#export PROJECT=/p/project && \
#export SCRATCH=/p/scratch && \
#export CESMDATAROOT=/p/scratch/CESMDATAROOT && \
#export CSMDATA=/p/scratch/CESMDATAROOT/inputdata && \
#export CASESCRIPT=/p/project/clm5.0/cime/scripts && \
#export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 && \
#export OMPI_ALLOW_RUN_AS_ROOT=1 && \
#cd $CSMDATA && \
#bash /p/clmuapp/usp/usp.sh --ATMDOM_FILE {ATMDOM_FILE} \
#--SURF '{SURF}' \
#--FORCING_FILE '{FORCING_FILE}' \
#--case_name {case_name} \
#--RUN_STARTDATE '{RUN_STARTDATE}' --START_TOD '{START_TOD}' \
#--hist_type '{hist_type}' --hist_nhtfrq {hist_nhtfrq} --hist_mfilt {hist_mfilt} \
#--STOP_OPTION {STOP_OPTION} --STOP_N {STOP_N} --START {START} --END {END} \
#--RUN_TYPE {RUN_TYPE} --RUN_REFCASE '{RUN_REFCASE}' --RUN_REFDATE '{RUN_REFDATE}' \
#--RUN_REFTOD '{RUN_REFTOD}' --urban_hac '{urban_hac}' \
#""",
#    "singularity": "{input_path}:/p/clmuapp {output_path}:/p/scratch/CESMDATAROOT/Archive/lnd/hist {log_path}:/p/scratch/CESMDATAROOT/CaseOutputs {scripts_path}:/p/scripts "
#
#}
#make this to oneline so that it can be easily used by windows
scripts_cmd = {
    "pts": "export CASESRPITS=/p/project/clm5.0/cime/scripts && export USER=root && export PROJECT=/p/project && export SCRATCH=/p/scratch && export CESMDATAROOT=/p/scratch/CESMDATAROOT && export CSMDATA=/p/scratch/CESMDATAROOT/inputdata && export CASESCRIPT=/p/project/clm5.0/cime/scripts && export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 && export OMPI_ALLOW_RUN_AS_ROOT=1 && bash /p/scripts/pts.sh --case_name {case_name} --RUN_STARTDATE '{RUN_STARTDATE}' --STOP_OPTION {STOP_OPTION} --STOP_N {STOP_N} --DATM_CLMNCEP_YR_START {DATM_CLMNCEP_YR_START} --DATM_CLMNCEP_YR_END {DATM_CLMNCEP_YR_END} --case_lat {case_lat} --case_lon {case_lon} --hist_avgflag_pertape {hist_avgflag_pertape} --hist_nhtfrq {hist_nhtfrq} --hist_mfilt {hist_mfilt} --output_murban {output_murban} --mu_urban {mu_urban} --fsurdat {fsurdat} --case_length {case_length}",
    "usp": "export CASESRPITS=/p/project/clm5.0/cime/scripts && export USER=root && export PROJECT=/p/project && export SCRATCH=/p/scratch && export CESMDATAROOT=/p/scratch/CESMDATAROOT && export CSMDATA=/p/scratch/CESMDATAROOT/inputdata && export CASESCRIPT=/p/project/clm5.0/cime/scripts && export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 && export OMPI_ALLOW_RUN_AS_ROOT=1 && cd $CSMDATA && bash /p/clmuapp/usp/usp.sh --ATMDOM_FILE {ATMDOM_FILE} --SURF '{SURF}' --FORCING_FILE '{FORCING_FILE}' --case_name {case_name} --RUN_STARTDATE '{RUN_STARTDATE}' --START_TOD '{START_TOD}' --hist_type '{hist_type}' --hist_nhtfrq {hist_nhtfrq} --hist_mfilt {hist_mfilt} --STOP_OPTION {STOP_OPTION} --STOP_N {STOP_N} --START {START} --END {END} --RUN_TYPE {RUN_TYPE} --RUN_REFCASE '{RUN_REFCASE}' --RUN_REFDATE '{RUN_REFDATE}' --RUN_REFTOD '{RUN_REFTOD}' --urban_hac '{urban_hac}' ",
    "singularity": "{input_path}:/p/clmuapp {output_path}:/p/scratch/CESMDATAROOT/Archive/lnd/hist {log_path}:/p/scratch/CESMDATAROOT/CaseOutputs {scripts_path}:/p/scripts "

}