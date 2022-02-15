#!/bin/bash


cache_option= #'--no-cache'
image_name="stone82_master"
version=$(cat VERSION)

set -e

# dockerize
docker build -t $image_name:$version .
