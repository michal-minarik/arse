#!/usr/bin/env bash
#build container

cp ../arse.py .
cp ../config.json .
cp ../sample_input.xlsx input.xlsx

docker build -t arse:0.0.2 .
