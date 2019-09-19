# Copyright 2019 Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM alpine:3.9
MAINTAINER Levente Kale <levente.kale@nokia.com>

ARG danm_binaries="netwatcher svcwatcher webhook"

COPY danm_binaries/ /usr/local/bin/

WORKDIR /

RUN apk add --no-cache curl libcap iputils

RUN set -x \
&&  env \
&&  adduser -u 147 -D -H -s /sbin/nologin danm \
&&  for component in $danm_binaries; do \
      chown root:danm /usr/local/bin/${component}; \
      chmod 750 /usr/local/bin/${component}; \
    done \
&&  rm -rf /var/cache/apk/* \
&&  rm -rf /var/lib/apt/lists/* \
&&  rm -rf /tmp/* \
&&  setcap cap_sys_ptrace,cap_sys_admin,cap_net_admin=eip /usr/local/bin/netwatcher \
&&  setcap cap_net_raw=eip /usr/sbin/arping

USER danm
