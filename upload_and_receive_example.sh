#!/bin/bash

# Encode your image in base64
BASE64_IMAGE=$(base64 -w 0 google.png)

# Create a temporary JSON file
JSON_FILE=$(mktemp)
echo "{\"image\":\"$BASE64_IMAGE\"}" > "$JSON_FILE"

# Send the request to the API using the correct endpoint and method
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d @"$JSON_FILE"

# Remove the temporary file
rm "$JSON_FILE"