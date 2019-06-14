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

%define COMPONENT danm
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 3.3.0
%define RPM_MINOR_VERSION 3
%define DANM_VERSION v%{RPM_MAJOR_VERSION}
%define CNI_VERSION 0.7.0
%define go_version 1.12.1
%define SRIOV_VERSION 9e4c973b2ac517c64867e33d61aee152d70dc330
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}
%define binary_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/binary-save
%define docker_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build
%define built_binaries_dir /binary-save

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service %{COMPONENT} component
License:        %{_platform_license} and BSD 3-Clause License
URL:            https://github.com/nokia/danm
BuildArch:      x86_64
Vendor:         %{_platform_vendor} and Nokia
Source0:        %{name}-%{version}.tar.gz

Requires: docker-ce >= 18.09.2, iputils, rsync
BuildRequires: docker-ce >= 18.09.2, rsync

# more info at: https://fedoraproject.org/wiki/Packaging:Debuginfo No build ID note in Flannel
%global debug_package %{nil}

%description
This RPM contains the DANM and related CNI binaries for CaaS subsystem.

%prep
%autosetup

%build
mkdir -p %{binary_build_dir}/cni
curl -fsSL -k https://github.com/containernetworking/plugins/releases/download/v%{CNI_VERSION}/cni-plugins-amd64-v%{CNI_VERSION}.tgz  | tar zx --strip-components=1 -C %{binary_build_dir}/cni

docker build \
  --network=host \
  --no-cache \
  --force-rm \
  --build-arg HTTP_PROXY="${http_proxy}" \
  --build-arg HTTPS_PROXY="${https_proxy}" \
  --build-arg NO_PROXY="${no_proxy}" \
  --build-arg http_proxy="${http_proxy}" \
  --build-arg https_proxy="${https_proxy}" \
  --build-arg no_proxy="${no_proxy}" \
  --build-arg DANM_VERSION="%{DANM_VERSION}" \
  --build-arg go_version="%{go_version}" \
  --build-arg SRIOV_VERSION="%{SRIOV_VERSION}" \
  --build-arg binaries="%{built_binaries_dir}" \
  --tag cni-builder:%{IMAGE_TAG} \
  %{docker_build_dir}/cni-builder/

builder_container=$(docker run -id --rm --network=none --entrypoint=/bin/sh cni-builder:%{IMAGE_TAG})
mkdir -p %{binary_build_dir}/danm
docker cp ${builder_container}:%{built_binaries_dir}/danm %{binary_build_dir}/
mkdir -p %{binary_build_dir}/flannel
docker cp ${builder_container}:%{built_binaries_dir}/flannel %{binary_build_dir}/
mkdir -p %{binary_build_dir}/sriov
docker cp ${builder_container}:%{built_binaries_dir}/sriov %{binary_build_dir}/

docker rm -f ${builder_container}
docker rmi cni-builder:%{IMAGE_TAG}

%install
mkdir -p %{buildroot}/etc/cni/net.d/
rsync -av cni-config/00-danm.conf %{buildroot}/etc/cni/net.d/00-danm.conf
rsync -av cni-config/flannel.conf %{buildroot}/etc/cni/net.d/flannel.conf

mkdir -p %{buildroot}/opt/cni/bin/
# Generic CNI plugins
# Don't use the standard ipvlan binary \
# Don't use portmap, quick fix for CVE-2019-9946 \
rsync -av \
      --chmod=go+rx,u+rwx \
      --exclude=ipvlan \
      --exclude=portmap \
       %{binary_build_dir}/cni/* %{buildroot}/opt/cni/bin
# DANM
install -D -m 0755 %{binary_build_dir}/danm/danm %{buildroot}/opt/cni/bin/danm
install -D -m 0755 %{binary_build_dir}/danm/fakeipam %{buildroot}/opt/cni/bin/fakeipam
# FLANNEL
install -D -m 0755 %{binary_build_dir}/flannel/flannel %{buildroot}/opt/cni/bin/flannel
# SRIOV
install -D -m 0755 %{binary_build_dir}/sriov/sriov %{buildroot}/opt/cni/bin/sriov

%files
# CONFIG
/etc/cni/net.d/00-danm.conf
/etc/cni/net.d/flannel.conf
# CNI binaries
/opt/cni/bin

%preun

%post

%postun

%clean
rm -rf ${buildroot}
