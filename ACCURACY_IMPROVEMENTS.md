# Accuracy Improvement Guide

## Current Implementation
- CLIP Model: ViT-B/32 (base model)
- Video frames: 8 frames sampled uniformly
- Similarity: Distance-based conversion
- Query encoding: Direct CLIP text encoding

## Improvements Implemented

### 1. **Better CLIP Model** (Optional - requires more memory)
- Upgrade from ViT-B/32 to ViT-L/14 or ViT-B/16
- Better accuracy but slower and uses more memory
- Can be configured in settings

### 2. **More Video Frames**
- Increased from 8 to 16 frames for better video understanding
- Better coverage of video content

### 3. **Better Similarity Calculation**
- Using cosine similarity directly (more accurate for normalized embeddings)
- Better distance-to-similarity conversion

### 4. **Query Expansion**
- Automatically expands queries with related terms
- Example: "drawing" → "drawing, sketching, art, painting"

### 5. **Better Text Prompts**
- Uses more descriptive prompts for better matching
- Example: "videos where I'm drawing" → "a video of a person drawing"

### 6. **Similarity Threshold Filtering**
- Filters out low-confidence results
- Only shows results above a certain similarity threshold

### 7. **Better Video Frame Selection**
- Uses keyframe detection for more relevant frames
- Focuses on frames with significant changes

## How to Use

The improvements are automatically enabled. You can configure:
- Model size (in ai_analyzer.py)
- Number of video frames
- Similarity threshold
- Query expansion (enabled by default)

