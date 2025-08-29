#!/usr/bin/env python3
"""
Simple Python script to perform VectorStock API request
Equivalent to the curl command:
curl -X GET "https://api.vectorstock.com/v1/list?free=false&expanded=false"
     -H "accept: application/json"
     -H "Authorization: Basic NjI2MTE1MTo0ODU0OTAwMC0zYWQwLTQwM2QtOThhNS00NTkwMTFkYTM0NDM="
"""

import json
from datetime import datetime

import requests


def main(URL: str, PARAMS: dict, HEADERS: dict, metadata_file: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        # Make the GET request
        response = requests.get(URL, params=PARAMS, headers=HEADERS)

        # Check if request was successful
        response.raise_for_status()

        # Print status code
        print(f"Status Code: {response.status_code}")
        print("-" * 50)

        # Print response headers
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print("-" * 50)

        # Print response body
        print("Response Body:")
        try:
            # Try to parse as JSON and pretty print
            json_response = response.json()
            # print(json.dumps(json_response, indent=2))

            # Save response to JSON file
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(json_response, f, indent=2, ensure_ascii=False)

            print("-" * 50)
            print(f"Response saved to: {metadata_file}")

            # Also save request metadata
            metadata = {
                "timestamp": timestamp,
                "url": URL,
                "params": PARAMS,
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": json_response,
            }
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            print(f"Request metadata saved to: {metadata_file}")

            return json_response

        except json.JSONDecodeError:
            print("Error: Response is not valid JSON")
            return None

    except requests.exceptions.RequestException:
        print(f"Error details saved to: {metadata_file}")
        return None


if __name__ == "__main__":
    start_after = 1310
    OUTPUT_FILE = "results/metadata/first_1000_images_metadata.json"

    URL = "https://api.vectorstock.com/v1/list"
    PARAMS = {"free": "false", "expanded": "false"}
    HEADERS = {
        "accept": "application/json",
        "Authorization": "Basic NjI2MTE1MTo0ODU0OTAwMC0zYWQwLTQwM2QtOThhNS00NTkwMTFkYTM0NDM=",
    }

    # API endpoint and parameters
    if start_after:
        PARAMS["start_after"] = start_after
        URL = f"https://api.vectorstock.com/v1/list/{start_after}"
        OUTPUT_FILE = f"results/metadata/1000_images_metadata_{start_after}.json"

    main(URL, PARAMS, HEADERS, OUTPUT_FILE)
