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
%define COMPONENT hyperdanm
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 4.0.0
%define RPM_MINOR_VERSION 1
%define DANM_VERSION 5e15d4e322fc5ff89b06ac70bd83b5ce4c09d0df
%define go_version 1.12.1
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}
%define danm_components netwatcher svcwatcher webhook
%define docker_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build
%define docker_save_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save
%define binary_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/binary-save
%define built_binaries_dir /binary-save

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service %{COMPONENT} component
License:        %{_platform_license} and BSD 3-Clause License
URL:            https://github.com/nokia/danm
BuildArch:      %{CPU_ARCHITECTURE}
Vendor:         %{_platform_vendor} and Nokia
Source0:        %{name}-%{version}.tar.gz

Requires:       docker-ce >= 18.09.2, rsync
BuildRequires:  docker-ce-cli >= 18.09.2, xz
Obsoletes:      caas-danm-webhook <= 4.0.0, caas-netwatcher <= 4.0.0, caas-svcwatcher <= 4.0.0

%description
This RPM contains the %{COMPONENT} container image, and related deployment artifacts for the CaaS subsystem.

%prep
%autosetup

%build
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
for component in %{danm_components}; do
  mkdir -p %{binary_build_dir}/
  docker cp ${builder_container}:%{built_binaries_dir}/${component} %{binary_build_dir}/
done
docker rm -f ${builder_container}
docker rmi danm-builder:%{IMAGE_TAG}

# Build hyperdanm container image
mkdir -p %{docker_build_dir}/%{COMPONENT}/danm_binaries
rsync -av %{binary_build_dir}/* %{docker_build_dir}/%{COMPONENT}/danm_binaries
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
  --tag %{COMPONENT}:%{IMAGE_TAG} \
  %{docker_build_dir}/%{COMPONENT}/

mkdir -p %{docker_save_dir}/
docker save %{COMPONENT}:%{IMAGE_TAG} | xz -z -T2 > %{docker_save_dir}/%{COMPONENT}:%{IMAGE_TAG}.tar
docker rmi -f %{COMPONENT}:%{IMAGE_TAG}

%install
mkdir -p %{buildroot}/%{_caas_container_tar_path}/
rsync -av %{docker_save_dir}/%{COMPONENT}:%{IMAGE_TAG}.tar %{buildroot}/%{_caas_container_tar_path}/

mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/danm_setup.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/danm_setup %{buildroot}/%{_roles_path}/

%files
%{_caas_container_tar_path}/%{COMPONENT}:%{IMAGE_TAG}.tar
%{_playbooks_path}/danm_setup.yaml
%{_roles_path}/danm_setup

%preun

%post
mkdir -p %{_postconfig_path}/
ln -sf %{_playbooks_path}/danm_setup.yaml %{_postconfig_path}/

%postun
if [ $1 -eq 0 ]; then
    rm -f %{_postconfig_path}/danm_setup.yaml
fi

%clean
rm -rf ${buildroot}
