# Installation

## Via Snap
sudo apt update
sudo apt install snapd
sudo snap install blender --classic

## Via Repository
sudo add-apt-repository ppa:thomas-schiex/blender
sudo apt install blender

## Setup python
/path/to/blender/2.80/python/bin/python -m ensurepip
/path/to/blender/2.80/python/bin/python -m pip uninstall numpy
rm -R /path/to/blender/2.80/python/bin/python/lib/site-packages/numpy
/path/to/blender/2.80/python/bin/python -m pip install numpy
/path/to/blender/2.80/python/bin/python -m pip install trimesh

# Blender+pycharm
https://b3d.interplanety.org/en/using-external-ide-pycharm-for-writing-blender-scripts/

