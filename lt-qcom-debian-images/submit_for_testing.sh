#!/bin/bash

rm -rf configs
git clone --depth 1 http://git.linaro.org/ci/job/configs.git

# main parameters
export DEPLOY_OS=debian
export OS_INFO=debian-${OS_FLAVOUR}
export BOOT_OS_PROMPT=\'root@linaro-alip:~#\'

# boot and rootfs parameters
export BOOT_URL=${PUBLISH_SERVER}${PUB_DEST}/boot-${VENDOR}-${OS_FLAVOUR}-${PLATFORM_NAME}-${BUILD_NUMBER}.img.gz
export BOOT_URL_COMP="gz"
export LXC_BOOT_FILE=$(basename ${BOOT_URL} .gz)
export ROOTFS_URL=${PUBLISH_SERVER}${PUB_DEST}/${VENDOR}-${OS_FLAVOUR}-alip-${PLATFORM_NAME}-${BUILD_NUMBER}.img.gz
export ROOTFS_URL_COMP="gz"
export LXC_ROOTFS_FILE=$(basename ${ROOTFS_URL} .gz)

# XXX: the debian rootfs images are build small as possible, resize
# to be able install LAVA test overlay
export RESIZE_ROOTFS=True

# Install jinja2-cli and ruamel.yaml, required by submit_for_testing.py
pip install --user --force-reinstall jinja2-cli ruamel.yaml

python configs/openembedded-lkft/submit_for_testing.py \
    --device-type ${DEVICE_TYPE} \
    --build-number ${BUILD_NUMBER} \
    --lava-server ${LAVA_SERVER} \
    --qa-server ${QA_SERVER} \
    --qa-server-team qcomlt \
    --qa-server-project ${OS_INFO} \
    --git-commit ${BUILD_NUMBER} \
    --template-path configs/lt-qcom/lava-job-definitions \
    --template-base-pre base_template.yaml \
    --template-names template.yaml template-wifi.yaml template-bt.yaml
