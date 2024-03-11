#!/bin/bash

set -e

pip install -r requirements.txt

clear
echo "Setup succeeded."

read -p "Press any key to continue..." -n1 -s