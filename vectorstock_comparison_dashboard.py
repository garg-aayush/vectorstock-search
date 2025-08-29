import json
import os

import pandas as pd
import streamlit as st

# Set page config
st.set_page_config(
    page_title="VectorStock Search Results Comparison Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .image-container {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f9f9f9;
        transition: all 0.3s ease;
    }
    .image-container:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .metadata-badge {
        display: inline-block;
        padding: 3px 8px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .license-expanded {
        background-color: #d4edda;
        color: #155724;
    }
    .license-exclusive {
        background-color: #cce5ff;
        color: #004085;
    }
    .credits-badge {
        background-color: #fff3cd;
        color: #856404;
    }
    .artist-badge {
        background-color: #f8d7da;
        color: #721c24;
    }
    .option-a-header {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .option-b-header {
        background-color: #fce4ec;
        color: #c2185b;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_prompt_queries():
    """Load the prompt queries from JSON file"""
    query_file = "data/Option-A-search-queries.json"
    if os.path.exists(query_file):
        with open(query_file, "r") as f:
            return json.load(f)
    return {}


@st.cache_data
def load_option_a_results(prompt_id):
    """Load OptionA baseline results for a specific prompt"""
    results_file = f"data/search_results/OptionA-rearranged-Baseline/{prompt_id}/search_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            data = json.load(f)
            return data.get("results", {}).get("images", [])
    return []


@st.cache_data
def load_option_b_results(prompt_id):
    """Load OptionB multi-query results for a specific prompt"""
    results_file = f"data/search_results/OptionB-prune-multi-queries/{prompt_id}/{prompt_id}_subset_100_final.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            data = json.load(f)
            return data.get("artworks", [])
    return []


@st.cache_data
def load_option_b_metadata(prompt_id):
    """Load OptionB metadata including search statistics"""
    results_file = f"data/search_results/OptionB-prune-multi-queries/{prompt_id}/{prompt_id}_subset_100_final.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            data = json.load(f)
            return data.get("selection_metadata", {})
    return {}


def prepare_dataframe(images):
    """Convert image list to pandas DataFrame"""
    if not images:
        return pd.DataFrame()

    flattened_images = []
    for img in images:
        flat_img = {
            "art_id": img.get("art_id"),
            "title": img.get("title", ""),
            "description": img.get("description", ""),
            "license": img.get("license", ""),
            "artist": img.get("artist", ""),
            "credits": img.get("credits", 0),
            "free": img.get("free", False),
            "preview_small_url": img.get("preview", {}).get("small", {}).get("url", ""),
            "preview_small_width": img.get("preview", {})
            .get("small", {})
            .get("width", 0),
            "preview_small_height": img.get("preview", {})
            .get("small", {})
            .get("height", 0),
            "preview_large_url": img.get("preview", {}).get("large", {}).get("url", ""),
            "preview_large_width": img.get("preview", {})
            .get("large", {})
            .get("width", 0),
            "preview_large_height": img.get("preview", {})
            .get("large", {})
            .get("height", 0),
        }
        flattened_images.append(flat_img)

    return pd.DataFrame(flattened_images)


def display_image_grid(images_df, title_prefix="", columns_per_row=4, key_prefix=""):
    """Display images in a grid layout"""
    if images_df.empty:
        st.warning("No images to display.")
        return

    # Display images in grid
    for idx in range(0, len(images_df), columns_per_row):
        cols = st.columns(columns_per_row)

        for col_idx in range(columns_per_row):
            if idx + col_idx < len(images_df):
                row = images_df.iloc[idx + col_idx]

                with cols[col_idx]:
                    with st.container():
                        # Display image
                        try:
                            st.image(
                                row["preview_small_url"],
                                caption=f"ID: {row['art_id']}",
                                use_column_width=True,
                            )
                        except Exception:
                            st.error("Failed to load image")

                        # Title
                        st.markdown(
                            f"**{row['title'][:40]}{'...' if len(row['title']) > 40 else ''}**"
                        )

                        # Metadata badges
                        col1, col2 = st.columns(2)
                        with col1:
                            license_class = (
                                "license-expanded"
                                if row["license"] == "expanded"
                                else "license-exclusive"
                            )
                            st.markdown(
                                f'<span class="metadata-badge {license_class}">{row["license"]}</span>',
                                unsafe_allow_html=True,
                            )
                        with col2:
                            st.markdown(
                                f'<span class="metadata-badge credits-badge">{row["credits"]} credits</span>',
                                unsafe_allow_html=True,
                            )

                        # Artist
                        st.caption(f"Artist: {row['artist']}")

                        # View details button
                        if st.button(
                            "View Details", key=f"{key_prefix}_details_{row['art_id']}"
                        ):
                            display_image_details(row)


def display_image_details(image_data):
    """Display detailed information about an image"""
    with st.expander("📋 Image Details", expanded=True):
        detail_col1, detail_col2 = st.columns([1, 2])

        with detail_col1:
            # Display larger preview
            st.image(image_data["preview_large_url"], use_column_width=True)

            # Download links
            st.markdown("### Preview Links")
            st.markdown(f"[Small Preview]({image_data['preview_small_url']})")
            st.markdown(f"[Large Preview]({image_data['preview_large_url']})")

        with detail_col2:
            st.markdown(f"### {image_data['title']}")
            st.markdown(f"**Art ID:** {image_data['art_id']}")
            st.markdown(f"**Artist:** {image_data['artist']}")
            st.markdown(f"**License:** {image_data['license']}")
            st.markdown(f"**Credits Required:** {image_data['credits']}")
            st.markdown(f"**Free:** {'Yes' if image_data['free'] else 'No'}")

            st.markdown("### Description")
            st.write(image_data["description"])

            st.markdown("### Dimensions")
            st.write(
                f"Small: {image_data['preview_small_width']}x{image_data['preview_small_height']}px"
            )
            st.write(
                f"Large: {image_data['preview_large_width']}x{image_data['preview_large_height']}px"
            )


def create_filters(images_df):
    """Create sidebar filters"""
    st.sidebar.header("🔍 Filters")

    # License filter
    licenses = sorted(images_df["license"].unique()) if not images_df.empty else []
    selected_licenses = st.sidebar.multiselect(
        "License Type", licenses, default=licenses, help="Filter by license type"
    )

    # Artist filter
    artists = sorted(images_df["artist"].unique()) if not images_df.empty else []
    selected_artist = st.sidebar.selectbox(
        "Artist", ["All"] + artists, help="Filter by specific artist"
    )

    # Credits filter
    if not images_df.empty:
        min_credits = int(images_df["credits"].min())
        max_credits = int(images_df["credits"].max())

        if min_credits == max_credits:
            st.sidebar.info(
                f"All images require {min_credits} credit{'s' if min_credits != 1 else ''}"
            )
            credits_range = (min_credits, max_credits)
        else:
            credits_range = st.sidebar.slider(
                "Credits Required",
                min_value=min_credits,
                max_value=max_credits,
                value=(min_credits, max_credits),
                help="Filter by credits required",
            )
    else:
        credits_range = (0, 10)

    # Search in title/description
    search_term = st.sidebar.text_input(
        "Search in Title/Description",
        placeholder="Enter keywords...",
        help="Search within image titles and descriptions",
    )

    return selected_licenses, selected_artist, credits_range, search_term


def apply_filters(df, licenses, artist, credits_range, search_term):
    """Apply filters to dataframe"""
    if df.empty:
        return df

    filtered_df = df.copy()

    # License filter
    if licenses:
        filtered_df = filtered_df[filtered_df["license"].isin(licenses)]

    # Artist filter
    if artist != "All":
        filtered_df = filtered_df[filtered_df["artist"] == artist]

    # Credits filter
    filtered_df = filtered_df[
        (filtered_df["credits"] >= credits_range[0])
        & (filtered_df["credits"] <= credits_range[1])
    ]

    # Search term filter
    if search_term:
        search_lower = search_term.lower()
        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(search_lower, na=False)
            | filtered_df["description"]
            .str.lower()
            .str.contains(search_lower, na=False)
        ]

    return filtered_df


def display_statistics_comparison(df_a, df_b):
    """Display comparison statistics for both options"""
    st.subheader("📊 Comparison Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="option-a-header"><h4>Option A - Baseline</h4></div>',
            unsafe_allow_html=True,
        )
        if not df_a.empty:
            st.metric("Total Images", len(df_a))
            st.metric("Unique Artists", df_a["artist"].nunique())
            st.metric("Average Credits", f"{df_a['credits'].mean():.2f}")

            # License distribution
            st.markdown("**License Distribution:**")
            license_counts = df_a["license"].value_counts()
            for license, count in license_counts.items():
                st.write(f"- {license}: {count} ({count/len(df_a)*100:.1f}%)")
        else:
            st.info("No data available")

    with col2:
        st.markdown(
            '<div class="option-b-header"><h4>Option B - Multi-Query</h4></div>',
            unsafe_allow_html=True,
        )
        if not df_b.empty:
            st.metric("Total Images", len(df_b))
            st.metric("Unique Artists", df_b["artist"].nunique())
            st.metric("Average Credits", f"{df_b['credits'].mean():.2f}")

            # License distribution
            st.markdown("**License Distribution:**")
            license_counts = df_b["license"].value_counts()
            for license, count in license_counts.items():
                st.write(f"- {license}: {count} ({count/len(df_b)*100:.1f}%)")
        else:
            st.info("No data available")


def find_common_images(df_a, df_b):
    """Find images that appear in both result sets"""
    if df_a.empty or df_b.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    common_ids = set(df_a["art_id"]) & set(df_b["art_id"])
    only_a_ids = set(df_a["art_id"]) - set(df_b["art_id"])
    only_b_ids = set(df_b["art_id"]) - set(df_a["art_id"])

    common_df = df_a[df_a["art_id"].isin(common_ids)]
    only_a_df = df_a[df_a["art_id"].isin(only_a_ids)]
    only_b_df = df_b[df_b["art_id"].isin(only_b_ids)]

    return common_df, only_a_df, only_b_df


def main():
    st.title("🔍 VectorStock Search Results Comparison Dashboard")
    st.markdown(
        "Compare results between **Option A (Baseline)** and **Option B (Multi-Query)**"
    )

    # Load prompt queries
    prompt_queries = load_prompt_queries()

    if not prompt_queries:
        st.error("Could not load prompt queries from data/Option-A-search-queries.json")
        return

    # Create prompt selector
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # Prompt selector
        prompt_options = list(prompt_queries.keys())
        selected_prompt = st.selectbox(
            "Select Prompt",
            prompt_options,
            format_func=lambda x: f"{x}: {prompt_queries[x][:50]}...",
        )

    with col2:
        # Display full query text
        st.info(f"**Query:** {prompt_queries[selected_prompt]}")

    with col3:
        # View mode selector
        view_mode = st.radio(
            "View Mode",
            ["Side by Side", "Option A Only", "Option B Only", "Comparison Analysis"],
            index=0,
        )

    # Load results for both options
    option_a_images = load_option_a_results(selected_prompt)
    option_b_images = load_option_b_results(selected_prompt)
    option_b_metadata = load_option_b_metadata(selected_prompt)

    # Convert to DataFrames
    df_a = prepare_dataframe(option_a_images)
    df_b = prepare_dataframe(option_b_images)

    # Display metadata info
    if option_b_metadata:
        st.info(
            f"**Option B Selection Info:** Selected {option_b_metadata.get('selected_count', 0)} images "
            f"from {option_b_metadata.get('original_total', 0)} total results"
        )

    # Create filters
    all_images_df = pd.concat([df_a, df_b], ignore_index=True).drop_duplicates(
        subset=["art_id"]
    )
    selected_licenses, selected_artist, credits_range, search_term = create_filters(
        all_images_df
    )

    # Apply filters
    filtered_df_a = apply_filters(
        df_a, selected_licenses, selected_artist, credits_range, search_term
    )
    filtered_df_b = apply_filters(
        df_b, selected_licenses, selected_artist, credits_range, search_term
    )

    # Display based on view mode
    if view_mode == "Side by Side":
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<div class="option-a-header"><h3>Option A - Baseline</h3></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"Showing {len(filtered_df_a)} of {len(df_a)} images")
            display_image_grid(filtered_df_a, columns_per_row=2, key_prefix="option_a")

        with col2:
            st.markdown(
                '<div class="option-b-header"><h3>Option B - Multi-Query</h3></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"Showing {len(filtered_df_b)} of {len(df_b)} images")
            display_image_grid(filtered_df_b, columns_per_row=2, key_prefix="option_b")

    elif view_mode == "Option A Only":
        st.markdown(
            '<div class="option-a-header"><h3>Option A - Baseline</h3></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"Showing {len(filtered_df_a)} of {len(df_a)} images")
        display_image_grid(filtered_df_a, columns_per_row=4, key_prefix="option_a_full")

    elif view_mode == "Option B Only":
        st.markdown(
            '<div class="option-b-header"><h3>Option B - Multi-Query</h3></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"Showing {len(filtered_df_b)} of {len(df_b)} images")
        display_image_grid(filtered_df_b, columns_per_row=4, key_prefix="option_b_full")

    elif view_mode == "Comparison Analysis":
        # Show statistics
        display_statistics_comparison(df_a, df_b)

        # Find common and unique images
        common_df, only_a_df, only_b_df = find_common_images(
            filtered_df_a, filtered_df_b
        )

        st.divider()

        # Display overlap analysis
        st.subheader("🔄 Overlap Analysis")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Common Images", len(common_df))
        with col2:
            st.metric("Only in Option A", len(only_a_df))
        with col3:
            st.metric("Only in Option B", len(only_b_df))

        # Show common images
        if not common_df.empty:
            st.subheader("🤝 Common Images")
            st.markdown(
                f"Images appearing in both result sets ({len(common_df)} images)"
            )
            display_image_grid(common_df, columns_per_row=4, key_prefix="common")

        # Show unique to Option A
        if not only_a_df.empty:
            with st.expander(
                f"📘 Unique to Option A ({len(only_a_df)} images)", expanded=False
            ):
                display_image_grid(only_a_df, columns_per_row=4, key_prefix="only_a")

        # Show unique to Option B
        if not only_b_df.empty:
            with st.expander(
                f"📕 Unique to Option B ({len(only_b_df)} images)", expanded=False
            ):
                display_image_grid(only_b_df, columns_per_row=4, key_prefix="only_b")

    # Footer
    st.markdown("---")
    st.caption("VectorStock Search Results Comparison Dashboard - Built with Streamlit")


if __name__ == "__main__":
    main()
