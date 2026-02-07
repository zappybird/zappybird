#!/bin/bash
set -e

echo "Reading repos.json..."
REPOS=$(jq -r '.repos[]' repos.json)

WORKDIR="loc-temp"
rm -rf "$WORKDIR"
mkdir "$WORKDIR"

TOTAL_JSON="{}"
TOTAL_FILES=0

echo "Cloning repositories and counting LOC..."

for REPO in $REPOS; do
    echo "Processing $REPO..."

    TARGET="$WORKDIR/$(basename $REPO)"
    git clone --depth 1 "https://github.com/$REPO.git" "$TARGET"

    # Count files manually
    FILE_COUNT=$(find "$TARGET" -type f | wc -l)
    TOTAL_FILES=$((TOTAL_FILES + FILE_COUNT))

    # Run tokei
    REPO_JSON=$(tokei "$TARGET" --output json)

    # Merge JSON
    TOTAL_JSON=$(jq -s '.[0] * .[1]' <(echo "$TOTAL_JSON") <(echo "$REPO_JSON"))
done

# Inject total file count
TOTAL_JSON=$(echo "$TOTAL_JSON" | jq --argjson f "$TOTAL_FILES" '.Total.files = $f')

echo "$TOTAL_JSON" > loc-data.json
echo "LOC data written to loc-data.json"
