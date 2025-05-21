#!/bin/bash

# Set directories
INPUT_DIR="./input_images"
OUTPUT_DIR="${INPUT_DIR}_analysis"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Find all image files
image_files=$(find "$INPUT_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" \))

# Counter for naming
counter=1

# Process each image
for image_path in $image_files; do
    echo "Processing image $counter: $image_path"
    
    # Create the output filename
    image_output="${OUTPUT_DIR}/image_${counter}.${image_path##*.}"
    json_output="${OUTPUT_DIR}/analysis_${counter}.json"
    
    # Copy the original image
    cp "$image_path" "$image_output"
    
    # Encode image in base64
    BASE64_IMAGE=$(base64 -w 0 "$image_path")
    
    # Create temporary JSON file for request
    JSON_FILE=$(mktemp)
    echo "{\"image\":\"$BASE64_IMAGE\"}" > "$JSON_FILE"
    
    # Send request to API and save response
    echo "Sending to API..."
    curl -s -X POST "http://localhost:8000/analyze" \
        -H "Content-Type: application/json" \
        -d @"$JSON_FILE" > "$json_output"
    
    # Remove temporary file
    rm "$JSON_FILE"
    
    echo "Saved analysis to $json_output"
    echo "---------------------------------"
    
    # Increment counter for next image
    ((counter++))
    
    # Wait 2 seconds before next request
    if [ -n "$(find "$INPUT_DIR" -type f | sed -n "$counter p")" ]; then
        echo "Waiting 2 seconds before next request..."
        sleep 2
    fi
done

echo "All images processed. Results saved in $OUTPUT_DIR"