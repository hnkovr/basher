## init.sh
#
#python3 -m venv .venv
#source .venv/bin/activate
#pip3 install -r requirements.txt

#!/bin/bash

# Function to reinstall packages
reinstall_packages() {
    pip freeze > uninstall.txt
    pip uninstall -r uninstall.txt -y
    pip install -r requirements.txt
}

# Parse arguments
while getopts "r" opt; do
    case $opt in
        r)
            REINSTALL=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

# Create virtual environment and activate it
python3 -m venv .venv
source .venv/bin/activate

# Install or reinstall packages
if [ "$REINSTALL" = true ]; then
    reinstall_packages
else
    pip3 install -r requirements.txt
fi
