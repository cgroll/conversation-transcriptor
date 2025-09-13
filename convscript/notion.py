"""
Notion integration for uploading transcripts to a Notion database.
"""
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

def get_notion_credentials() -> tuple:
    """Get Notion credentials from environment variables."""
    write_token = os.getenv("NOTION_WRITE_API_TOKEN")
    database_id = os.getenv("NOTION_TRANSCRIPTS_DATABASE_ID")
    
    if not write_token:
        raise ValueError("NOTION_WRITE_API_TOKEN not found in environment variables")
    if not database_id:
        raise ValueError("NOTION_TRANSCRIPTS_DATABASE_ID not found in environment variables")
        
    return write_token, database_id

def get_today_date() -> str:
    """Get today's date in ISO format."""
    return datetime.now().date().isoformat()

def check_database_properties() -> Optional[Dict[str, Any]]:
    """
    Check what properties are available in the transcripts database.
    
    Returns:
        Dictionary of database properties or None if failed
    """
    try:
        write_token, database_id = get_notion_credentials()
        client = Client(auth=write_token)
        
        database = client.databases.retrieve(database_id)
        properties = database.get('properties', {})
        
        print("📋 Available database properties:")
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get('type', 'unknown')
            print(f"  • '{prop_name}': {prop_type}")
        
        return properties
        
    except Exception as e:
        print(f"❌ Error checking database properties: {e}")
        return None

def find_date_property_name() -> Optional[str]:
    """
    Find the correct name of a date property in the database.
    
    Returns:
        Property name if found, None otherwise
    """
    try:
        properties = check_database_properties()
        if not properties:
            return None
        
        # Look for date properties
        date_properties = []
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'date':
                date_properties.append(prop_name)
        
        if date_properties:
            print(f"📅 Found date properties: {date_properties}")
            return date_properties[0]  # Return first date property
        else:
            print("📅 No date properties found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error finding date property: {e}")
        return None

def find_url_property_name() -> Optional[str]:
    """
    Find the correct name of a URL property in the database.
    
    Returns:
        Property name if found, None otherwise
    """
    try:
        properties = check_database_properties()
        if not properties:
            return None
        
        # Look for URL properties
        url_properties = []
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'url':
                url_properties.append(prop_name)
        
        if url_properties:
            print(f"🔗 Found URL properties: {url_properties}")
            return url_properties[0]  # Return first URL property
        else:
            print("🔗 No URL properties found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error finding URL property: {e}")
        return None

def generate_default_title(file_path: str) -> str:
    """
    Generate a default title from the transcript filename.
    
    Args:
        file_path: Path to the transcript file
        
    Returns:
        Default title based on filename
    """
    filename = Path(file_path).stem
    
    # Remove common suffixes like model names and output indicators
    suffixes_to_remove = [
        r'_large-v3-turbo.*',
        r'_cli_output$',
        r'_debug_output$',
        r'_output$',
        r'_transcript$'
    ]
    
    clean_name = filename
    for suffix in suffixes_to_remove:
        clean_name = re.sub(suffix, '', clean_name, flags=re.IGNORECASE)
    
    # Replace underscores and hyphens with spaces
    clean_name = re.sub(r'[-_]+', ' ', clean_name)
    
    # Capitalize words
    title = ' '.join(word.capitalize() for word in clean_name.split())
    
    # Limit to reasonable length
    if len(title) > 60:
        title = title[:57] + "..."
    
    return title or "Transcript"

def get_user_title(default_title: str) -> str:
    """
    Ask user for a title, showing the default option.
    
    Args:
        default_title: The generated default title
        
    Returns:
        User's chosen title
    """
    print(f"\nDefault title: '{default_title}'")
    user_input = input("Enter a different title (or press Enter to use default): ").strip()
    
    return user_input if user_input else default_title

def safe_filename(title: str, max_length: int = 200) -> str:
    """
    Convert a title to a safe filename by removing/replacing problematic characters.
    Handles filesystem limits and ensures filename compatibility across platforms.
    
    Args:
        title: The title to convert
        max_length: Maximum length for the filename (default 200, leaves room for extensions and suffixes)
        
    Returns:
        Safe filename string
    """
    import string
    
    if not title or not title.strip():
        return "transcript"
    
    # Remove or replace characters that are problematic in filenames
    # Allow letters, numbers, spaces, hyphens, underscores, dots, parentheses
    safe_chars = string.ascii_letters + string.digits + ' -_.()'
    safe_title = ''.join(c if c in safe_chars else '_' for c in title.strip())
    
    # Remove multiple consecutive underscores/spaces and clean up
    safe_title = re.sub(r'[_\s]+', '_', safe_title)  # Replace multiple spaces/underscores with single underscore
    safe_title = re.sub(r'__+', '_', safe_title)     # Replace multiple underscores with single
    safe_title = safe_title.strip('_').strip()       # Remove leading/trailing underscores and spaces
    
    # Handle very long filenames
    if len(safe_title) > max_length:
        # Try to break at word boundaries
        words = safe_title.split('_')
        truncated = ""
        for word in words:
            if len(truncated + '_' + word) > max_length - 3:  # Leave space for "..."
                break
            if truncated:
                truncated += '_'
            truncated += word
        
        if truncated:
            safe_title = truncated + "..."
        else:
            # If even the first word is too long, just truncate
            safe_title = safe_title[:max_length-3] + "..."
    
    # Ensure we have a valid filename
    if not safe_title or safe_title in ['.', '..']:
        safe_title = "transcript"
    
    # Remove any trailing dots (problematic on Windows)
    safe_title = safe_title.rstrip('.')
    
    return safe_title

def markdown_to_notion_blocks(content: str) -> List[Dict[str, Any]]:
    """
    Convert plain text content to Notion blocks.
    This handles the transcript content as paragraphs.
    
    Args:
        content: Plain text content from transcript
        
    Returns:
        List of Notion block objects (no limit applied here)
    """
    if not content.strip():
        return [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Empty transcript"}}]}
        }]
    
    # Split content into paragraphs (by double newlines or long single newlines)
    paragraphs = re.split(r'\n\s*\n', content.strip())
    
    blocks = []
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Split very long paragraphs to avoid Notion's limits
        if len(paragraph) > 1900:  # Leave some buffer under 2000 char limit
            # Split at sentence boundaries when possible
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            current_block = ""
            
            for sentence in sentences:
                if len(current_block + sentence) > 1900:
                    if current_block:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": current_block.strip()}}]}
                        })
                    current_block = sentence
                else:
                    current_block += (" " if current_block else "") + sentence
            
            if current_block:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": current_block.strip()}}]}
                })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": paragraph}}]}
            })
    
    return blocks

def split_blocks_into_parts(blocks: List[Dict[str, Any]], max_blocks_per_part: int = 95) -> List[List[Dict[str, Any]]]:
    """
    Split blocks into multiple parts to handle Notion's 100-block limit.
    
    Args:
        blocks: List of Notion blocks
        max_blocks_per_part: Maximum blocks per part (default 95 to leave room for navigation)
        
    Returns:
        List of block lists, one for each part
    """
    if len(blocks) <= max_blocks_per_part:
        return [blocks]
    
    parts = []
    current_part = []
    
    for block in blocks:
        if len(current_part) >= max_blocks_per_part:
            parts.append(current_part)
            current_part = []
        
        current_part.append(block)
    
    # Add remaining blocks
    if current_part:
        parts.append(current_part)
    
    return parts

def add_navigation_to_parts(parts: List[List[Dict[str, Any]]], page_urls: List[str], base_title: str) -> List[List[Dict[str, Any]]]:
    """
    Add navigation links between parts.
    
    Args:
        parts: List of block lists
        page_urls: List of page URLs (will be filled as pages are created)
        base_title: Base title for the pages
        
    Returns:
        Updated parts with navigation blocks
    """
    if len(parts) <= 1:
        return parts
    
    updated_parts = []
    
    for i, part in enumerate(parts):
        part_num = i + 1
        updated_part = list(part)  # Copy the part
        
        # Add navigation header at the top
        nav_header = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"📄 {base_title} - Part {part_num} of {len(parts)}"}, "annotations": {"bold": True}}]}
        }
        updated_part.insert(0, nav_header)
        
        # Add navigation footer at the bottom
        nav_links = []
        for j in range(len(parts)):
            if j == i:
                nav_links.append(f"Part {j+1} (current)")
            else:
                # We'll update with actual URLs later
                nav_links.append(f"Part {j+1}")
        
        nav_footer = {
            "object": "block",
            "type": "paragraph", 
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"📑 Navigation: {' | '.join(nav_links)}"}}]}
        }
        updated_part.append(nav_footer)
        
        updated_parts.append(updated_part)
    
    return updated_parts

def upload_transcript_to_notion(file_path: str, title: Optional[str] = None, date: Optional[str] = None, url: Optional[str] = None, include_date: bool = True) -> Optional[str]:
    """
    Upload a transcript file to Notion database.
    Automatically splits long transcripts into multiple pages if needed.
    
    Args:
        file_path: Path to the transcript text file
        title: Optional custom title. If None, will ask user for input.
        date: Optional custom date in ISO format (YYYY-MM-DD). If None, uses today.
        url: Optional URL to store in URL property of the Notion page.
        include_date: Whether to try to set a date property (default True). Set False if database has no date property.
        
    Returns:
        Page URL of first part if successful, None otherwise. 
        For multi-part uploads, returns URL of Part I.
    """
    try:
        # Get credentials
        write_token, database_id = get_notion_credentials()
        client = Client(auth=write_token)
        
        # Validate file exists and is readable
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist")
            return None
            
        if not file_path.endswith('.txt'):
            print(f"Warning: File '{file_path}' is not a .txt file")
        
        # Read transcript content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            return None
            
        if not content.strip():
            print(f"Warning: File '{file_path}' is empty")
            content = f"Empty transcript file: {file_path}"
        
        # Get title
        if title is None:
            default_title = generate_default_title(file_path)
            title = get_user_title(default_title)
        
        # Convert content to Notion blocks
        blocks = markdown_to_notion_blocks(content)
        
        # Check if we need to split into multiple parts
        if len(blocks) > 95:  # Leave room for navigation
            print(f"📄 Long transcript detected: {len(blocks)} blocks")
            print(f"📚 Splitting into multiple parts...")
            
            parts = split_blocks_into_parts(blocks, max_blocks_per_part=90)  # Even more conservative
            print(f"📄 Split into {len(parts)} parts")
            
            # Upload all parts
            page_urls = []
            for i, part_blocks in enumerate(parts):
                part_num = i + 1
                part_title = f"{title} - Part {part_num}"
                
                print(f"📤 Uploading Part {part_num}/{len(parts)}: {len(part_blocks)} blocks...")
                
                # Add navigation header
                nav_header = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"📄 {title} - Part {part_num} of {len(parts)}"}, "annotations": {"bold": True}}]}
                }
                part_blocks.insert(0, nav_header)
                
                # Create properties for this part
                properties = create_page_properties(part_title, date, url, include_date)
                
                # Upload this part
                page_url = create_notion_page(client, database_id, properties, part_blocks, part_title)
                if page_url:
                    page_urls.append(page_url)
                    print(f"✅ Part {part_num} uploaded: {page_url}")
                else:
                    print(f"❌ Failed to upload Part {part_num}")
                    return None
            
            if page_urls:
                print(f"🎉 Successfully uploaded {len(page_urls)} parts!")
                print(f"🔗 Part I URL: {page_urls[0]}")
                return page_urls[0]  # Return first part URL
            else:
                return None
        
        else:
            # Single page upload
            print(f"📄 Single page upload: {len(blocks)} blocks")
            properties = create_page_properties(title, date, url, include_date)
            return create_notion_page(client, database_id, properties, blocks, title)
            
    except Exception as e:
        print(f"❌ Error uploading transcript to Notion: {e}")
        return None

def create_page_properties(title: str, date: Optional[str], url: Optional[str], include_date: bool) -> Dict[str, Any]:
    """
    Create the properties dictionary for a Notion page.
    
    Args:
        title: Page title
        date: Optional date
        url: Optional URL
        include_date: Whether to include date property
        
    Returns:
        Properties dictionary
    """
    properties = {
        "title": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    }
    
    # Add date property if requested and available
    if include_date:
        date_property_name = find_date_property_name()
        if date_property_name:
            upload_date = date if date else get_today_date()
            try:
                from datetime import datetime
                if upload_date:
                    parsed_date = datetime.fromisoformat(upload_date)
                    formatted_date = parsed_date.date().isoformat()
                    properties[date_property_name] = {
                        "date": {
                            "start": formatted_date
                        }
                    }
                    print(f"📅 Using date property: '{date_property_name}' = {formatted_date}")
            except ValueError as date_error:
                print(f"⚠️  Invalid date format '{upload_date}', using today instead")
                today = get_today_date()
                properties[date_property_name] = {
                    "date": {
                        "start": today
                    }
                }
        else:
            print("⚠️  No date property found in database, skipping date")
    
    # Add URL property if provided
    if url:
        url_property_name = find_url_property_name()
        if url_property_name:
            properties[url_property_name] = {
                "url": url
            }
            print(f"🔗 Using URL property: '{url_property_name}' = {url}")
        else:
            print("⚠️  No URL property found in database, skipping URL")
    
    return properties

def create_notion_page(client, database_id: str, properties: Dict[str, Any], blocks: List[Dict[str, Any]], title: str) -> Optional[str]:
    """
    Create a single Notion page.
    
    Args:
        client: Notion client
        database_id: Database ID
        properties: Page properties
        blocks: Content blocks
        title: Page title for logging
        
    Returns:
        Page URL if successful, None otherwise
    """
    try:
        # Create page in Notion
        new_page = client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=blocks
        )
        
        page_url = new_page.get('url', '')
        print(f"✅ Successfully uploaded: '{title}'")
        return page_url
        
    except Exception as e:
        print(f"❌ Error creating page '{title}': {e}")
        return None

def upload_all_transcripts_in_directory(directory_path: str = "data/outputs") -> List[str]:
    """
    Upload all .txt files from a directory to Notion.
    
    Args:
        directory_path: Path to directory containing transcript files
        
    Returns:
        List of successfully uploaded page URLs
    """
    uploaded_pages = []
    
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist")
        return uploaded_pages
    
    # Find all .txt files
    txt_files = []
    for file in os.listdir(directory_path):
        if file.endswith('.txt'):
            txt_files.append(os.path.join(directory_path, file))
    
    if not txt_files:
        print(f"No .txt files found in '{directory_path}'")
        return uploaded_pages
        
    print(f"Found {len(txt_files)} transcript files to upload:")
    for i, file_path in enumerate(txt_files, 1):
        print(f"  {i}. {os.path.basename(file_path)}")
    
    # Upload each file
    for file_path in txt_files:
        print(f"\n--- Processing: {os.path.basename(file_path)} ---")
        page_url = upload_transcript_to_notion(file_path)
        if page_url:
            uploaded_pages.append(page_url)
        
        # Add a small pause between uploads to be respectful to Notion API
        import time
        time.sleep(1)
    
    print(f"\n🎉 Upload complete! Successfully uploaded {len(uploaded_pages)} out of {len(txt_files)} files.")
    
    return uploaded_pages