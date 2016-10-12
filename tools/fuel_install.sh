#!/bin/bash

"""
This script is to make the environment ready in Python virtual
environment to execute the mirantis scripts
for deploying the cluster using the contrail-fuel-plugin.
This script will install the required packages, pull the required repos and
launch the automation script to deploy the cluster.
"""

set -ex

sudo apt-get install --yes \
git \
libyaml-dev \
libffi-dev \
python-dev \
python-pip \
qemu \
qemu-utils \
libvirt-bin \
libvirt-dev \
vlan \
bridge-utils \
ebtables \
pm-utils \
genisoimage \
libsqlite3-0 \
python-virtualenv \
libgmp-dev \
pkg-config

export WORKING_DIR=$HOME/test$( date +%M-%H-%d-%m-%Y )
mkdir -p ${WORKING_DIR}

cd $WORKING_DIR
sudo apt-get install --yes python-virtualenv
virtualenv --no-site-packages fuel-devops-venv
. fuel-devops-venv/bin/activate


export DEVOPS_DB_NAME=$WORKING_DIR/fuel-devops.sqlite
export DEVOPS_DB_ENGINE="django.db.backends.sqlite3"


git clone https://github.com/openstack/fuel-qa

#. $WORKING_DIR/fuel-devops-venv/bin/activate
pip install -r $WORKING_DIR/fuel-qa/fuelweb_test/requirements.txt --upgrade

#cd ../
#git clone https://github.com/ehles/fuel_manage_env.git
git clone https://github.com/stnaik/fuel_manage_env.git
git clone https://github.com/openstack/fuel-devops.git

cd fuel_manage_env/
export CLUSTER_CONFIG=random_lab_config.yaml
export PYTHONPATH=$PYTHONPATH:$WORKING_DIR/fuel-qa
export PYTHONPATH=$PYTHONPATH:$WORKING_DIR/fuel-devops


pip install ipdb
pip install python-dateutil
pip install cryptography
apt-get install libssl-dev
pip install cryptography
pip install django
pip install jsonfield
pip install babel
pip install imagesize
pip install pbr
pip install positional
pip install iso8601
pip install debtcollector
pip install stevedore
pip install oslo.config
pip install oslo.concurrency
pip install oslo.serialization

export CLUSTER_CONFIG=$WORKING_DIR/fuel_manage_env/conf_samples/conf_auto_contrail.yaml
python $WORKING_DIR/fuel_manage_env/manage_env.py



