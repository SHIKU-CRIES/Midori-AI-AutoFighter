#!/bin/bash

cd windows

chmod +x builder.sh

./builder.sh

cd ..

cd linux

chmod +x builder.sh

./builder.sh