#!/usr/bin/env python3
"""Fix double comma syntax error from bulk script."""

import re
from pathlib import Path

def main():
    vishal_dir = Path('VISHALMUSIC')
    
    files_modified = 0
    
    for py_file in vishal_dir.rglob('*.py'):
        if py_file.name == 'colored_buttons.py':
            continue
        
        content = py_file.read_text(encoding='utf-8')
        original = content
        
        # Fix: ),, style=" → ", style="
        content = re.sub(r'\),\s*,\s*style=', ', style=', content)
        
        if content != original:
            py_file.write_text(content, encoding='utf-8')
            files_modified += 1
            print(f"Fixed: {py_file.relative_to(vishal_dir)}")
    
    print(f"\nTotal files fixed: {files_modified}")

if __name__ == '__main__':
    main()
