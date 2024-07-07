#!/bin/bash

case "$1" in
  d)
    docker-compose down
    ;;
  u)
    docker-compose up -d --build
    ;;
  r)
    uvicorn app.main:app --reload
    ;;
  *)
    echo "Usage: $0 {d|u|r}"
    exit 1
    ;;
esac

exit 0
