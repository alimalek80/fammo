"""
Utilities for managing Django translations (.po files)
"""
import os
import re
import subprocess
from pathlib import Path
from django.conf import settings
from collections import defaultdict


def get_po_file_path(language_code):
    """Get the path to a .po file for a given language"""
    locale_path = Path(settings.BASE_DIR) / "locale"
    po_file = locale_path / language_code / "LC_MESSAGES" / "django.po"
    return po_file


def parse_po_file(language_code):
    """
    Parse a .po file and extract all translations.
    Returns a list of dictionaries with msgid, msgstr, locations, and line numbers.
    """
    po_file = get_po_file_path(language_code)
    
    if not po_file.exists():
        return []
    
    translations = []
    current_entry = None
    current_locations = []
    current_msgid = []
    current_msgstr = []
    in_msgid = False
    in_msgstr = False
    line_number = 0
    
    with open(po_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line_number = line_num
            
            # Skip empty lines and comments (except location comments)
            if line.startswith('#:'):
                # Location comment
                locations = line[2:].strip().split()
                current_locations.extend(locations)
                continue
            elif line.startswith('#') or not line.strip():
                # Skip other comments and empty lines
                if in_msgid or in_msgstr:
                    # End of entry
                    if current_entry is not None and current_msgid:
                        msgid_text = ''.join(current_msgid)
                        msgstr_text = ''.join(current_msgstr)
                        
                        # Skip empty msgid (header)
                        if msgid_text.strip():
                            current_entry['msgid'] = msgid_text
                            current_entry['msgstr'] = msgstr_text
                            current_entry['locations'] = current_locations.copy()
                            translations.append(current_entry)
                    
                    current_entry = None
                    current_locations = []
                    current_msgid = []
                    current_msgstr = []
                    in_msgid = False
                    in_msgstr = False
                continue
            
            # Check for msgid
            if line.startswith('msgid '):
                if current_entry is not None and current_msgid:
                    # Save previous entry
                    msgid_text = ''.join(current_msgid)
                    msgstr_text = ''.join(current_msgstr)
                    
                    if msgid_text.strip():
                        current_entry['msgid'] = msgid_text
                        current_entry['msgstr'] = msgstr_text
                        current_entry['locations'] = current_locations.copy()
                        translations.append(current_entry)
                
                # Start new entry
                current_entry = {'line_number': line_number}
                current_msgid = [extract_string(line[6:])]
                current_msgstr = []
                in_msgid = True
                in_msgstr = False
                continue
            
            # Check for msgstr
            if line.startswith('msgstr '):
                current_msgstr = [extract_string(line[7:])]
                in_msgid = False
                in_msgstr = True
                continue
            
            # Continuation line (quoted string)
            if line.strip().startswith('"'):
                if in_msgid:
                    current_msgid.append(extract_string(line))
                elif in_msgstr:
                    current_msgstr.append(extract_string(line))
    
    # Don't forget the last entry
    if current_entry is not None and current_msgid:
        msgid_text = ''.join(current_msgid)
        msgstr_text = ''.join(current_msgstr)
        
        if msgid_text.strip():
            current_entry['msgid'] = msgid_text
            current_entry['msgstr'] = msgstr_text
            current_entry['locations'] = current_locations.copy()
            translations.append(current_entry)
    
    return translations


def extract_string(line):
    """Extract the content from a quoted string in .po file"""
    # Remove leading/trailing whitespace
    line = line.strip()
    # Remove quotes
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    # Unescape
    line = line.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
    return line


def escape_string(text):
    """Escape a string for .po file format"""
    text = text.replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    return text


def update_translation(language_code, msgid, new_msgstr):
    """
    Update a specific translation in the .po file.
    Returns True on success, False on failure.
    """
    po_file = get_po_file_path(language_code)
    
    if not po_file.exists():
        return False
    
    # Read the file
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and update the translation
    found = False
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for msgid
        if line.startswith('msgid '):
            current_msgid = extract_string(line[6:])
            
            # Check for multiline msgid
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('"'):
                current_msgid += extract_string(lines[j])
                j += 1
            
            # If this is the msgid we're looking for
            if current_msgid == msgid:
                found = True
                # Find the msgstr line(s)
                k = j
                while k < len(lines) and not lines[k].startswith('msgstr '):
                    k += 1
                
                if k < len(lines):
                    # Replace msgstr
                    # Remove old msgstr lines
                    msgstr_start = k
                    k += 1
                    while k < len(lines) and lines[k].strip().startswith('"'):
                        k += 1
                    
                    # Create new msgstr
                    escaped_msgstr = escape_string(new_msgstr)
                    new_msgstr_line = f'msgstr "{escaped_msgstr}"\n'
                    
                    # Replace the lines
                    lines[msgstr_start:k] = [new_msgstr_line]
                
                break
        
        i += 1
    
    if found:
        # Write back to file
        with open(po_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    
    return False


def compile_messages():
    """
    Compile all .po files to .mo files using Django's compilemessages command.
    Returns (success, output, error)
    """
    try:
        import sys
        python_executable = sys.executable
        manage_py = settings.BASE_DIR / 'manage.py'
        
        result = subprocess.run(
            [python_executable, str(manage_py), 'compilemessages'],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60,
            shell=False
        )
        
        # Success if returncode is 0
        success = result.returncode == 0
        
        # If stdout is empty but returncode is 0, it means files are up to date (which is success)
        # Add a helpful message in this case
        output = result.stdout
        if success and not output.strip():
            output = "All translation files are already compiled and up to date."
        
        return (success, output, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, '', 'Command timed out after 60 seconds')
    except Exception as e:
        return (False, '', f'Error: {str(e)}')



def make_messages():
    """
    Run makemessages to extract new translatable strings from templates.
    Returns (success, output, error)
    """
    try:
        import sys
        python_executable = sys.executable
        manage_py = settings.BASE_DIR / 'manage.py'
        
        result = subprocess.run(
            [python_executable, str(manage_py), 'makemessages', '-a', '--no-obsolete'],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            shell=False
        )
        
        # Consider it successful if returncode is 0 or if output contains "processing"
        success = result.returncode == 0 or 'processing' in result.stdout.lower()
        
        return (success, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, '', 'Command timed out after 120 seconds')
    except Exception as e:
        return (False, '', f'Error: {str(e)}')



def get_available_languages():
    """Get list of available languages from settings"""
    return [lang[0] for lang in settings.LANGUAGES if lang[0] != 'en']


def get_translation_stats(language_code):
    """Get statistics about translations for a language"""
    translations = parse_po_file(language_code)
    
    total = len(translations)
    translated = sum(1 for t in translations if t['msgstr'].strip())
    untranslated = total - translated
    
    return {
        'total': total,
        'translated': translated,
        'untranslated': untranslated,
        'percentage': round((translated / total * 100) if total > 0 else 0, 1)
    }


def group_translations_by_context(translations):
    """Group translations by their source file/context"""
    grouped = defaultdict(list)
    
    for trans in translations:
        locations = trans.get('locations', [])
        if locations:
            # Use the first location as the context
            context = locations[0].split(':')[0] if ':' in locations[0] else locations[0]
            # Simplify the path
            context = context.replace('.\\', '').replace('/', ' / ')
        else:
            context = 'Unknown'
        
        grouped[context].append(trans)
    
    return dict(grouped)
