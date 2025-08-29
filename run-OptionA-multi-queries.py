#!/usr/bin/env python3
"""
Run VectorStock searches from JSON configuration file
"""

import json
import os
import sys

from src.vectorstock_keyword_search_dirname import VectorStockSearchClient


def run_searches_from_json(json_file_path, output_dir="search_results"):
    """Run searches from JSON configuration file"""

    # Read the JSON file
    with open(json_file_path, "r") as f:
        search_configs = json.load(f)

    client = VectorStockSearchClient()

    for i, config in enumerate(search_configs):
        name = config.get("name", f"Search_{i+1}")
        current_output_dir = os.path.join(output_dir, f"search_{i+1}")
        print(f"\n{'='*60}")
        print(f"Running search: {name}")
        print(f"{'='*60}")

        # Extract search parameters
        search_params = {k: v for k, v in config.items() if k != "name"}

        try:
            client.search_and_save(output_dir=current_output_dir, **search_params)
            print(f"✅ Completed: {name}")
        except Exception as e:
            print(f"❌ Failed: {name} - Error: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_searches.py <json_file_path> <output_dir>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    output_dir = sys.argv[2]
    run_searches_from_json(json_file_path, output_dir)
    run_searches_from_json(json_file_path, output_dir)
