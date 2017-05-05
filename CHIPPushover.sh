#!/bin/sh

#set -- "${1:-$(</dev/stdin)}" "${@:2}"

if [ $# -lt 1 ] 
then
  echo "Usage: ./CHIPPushover.sh <message>"
else
  msg=$1
  echo [$msg] will be pushed to mobile device

  curl -s \
    --form-string "token=<your token>" \   # change this, you need an Pushover.net account
    --form-string "user=<your user key>" \ # change this
    --form-string "message=$msg" \
    https://api.pushover.net/1/messages.json
    echo
fi
