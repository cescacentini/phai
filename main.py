"""
Main application entry point for PHAI media organizer.
"""
import argparse
import os
import sys
from pathlib import Path
from tqdm import tqdm

from media_organizer import organize_media, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from ai_analyzer import MediaAnalyzer
from search_index import MediaSearchIndex


def organize_command(args):
    """Organize media files into date-based folders."""
    print(f"Organizing media from {args.source} to {args.destination}...")
    
    organized = organize_media(
        source_dir=args.source,
        dest_dir=args.destination,
        copy_files=not args.move
    )
    
    print(f"\n✓ Organized {len(organized)} files successfully!")


def index_command(args):
    """Index media files for search."""
    print(f"Indexing media in {args.media_dir}...")
    
    # Initialize components
    analyzer = MediaAnalyzer()
    search_index = MediaSearchIndex(index_path=args.index_path)
    
    # Find all media files
    media_path = Path(args.media_dir)
    all_extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
    
    media_files = []
    for ext in all_extensions:
        media_files.extend(media_path.rglob(f'*{ext}'))
        media_files.extend(media_path.rglob(f'*{ext.upper()}'))
    
    print(f"Found {len(media_files)} media files to index...")
    
    # Process files
    indexed = 0
    skipped = 0
    
    for media_file in tqdm(media_files, desc="Indexing"):
        try:
            file_path = str(media_file)
            file_ext = media_file.suffix.lower()
            
            # Determine file type
            if file_ext in IMAGE_EXTENSIONS:
                embedding = analyzer.extract_image_embedding(file_path)
                file_type = "image"
            elif file_ext in VIDEO_EXTENSIONS:
                embedding = analyzer.extract_video_embedding(file_path)
                file_type = "video"
            else:
                continue
            
            # Add to index
            search_index.add_media(file_path, embedding, file_type)
            indexed += 1
            
        except Exception as e:
            print(f"\nError indexing {media_file}: {e}")
            skipped += 1
    
    # Save index
    search_index.save()
    
    print(f"\n✓ Indexed {indexed} files successfully!")
    if skipped > 0:
        print(f"⚠ Skipped {skipped} files due to errors")
    
    # Show stats
    stats = search_index.get_stats()
    print(f"\nIndex Statistics:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Images: {stats['images']}")
    print(f"  Videos: {stats['videos']}")


def search_command(args):
    """Search for media using natural language."""
    # Initialize components
    analyzer = MediaAnalyzer()
    search_index = MediaSearchIndex(index_path=args.index_path)
    
    # Encode query
    print(f"Searching for: '{args.query}'...")
    query_embedding = analyzer.encode_text_query(args.query)
    
    # Search
    results = search_index.search(query_embedding, k=args.limit)
    
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        file_path = result['file_path']
        file_type = result['file_type']
        similarity = result['similarity']
        
        print(f"{i}. [{file_type.upper()}] {file_path}")
        print(f"   Similarity: {similarity*100:.1f}%")
        print()


def serve_command(args):
    """Start the web server."""
    from web_app import app, initialize_app
    
    initialize_app(
        index_path=args.index_path,
        media_path=args.media_dir
    )
    
    print(f"Starting web server on http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    
    app.run(debug=args.debug, host='0.0.0.0', port=args.port)


def main():
    parser = argparse.ArgumentParser(
        description='PHAI - Personal Media AI Organizer',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Organize command
    organize_parser = subparsers.add_parser('organize', help='Organize media into date folders')
    organize_parser.add_argument('--source', required=True, help='Source directory with media files')
    organize_parser.add_argument('--destination', required=True, help='Destination directory for organized files')
    organize_parser.add_argument('--move', action='store_true', help='Move files instead of copying')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index media for search')
    index_parser.add_argument('--media-dir', required=True, help='Directory with organized media')
    index_parser.add_argument('--index-path', default='./data/index', help='Path to store index')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for media')
    search_parser.add_argument('query', help='Search query (natural language)')
    search_parser.add_argument('--index-path', default='./data/index', help='Path to index')
    search_parser.add_argument('--limit', type=int, default=10, help='Number of results')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start web interface')
    serve_parser.add_argument('--index-path', default='./data/index', help='Path to index')
    serve_parser.add_argument('--media-dir', default='./organized_media', help='Directory with media files')
    serve_parser.add_argument('--port', type=int, default=5000, help='Port to run server on')
    serve_parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'organize':
        organize_command(args)
    elif args.command == 'index':
        index_command(args)
    elif args.command == 'search':
        search_command(args)
    elif args.command == 'serve':
        serve_command(args)


if __name__ == '__main__':
    main()


