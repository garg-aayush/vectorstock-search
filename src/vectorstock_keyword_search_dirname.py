#!/usr/bin/env python3
"""
VectorStock Search API Client

This script allows you to make search requests to the VectorStock API
and saves the search query, parameters, and results to JSON files.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

import requests


class VectorStockSearchClient:
    """Client for interacting with VectorStock Search API"""

    def __init__(self):
        self.base_url = "https://api.vectorstock.com/p1/search"

        # Valid values for specific parameters
        self.valid_categories = [
            "abstract",
            "animals-wildlife",
            "artistic-experimental",
            "backgrounds-textures",
            "beauty-fashion",
            "borders-frames",
            "buildings-landmarks",
            "business-finance",
            "cartoons",
            "celebration-party",
            "children-family",
            "christmas",
            "cityscapes",
            "communication",
            "computers",
            "copy-space",
            "dj-dance-music",
            "dancing",
            "design-elements",
            "digital-media",
            "document-template",
            "easter",
            "education",
            "entertainment",
            "flags-ribbons",
            "floral-decorative",
            "fonts-type",
            "food-drink",
            "game-assets",
            "geographical-maps",
            "graffiti",
            "graphs-charts",
            "grunge",
            "halloween",
            "healthcare-medical",
            "heraldry",
            "housing",
            "icon-emblem-(single)",
            "icons-emblems-(sets)",
            "industrial",
            "infographics",
            "interiors",
            "landscapes-nature",
            "logos",
            "military",
            "miscellaneous",
            "music",
            "objects-still-life",
            "packaging",
            "patterns-(seamless)",
            "patterns-(single)",
            "people",
            "photo-real",
            "religion",
            "science",
            "seasons",
            "shopping-retail",
            "signs-symbols",
            "silhouettes",
            "sports-recreation",
            "t-shirt-graphics",
            "technology",
            "telecommunications",
            "transportation",
            "urban-scenes",
            "user-interface",
            "vacation-travel",
            "valentines-day",
            "vintage",
            "weddings",
        ]

        self.valid_object_detection = ["show_objects", "hide_objects"]
        self.valid_order = ["trending", "bestmatch", "latest", "isolated", "featured"]

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean parameters"""
        validated_params = {}

        # Required parameter
        if "keywords" not in params or not params["keywords"]:
            raise ValueError("'keywords' is a required parameter")
        validated_params["keywords"] = params["keywords"]

        # Optional parameters
        if "category" in params and params["category"]:
            if params["category"] not in self.valid_categories:
                raise ValueError(f"Invalid category: {params['category']}")
            validated_params["category"] = params["category"]

        if "artist" in params and params["artist"]:
            validated_params["artist"] = params["artist"]

        if "page" in params and params["page"] is not None:
            validated_params["page"] = int(params["page"])

        # Boolean parameters
        boolean_params = [
            "free",
            "expanded",
            "svg_only",
            "templates_only",
            "pod_first",
            "cmyk_only",
            "png_only",
            "editorial",
            "count_only",
        ]
        for param in boolean_params:
            if param in params and params[param] is not None:
                validated_params[param] = bool(params[param])

        if "object_detection" in params and params["object_detection"]:
            if params["object_detection"] not in self.valid_object_detection:
                raise ValueError(
                    f"Invalid object_detection: {params['object_detection']}"
                )
            validated_params["object_detection"] = params["object_detection"]

        # Integer range parameters
        if "object_count_min" in params and params["object_count_min"] is not None:
            value = int(params["object_count_min"])
            if not 1 <= value <= 200:
                raise ValueError("object_count_min must be between 1 and 200")
            validated_params["object_count_min"] = value

        if "object_count_max" in params and params["object_count_max"] is not None:
            value = int(params["object_count_max"])
            if not 1 <= value <= 200:
                raise ValueError("object_count_max must be between 1 and 200")
            validated_params["object_count_max"] = value

        if "color" in params and params["color"]:
            # Validate hex color format
            color = params["color"].strip()
            if not color.startswith("#"):
                color = f"#{color}"
            if len(color) != 7 or not all(
                c in "0123456789ABCDEFabcdef" for c in color[1:]
            ):
                raise ValueError("color must be a valid hexadecimal color code")
            validated_params["color"] = color

        if "color_threshold" in params and params["color_threshold"] is not None:
            value = int(params["color_threshold"])
            if not 1 <= value <= 10:
                raise ValueError("color_threshold must be between 1 and 10")
            validated_params["color_threshold"] = value

        if "score_popular" in params and params["score_popular"] is not None:
            value = int(params["score_popular"])
            if not 1 <= value <= 10:
                raise ValueError("score_popular must be between 1 and 10")
            validated_params["score_popular"] = value

        if "artist_score" in params and params["artist_score"] is not None:
            value = int(params["artist_score"])
            if not 1 <= value <= 10:
                raise ValueError("artist_score must be between 1 and 10")
            validated_params["artist_score"] = value

        if "order" in params and params["order"]:
            if params["order"] not in self.valid_order:
                raise ValueError(f"Invalid order: {params['order']}")
            validated_params["order"] = params["order"]

        return validated_params

    def search(self, **kwargs) -> Dict[str, Any]:
        """
        Make a search request to the VectorStock API

        Returns:
            Dictionary containing the response data
        """
        # Validate parameters
        params = self.validate_parameters(kwargs)

        # Make the request
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def search_and_save(self, output_dir: str = ".", **kwargs) -> None:
        """
        Make a search request and save the query, parameters, and results to JSON files

        Args:
            output_dir: Directory to save the JSON files
            **kwargs: Search parameters
        """
        # Create timestamp for subfolder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create timestamped subfolder within output directory
        timestamp_dir = os.path.join(output_dir)
        os.makedirs(timestamp_dir, exist_ok=True)

        # Validate and get clean parameters
        params = self.validate_parameters(kwargs)

        # Construct the full query URL
        query_url = f"{self.base_url}?" + "&".join(
            [f"{k}={v}" for k, v in params.items()]
        )

        # Save the search query
        query_data = {"timestamp": timestamp, "url": query_url, "method": "GET"}
        query_filename = os.path.join(timestamp_dir, "search_query.json")
        with open(query_filename, "w") as f:
            json.dump(query_data, f, indent=2)
        print(f"Search query saved to: {query_filename}")

        # Save the search parameters
        params_data = {"timestamp": timestamp, "parameters": params}
        params_filename = os.path.join(timestamp_dir, "search_params.json")
        with open(params_filename, "w") as f:
            json.dump(params_data, f, indent=2)
        print(f"Search parameters saved to: {params_filename}")

        # Make the API request and save results
        try:
            results = self.search(**kwargs)
            results_data = {
                "timestamp": timestamp,
                "query": params.get("keywords", ""),
                "parameters_used": params,
                "results": results,
            }
            results_filename = os.path.join(timestamp_dir, "search_results.json")
            with open(results_filename, "w") as f:
                json.dump(results_data, f, indent=2)
            print(f"Search results saved to: {results_filename}")

            # Print summary
            print(f"\nAll files saved to: {timestamp_dir}")
            if isinstance(results, dict):
                if "total" in results:
                    print(f"Search completed: {results.get('total', 0)} results found")
                elif "count" in results:
                    print(f"Search completed: {results.get('count', 0)} results found")
                else:
                    print("Search completed successfully")

        except Exception as e:
            print(f"\nError during search: {str(e)}")
            # Save error information
            error_data = {
                "timestamp": timestamp,
                "query": params.get("keywords", ""),
                "parameters_used": params,
                "error": str(e),
            }
            error_filename = os.path.join(timestamp_dir, "search_error.json")
            with open(error_filename, "w") as f:
                json.dump(error_data, f, indent=2)
            print(f"Error details saved to: {error_filename}")
            print(f"All files saved to: {timestamp_dir}")


def main():
    """Example usage of the VectorStock Search Client"""

    # Create client instance
    client = VectorStockSearchClient()

    # Example 1: Basic search
    print("Example 1: Basic search for 'business icons'")
    client.search_and_save(keywords="business icons", output_dir="search_results")

    print("\n" + "=" * 50 + "\n")

    # Example 2: Advanced search with multiple parameters
    print("Example 2: Advanced search with filters")
    client.search_and_save(
        keywords="nature landscape",
        category="landscapes-nature",
        free=True,
        svg_only=True,
        order="trending",
        page=1,
        output_dir="search_results",
    )

    print("\n" + "=" * 50 + "\n")

    # Example 3: Search with color filter
    print("Example 3: Search with color filter")
    client.search_and_save(
        keywords="abstract background",
        color="#3498db",  # Blue color
        color_threshold=7,
        score_popular=8,
        output_dir="search_results",
    )


if __name__ == "__main__":
    # Run examples
    main()

    # Or use it interactively
    print("\n" + "=" * 50 + "\n")
    print("You can also use the client interactively:")
    print(">>> client = VectorStockSearchClient()")
    print(
        ">>> client.search_and_save(keywords='your search term', category='business-finance')"
    )
