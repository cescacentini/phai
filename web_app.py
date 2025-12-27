"""
Web application for media search and management.
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from pathlib import Path
from ai_analyzer import MediaAnalyzer
from search_index import MediaSearchIndex

app = Flask(__name__)
CORS(app)

# Global instances
analyzer = None
search_index = None
media_base_path = None


def initialize_app(index_path: str = "./data/index", media_path: str = None):
    """Initialize the web application."""
    global analyzer, search_index, media_base_path
    
    analyzer = MediaAnalyzer()
    search_index = MediaSearchIndex(index_path)
    media_base_path = media_path or "./organized_media"
    
    print("Web application initialized")


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """Handle semantic search queries."""
    try:
        data = request.json
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Encode query
        query_embedding = analyzer.encode_text_query(query)
        
        # Search
        results = search_index.search(query_embedding, k=limit)
        
        # Add file existence check and prepare response
        formatted_results = []
        for result in results:
            file_path = result['file_path']
            if os.path.exists(file_path):
                # Use absolute path for serving
                abs_path = os.path.abspath(file_path)
                formatted_results.append({
                    'file_path': abs_path,
                    'file_type': result['file_type'],
                    'similarity': round(result['similarity'], 3),
                    'distance': round(result['distance'], 3)
                })
        
        return jsonify({
            'results': formatted_results,
            'query': query,
            'count': len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/media/<path:file_path>')
def serve_media(file_path: str):
    """Serve media files."""
    try:
        # Decode the file path
        file_path = file_path.replace('%2F', '/').replace('%5C', '\\')
        
        # Check if it's an absolute path or relative
        if os.path.isabs(file_path):
            full_path = os.path.normpath(file_path)
        else:
            full_path = os.path.join(media_base_path, file_path)
            full_path = os.path.normpath(full_path)
        
        # Security: ensure file is within media base path (for relative paths)
        # or allow absolute paths if they exist
        if not os.path.isabs(file_path):
            if not full_path.startswith(os.path.normpath(media_base_path)):
                return jsonify({'error': 'Access denied'}), 403
        
        if os.path.exists(full_path):
            return send_file(full_path)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get index statistics."""
    try:
        stats = search_index.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import sys
    index_path = sys.argv[1] if len(sys.argv) > 1 else "./data/index"
    media_path = sys.argv[2] if len(sys.argv) > 2 else "./organized_media"
    initialize_app(index_path, media_path)
    app.run(debug=True, host='0.0.0.0', port=5000)

