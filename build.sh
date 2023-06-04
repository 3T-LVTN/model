#!/bin/bash

# Parse options
options=$(getopt -o e:f: --long env:,env-file: -- "$@")
eval set -- $options

# Loop over options
while true; do
  case "$1" in
    -e|--env)
      export ENV="$2"
      shift 2
      ;;
    -f|--env-file)
      export ENV_FILE="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Invalid option: $1"
      exit 1
      ;;
  esac
done
echo $ENV
echo $ENV_FILE
DOCKER_BUILD_KIT=1 docker build -t vove_model_$ENV --file ./docker/app/Dockerfile .
DOCKER_BUILD_KIT=1 docker build -t vove_celery_$ENV --file ./docker/celery/Dockerfile .
docker-compose up -d
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