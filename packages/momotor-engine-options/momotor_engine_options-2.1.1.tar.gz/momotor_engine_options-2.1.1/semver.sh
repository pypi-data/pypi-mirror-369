#!/bin/sh

# Configure git
git config --global user.name "semantic-release (via GitlabCI)"
git config --global user.email "tue.gitlab@momotor.org"
git checkout "$CI_COMMIT_REF_NAME"
git status

set -eux

# Bump the version
if [ "$CI_COMMIT_REF_PROTECTED" = "true" ]; then
  semantic-release -v version --skip-build
  semantic-release -v publish
else
  semantic-release -v version --skip-build --no-vcs-release
fi
