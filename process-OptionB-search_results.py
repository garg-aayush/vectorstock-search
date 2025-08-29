#!/usr/bin/env python3
"""
Process VectorStock search results from multiple search folders.

This script takes a folder containing multiple search_* subfolders and creates:
1. A JSON file with all unique artworks (no duplicate art IDs)
2. A CSV file mapping art IDs to the search folders they appeared in
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def load_search_results(search_folder: Path) -> List[Dict]:
    """Load search results from a search folder."""
    results_file = search_folder / "search_results.json"

    if not results_file.exists():
        print(f"Warning: {results_file} does not exist")
        return []

    try:
        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract images from the results
        if "results" in data and "images" in data["results"]:
            return data["results"]["images"]
        else:
            print(f"Warning: No images found in {results_file}")
            return []

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in {results_file}: {e}")
        return []
    except Exception as e:
        print(f"Error reading {results_file}: {e}")
        return []


def process_search_folders(
    input_folder: Path,
) -> tuple[Dict[int, Dict], Dict[int, List[str]]]:
    """
    Process all search_* folders in the input directory.

    Returns:
        - unique_artworks: Dict mapping art_id to artwork data
        - art_id_to_folders: Dict mapping art_id to list of folder names it appeared in
    """
    unique_artworks = {}
    art_id_to_folders = defaultdict(list)

    # Find all search_* folders
    search_folders = [
        f for f in input_folder.iterdir() if f.is_dir() and f.name.startswith("search_")
    ]

    # Sort folders for consistent processing order
    search_folders.sort(key=lambda x: x.name)

    print(
        f"Found {len(search_folders)} search folders: {[f.name for f in search_folders]}"
    )

    for search_folder in search_folders:
        folder_name = search_folder.name
        print(f"\nProcessing {folder_name}...")

        # Load artworks from this search folder
        artworks = load_search_results(search_folder)
        print(f"  Found {len(artworks)} artworks")

        for artwork in artworks:
            art_id = artwork.get("art_id")

            if art_id is None:
                print(f"  Warning: Artwork missing art_id: {artwork}")
                continue

            # Add to unique artworks (first occurrence wins)
            if art_id not in unique_artworks:
                unique_artworks[art_id] = artwork

            # Track which folders this art_id appeared in
            if folder_name not in art_id_to_folders[art_id]:
                art_id_to_folders[art_id].append(folder_name)

    return unique_artworks, dict(art_id_to_folders)


def save_unique_artworks_json(artworks: Dict[int, Dict], output_file: Path) -> None:
    """Save unique artworks to JSON file."""
    output_data = {
        "total_unique_artworks": len(artworks),
        "artworks": list(artworks.values()),
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(artworks)} unique artworks to {output_file}")


def save_art_id_mapping_csv(
    art_id_to_folders: Dict[int, List[str]], output_file: Path
) -> None:
    """Save art ID to folder mapping as CSV."""
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(["art_id", "search_folders"])

        # Write data (sort by art_id for consistency)
        for art_id in sorted(art_id_to_folders.keys()):
            folders = art_id_to_folders[art_id]
            # Join folder names with semicolon separator
            folders_str = ";".join(sorted(folders))
            writer.writerow([art_id, folders_str])

    print(
        f"✅ Saved art ID mapping for {len(art_id_to_folders)} artworks to {output_file}"
    )


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python process_search_results.py <input_folder>")
        print(
            "Example: python process_search_results.py data/search_results/OptionB-multi-queries/prompt1"
        )
        sys.exit(1)

    input_folder = Path(sys.argv[1])

    if not input_folder.exists() or not input_folder.is_dir():
        print(
            f"Error: Input folder '{input_folder}' does not exist or is not a directory"
        )
        sys.exit(1)

    print(f"Processing search results in: {input_folder}")
    print("=" * 60)

    # Process all search folders
    unique_artworks, art_id_to_folders = process_search_folders(input_folder)

    if not unique_artworks:
        print("No artworks found in any search folders!")
        sys.exit(1)

    # Generate output file names based on input folder
    base_name = input_folder.name
    output_folder = input_folder

    unique_artworks_file = output_folder / f"{base_name}_unique_artworks.json"
    art_id_mapping_file = output_folder / f"{base_name}_art_id_mapping.csv"

    # Save outputs
    save_unique_artworks_json(unique_artworks, unique_artworks_file)
    save_art_id_mapping_csv(art_id_to_folders, art_id_mapping_file)

    # Print summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Total unique artworks: {len(unique_artworks)}")
    print(f"Total art ID mappings: {len(art_id_to_folders)}")

    # Show distribution of how many folders each artwork appeared in
    folder_count_distribution = defaultdict(int)
    for folders in art_id_to_folders.values():
        folder_count_distribution[len(folders)] += 1

    print("\nArtwork appearance distribution:")
    for num_folders in sorted(folder_count_distribution.keys()):
        count = folder_count_distribution[num_folders]
        print(f"  {count} artworks appeared in {num_folders} folder(s)")


if __name__ == "__main__":
    main()
