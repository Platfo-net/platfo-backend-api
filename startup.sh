#!/bin/bash

#Start app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload