#!/bin/bash

# Option A Baseline Search Script
# Reads search queries from Option-A-search-queries.txt and runs searches using make_search_request.py

set -e  # Exit on any error

# Configuration
QUERIES_FILE="data/Option-A-search-queries.txt"
SEARCH_SCRIPT="make_search_request.py"
OUTPUT_DIR="data/search_results/OptionA-Baseline"

# Check if required files exist
if [[ ! -f "$QUERIES_FILE" ]]; then
    echo "Error: Queries file not found: $QUERIES_FILE"
    exit 1
fi

if [[ ! -f "$SEARCH_SCRIPT" ]]; then
    echo "Error: Search script not found: $SEARCH_SCRIPT"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Initialize counters
successful_searches=0
failed_searches=0
current_query=0

echo "Starting Option A baseline searches..."

# Read queries and process each one
while IFS= read -r query || [[ -n "$query" ]]; do
    # Skip empty lines
    if [[ -z "$query" || "$query" =~ ^[[:space:]]*$ ]]; then
        continue
    fi
    
    current_query=$((current_query + 1))
    
    echo "Processing query $current_query: '$query'"
    
    # Run the search request
    if python3 "$SEARCH_SCRIPT" "$query" --output-dir "$OUTPUT_DIR"; then
        echo "Success: '$query'"
        successful_searches=$((successful_searches + 1))
    else
        echo "Failed: '$query'"
        failed_searches=$((failed_searches + 1))
    fi
    
    # Add a small delay between requests
    sleep 1
    
done < "$QUERIES_FILE"

# Print final summary
echo ""
echo "Summary:"
echo "Total queries processed: $current_query"
echo "Successful searches: $successful_searches"
echo "Failed searches: $failed_searches"
echo "Results saved in: $OUTPUT_DIR"
