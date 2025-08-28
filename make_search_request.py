#!/usr/bin/env python3
"""
VectorStock Search CLI

Command-line interface for the VectorStock Search API
"""

import argparse

from src.vectorstock_keyword_search import VectorStockSearchClient


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Search VectorStock API and save results to JSON files"
    )

    # Required argument
    parser.add_argument("keywords", help="Search keywords (required)")

    # Optional arguments
    parser.add_argument(
        "--category",
        help="Category filter",
        choices=VectorStockSearchClient().valid_categories,
    )
    parser.add_argument("--artist", help="Artist name filter")
    parser.add_argument("--page", type=int, help="Page number for pagination")
    parser.add_argument("--free", action="store_true", help="Search free vectors only")
    parser.add_argument(
        "--expanded", action="store_true", help="Expanded license vectors only"
    )
    parser.add_argument(
        "--object-detection",
        choices=["show_objects", "hide_objects"],
        help="Object detection filter",
    )
    parser.add_argument(
        "--object-count-min", type=int, help="Minimum object count (1-200)"
    )
    parser.add_argument(
        "--object-count-max", type=int, help="Maximum object count (1-200)"
    )
    parser.add_argument("--svg-only", action="store_true", help="SVG files only")
    parser.add_argument(
        "--templates-only", action="store_true", help="Template vectors only"
    )
    parser.add_argument(
        "--pod-first", action="store_true", help="Show Print-On-Demand first"
    )
    parser.add_argument(
        "--cmyk-only", action="store_true", help="CMYK color model only"
    )
    parser.add_argument(
        "--png-only", action="store_true", help="Transparent PNG files only"
    )
    parser.add_argument(
        "--editorial", action="store_true", help="Include editorial licenses"
    )
    parser.add_argument("--count-only", action="store_true", help="Return count only")
    parser.add_argument("--color", help="Hex color code (e.g., #FF0000 or FF0000)")
    parser.add_argument("--color-threshold", type=int, help="Color threshold (1-10)")
    parser.add_argument("--score-popular", type=int, help="Popularity score (1-10)")
    parser.add_argument("--artist-score", type=int, help="Artist score (1-10)")
    parser.add_argument(
        "--order",
        choices=["trending", "bestmatch", "latest", "isolated", "featured"],
        help="Sort order",
    )
    parser.add_argument(
        "--output-dir",
        default="search_results",
        help="Output directory for JSON files (default: search_results)",
    )

    return parser


def main():
    """Main CLI function"""
    parser = create_parser()
    args = parser.parse_args()

    # Build search parameters from command line arguments
    search_params = {"keywords": args.keywords}

    # Add optional parameters if provided
    if args.category:
        search_params["category"] = args.category
    if args.artist:
        search_params["artist"] = args.artist
    if args.page:
        search_params["page"] = args.page
    if args.free:
        search_params["free"] = True
    if args.expanded:
        search_params["expanded"] = True
    if args.object_detection:
        search_params["object_detection"] = args.object_detection
    if args.object_count_min:
        search_params["object_count_min"] = args.object_count_min
    if args.object_count_max:
        search_params["object_count_max"] = args.object_count_max
    if args.svg_only:
        search_params["svg_only"] = True
    if args.templates_only:
        search_params["templates_only"] = True
    if args.pod_first:
        search_params["pod_first"] = True
    if args.cmyk_only:
        search_params["cmyk_only"] = True
    if args.png_only:
        search_params["png_only"] = True
    if args.editorial:
        search_params["editorial"] = True
    if args.count_only:
        search_params["count_only"] = True
    if args.color:
        search_params["color"] = args.color
    if args.color_threshold:
        search_params["color_threshold"] = args.color_threshold
    if args.score_popular:
        search_params["score_popular"] = args.score_popular
    if args.artist_score:
        search_params["artist_score"] = args.artist_score
    if args.order:
        search_params["order"] = args.order

    # Create client and perform search
    client = VectorStockSearchClient()

    print(f"Searching for: {args.keywords}")
    print(f"Output directory: {args.output_dir}")
    print("-" * 50)

    try:
        client.search_and_save(output_dir=args.output_dir, **search_params)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
