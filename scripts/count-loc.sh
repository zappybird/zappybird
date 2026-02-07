#!/bin/bash

set -e

echo "Reading repos.json..."
REPOS=$(jq -r '.repos[]' repos.json)

# Create a temp directory
WORKDIR="loc-temp"
rm -rf "$WORKDIR"
mkdir "$WORKDIR"

TOTAL_JSON="{}"

echo "Cloning repositories and counting LOC..."

for REPO in $REPOS; do
    echo "Processing $REPO..."

    git clone --depth 1 "https://github.com/$REPO.git" "$WORKDIR/$(basename $REPO)"

    # Run tokei on the repo
    REPO_JSON=$(tokei "$WORKDIR/$(basename $REPO)" --output json)

    # Merge JSON results
    TOTAL_JSON=$(jq -s '.[0] * .[1]' <(echo "$TOTAL_JSON") <(echo "$REPO_JSON"))
done

echo "$TOTAL_JSON" > loc-data.json
echo "LOC data written to loc-data.json"
