#!/bin/bash
#
# This script is meant for running tempest quickly on a Ubuntu machine
# Checkout Juniper tempest code; cd tempest ; Then, 
#
#   'curl -sSL https://raw.githubusercontent.com/Juniper/contrail-tools/testers/tempest/tempest_run.sh | sh'
# or:
#   'wget -qO- https://raw.githubusercontent.com/Juniper/contrail-tools/testers/tempest/tempest_run.sh | sh'
#
# By default, it assumes that openstack, contrail is running on local node
# Target node where Openstack/Contrail is setup can be any node(local/remote)
# If remote, set the below environment variables appropriately
set -x

export TEMPEST_WS=${TEMPEST_WS:-$(pwd)}
BUILD_STRING_FILE="build_id.txt"
export TEMPEST_DIR=$TEMPEST_WS
export KEYSTONE_SERVICE_HOST=${KEYSTONE_SERVICE_HOST:-127.0.0.1}

export PUBLIC_NETWORK_NAME=${PUBLIC_NETWORK_NAME:-public_net}
export PUBLIC_NETWORK_SUBNET=${PUBLIC_NETWORK_SUBNET:-10.1.1.0/24}
export PUBLIC_NETWORK_RI_FQ_NAME=${PUBLIC_NETWORK_RI_FQ_NAME:-"default-domain:admin:$PUBLIC_NETWORK_NAME:$PUBLIC_NETWORK_NAME"}
export PUBLIC_NETWORK_RT=${PUBLIC_NETWORK_RT:-10003}
export ROUTER_ASN=${ROUTER_ASN:-64512}
export PUBLIC_ACCESS_AVAILABLE=${PUBLIC_ACCESS_AVAILABLE:-0}

export HTTP_IMAGE_PATH=${HTTP_IMAGE_PATH:-http://10.204.216.50/images/cirros/cirros-0.3.1-x86_64-disk.img}
KEYSTONE_SERVICE_HOST_USER=${KEYSTONE_SERVICE_HOST_USER:-root}
KEYSTONE_SERVICE_HOST_PASSWORD=${KEYSTONE_SERVICE_HOST_PASSWORD:-c0ntrail123}
export TENANT_ISOLATION=${TENANT_ISOLATION:-true}

export API_SERVER_IP=${API_SERVER_IP:-127.0.0.1}
export API_SERVER_HOST_USER=${API_SERVER_HOST_USER:-root}
export API_SERVER_HOST_PASSWORD=${API_SERVER_HOST_PASSWORD:-c0ntrail123}
export OS_USERNAME=${OS_USERNAME:-admin}
export OS_PASSWORD=${OS_PASSWORD:-contrail123}
export OS_TENANT_NAME=${OS_TENANT_NAME:-admin}
export OS_AUTH_URL=http://${KEYSTONE_SERVICE_HOST}:5000/v2.0/
export OS_NO_CACHE=1
export SSHOPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

function get_api_server_distro () {
    /usr/bin/sshpass -p $API_SERVER_HOST_PASSWORD ssh $SSHOPT ${API_SERVER_HOST_USER}@${API_SERVER_IP} "
            if [ -f /etc/lsb-release ]; then (cat /etc/lsb-release | grep DISTRIB_DESCRIPTION | cut -d "=" -f2 )
            else
                cat /etc/redhat-release | sed s/\(Final\)//
            fi"

}

function command_exists() {
    command -v "$@" > /dev/null 2>&1
}

#Get current Contrail Build version from the node 

if ! command_exists sshpass 
then
    apt-get -y install sshpass
fi

build_string_cmd="contrail-version |grep contrail-install |head -1| awk '{print \$2}'"
CONTRAIL_BUILD_STRING=`/usr/bin/sshpass -p $KEYSTONE_SERVICE_HOST_PASSWORD ssh $SSHOPT -t ${KEYSTONE_SERVICE_HOST_USER}@${KEYSTONE_SERVICE_HOST} "$build_string_cmd" 2>/dev/null` || echo "Unable to detect Build Id"

rm -f ${BUILD_STRING_FILE}
echo "Build string is $CONTRAIL_BUILD_STRING"
export CONTRAIL_BUILD_STRING

# API SERVER DISTRO
api_server_distro=`get_api_server_distro` 
echo $api_server_distro $CONTRAIL_BUILD_STRING > ${BUILD_STRING_FILE}

function report_gen {
    TEST_CONFIG_FILE="sanity_params.ini"
    REPORT_INI_FILE="tempest_report.ini"
    TMP_REPORT_FILE="report/junit-noframes.html"
    REPORT_FILE="report/tempest_report.html"
    cd /contrail-test
    export PYTHONPATH=$PYTHONPATH:$PWD/scripts:$PWD/fixtures:$PWD
    python tools/report_gen.py $TEST_CONFIG_FILE $REPORT_INI_FILE
    python tools/update_testsuite_properties.py $REPORT_INI_FILE $RESULT_XML
    cp $RESULT_XML ./result.xml
    ant || die "ant job failed!"
    cp $TMP_REPORT_FILE $REPORT_FILE
    cp $TEMPEST_DIR/*.log ./logs/
    python tools/upload_to_webserver.py $TEST_CONFIG_FILE $REPORT_INI_FILE $REPORT_FILE
    sleep 2
    if [ -f $REPORT_FILE ]; then
        export EMAIL_SUBJECT="Tempest Report"
        python tools/send_mail.py $TEST_CONFIG_FILE $REPORT_FILE $REPORT_INI_FILE
    fi
    cd -
}

RESULT_XML=$TEMPEST_DIR/result.xml
cd $TEMPEST_DIR
bash -x $TEMPEST_DIR/run_contrail_tempest.sh -p -V -r $RESULT_XML
report_gen
retval=$?
exit $retval
