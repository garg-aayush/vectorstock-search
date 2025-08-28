import json
import os
import sys
from datetime import datetime
from io import BytesIO

import pandas as pd
import requests
import streamlit as st
from PIL import Image

# Add the src directory to the path so we can import the search client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.vectorstock_keyword_search import VectorStockSearchClient

# Set page config
st.set_page_config(
    page_title="VectorStock Search Results Dashboard",
    page_icon="🎨",
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
    </style>
    """,
    unsafe_allow_html=True,
)


def get_available_searches():
    """Get list of available search results"""
    search_results_dir = "search_results"
    if not os.path.exists(search_results_dir):
        return []

    searches = []
    for timestamp_dir in sorted(os.listdir(search_results_dir), reverse=True):
        dir_path = os.path.join(search_results_dir, timestamp_dir)
        if os.path.isdir(dir_path):
            results_file = os.path.join(dir_path, "search_results.json")
            if os.path.exists(results_file):
                try:
                    with open(results_file, "r") as f:
                        data = json.load(f)
                        searches.append(
                            {
                                "timestamp": timestamp_dir,
                                "query": data.get("query", "Unknown"),
                                "total": data.get("results", {}).get("total", 0),
                                "page": data.get("results", {}).get("page", 1),
                                "path": results_file,
                            }
                        )
                except Exception:
                    pass
    return searches


@st.cache_data
def load_search_results(json_path):
    """Load search results from JSON file"""
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return None


@st.cache_data
def load_image_from_url(url):
    """Load image from URL with error handling"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"Failed to load image: {str(e)}")
    return None


def display_search_metadata(data):
    """Display search metadata in the header"""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Search Query", data["query"])
    with col2:
        st.metric("Images Loaded", len(data["results"]["images"]))
    with col3:
        st.metric("Total Available", f"{data['results']['total']:,}")
    with col4:
        st.metric(
            "Current Page", f"{data['results']['page']} / {data['results']['pages']:,}"
        )
    with col5:
        timestamp = datetime.strptime(data["timestamp"], "%Y%m%d_%H%M%S")
        st.metric("Search Date", timestamp.strftime("%Y-%m-%d %H:%M"))


def create_filters(images_df):
    """Create sidebar filters"""
    st.sidebar.header("🔍 Filters")

    # License filter
    licenses = sorted(images_df["license"].unique())
    selected_licenses = st.sidebar.multiselect(
        "License Type", licenses, default=licenses, help="Filter by license type"
    )

    # Artist filter
    artists = sorted(images_df["artist"].unique())
    selected_artist = st.sidebar.selectbox(
        "Artist", ["All"] + artists, help="Filter by specific artist"
    )

    # Credits filter
    min_credits = int(images_df["credits"].min())
    max_credits = int(images_df["credits"].max())

    if min_credits == max_credits:
        # If all images have the same credit value, just display it
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

    # Free/Paid filter
    free_filter = st.sidebar.radio(
        "Type", ["All", "Free Only", "Paid Only"], help="Filter by free or paid images"
    )

    # Search in title/description
    search_term = st.sidebar.text_input(
        "Search in Title/Description",
        placeholder="Enter keywords...",
        help="Search within image titles and descriptions",
    )

    return selected_licenses, selected_artist, credits_range, free_filter, search_term


def apply_filters(df, licenses, artist, credits_range, free_filter, search_term):
    """Apply filters to dataframe"""
    filtered_df = df.copy()

    # License filter
    filtered_df = filtered_df[filtered_df["license"].isin(licenses)]

    # Artist filter
    if artist != "All":
        filtered_df = filtered_df[filtered_df["artist"] == artist]

    # Credits filter
    filtered_df = filtered_df[
        (filtered_df["credits"] >= credits_range[0])
        & (filtered_df["credits"] <= credits_range[1])
    ]

    # Free/Paid filter
    if free_filter == "Free Only":
        filtered_df = filtered_df[filtered_df["free"]]
    elif free_filter == "Paid Only":
        filtered_df = filtered_df[~filtered_df["free"]]

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


def display_image_grid(filtered_df, original_df, columns_per_row=4):
    """Display images in a grid layout"""
    if filtered_df.empty:
        st.warning("No images match the current filters.")
        return

    st.subheader(f"📸 Showing {len(filtered_df)} of {len(original_df)} loaded images")

    # Sort options
    sort_col1, sort_col2 = st.columns([3, 1])
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by",
            [
                "Art ID",
                "Title",
                "Artist",
                "Credits (Low to High)",
                "Credits (High to Low)",
            ],
            key="sort_select",
        )

    # Apply sorting
    if sort_by == "Art ID":
        filtered_df = filtered_df.sort_values("art_id")
    elif sort_by == "Title":
        filtered_df = filtered_df.sort_values("title")
    elif sort_by == "Artist":
        filtered_df = filtered_df.sort_values("artist")
    elif sort_by == "Credits (Low to High)":
        filtered_df = filtered_df.sort_values("credits")
    elif sort_by == "Credits (High to Low)":
        filtered_df = filtered_df.sort_values("credits", ascending=False)

    # Display images in grid
    for idx in range(0, len(filtered_df), columns_per_row):
        cols = st.columns(columns_per_row)

        for col_idx in range(columns_per_row):
            if idx + col_idx < len(filtered_df):
                row = filtered_df.iloc[idx + col_idx]

                with cols[col_idx]:
                    with st.container():
                        # Display image
                        try:
                            st.image(
                                row["preview_small_url"],
                                width="stretch",
                                caption=f"ID: {row['art_id']}",
                            )
                        except Exception:
                            st.error("Failed to load image")

                        # Title
                        st.markdown(
                            f"**{row['title'][:50]}{'...' if len(row['title']) > 50 else ''}**"
                        )

                        # View details button
                        if st.button("View Details", key=f"details_{row['art_id']}"):
                            display_image_details(row)


def display_image_details(image_data):
    """Display detailed information about an image in a modal-like view"""
    with st.expander("📋 Image Details", expanded=True):
        detail_col1, detail_col2 = st.columns([1, 2])

        with detail_col1:
            # Display larger preview
            st.image(image_data["preview_large_url"], width="stretch")

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


def prepare_dataframe(data):
    """Convert JSON data to pandas DataFrame for easier manipulation"""
    images = data["results"]["images"]

    # Flatten the nested structure
    flattened_images = []
    for img in images:
        flat_img = {
            "art_id": img["art_id"],
            "title": img["title"],
            "description": img["description"],
            "license": img["license"],
            "artist": img["artist"],
            "credits": img["credits"],
            "free": img["free"],
            "preview_small_url": img["preview"]["small"]["url"],
            "preview_small_width": img["preview"]["small"]["width"],
            "preview_small_height": img["preview"]["small"]["height"],
            "preview_large_url": img["preview"]["large"]["url"],
            "preview_large_width": img["preview"]["large"]["width"],
            "preview_large_height": img["preview"]["large"]["height"],
        }
        flattened_images.append(flat_img)

    return pd.DataFrame(flattened_images)


def display_statistics(df):
    """Display statistics about the search results"""
    with st.expander("📊 Statistics", expanded=False):
        stat_col1, stat_col2, stat_col3 = st.columns(3)

        with stat_col1:
            st.markdown("### License Distribution")
            license_counts = df["license"].value_counts()
            st.bar_chart(license_counts)

        with stat_col2:
            st.markdown("### Top Artists")
            top_artists = df["artist"].value_counts().head(10)
            st.bar_chart(top_artists)

        with stat_col3:
            st.markdown("### Credits Distribution")
            credits_dist = df["credits"].value_counts().sort_index()
            st.bar_chart(credits_dist)


def check_existing_search(search_params):
    """Check if we already have results for these exact search parameters"""
    search_results_dir = "search_results"
    if not os.path.exists(search_results_dir):
        return None

    print(f"\n🔍 Checking cache for parameters: {search_params}")

    # Check each existing search
    for timestamp_dir in os.listdir(search_results_dir):
        dir_path = os.path.join(search_results_dir, timestamp_dir)
        if os.path.isdir(dir_path):
            params_file = os.path.join(dir_path, "search_params.json")
            if os.path.exists(params_file):
                try:
                    with open(params_file, "r") as f:
                        saved_params_data = json.load(f)
                        saved_params = saved_params_data.get("parameters", {})

                        # Compare parameters (excluding timestamp)
                        if saved_params == search_params:
                            # Found matching search!
                            results_file = os.path.join(dir_path, "search_results.json")
                            if os.path.exists(results_file):
                                print(
                                    f"   ✅ Cache hit! Found matching search from {timestamp_dir}"
                                )
                                return {
                                    "timestamp": timestamp_dir,
                                    "path": results_file,
                                    "params": saved_params,
                                }
                except Exception:
                    pass

    print("   ❌ No cache match found")
    return None


def run_new_search(keywords, **kwargs):
    """Run a new search using the VectorStock API"""
    with st.spinner(f"Searching for '{keywords}'..."):
        try:
            # Remove any None values from kwargs
            search_params = {"keywords": keywords}
            search_params.update({k: v for k, v in kwargs.items() if v is not None})

            # Check if we already have these exact results
            existing_search = check_existing_search(search_params)

            if existing_search:
                # Use cached results
                timestamp = datetime.strptime(
                    existing_search["timestamp"], "%Y%m%d_%H%M%S"
                )
                cache_msg = (
                    f"✨ Using cached results from {timestamp.strftime('%Y-%m-%d %H:%M:%S')}. "
                    f"These search parameters were already queried."
                )
                print(f"\n{cache_msg}")  # Log to terminal
                st.info(cache_msg)  # Show briefly in UI
                st.success("Search results loaded from cache!")
            else:
                # Make new API call
                print(f"\n🔍 Making new API call for: {keywords}")
                print(f"   Parameters: {search_params}")
                client = VectorStockSearchClient()
                client.search_and_save(output_dir="search_results", **search_params)
                st.success("Search completed! New results saved.")

            st.rerun()  # Refresh the page to show results
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            print(f"\n❌ {error_msg}")  # Log error to terminal
            st.error(error_msg)


def main():
    st.title("🎨 VectorStock Search Results Dashboard")

    # Log dashboard refresh (helps debug when rerun happens)
    print("\n📊 Dashboard refreshed")

    # Search Interface Section
    with st.container():
        st.subheader("🔎 Search VectorStock")

        with st.form("search_form"):
            # Basic search parameters
            st.markdown("### Basic Search")
            col1, col2, col3 = st.columns(3)

            with col1:
                keywords = st.text_input(
                    "Keywords *",
                    placeholder="e.g., Halloween, business icons",
                    help="Search keywords (required)",
                )
                category = st.selectbox(
                    "Category",
                    [""] + VectorStockSearchClient().valid_categories,
                    help="Filter by category",
                )

            with col2:
                artist = st.text_input(
                    "Artist",
                    placeholder="Artist name",
                    help="Filter by specific artist",
                )
                page = st.number_input(
                    "Page", min_value=1, value=1, help="Page number to fetch"
                )

            with col3:
                order = st.selectbox(
                    "Sort by",
                    ["bestmatch", "trending", "latest", "isolated", "featured"],
                    help="Sort order for results",
                )
                count_only = st.checkbox(
                    "Count only", help="Return only the count of results (no images)"
                )

            # License and format filters
            st.markdown("### License & Format Filters")
            col4, col5, col6, col7 = st.columns(4)

            with col4:
                free_only = st.checkbox("Free only", help="Show only free images")
                expanded_only = st.checkbox("Expanded license only")
                editorial = st.checkbox(
                    "Include editorial", help="Include editorial licenses"
                )

            with col5:
                svg_only = st.checkbox("SVG only", help="Only SVG format")
                png_only = st.checkbox("PNG only", help="Only transparent PNG")
                cmyk_only = st.checkbox("CMYK only", help="CMYK color model only")

            with col6:
                templates_only = st.checkbox(
                    "Templates only", help="Template vectors only"
                )
                pod_first = st.checkbox("POD first", help="Show Print-On-Demand first")

            with col7:
                object_detection = st.selectbox(
                    "Object detection",
                    ["", "show_objects", "hide_objects"],
                    help="Filter by object detection",
                )

            # Advanced filters
            with st.expander("🔧 Advanced Filters", expanded=False):
                adv_col1, adv_col2, adv_col3 = st.columns(3)

                with adv_col1:
                    st.markdown("**Object Count**")
                    object_count_min = st.number_input(
                        "Min objects",
                        min_value=1,
                        max_value=200,
                        value=1,
                        help="Minimum object count (1-200)",
                    )
                    object_count_max = st.number_input(
                        "Max objects",
                        min_value=1,
                        max_value=200,
                        value=200,
                        help="Maximum object count (1-200)",
                    )

                with adv_col2:
                    st.markdown("**Color Filter**")
                    color = st.text_input(
                        "Color (hex)",
                        placeholder="#FF0000",
                        help="Hex color code (e.g., #FF0000 or FF0000)",
                    )
                    color_threshold = st.slider(
                        "Color threshold",
                        min_value=1,
                        max_value=10,
                        value=5,
                        help="Color matching threshold (1-10)",
                    )

                with adv_col3:
                    st.markdown("**Scoring**")
                    score_popular = st.slider(
                        "Popularity score",
                        min_value=1,
                        max_value=10,
                        value=5,
                        help="Popularity score filter (1-10)",
                    )
                    artist_score = st.slider(
                        "Artist score",
                        min_value=1,
                        max_value=10,
                        value=5,
                        help="Artist score filter (1-10)",
                    )

            submitted = st.form_submit_button(
                "🔍 Search", use_container_width=True, type="primary"
            )

            if submitted:
                if keywords:
                    # Build search parameters
                    search_params = {"page": page, "order": order}

                    # Add optional parameters if provided
                    if category:
                        search_params["category"] = category
                    if artist:
                        search_params["artist"] = artist
                    if free_only:
                        search_params["free"] = True
                    if expanded_only:
                        search_params["expanded"] = True
                    if editorial:
                        search_params["editorial"] = True
                    if svg_only:
                        search_params["svg_only"] = True
                    if png_only:
                        search_params["png_only"] = True
                    if cmyk_only:
                        search_params["cmyk_only"] = True
                    if templates_only:
                        search_params["templates_only"] = True
                    if pod_first:
                        search_params["pod_first"] = True
                    if count_only:
                        search_params["count_only"] = True
                    if object_detection:
                        search_params["object_detection"] = object_detection

                    # Advanced filters
                    if object_count_min != 1 or object_count_max != 200:
                        if object_count_min <= object_count_max:
                            search_params["object_count_min"] = object_count_min
                            search_params["object_count_max"] = object_count_max
                        else:
                            st.error(
                                "Min objects must be less than or equal to max objects"
                            )
                            return

                    if color:
                        search_params["color"] = color
                        search_params["color_threshold"] = color_threshold

                    if score_popular != 5:
                        search_params["score_popular"] = score_popular
                    if artist_score != 5:
                        search_params["artist_score"] = artist_score

                    run_new_search(keywords, **search_params)
                else:
                    st.error("Please enter search keywords")

    st.divider()

    # Load existing searches
    available_searches = get_available_searches()

    if not available_searches:
        st.warning(
            "No search results found. Use the search form above to create your first search!"
        )
        return

    # Search result selector
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            # Create display options for the selectbox and track duplicates
            search_options = []
            params_seen = {}

            for i, search in enumerate(available_searches):
                timestamp = datetime.strptime(search["timestamp"], "%Y%m%d_%H%M%S")

                # Load the actual parameters for this search
                params_file = os.path.join(
                    os.path.dirname(search["path"]), "search_params.json"
                )
                search_params_str = ""
                if os.path.exists(params_file):
                    try:
                        with open(params_file, "r") as f:
                            params_data = json.load(f)
                            params = params_data.get("parameters", {})
                            # Create a string representation of params for comparison
                            search_params_str = json.dumps(params, sort_keys=True)
                    except Exception:
                        pass

                # Check if we've seen these params before
                is_duplicate = ""
                if search_params_str and search_params_str in params_seen:
                    is_duplicate = (
                        " 🔄"  # Recycling symbol to indicate cached/duplicate
                    )
                else:
                    params_seen[search_params_str] = i

                display_text = f"{search['query']} - {timestamp.strftime('%Y-%m-%d %H:%M')} (Page {search['page']}, {search['total']:,} total){is_duplicate}"
                search_options.append(display_text)

            selected_idx = st.selectbox(
                "📂 Select search results to view:",
                range(len(search_options)),
                format_func=lambda x: search_options[x],
                help="Choose from previous search results",
            )

    # Load selected search results
    selected_search = available_searches[selected_idx]
    data = load_search_results(selected_search["path"])

    if data is None:
        st.error("Failed to load search results. The file may be corrupted.")
        return

    # Display search metadata
    display_search_metadata(data)

    # Check if we have any images
    if not data["results"]["images"]:
        st.warning(
            f"⚠️ No images found on page {data['results']['page']}. "
            f"VectorStock has {data['results']['total']:,} total results across {data['results']['pages']:,} pages. "
            f"Try searching for a different page number (1 to {data['results']['pages']})."
        )

        # Show search history for easy access to other results
        st.info(
            "💡 Tip: Use the dropdown above to switch to other search results, or run a new search."
        )
        return

    # Add info about pagination
    st.info(
        f"ℹ️ Showing {len(data['results']['images'])} images from page {data['results']['page']}. "
        f"VectorStock has {data['results']['total']:,} total results across {data['results']['pages']:,} pages. "
        f"To fetch more pages, use the search script with the 'page' parameter."
    )

    # Prepare DataFrame
    images_df = prepare_dataframe(data)

    # Create filters in sidebar
    selected_licenses, selected_artist, credits_range, free_filter, search_term = (
        create_filters(images_df)
    )

    # Apply filters
    filtered_df = apply_filters(
        images_df,
        selected_licenses,
        selected_artist,
        credits_range,
        free_filter,
        search_term,
    )

    # Display statistics
    display_statistics(images_df)

    # Display image grid
    display_image_grid(filtered_df, images_df)

    # Footer
    st.markdown("---")
    st.caption("VectorStock Search Results Dashboard - Built with Streamlit")


if __name__ == "__main__":
    main()
