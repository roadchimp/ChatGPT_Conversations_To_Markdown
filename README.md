# ChatGPT Conversations to Markdown

This project is a fork of [daugaard47/ChatGPT_Conversations_To_Markdown](https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown) with several enhancements:

* Platform-agnostic support (works on macOS, Windows, and Linux)
* Command-line argument support for specifying the export directory
* Enhanced attachment handling with proper file organization
* Preserved links to images and files in the markdown output

## Features

* Convert ChatGPT conversations stored in JSON format to Markdown
* Customize user and assistant names using a configuration file
* Include or exclude date in the output Markdown files
* Customize the format of file names, dates, and message separators
* Process all JSON files in a specified directory
* Automatically organize and link attachments (images and files)
* Platform-independent path handling

## Installation

1. Clone the repository or download the ZIP file and extract it to a folder on your computer:
```bash
git clone https://github.com/yourusername/ChatGPT_Conversations_To_Markdown.git
```

2. Change into the project directory:
```bash
cd ChatGPT_Conversations_To_Markdown
```

3. Create a virtual environment (recommended):
```bash
python -m venv venv
```

4. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

5. Install the required Python dependencies:
```bash
pip install tqdm
```

## Usage

1. Place your ChatGPT export files in a directory (e.g., "041725_Export")

2. Run the script with the export directory:
```bash
python chatgpt_export_to_markdown.py -e "041725_Export"
```

3. The script will:
   * Create a `ChatGPT/` directory with the following structure:
     ```
     ChatGPT/
     ├── 00attachments/
     │   ├── images/
     │   └── files/
     └── conversations/
     ```
   * Process all conversations from the export directory
   * Copy and organize attachments
   * Generate markdown files with proper references to attachments

4. When the script completes, you'll see a message like:
```
Export completed! You can find your conversations in: ChatGPT/conversations
```

## Configuration

The script uses a `config.json` file for basic formatting options. You can modify these settings:

```json
{
  "user_name": "You",
  "assistant_name": "ChatGPT",
  "date_format": "%Y-%m-%d %H:%M:%S",
  "file_name_format": "{title}",
  "include_date": true,
  "message_separator": "\n\n",
  "skip_empty_messages": true
}
```

## Command Line Options

* `-e, --export-dir`: Directory containing the ChatGPT export files (default: "041725_Export")
* `-c, --config`: Path to configuration file (default: "config.json")

Example with custom config:
```bash
python chatgpt_export_to_markdown.py -e "my_export_folder" -c "my_config.json"
```

## License

This project is based on the original work by [daugaard47](https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown) and is licensed under the same terms.
