#!/bin/sh

temp=$( realpath "$0"  )
basePath=$( dirname "$temp" )/..

nvidia-docker run \
	-it \
	--rm \
	--name mist4python \
	--network=bridge \
	-p 9999:8888 \
	--volume "$basePath":/home/jovyan/work \
	--volume $(readlink -f "$basePath"/datasets/):/notebooks/datasets/ \
	maxfrei750/mist4python:latest
