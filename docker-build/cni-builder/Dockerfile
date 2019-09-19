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

FROM centos:7
MAINTAINER Krisztian Lengyel <krisztian.lengyel@nokia.com>

ARG SRIOV_VERSION
ARG go_version
ARG binaries
ENV GOPATH /go
ARG go_install_dir="/usr/local/go"
ARG glide_install_dir="/usr/local/glide"
ENV PATH="$GOPATH/bin:$go_install_dir/bin:$glide_install_dir:$PATH"
ENV CGO_ENABLED=0
ENV GOOS=linux
ARG build_packages="gcc gcc-c++ glibc-devel make autoconf git which libtool curl"

WORKDIR /

RUN mkdir -p $GOPATH/bin \
&&  mkdir -p $GOPATH/src

RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
&&  yum install -y --setopt=skip_missing_names_on_install=False \
      ${build_packages} \
      ${danm_dependencies} \
      bash \
      golang \
&&    set -x \
&&  mkdir -p ${go_install_dir} \
&&  curl -fsSL -k https://dl.google.com/go/go${go_version}.linux-arm64.tar.gz | tar zx --strip-components=1 -C ${go_install_dir} \
&&  glide_version="$(curl -sSLf https://glide.sh/version)" \
&&  mkdir -p ${glide_install_dir} \
&&  curl -fsSL https://github.com/Masterminds/glide/releases/download/${glide_version}/glide-${glide_version}-linux-arm64.tar.gz | tar zx --strip-components=1 -C ${glide_install_dir} \
&&  mkdir -p ${binaries} \
#
# Get Flannel
#
&&  go get -v github.com/containernetworking/plugins/plugins/meta/flannel \
&&  cp ${GOPATH}/bin/flannel ${binaries} \
#
# Build sriov-cni
#
&&  mkdir -p ${GOPATH}/src/github.com/intel/ \
&&  cd ${GOPATH}/src/github.com/intel/ \
&&  git clone https://github.com/intel/sriov-cni.git \
&&  cd ${GOPATH}/src/github.com/intel/sriov-cni \
&&  git checkout ${SRIOV_VERSION} \
&&  make \
&&  cp $GOPATH/src/github.com/intel/sriov-cni/build/sriov ${binaries}
