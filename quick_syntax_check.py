#!/usr/bin/env python3
"""
Quick syntax check for justdial_researcher.py
"""

import ast

def check_syntax(file_path):
    """Check if a Python file has syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the AST
        ast.parse(content)
        print("✅ SYNTAX CHECK PASSED!")
        print("✅ justdial_researcher.py has no syntax errors")
        return True
        
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR FOUND:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    file_path = r"C:\01_Projects\Teakwood_Business\Web_Scraping\Dashboard\modules\justdial_researcher.py"
    check_syntax(file_path)
