#!/bin/bash

export env=test
source venv/bin/activate
python3 -m pytest
