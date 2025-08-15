#!/bin/sh

CHANNEL=$1
FILE=$2

apk update
apk add openssh-client

eval $(ssh-agent -s)
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "$DOCS_SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null
ssh-keyscan -t rsa "${DOCS_HOST}" >> ~/.ssh/known_hosts

scp "${FILE}" "${DOCS_USER}@${DOCS_HOST}:${DOCS_PATH}"
ssh "${DOCS_USER}@${DOCS_HOST}" "publish/publish.py ${CHANNEL} ${FILE}"
ssh "${DOCS_USER}@${DOCS_HOST}" "rm ${DOCS_PATH}/${FILE} || true"
