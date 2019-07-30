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

FROM centos:7.6.1810
MAINTAINER Krisztian Lengyel <krisztian.lengyel@nokia.com>

ARG DANM_VERSION
ARG components="danm fakeipam"
ARG go_version
ARG binaries
ENV GOPATH /go
ARG go_install_dir="/usr/local/go"
ARG glide_install_dir="/usr/local/glide"
ENV PATH $GOPATH/bin:$go_install_dir/bin:$glide_install_dir:$PATH
ENV CGO_ENABLED=0
ENV GOOS=linux
ARG code_generator_version="kubernetes-1.13.4"
ARG build_packages="gcc gcc-c++ glibc-devel make autoconf git which libtool"
ARG danm_dependencies="iptables socat grep findutils curl conntrack-tools iputils"

WORKDIR /

RUN mkdir -p $GOPATH/bin \
&&  mkdir -p $GOPATH/src

RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
&&  yum install -y --setopt=skip_missing_names_on_install=False \
      ${build_packages} \
      ${danm_dependencies} \
      bash \
      golang \
&&  set -x \
&&  mkdir -p ${go_install_dir} \
&&  curl -fsSL -k https://dl.google.com/go/go${go_version}.linux-amd64.tar.gz | tar zx --strip-components=1 -C ${go_install_dir} \
&&  glide_version="$(curl -sSLf https://glide.sh/version)" \
&&  mkdir -p ${glide_install_dir} \
&&  curl -fsSL https://github.com/Masterminds/glide/releases/download/${glide_version}/glide-${glide_version}-linux-amd64.tar.gz | tar zx --strip-components=1 -C ${glide_install_dir} \
&&  mkdir -p $GOPATH/src/github.com/nokia \
&&  git clone https://github.com/nokia/danm.git $GOPATH/src/github.com/nokia/danm \
&&  cd $GOPATH/src/github.com/nokia/danm \
&&  git fetch --tags \
&&  git checkout ${DANM_VERSION} \
&&  glide install --strip-vendor \
&&  go get -d github.com/vishvananda/netlink \
&&  go get github.com/containernetworking/plugins/pkg/ns \
&&  go get github.com/golang/groupcache/lru \
&&  rm -rf $GOPATH/src/k8s.io/code-generator \
&&  git clone -b ${code_generator_version} --depth 1 https://github.com/kubernetes/code-generator.git $GOPATH/src/k8s.io/code-generator \
&&  go install k8s.io/code-generator/cmd/deepcopy-gen \
&&  go install k8s.io/code-generator/cmd/client-gen \
&&  go install k8s.io/code-generator/cmd/lister-gen \
&&  go install k8s.io/code-generator/cmd/informer-gen \
&&  deepcopy-gen --alsologtostderr --input-dirs github.com/nokia/danm/crd/apis/danm/v1 -O zz_generated.deepcopy --bounding-dirs github.com/nokia/danm/crd/apis \
&&  client-gen --alsologtostderr --clientset-name versioned --input-base "" --input github.com/nokia/danm/crd/apis/danm/v1 --clientset-path github.com/nokia/danm/crd/client/clientset \
&&  lister-gen --alsologtostderr --input-dirs github.com/nokia/danm/crd/apis/danm/v1 --output-package github.com/nokia/danm/crd/client/listers \
&&  informer-gen --alsologtostderr --input-dirs github.com/nokia/danm/crd/apis/danm/v1 --versioned-clientset-package github.com/nokia/danm/crd/client/clientset/versioned --listers-package github.com/nokia/danm/crd/client/listers --output-package github.com/nokia/danm/crd/client/informers \
&&  mkdir -p ${binaries} \
&&  for component in $components; do \
      go install -a -ldflags '-extldflags "-static"' github.com/nokia/danm/cmd/${component}; \
      cp $GOPATH/bin/${component} ${binaries}/${component}; \
    done
