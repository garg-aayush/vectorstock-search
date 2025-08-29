# VectorStock Search Results Comparison Dashboard

This dashboard allows you to compare search results between two different approaches:
- **Option A**: Baseline single-query search results
- **Option B**: Multi-query optimized search results

## Features

### 1. Prompt Selection
- Select from 11 different prompts (prompt1 through prompt11)
- View the actual search query text for each prompt
- Results are loaded from pre-computed search results

### 2. View Modes
The dashboard offers 4 different view modes:

- **Side by Side**: View both Option A and Option B results in parallel columns
- **Option A Only**: Focus on baseline results only  
- **Option B Only**: Focus on multi-query results only
- **Comparison Analysis**: Statistical comparison and overlap analysis

### 3. Filtering Options
Filter results by:
- License type (expanded/exclusive)
- Artist name
- Credits required
- Text search in titles and descriptions

### 4. Comparison Analysis Features
- **Statistics Comparison**: Compare total images, unique artists, average credits, and license distribution
- **Overlap Analysis**: See which images appear in both result sets
- **Unique Images**: Identify images that only appear in one result set

## How to Run

```bash
streamlit run vectorstock_comparison_dashboard.py
```

Or to run on a specific port:
```bash
streamlit run vectorstock_comparison_dashboard.py --server.port 8502
```

## Data Sources

- **Prompt Queries**: `data/Option-A-search-queries.json`
- **Option A Results**: `data/search_results/OptionA-rearranged-Baseline/`
- **Option B Results**: `data/search_results/OptionB-prune-multi-queries/`

## Dashboard Layout

1. **Header**: Title and description
2. **Control Panel**: Prompt selector, query display, and view mode selector
3. **Filters**: Sidebar with filtering options
4. **Main Content Area**: Displays images based on selected view mode
5. **Image Details**: Click "View Details" on any image to see full information

## View Mode Details

### Side by Side View
- Shows both result sets in parallel
- Each column displays images in a 2-column grid
- Useful for direct visual comparison

### Single Option Views
- Full-width display with 4-column grid
- Better for detailed examination of one result set

### Comparison Analysis
- Statistical overview of both result sets
- Venn diagram-style overlap analysis
- Expandable sections for unique images

## Color Coding

- **Blue header/background**: Option A (Baseline)
- **Pink header/background**: Option B (Multi-Query)
- **Green badges**: Expanded license
- **Blue badges**: Exclusive license
- **Yellow badges**: Credits required
- **Red badges**: Artist name
