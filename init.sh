#!/bin/bash

# installing python 3.8
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt install python3.8 -y
sudo apt install python3.8-distutils -y

# installing awscli VERSION 
sudo apt  install awscli -y

# Creating a Virtual Environment For Python3.8 
sudo apt install python3-virtualenv -y
virtualenv --python="/usr/bin/python3.8" sandbox  
source sandbox/bin/activate 

# Installing Dependencies
pip install -r requirements.txt

deactivate # deactivating Virtual Envrironment

chmod a+x run.sh # make run.sh executable

mkdir -p log # create log directory if it doesn't exist