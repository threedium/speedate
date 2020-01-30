#!/bin/bash
app="speedate"
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD:/api ${app}