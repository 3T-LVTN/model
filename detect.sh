#!/bin/sh

### below python to test
# python error.py

status=$?
echo $status
url="https://hooks.slack.com/services/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"
header="'Content-Type: application/json'"
data="{\"text\": \"pull image failed\" }"
echo $header
echo $data
if [[ $status -ne 0 ]]; then
 sh "curl --location $url --header $header  --data '$data'"
fi
### uncomment below to debug local
# function pause(){
#    read -p "$*"
# }
# pause 'Press [Enter] key to continue...'