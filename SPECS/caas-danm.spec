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

%define CPU_ARCHITECTURE aarch64
%define COMPONENT danm
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 4.0.0
%define RPM_MINOR_VERSION 4
%define DANM_VERSION 5e15d4e322fc5ff89b06ac70bd83b5ce4c09d0df
%define CNI_VERSION 0.8.1
%define go_version 1.12.9
%define SRIOV_VERSION 9e4c973b2ac517c64867e33d61aee152d70dc330
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}
%define binary_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/binary-save
%define docker_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build
%define build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/build
%define built_binaries_dir /binary-save
%define danm_components danm fakeipam
%define cnis flannel sriov

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service %{COMPONENT} component
License:        %{_platform_license} and BSD 3-Clause License
URL:            https://github.com/nokia/danm
BuildArch:      %{CPU_ARCHITECTURE}
Vendor:         %{_platform_vendor} and Nokia
Source0:        %{name}-%{version}.tar.gz

Requires: docker-ce >= 18.09.2, iputils, rsync
BuildRequires: docker-ce-cli >= 18.09.2, curl

# more info at: https://fedoraproject.org/wiki/Packaging:Debuginfo No build ID note in Flannel
%global debug_package %{nil}

%description
This RPM contains the DANM and related CNI binaries for CaaS subsystem.

%prep
%autosetup

%build
mkdir -p %{binary_build_dir}/cni
curl -fsSL -k https://github.com/containernetworking/plugins/releases/download/v%{CNI_VERSION}/cni-plugins-linux-amd64-v%{CNI_VERSION}.tgz  | tar zx --strip-components=1 -C %{binary_build_dir}/cni

# Build DANM binaries
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
  --build-arg binaries="%{built_binaries_dir}" \
  --build-arg components="%{danm_components}" \
  --tag danm-builder:%{IMAGE_TAG} \
  %{docker_build_dir}/danm-builder/

builder_container=$(docker run -id --rm --network=none --entrypoint=/bin/sh danm-builder:%{IMAGE_TAG})
mkdir -p %{binary_build_dir}/danm
for component in %{danm_components}; do
  docker cp ${builder_container}:%{built_binaries_dir}/${component} %{binary_build_dir}/danm/
done
docker rm -f ${builder_container}
docker rmi danm-builder:%{IMAGE_TAG}

# Build CNI binaries
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
  --build-arg go_version="%{go_version}" \
  --build-arg SRIOV_VERSION="%{SRIOV_VERSION}" \
  --build-arg binaries="%{built_binaries_dir}" \
  --tag cni-builder:%{IMAGE_TAG} \
  %{docker_build_dir}/cni-builder/

builder_container=$(docker run -id --rm --network=none --entrypoint=/bin/sh cni-builder:%{IMAGE_TAG})
mkdir -p %{binary_build_dir}/built_cnis
for cni in %{cnis}; do
  docker cp ${builder_container}:%{built_binaries_dir}/${cni} %{binary_build_dir}/built_cnis/
done
docker rm -f ${builder_container}
docker rmi cni-builder:%{IMAGE_TAG}

# Collect DANM CRDs
git clone https://github.com/nokia/danm.git %{build_dir}/danm
cd %{build_dir}/danm
git checkout %{DANM_VERSION}

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
for component in %{danm_components}; do
  install -D -m 0755 %{binary_build_dir}/danm/${component} %{buildroot}/opt/cni/bin/${component}
done
# Other CNIs
for cni in %{cnis}; do
  install -D -m 0755 %{binary_build_dir}/built_cnis/${cni} %{buildroot}/opt/cni/bin/${cni}
done

# DANM CRDs
mkdir -p %{buildroot}/%{_caas_danm_crd_path}
rsync -av %{build_dir}/danm/integration/crds/production/ %{buildroot}/%{_caas_danm_crd_path}


%files
# CONFIG
/etc/cni/net.d/00-danm.conf
/etc/cni/net.d/flannel.conf
# CNI binaries
/opt/cni/bin
# DANM CRDs
/%{_caas_danm_crd_path}

%preun

%post

%postun

%clean
rm -rf ${buildroot}
