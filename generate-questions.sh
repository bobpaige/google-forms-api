#!/bin/bash
## Create/Synchronize Google Forms based on a configuration file
##
## Usage:
##   $ ./generate-questions.sh chapter1-yml
##

if [ $# -eq 0 ]; then
  grep "^##" $0 | cut -c 3-
  exit 0
fi

if [ ! -d .venv ]; then
  banner "Creating virtual environment"
  python -m venv .venv
elsed
  banner "Using virtual environment .venv"
fi

banner "Installing requirements"
source .venv/Scripts/activate
pip3 install -r requirements.txt > .requirements-installed.txt
echo $(/usr/bin/grep installed .requirements-installed.txt | /usr/bin/wc -l | /usr/bin/cut -f1 -d\ ) new requirements installed
echo $(/usr/bin/grep satisfied .requirements-installed.txt | /usr/bin/wc -l | /usr/bin/cut -f1 -d\ ) requirements previously installed

# source again so the banner command works
source ~/.bashrc

banner "Generating questions for $1"
python forms_manager.py --input-file $1