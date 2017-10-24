#!/bin/bash

ctx logger info "Update compiler"
sudo CGO_ENABLED=0 go install -a -installsuffix cgo std

ctx logger info "Go to /opt"
sudo mkdir -p /opt/cloudify-kubernetes-provider
sudo chmod -R 755 /opt/
sudo chown $USER:$GROUP /opt/cloudify-kubernetes-provider/
cd /opt/

ctx logger info "Kubernetes Provider: Download top level sources"
# take ~ 16m34.350s for rebuild, 841M Disk Usage
set -e
rm -rf cloudify-rest-go-client || true
set +e

git clone https://github.com/cloudify-incubator/cloudify-kubernetes-provider.git --depth 1 -b master
sed -i "s|git@github.com:|https://github.com/|g" cloudify-kubernetes-provider/.gitmodules

cd cloudify-kubernetes-provider
ctx logger info "Kubernetes Provider: Download submodules sources"
git submodule init
git submodule update
