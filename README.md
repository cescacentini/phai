# Personal Media AI Organizer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent media management system that organizes your pictures and videos by date, categorizes them using AI, and enables semantic search to find media based on natural language queries.

## ✨ Features

- 📅 **Date-based Organization**: Automatically organizes media into YYYYMMDD folders based on creation date
- 🤖 **AI Categorization**: Uses CLIP vision AI models to understand and categorize your media
- 🔍 **Semantic Search**: Find videos and pictures using natural language (e.g., "videos where I'm drawing")
- 📁 **Smart File Management**: Preserves original files while organizing copies
- 🖥️ **Modern GUI Interface**: Beautiful dark-mode interface built with CustomTkinter
- ⏹️ **Stop Operations**: Stop any long-running operation at any time
- 🔄 **Auto-Indexing**: Automatically indexes files after organizing
- 🎯 **High Accuracy**: Advanced query expansion and similarity matching


## Installation

1. Install Python 3.8 or higher

2. Create and activate a virtual environment (recommended):
```bash
# Create virtual environment
python3 -m venv PHAIenv

# Activate virtual environment
# On macOS/Linux:
source PHAIenv/bin/activate
# On Windows:
# PHAIenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git
```

**Note:** 
- The CLIP model will be automatically downloaded on first run (~350MB). This may take a few minutes.
- If you have a CUDA-capable GPU, install `torch` and `torchvision` with CUDA support for faster processing.
- Remember to activate the virtual environment (`source PHAIenv/bin/activate`) before running any commands.

## Quick Start

### Option 1: GUI Application (Recommended)

The easiest way to use PHAI is through the graphical interface:

**On macOS - Double-click the app:**
```
Just double-click PHAI.app in the project folder!
```

**Or run from terminal:**
```bash
# macOS/Linux
./run_gui.sh

# Windows
run_gui.bat

# Or manually
source PHAIenv/bin/activate  # On Windows: PHAIenv\Scripts\activate
python gui_app.py
```

The GUI provides:
- 📁 **Folder Selection**: Browse and select folders for organizing and indexing
- 🔄 **Organize Media**: Organize files into date-based folders with progress tracking
- 🤖 **Auto-Indexing**: Automatically indexes files after organizing (can be disabled)
- 📊 **Index Media**: Manually index your media for search with real-time progress
- ➕ **Add to Index**: Add new files to an existing index without re-indexing everything
- 🔍 **Search Interface**: Natural language search with visual results (double-click to open files)
- ⏹️ **Stop Buttons**: Stop any operation at any time

### Option 2: Command Line Interface

### Step 1: Organize Your Media
Organize your pictures and videos into date-based folders (YYYYMMDD format):
```bash
python main.py organize --source /path/to/your/media --destination ./organized_media
```

This will:
- Extract creation dates from EXIF data (for images) or file metadata
- Create folders named YYYYMMDD (e.g., 20240115 for January 15, 2024)
- Copy files into the appropriate date folders

**Options:**
- `--move`: Move files instead of copying (default: copy)

### Step 2: Index Media for Search
Create a searchable index of your media:
```bash
python main.py index --media-dir ./organized_media
```

This will:
- Analyze each image and video using AI
- Extract semantic embeddings
- Build a searchable index

**Note:** This process may take time depending on the number of files. Videos are processed by sampling frames.

### Step 3: Search Your Media

#### Web Interface (Recommended)
Start the web interface:
```bash
python main.py serve --media-dir ./organized_media
```

Then open http://localhost:5000 in your browser and search using natural language!

#### Command Line
```bash
python main.py search "videos where I'm drawing" --limit 10
```

## Usage Examples

### Organize Media
```bash
# Copy files to organized folders
python main.py organize --source ~/Downloads/photos --destination ./organized_media

# Move files instead of copying
python main.py organize --source ~/Downloads/photos --destination ./organized_media --move
```

### Index Media
```bash
# Index with default index location
python main.py index --media-dir ./organized_media

# Specify custom index location
python main.py index --media-dir ./organized_media --index-path ./my_index
```

### Search
```bash
# Search for specific content
python main.py search "videos where I'm drawing"
python main.py search "pictures of my dog"
python main.py search "outdoor scenes"
python main.py search "people cooking"

# Limit results
python main.py search "videos" --limit 5
```

### Web Interface
```bash
# Start server with default settings
python main.py serve

# Custom port and media directory
python main.py serve --port 8080 --media-dir ./organized_media

# Debug mode
python main.py serve --debug
```

## Configuration

Create a `.env` file to configure paths:
```
MEDIA_SOURCE_DIR=/path/to/source
MEDIA_DEST_DIR=/path/to/destination
INDEX_PATH=./data/index
```

