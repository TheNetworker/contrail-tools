#!/usr/bin/env bash

TOOLS_WS=${TOOLS_WS:-$(pwd)}
source $TOOLS_WS/testers/utils
source $TOOLS_WS/testers/smlite_utils
# AVAILABLE_TESTBEDS is a comma separated list of testbed filenames or paths
testbeds=(${AVAILABLE_TESTBEDS//,/ })
echo "AVAILABLE TESTBEDS : ${testbeds[@]}"

get_testbed
create_testbed
initialize_any_vms
run_smgr_task
unlock_testbed $TBFILE_NAME
