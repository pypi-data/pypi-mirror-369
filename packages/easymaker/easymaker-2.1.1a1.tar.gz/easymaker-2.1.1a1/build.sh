#!/bin/bash

USE_SELINUX=${USE_SELINUX:-true}

if [ "$USE_SELINUX" = "true" ]; then
    docker build --build-arg MOUNT_OPTIONS=",bind-propagation=rshared,z" -t easymaker-sdk:latest .
else
    docker build --build-arg MOUNT_OPTIONS="" -t easymaker-sdk:latest .
fi
