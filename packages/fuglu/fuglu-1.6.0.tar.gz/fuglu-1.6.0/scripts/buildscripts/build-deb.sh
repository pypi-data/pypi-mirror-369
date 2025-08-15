#!/bin/bash

apt update
apt -y install wget vim python3-pip
apt -y install python3-stdeb fakeroot python3-all dh-python
python3 setup.py  --command-packages=stdeb.command bdist_deb

ls ./deb_dist/
dpkg -c ./deb_dist/python3-fuglu_1.4.0-1_all.deb
