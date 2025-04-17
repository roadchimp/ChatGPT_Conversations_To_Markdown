import json
import os
import sys
import glob
import shutil
import re
import argparse
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

class ChatGPTExporter:
    def __init__(self, config_path="config.json", export_dir=None):
        self.config = self._load_config(config_path)
        self.attachments_dir = Path("ChatGPT/00attachments")
        self.conversations_dir = Path("ChatGPT/conversations")
        self.images_dir = self.attachments_dir / "images"
        self.files_dir = self.attachments_dir / "files"
        self.export_dir = export_dir or "041725_Export"
        
        # Create necessary directories
        self._create_directories()
        
        # Track processed files to avoid duplicates
        self.processed_files = set()
        
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        with open(config_path, 'r') as file:
            return json.load(file)
    
    def _create_directories(self):
        """Create necessary directory structure."""
        for directory in [self.attachments_dir, self.conversations_dir, 
                         self.images_dir, self.files_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to be filesystem-safe."""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length to avoid path length issues
        return sanitized[:255]
    
    def _process_attachment(self, file_path, original_filename):
        """Process and copy an attachment to the appropriate directory."""
        # Determine if it's an image based on extension
        is_image = original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))
        target_dir = self.images_dir if is_image else self.files_dir
        
        # Create a unique filename
        base_name = self._sanitize_filename(original_filename)
        counter = 1
        new_filename = base_name
        
        while (target_dir / new_filename).exists():
            name, ext = os.path.splitext(base_name)
            new_filename = f"{name}_{counter}{ext}"
            counter += 1
        
        # Copy the file
        target_path = target_dir / new_filename
        shutil.copy2(file_path, target_path)
        
        # Return the relative path for markdown
        return f"../00attachments/{'images' if is_image else 'files'}/{new_filename}"
    
    def _get_message_content(self, message):
        """Extract content from a message, handling various formats and attachments."""
        content = ""
        
        if "parts" in message["content"]:
            parts = message["content"]["parts"]
            for part in parts:
                if isinstance(part, dict):
                    if "text" in part:
                        content += part["text"] + "\n"
                    elif "image_url" in part:
                        # Handle image URLs
                        image_url = part["image_url"]
                        if "file-" in image_url:
                            # Extract filename from URL
                            filename = image_url.split("file-")[1].split("-")[0]
                            # Find the corresponding file in the export directory
                            matching_files = list(Path("041725_Export").glob(f"*{filename}*"))
                            if matching_files:
                                relative_path = self._process_attachment(
                                    matching_files[0], 
                                    matching_files[0].name
                                )
                                content += f"![Image]({relative_path})\n"
                else:
                    content += str(part) + "\n"
        elif "text" in message["content"]:
            content = message["content"]["text"]
        elif "result" in message["content"]:
            content = message["content"]["result"]
        
        return content.strip()
    
    def _get_title(self, title, first_message):
        """Generate a title for the conversation."""
        if title:
            return title
        
        content = self._get_message_content(first_message)
        first_line = content.split("\n", 1)[0]
        return first_line.rstrip() + "..."
    
    def process_conversation(self, entry):
        """Process a single conversation entry."""
        title = entry.get("title", None)
        mapping = entry.get("mapping", {})
        
        # Extract messages
        messages = [
            item["message"] 
            for item in mapping.values() 
            if isinstance(item, dict) and item.get("message") is not None
        ]
        
        # Sort messages by create_time
        messages.sort(key=lambda x: x.get("create_time") or float('-inf'))
        
        # Generate title
        inferred_title = self._get_title(title, messages[0] if messages else {"content": {"text": "Untitled"}})
        sanitized_title = self._sanitize_filename(inferred_title)
        file_name = f"{self.config['file_name_format'].format(title=sanitized_title.replace(' ', '_').replace('/', '_'))}.md"
        file_path = self.conversations_dir / file_name
        
        # Write messages to file
        with open(file_path, "w", encoding="utf-8") as f:
            if messages and messages[0].get("create_time") and self.config['include_date']:
                date = datetime.fromtimestamp(messages[0]["create_time"]).strftime(self.config['date_format'])
                f.write(f"<sub>{date}</sub>{self.config['message_separator']}")
            
            for message in messages:
                author_role = message["author"]["role"]
                content = self._get_message_content(message)
                author_name = self.config['user_name'] if author_role == "user" else self.config['assistant_name']
                
                if not self.config['skip_empty_messages'] or content.strip():
                    f.write(f"**{author_name}**: {content}{self.config['message_separator']}")
    
    def process_export(self, export_dir="041725_Export"):
        """Process all conversations in the export directory."""
        export_path = Path(export_dir)
        
        # Process JSON files
        json_files = list(export_path.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {export_dir}")
            return
        
        for json_file in tqdm(json_files, desc="Processing conversations"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for entry in data:
                        self.process_conversation(entry)
                else:
                    self.process_conversation(data)
            
            except Exception as e:
                print(f"Error processing {json_file}: {str(e)}")
        
        print(f"Export completed! You can find your conversations in: {self.conversations_dir}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Export ChatGPT conversations to markdown format')
    parser.add_argument('--export-dir', '-e', 
                      help='Directory containing the ChatGPT export files',
                      default="041725_Export")
    parser.add_argument('--config', '-c',
                      help='Path to configuration file',
                      default="config.json")
    
    args = parser.parse_args()
    
    # Initialize and run exporter
    exporter = ChatGPTExporter(config_path=args.config, export_dir=args.export_dir)
    exporter.process_export(args.export_dir)

if __name__ == "__main__":
    main() 