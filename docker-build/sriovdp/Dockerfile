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

ARG SRIOVDP
ENV SRIOVDP_VERSION=$SRIOVDP
ENV GOPATH /go
ARG go_install_dir="/usr/local/go"
ARG go_version
ENV PATH $GOPATH/bin:$go_install_dir/bin:/usr/local/go/bin:$PATH
ENV GOOS=linux

WORKDIR /

RUN apk add --no-cache jq \
&& apk add --no-cache --virtual .tools ca-certificates gcc musl-dev go glide git bash curl tar \
&& mkdir -p $go_install_dir \
&& curl -fsSL -k https://dl.google.com/go/go${go_version}.src.tar.gz | tar zx --strip-components=1 -C ${go_install_dir} \
&& cd ${go_install_dir}/src/ \
&& ./make.bash \
&& mkdir -p $GOPATH/src/github.com/intel \
&& git clone https://github.com/intel/sriov-network-device-plugin.git $GOPATH/src/github.com/intel/sriov-network-device-plugin --branch=v${SRIOVDP_VERSION} \
&& cd $GOPATH/src/github.com/intel/sriov-network-device-plugin \
&& glide --quiet install -v \
&& go install -a -ldflags '-extldflags "-static"' github.com/intel/sriov-network-device-plugin/cmd/sriovdp \
&& cp $GOPATH/bin/sriovdp /usr/local/bin/sriovdp \
&& rm -rf $GOPATH/src \
&& rm -rf $GOPATH/bin \
&& apk del .tools \
&& rm -rf $go_install_dir \
&& rm -rf /var/cache/apk/* \
&& rm -rf /var/lib/apt/lists/* \
&& rm -rf /tmp/* \
&& rm -rf ~/.glide

RUN chmod 700 /usr/local/bin/sriovdp

LABEL io.k8s.display-name="SRIOV Network Device Plugin"
ENTRYPOINT ["/usr/local/bin/sriovdp"]
