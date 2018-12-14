#!/bin/sh
#
# Copyright 2018 RackTop Systems Inc. and/or its affiliates.
# http://www.racktopsystems.com
#
# The contents of this file are subject to the terms of the RackTop Commercial
# License ("RTCL"). You may not use, redistribute, or modify this file in source
# or binary forms except in compliance with the RTCL. You can obtain a copy at
# http://racktopsystems.com/legal/rtcl.txt.

services=(
    "datareplicationd"
    "dataprotectiond"
    "secured"
)

for s in "${services[@]}"; do
    svcadm enable "$s"
done
