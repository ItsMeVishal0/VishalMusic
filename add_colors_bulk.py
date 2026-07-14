#!/usr/bin/env python3
"""
Bulk add color styles to all styled_button() calls that don't have style parameter.

Strategy:
- Close/Cancel/Delete buttons → Red (danger)
- Info/Help/Navigation buttons → Blue (primary)  
- Confirm/Yes/Add buttons → Green (success)
"""

import os
import re
from pathlib import Path

# Color assignment rules based on button text
DANGER_KEYWORDS = ['close', 'cancel', 'delete', 'remove', 'stop', 'exit', 'back', 'no']
SUCCESS_KEYWORDS = ['confirm', 'yes', 'add', 'start', 'play', 'resume', 'join', 'accept']
# Everything else gets PRIMARY (blue)

def get_style_for_button(button_text):
    """Determine button style based on text content."""
    text_lower = button_text.lower()
    
    # Check danger keywords first
    if any(keyword in text_lower for keyword in DANGER_KEYWORDS):
        return 'danger'
    
    # Check success keywords
    if any(keyword in text_lower for keyword in SUCCESS_KEYWORDS):
        return 'success'
    
    # Default to primary (blue) for info/navigation
    return 'primary'


def add_style_to_button(line, indent=''):
    """Add style parameter to styled_button() call if missing."""
    
    # Skip if already has style=
    if 'style=' in line:
        return line
    
    # Extract button text to determine color
    text_match = re.search(r'text=["\']([^"\']+)["\']', line)
    if not text_match:
        # Try without named parameter
        text_match = re.search(r'styled_button\(["\']([^"\']+)["\']', line)
    
    if text_match:
        button_text = text_match.group(1)
        style = get_style_for_button(button_text)
    else:
        # Default to primary if can't determine
        style = 'primary'
    
    # Add style parameter before closing parenthesis
    # Handle multiline buttons
    if line.rstrip().endswith(','):
        # Button continues on next line
        return line.rstrip() + f', style="{style}"' + '\n'
    elif line.rstrip().endswith(')'):
        # Single line button - add before )
        return line.rstrip()[:-1] + f', style="{style}")' + '\n'
    else:
        return line
    

def process_file(filepath):
    """Process a Python file and add style to styled_button calls."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for i, line in enumerate(lines):
        if 'styled_button(' in line and 'style=' not in line:
            # Get indentation
            indent = len(line) - len(line.lstrip())
            new_line = add_style_to_button(line, ' ' * indent)
            
            if new_line != line:
                modified = True
                print(f"  Modified line {i+1}: {line.strip()[:60]}...")
            
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    
    return False


def main():
    """Process all Python files in VISHALMUSIC directory."""
    
    vishal_dir = Path('VISHALMUSIC')
    
    if not vishal_dir.exists():
        print("ERROR: VISHALMUSIC directory not found!")
        return
    
    print("Adding colors to styled_button() calls...\n")
    
    files_modified = 0
    total_files = 0
    
    for py_file in vishal_dir.rglob('*.py'):
        # Skip colored_buttons.py itself
        if py_file.name == 'colored_buttons.py':
            continue
        
        total_files += 1
        
        # Check if file has styled_button without style
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'styled_button(' in content:
            # Check for buttons without style
            if re.search(r'styled_button\([^)]*\)(?!.*style=)', content):
                print(f"Processing: {py_file.relative_to(vishal_dir)}")
                
                if process_file(py_file):
                    files_modified += 1
                    print(f"   Modified!\n")
    
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"Files processed: {total_files}")
    print(f"Files modified: {files_modified}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
