#!/usr/bin/env python3
"""
Remove all emojis from markdown files in the project.
This ensures professional documentation without emoji characters.
"""

import os
import re
from pathlib import Path

# Emoji pattern - matches most Unicode emoji characters
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    "\u2600-\u26FF"          # miscellaneous symbols
    "\u2700-\u27BF"          # dingbats
    "]+",
    flags=re.UNICODE
)

# Common emojis to specifically target
COMMON_EMOJIS = [
    '✅', '❌', '🚀', '😊', '🏆', '⚠️', '📊', '💡', 
    '🔥', '👍', '🎯', '📈', '💰', '🏠', '🌟', '💪',
    '🎉', '✨', '👏', '🙌', '💯', '🔴', '🟢', '🟡',
    '📝', '📌', '🔔', '⭐', '🎓', '💼', '📱', '💻'
]

def remove_emojis(text):
    """Remove all emojis from text."""
    # First remove common emojis explicitly
    for emoji in COMMON_EMOJIS:
        text = text.replace(emoji, '')
    
    # Then use regex pattern for any remaining emojis
    text = EMOJI_PATTERN.sub('', text)
    
    # Clean up any double spaces left behind
    text = re.sub(r'  +', ' ', text)
    
    # Clean up lines that are now just whitespace
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Keep the line but strip trailing whitespace
        cleaned_lines.append(line.rstrip())
    
    return '\n'.join(cleaned_lines)

def process_file(file_path):
    """Process a single markdown file to remove emojis."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has emojis
        has_emojis = any(emoji in content for emoji in COMMON_EMOJIS) or EMOJI_PATTERN.search(content)
        
        if not has_emojis:
            return False
        
        # Remove emojis
        cleaned_content = remove_emojis(content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all markdown files."""
    project_root = Path('/Users/sittminthar/Desktop/Datathon_Project-Properties-Dataset-')
    
    # Directories to process
    dirs_to_process = [
        project_root / 'docs',
        project_root / 'reasoning',
        project_root / 'Product_1_Rental_Demand_Forecasting',
        project_root / 'Product_2_Demand_Supply_Gap_Identification',
        project_root / 'Product_3_Conversational_AI_Chatbot',
        project_root  # For root-level README.md
    ]
    
    # Also process specific files
    files_to_process = [
        project_root / 'README.md',
        project_root / 'CHATBOT_DEMO_SCRIPT.md',
    ]
    
    processed_count = 0
    total_count = 0
    
    print("Removing emojis from markdown files...")
    print("=" * 60)
    
    # Process directories
    for directory in dirs_to_process:
        if not directory.exists():
            continue
        
        for md_file in directory.glob('*.md'):
            # Skip node_modules
            if 'node_modules' in str(md_file):
                continue
            
            total_count += 1
            if process_file(md_file):
                processed_count += 1
                print(f"Cleaned: {md_file.relative_to(project_root)}")
    
    # Process specific files
    for file_path in files_to_process:
        if file_path.exists():
            total_count += 1
            if process_file(file_path):
                processed_count += 1
                print(f"Cleaned: {file_path.relative_to(project_root)}")
    
    print("=" * 60)
    print(f"Processed {processed_count} files with emojis out of {total_count} total markdown files")
    print("All emojis removed successfully!")

if __name__ == '__main__':
    main()
