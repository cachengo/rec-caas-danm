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

ARG SRIOV
ENV SRIOV_VERSION=$SRIOV
ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH
ENV GOOS=linux

WORKDIR /

RUN apk add --no-cache --virtual .tools ca-certificates gcc musl-dev go glide git \
&& mkdir -p $GOPATH/src/github.com/intel \
&& git clone https://github.com/intel/sriov-network-device-plugin.git $GOPATH/src/github.com/intel/sriov-network-device-plugin --branch=v${SRIOV_VERSION} \
&& cd $GOPATH/src/github.com/intel/sriov-network-device-plugin \
&& glide --quiet install -v \
&& go install -a -ldflags '-extldflags "-static"' github.com/intel/sriov-network-device-plugin/cmd/sriovdp \
&& cp $GOPATH/bin/sriovdp /usr/local/bin/sriovdp \
&& rm -rf $GOPATH/src \
&& rm -rf $GOPATH/bin \
&& apk del .tools \
&& rm -rf /var/cache/apk/* \
&& rm -rf /var/lib/apt/lists/* \
&& rm -rf /tmp/* \
&& rm -rf ~/.glide

RUN chmod 700 /usr/local/bin/sriovdp 

LABEL io.k8s.display-name="SRIOV Network Device Plugin"
ENTRYPOINT ["/usr/local/bin/sriovdp"]
