# VectorStock Search Results Dashboard

A web-based dashboard for visualizing and exploring VectorStock search results. This dashboard provides an intuitive interface to browse, filter, and analyze vector stock images from search queries.

## Features

- **Integrated Search**: Run new VectorStock searches directly from the dashboard
  - **All API Parameters Supported**: Keywords, category, artist, page, sort order
  - **License Filters**: Free only, expanded license, editorial inclusion
  - **Format Filters**: SVG, PNG, CMYK, templates, POD priority
  - **Advanced Filters**: Object detection, object count, color matching, popularity/artist scores
  - **Smart Caching**: Automatically detects and reuses cached results for identical search parameters
- **Search History**: Browse and switch between previous search results
  - Shows 🔄 symbol for searches with duplicate parameters
  - Displays timestamp, query, page number, and total results
- **Visual Image Grid**: Display search results in a responsive grid layout with preview images
- **Advanced Filtering**: Filter loaded results by:
  - License type (expanded/exclusive)
  - Artist
  - Credits required
  - Free vs Paid images
  - Search within titles and descriptions
- **Sorting Options**: Sort images by Art ID, Title, Artist, or Credits
- **Detailed View**: Click "View Details" on any image to see:
  - Larger preview
  - Complete description
  - Image dimensions
  - Direct links to preview images
- **Statistics Dashboard**: Visual charts showing:
  - License distribution
  - Top artists
  - Credits distribution
- **Search Metadata**: Display search query, loaded images count, total available results, and timestamp

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd /Users/aayushgarg/JIFFY/JED-433-VectorStockSearch
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .vectorstock-dashboard
   source .vectorstock-dashboard/bin/activate  # On macOS/Linux
   # Or on Windows: .vectorstock-dashboard\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Dashboard

1. Make sure your virtual environment is activated:
   ```bash
   source .vectorstock-dashboard/bin/activate
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run vectorstock_dashboard.py
   ```

3. The dashboard will automatically open in your default web browser at `http://localhost:8501`

## Public Deployment

This dashboard is designed for public access without authentication. To deploy on Runpod or other platforms:

1. See `PUBLIC_DEPLOYMENT_QUICK_START.md` for quick deployment
2. See `RUNPOD_DEPLOYMENT.md` for detailed instructions

**Note**: The dashboard provides public access to all search results - ensure this is appropriate for your use case.

## Project Structure

```
JED-433-VectorStockSearch/
├── vectorstock_dashboard.py    # Main dashboard application
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── search_results/            # Directory containing search result JSON files
│   └── 20250827_132048/
│       └── search_results.json
└── .vectorstock-dashboard/    # Python virtual environment (created during setup)
```

## Usage Guide

### Running New Searches

1. **Basic Search Parameters**:
   - **Keywords** (required) - Enter search terms
   - **Category** - Select from VectorStock categories
   - **Artist** - Filter by specific artist name
   - **Page** - Choose page number for pagination
   - **Sort Order** - best match, trending, latest, isolated, or featured
   - **Count Only** - Return only result count (no images)

2. **License & Format Filters**:
   - **Free Only** - Show only free images
   - **Expanded License Only** - Filter expanded license images
   - **Include Editorial** - Include editorial licenses
   - **SVG Only** - Only SVG format files
   - **PNG Only** - Only transparent PNG files
   - **CMYK Only** - CMYK color model only
   - **Templates Only** - Template vectors only
   - **POD First** - Show Print-On-Demand first
   - **Object Detection** - show_objects or hide_objects

3. **Advanced Filters** (expandable section):
   - **Object Count** - Set min/max object count (1-200)
   - **Color Filter** - Search by hex color with threshold (1-10)
   - **Popularity Score** - Filter by popularity (1-10)
   - **Artist Score** - Filter by artist score (1-10)

4. **Smart Caching**: The dashboard automatically detects if you've already searched with the same parameters:
   - If identical search parameters are found, it uses cached results instead of making a new API call
   - Shows a notification when using cached results with the original search timestamp
   - Saves API calls and improves response time

5. **Search History**: Use the dropdown to switch between previous search results
   - Shows query, timestamp, page number, and total results
   - 🔄 symbol indicates searches with duplicate parameters (same search run multiple times)
   - Automatically loads the most recent search

### Browsing Results

1. **Main View**: The dashboard displays images from the selected search in a grid layout
2. **Filtering**: Use the sidebar on the left to filter loaded images:
   - Select specific license types
   - Choose an artist or view all
   - Adjust the credits range slider
   - Filter by free/paid status
   - Search for keywords in titles/descriptions
3. **Sorting**: Use the dropdown menu above the image grid to sort results
4. **Image Details**: Click "View Details" on any image to see expanded information
5. **Statistics**: Click the "Statistics" expander to view data visualizations

## Data Format

The dashboard expects search results in JSON format with the following structure:
- `timestamp`: Search timestamp
- `query`: Search query used
- `results`: Object containing:
  - `images`: Array of image objects with art_id, title, description, license, artist, credits, preview URLs, etc.
  - `total`: Total number of results
  - `page`: Current page number
  - `pages`: Total number of pages

## Customization

You can customize the dashboard by modifying `vectorstock_dashboard.py`:
- Change the number of columns in the image grid (default: 4)
- Modify the color scheme in the CSS section
- Add additional filters or sorting options
- Customize the statistics displays

## Troubleshooting

- **Images not loading**: Check your internet connection as images are loaded from VectorStock CDN
- **Dashboard not starting**: Ensure the virtual environment is activated and all dependencies are installed
- **JSON file not found**: Verify the search results JSON file exists in the expected location

## License

This dashboard is created for internal use to visualize VectorStock search results.
