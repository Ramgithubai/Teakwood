#!/usr/bin/env python3
"""
Quick fix for GitHub secret scanning detection
"""

# Read the file
with open('ai_csv_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace potentially problematic API key examples
replacements = [
    # Replace example API keys that might trigger secret scanning
    ('your_groq_key_here', 'your_api_key_here'),
    ('your_openai_key_here', 'your_api_key_here'),
    ('your_anthropic_key_here', 'your_api_key_here'),
    ('sk-your_openai_key_here', 'sk-your_key_here'),
    ('GROQ_API_KEY=your_groq_key_here', 'GROQ_API_KEY=your_key_here'),
    ('OPENAI_API_KEY=sk-your_openai_key_here', 'OPENAI_API_KEY=sk-your_key_here'),
    ('ANTHROPIC_API_KEY=your_anthropic_key_here', 'ANTHROPIC_API_KEY=your_key_here'),
    # Replace any potential patterns
    ('gsk_', 'your_groq_key_prefix_'),
    ('sk-proj', 'sk-your_key_prefix'),
]

changes_made = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        changes_made += 1
        print(f"Replaced: {old} -> {new}")

if changes_made > 0:
    # Write back the fixed content
    with open('ai_csv_analyzer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Made {changes_made} changes to fix secret scanning issues")
else:
    print("ℹ️ No obvious API key patterns found to replace")

# Also check for any lines containing potential API key patterns
lines = content.split('\n')
suspicious_lines = []

for i, line in enumerate(lines, 1):
    line_lower = line.lower()
    if ('groq' in line_lower and 'key' in line_lower and 
        any(char in line for char in ['=', '"', "'"])):
        suspicious_lines.append(f"Line {i}: {line.strip()}")

if suspicious_lines:
    print("\n⚠️ Potentially suspicious lines found:")
    for line in suspicious_lines[:5]:  # Show first 5
        print(line)
