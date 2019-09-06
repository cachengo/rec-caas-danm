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
%define COMPONENT flannel
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 0.11.0
%define RPM_MINOR_VERSION 5
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service flannel component
License:        %{_platform_license} and MIT license and BSD and Apache License and ISC License and COMMON DEVELOPMENT AND DISTRIBUTION LICENSE and GNU Lesser General Public License v3.0 only
URL:            https://github.com/coreos/flannel
BuildArch:      %{CPU_ARCHITECTURE}
Vendor:         %{_platform_vendor} and coreos/flannel unmodified
Source0:        %{name}-%{version}.tar.gz

Requires: docker-ce >= 18.09.2, rsync
BuildRequires: docker-ce-cli >= 18.09.2, xz

%description
This RPM contains the Flannel container image, and related deployment artifacts for the CaaS subsystem.

%prep
%autosetup

%build
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
  --build-arg FLANNEL="%{RPM_MAJOR_VERSION}" \
  --build-arg FLANNEL_ARCHITECTURE="amd64" \
  --tag %{COMPONENT}:%{IMAGE_TAG} \
  %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build/%{COMPONENT}/

mkdir -p %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save/

docker save %{COMPONENT}:%{IMAGE_TAG} | xz -z -T2 > %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save/%{COMPONENT}:%{IMAGE_TAG}.tar

docker rmi -f %{COMPONENT}:%{IMAGE_TAG}

%install
mkdir -p %{buildroot}/%{_caas_container_tar_path}
rsync -av %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save/%{COMPONENT}:%{IMAGE_TAG}.tar %{buildroot}/%{_caas_container_tar_path}/

mkdir -p %{buildroot}/%{_playbooks_path}
rsync -av ansible/playbooks/flannel.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}
rsync -av ansible/roles/flannel %{buildroot}/%{_roles_path}/

%files
%{_caas_container_tar_path}/%{COMPONENT}:%{IMAGE_TAG}.tar
%{_playbooks_path}/flannel.yaml
%{_roles_path}/flannel

%preun

%post
mkdir -p %{_postconfig_path}
ln -sf %{_playbooks_path}/flannel.yaml %{_postconfig_path}/

%postun
if [ $1 -eq 0 ]; then
    rm -f %{_postconfig_path}/flannel.yaml
fi

%clean
rm -rf ${buildroot}
