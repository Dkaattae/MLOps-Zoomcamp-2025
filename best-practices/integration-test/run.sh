#!/usr/bin/env bash

export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

cd ..
docker-compose up -d
sleep 1

aws --endpoint-url=http://localhost:4566 s3  mb s3://nyc-duration --region us-east-1

cd integration-test
python sample_data_setup.py

cd ..
docker build -t ${LOCAL_IMAGE_NAME} .

docker run --rm --entrypoint "" ${LOCAL_IMAGE_NAME} pipenv run pytest tests

docker run --rm \
    --add-host=host.docker.internal:host-gateway \
    -e INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet" \
    -e OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet" \
    -e AWS_ACCESS_KEY_ID=test \
    -e AWS_SECRET_ACCESS_KEY=test \
    ${LOCAL_IMAGE_NAME} 

cd integration-test
python integration_test.py

docker-compose down