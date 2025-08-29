#!/usr/bin/env python3
"""
Create a subset of 100 artwork IDs from the art_id_mapping CSV with the following logic:
1. Include ALL artworks that appear in multiple search folders (priority)
2. Fill remaining slots ensuring minimum 10 images from each search folder
3. Distribute remaining slots proportionally across search folders
4. Fill any remaining slots with available artworks to reach exactly 100
5. Shuffle the final selection and create a subset JSON
"""

import argparse
import csv
import json
import os
import random
from collections import Counter, defaultdict

import pandas as pd


def analyze_and_create_subset(csv_file_path, target_size=100, min_per_search=10):
    """
    Create a subset of artworks based on the specified criteria.

    Args:
        csv_file_path: Path to the CSV file with art_id and search_folders columns
        target_size: Target number of artworks in subset (default: 100)
        min_per_search: Minimum artworks per search folder (default: 10)

    Returns:
        List of selected art_ids and analysis results
    """

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Remove any empty rows
    df = df.dropna()

    # Analyze the data
    multi_folder_artworks = []
    single_folder_artworks = defaultdict(list)
    search_folder_counts = Counter()
    all_artworks = set()  # Track all available artworks

    print("=" * 60)
    print("DATA ANALYSIS")
    print("=" * 60)

    for _, row in df.iterrows():
        art_id = int(row["art_id"])  # Ensure art_id is integer
        search_folders = str(row["search_folders"]).strip()
        all_artworks.add(art_id)

        if ";" in search_folders:
            # Artwork appears in multiple folders
            multi_folder_artworks.append((art_id, search_folders))
            folders = search_folders.split(";")
            for folder in folders:
                search_folder_counts[folder.strip()] += 1
        else:
            # Artwork appears in single folder
            single_folder_artworks[search_folders].append(art_id)
            search_folder_counts[search_folders] += 1

    total_available = len(all_artworks)
    print(f"Total artworks available: {total_available}")
    print(f"Artworks in multiple folders: {len(multi_folder_artworks)}")
    print(f"Artworks in single folders: {len(df) - len(multi_folder_artworks)}")

    if total_available < target_size:
        print(
            f"WARNING: Only {total_available} artworks available, less than target {target_size}"
        )
        target_size = total_available

    print("\nDistribution across search folders:")
    for folder, count in sorted(search_folder_counts.items()):
        print(f"  {folder}: {count} artworks")

    print("\nSingle folder distribution:")
    for folder, artworks in sorted(single_folder_artworks.items()):
        print(f"  {folder}: {len(artworks)} artworks")

    # Step 1: Include ALL multi-folder artworks (highest priority)
    selected_artworks = []
    selected_art_ids = set()

    for art_id, folders in multi_folder_artworks:
        selected_artworks.append(
            {
                "art_id": art_id,
                "search_folders": folders,
                "selection_reason": "multi_folder",
            }
        )
        selected_art_ids.add(art_id)

    remaining_slots = target_size - len(selected_artworks)

    print("\n" + "=" * 60)
    print("SUBSET CREATION LOGIC")
    print("=" * 60)
    print(f"Step 1: Selected {len(selected_artworks)} multi-folder artworks")
    print(f"Remaining slots to fill: {remaining_slots}")

    if remaining_slots <= 0:
        print("Multi-folder artworks meet or exceed target size!")
        # Shuffle and return only the target size
        random.shuffle(selected_artworks)
        return selected_artworks[:target_size]

    # Step 2: Ensure minimum representation from each search folder
    search_folders = [f"search_{i}" for i in range(1, 7)]  # search_1 to search_6

    # Count how many from each folder we already have (from multi-folder artworks)
    current_folder_counts = defaultdict(int)
    for artwork in selected_artworks:
        folders = artwork["search_folders"].split(";")
        for folder in folders:
            current_folder_counts[folder.strip()] += 1

    print(f"\nStep 2: Ensuring minimum {min_per_search} per search folder")
    print("Current representation from multi-folder artworks:")
    for folder in search_folders:
        count = current_folder_counts.get(folder, 0)
        print(f"  {folder}: {count} artworks")

    # Add artworks to meet minimum requirements
    for folder in search_folders:
        current_count = current_folder_counts.get(folder, 0)
        needed = max(0, min_per_search - current_count)

        if needed > 0 and remaining_slots > 0:
            available_artworks = [
                aid
                for aid in single_folder_artworks.get(folder, [])
                if aid not in selected_art_ids
            ]
            to_add = min(needed, len(available_artworks), remaining_slots)

            if to_add > 0:
                # Randomly select artworks to add
                selected_from_folder = random.sample(available_artworks, to_add)

                for art_id in selected_from_folder:
                    selected_artworks.append(
                        {
                            "art_id": art_id,
                            "search_folders": folder,
                            "selection_reason": "min_requirement",
                        }
                    )
                    selected_art_ids.add(art_id)

                remaining_slots -= to_add
                current_folder_counts[folder] += to_add

                print(
                    f"Added {to_add} artworks from {folder} to meet minimum requirement"
                )

    print("\nAfter meeting minimum requirements:")
    print(f"Selected artworks: {len(selected_artworks)}")
    print(f"Remaining slots: {remaining_slots}")

    # Step 3: Fill remaining slots proportionally
    if remaining_slots > 0:
        print(f"\nStep 3: Filling remaining {remaining_slots} slots proportionally")

        # Get all remaining available artworks
        all_remaining = []
        for folder in search_folders:
            available_artworks = [
                aid
                for aid in single_folder_artworks.get(folder, [])
                if aid not in selected_art_ids
            ]
            for art_id in available_artworks:
                all_remaining.append((art_id, folder))

        total_remaining = len(all_remaining)
        print(f"Total remaining artworks available: {total_remaining}")

        if total_remaining > 0:
            # Calculate proportional distribution based on folder sizes
            folder_remaining = {}
            for folder in search_folders:
                available_count = len(
                    [
                        aid
                        for aid in single_folder_artworks.get(folder, [])
                        if aid not in selected_art_ids
                    ]
                )
                folder_remaining[folder] = available_count

            total_folder_remaining = sum(folder_remaining.values())

            if total_folder_remaining > 0:
                for folder in search_folders:
                    available_count = folder_remaining[folder]
                    if available_count > 0:
                        # Calculate proportional allocation
                        proportion = available_count / total_folder_remaining
                        target_to_add = int(remaining_slots * proportion)

                        # Add extra slot if there's a remainder and we're not at target yet
                        if (remaining_slots * proportion) % 1 > 0.5:
                            target_to_add += 1

                        available_artworks = [
                            aid
                            for aid in single_folder_artworks.get(folder, [])
                            if aid not in selected_art_ids
                        ]
                        to_add = min(
                            target_to_add, len(available_artworks), remaining_slots
                        )

                        if to_add > 0:
                            selected_from_folder = random.sample(
                                available_artworks, to_add
                            )

                            for art_id in selected_from_folder:
                                selected_artworks.append(
                                    {
                                        "art_id": art_id,
                                        "search_folders": folder,
                                        "selection_reason": "proportional",
                                    }
                                )
                                selected_art_ids.add(art_id)

                            remaining_slots -= to_add
                            current_folder_counts[folder] += to_add

                            print(
                                f"Added {to_add} artworks from {folder} (proportional)"
                            )

    # Step 4: Fill any remaining slots with ANY available artworks to reach target
    if remaining_slots > 0:
        print(
            f"\nStep 4: Filling final {remaining_slots} slots with any available artworks"
        )

        # Get all remaining artworks from any folder
        all_remaining_artworks = []
        for folder, art_ids in single_folder_artworks.items():
            for art_id in art_ids:
                if art_id not in selected_art_ids:
                    all_remaining_artworks.append((art_id, folder))

        if len(all_remaining_artworks) >= remaining_slots:
            final_selection = random.sample(all_remaining_artworks, remaining_slots)

            for art_id, folder in final_selection:
                selected_artworks.append(
                    {
                        "art_id": art_id,
                        "search_folders": folder,
                        "selection_reason": "fill_to_target",
                    }
                )
                selected_art_ids.add(art_id)

            remaining_slots = 0
            print(f"Added {len(final_selection)} artworks to reach target size")
        else:
            print(
                f"WARNING: Only {len(all_remaining_artworks)} artworks left, cannot reach target"
            )

    # Step 5: Shuffle the final selection
    print("\nStep 5: Shuffling the final selection...")
    random.shuffle(selected_artworks)

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUBSET SUMMARY")
    print("=" * 60)
    print(f"Target size: {target_size}")
    print(f"Actual selected artworks: {len(selected_artworks)}")
    print("Final distribution:")

    final_counts = defaultdict(int)
    reason_counts = defaultdict(int)

    for artwork in selected_artworks:
        folders = artwork["search_folders"].split(";")
        reason_counts[artwork["selection_reason"]] += 1
        for folder in folders:
            final_counts[folder.strip()] += 1

    for folder in search_folders:
        count = final_counts.get(folder, 0)
        print(f"  {folder}: {count} artworks")

    print("\nSelection reasons:")
    for reason, count in reason_counts.items():
        print(f"  {reason}: {count} artworks")

    return selected_artworks


def create_subset_json(selected_artworks, original_json_path, output_json_path):
    """
    Create a subset JSON file containing only the selected artworks.

    Args:
        selected_artworks: List of selected artwork dictionaries
        original_json_path: Path to the original unique artworks JSON file
        output_json_path: Path for the output subset JSON file
    """

    # Extract the art_ids from selected artworks
    selected_art_ids = {artwork["art_id"] for artwork in selected_artworks}

    print(f"\nCreating subset JSON from {len(selected_art_ids)} selected artworks...")

    # Load the original JSON file
    try:
        with open(original_json_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)
    except Exception as e:
        print(f"Error reading original JSON file: {e}")
        return

    # Filter artworks to include only selected ones
    subset_artworks = []
    found_art_ids = set()

    if "artworks" in original_data:
        for artwork in original_data["artworks"]:
            if artwork.get("art_id") in selected_art_ids:
                subset_artworks.append(artwork)
                found_art_ids.add(artwork.get("art_id"))

    # Check if all selected artworks were found
    missing_art_ids = selected_art_ids - found_art_ids
    if missing_art_ids:
        print(
            f"Warning: {len(missing_art_ids)} selected artworks were not found in the original JSON:"
        )
        for art_id in list(missing_art_ids)[:5]:  # Show first 5 missing
            print(f"  {art_id}")
        if len(missing_art_ids) > 5:
            print(f"  ... and {len(missing_art_ids) - 5} more")

    # Create the subset JSON structure
    subset_data = {
        "total_unique_artworks": len(subset_artworks),
        "selection_metadata": {
            "original_total": original_data.get(
                "total_unique_artworks", len(original_data.get("artworks", []))
            ),
            "selected_count": len(selected_artworks),
            "found_count": len(found_art_ids),
            "missing_count": len(missing_art_ids),
        },
        "artworks": subset_artworks,
    }

    # Save the subset JSON
    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(subset_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Subset JSON saved to: {output_json_path}")
        print(
            f"   Original artworks: {original_data.get('total_unique_artworks', 'unknown')}"
        )
        print(f"   Subset artworks: {len(subset_artworks)}")
        print(f"   Found: {len(found_art_ids)}, Missing: {len(missing_art_ids)}")

    except Exception as e:
        print(f"Error saving subset JSON: {e}")


def save_subset_csv(selected_artworks, output_file):
    """Save the selected subset to a CSV file."""
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["art_id", "search_folders", "selection_reason"])

        for artwork in selected_artworks:
            writer.writerow(
                [
                    artwork["art_id"],
                    artwork["search_folders"],
                    artwork["selection_reason"],
                ]
            )

    print(f"✅ Subset CSV saved to: {output_file}")


if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)

    parser = argparse.ArgumentParser(description="Prune search results")
    parser.add_argument(
        "--substr",
        type=str,
        default="prompt1",
        help="Substring for the output directory",
    )
    args = parser.parse_args()

    substr = args.substr

    # Input and output files
    input_csv = f"/Users/aayushgarg/JIFFY/JED-433-VectorStockSearch/data/search_results/OptionB-multi-queries/{substr}/{substr}_art_id_mapping.csv"
    original_json = f"/Users/aayushgarg/JIFFY/JED-433-VectorStockSearch/data/search_results/OptionB-multi-queries/{substr}/{substr}_unique_artworks.json"

    output_dir = f"/Users/aayushgarg/JIFFY/JED-433-VectorStockSearch/data/search_results/OptionB-prune-multi-queries/{substr}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_csv = f"{output_dir}/{substr}_subset_100_final.csv"
    output_json = f"{output_dir}/{substr}_subset_100_final.json"

    # Create the subset
    selected_artworks = analyze_and_create_subset(
        input_csv, target_size=100, min_per_search=10
    )

    # Save the results
    save_subset_csv(selected_artworks, output_csv)

    # Create and save the subset JSON
    create_subset_json(selected_artworks, original_json, output_json)

    print("\n" + "=" * 60)
    print("PROCESS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 CSV subset: {output_csv}")
    print(f"📄 JSON subset: {output_json}")
    print(f"📄 JSON subset: {output_json}")
