#!/bin/bash

export env=development
source venv/bin/activate
uvicorn app.main:app --reload
