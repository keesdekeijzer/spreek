#!/bin/bash

# eerst naar de directory gaan
cd ~/Projecten/Piper

# venv activeren
source venv/bin/activate

# start de piper server
python3 -m piper.http_server -m voice/nl_BE-nathalie-medium
