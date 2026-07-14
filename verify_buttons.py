#!/usr/bin/env python3
"""Verify how many styled_button calls have style parameter."""

import re
from pathlib import Path

def main():
    vishal_dir = Path('VISHALMUSIC')
    
    total_buttons = 0
    buttons_with_style = 0
    buttons_without_style = []
    
    for py_file in vishal_dir.rglob('*.py'):
        if py_file.name == 'colored_buttons.py':
            continue
        
        content = py_file.read_text(encoding='utf-8')
        
        # Find all styled_button calls including multiline
        pattern = r'styled_button\s*\([^)]+(?:\([^)]*\)[^)]*)*\)'
        buttons = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        for button in buttons:
            total_buttons += 1
            
            if 'style=' in button:
                buttons_with_style += 1
            else:
                # Check if it's just the function definition
                if 'def styled_button' not in button and 'import styled_button' not in button:
                    buttons_without_style.append((py_file.relative_to(vishal_dir), button[:80]))
    
    print(f"Total buttons: {total_buttons}")
    print(f"With style: {buttons_with_style}")
    print(f"Without style: {total_buttons - buttons_with_style}")
    print(f"\nPercentage with colors: {buttons_with_style/total_buttons*100:.1f}%")
    
    if buttons_without_style:
        print(f"\nButtons without style ({len(buttons_without_style)}):")
        for file, button in buttons_without_style[:10]:
            print(f"  {file}: {button}...")

if __name__ == '__main__':
    main()
