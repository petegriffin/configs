#!/bin/bash

# Publish logs
test -d ${HOME}/bin || mkdir ${HOME}/bin
wget -q https://git.linaro.org/ci/publishing-api.git/blob_plain/HEAD:/linaro-cp.py -O ${HOME}/bin/linaro-cp.py
time python ${HOME}/bin/linaro-cp.py \
  --link-latest \
  logs/debian-source reference-platform/enterprise/components/openstack/kolla-logs/${BUILD_NUMBER}

echo "Images: https://hub.docker.com/u/linaro/"
echo "Logs:   https://snapshots.linaro.org/reference-platform/enterprise/components/openstack/kolla-logs/${BUILD_NUMBER}/"
