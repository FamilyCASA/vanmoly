path = 'D:/desktop/DESIGNARY-SYS-V3.0/backend/app/routes/case_routes.py'
with open(path, 'rb') as f:
    data = f.read()

lines = []
pos = 0
while pos < len(data):
    crlf = data.find(b'\r\n', pos)
    lf = data.find(b'\n', pos)
    if crlf != -1 and (lf == -1 or crlf < lf):
        lines.append(data[pos:crlf])
        pos = crlf + 2
    elif lf != -1:
        lines.append(data[pos:lf])
        pos = lf + 1
    else:
        lines.append(data[pos:])
        break

print(f'Total lines: {len(lines)}')
print()

# Look for unclosed strings: lines ending with non-ASCII without closing quote
# Pattern: "' followed by valid UTF-8 Chinese text but no closing '"
# The bad pattern is: = '中文 without closing '

fixes = []
for i, raw in enumerate(lines):
    try:
        decoded = raw.decode('utf-8')
    except:
        decoded = raw.decode('latin-1')
    
    # Check for unclosed string literals
    # Pattern: ends with Chinese chars but no closing quote
    stripped = decoded.rstrip()
    if stripped.endswith("'"):
        continue  # properly closed
    
    # Check if line has a Chinese character near the end
    # and ends without closing the string
    # E.g., "case.status = '已发布" (missing closing ')
    # The raw bytes would end with: e5 b7 b2 e5 8f 91 e5 b8 83 (no trailing 27)
    
    if b"= '" in raw and not raw.rstrip().endswith(b"'"):
        # Check if the part after = ' has Chinese but no closing quote
        eq_pos = raw.find(b"= '")
        if eq_pos != -1:
            after = raw[eq_pos+3:]
            # If after contains UTF-8 Chinese but no 0x27 (') after the Chinese
            # and the line ends (no more content after)
            ends_with_nonascii = False
            for j in range(len(after)):
                b = after[j]
                if b > 127:
                    ends_with_nonascii = True
            
            if ends_with_nonascii and not raw.rstrip().endswith(b"'"):
                # Find the closing quote position in raw bytes
                # We need to find the next ' after the = '
                # But there might not be one
                fixes.append((i+1, raw, decoded.strip()))

print(f'Found {len(fixes)} lines with potentially unclosed strings:')
for ln, raw, dec in fixes:
    print(f'Line {ln}:')
    print(f'  Raw bytes: {repr(raw[:80])}')
    print(f'  Decoded: {dec}')
    print()

# Also scan for the specific pattern: status = '已发布 (missing ')
# Using regex on bytes
import re
pattern = re.compile(b"= '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83(?!')")
matches = []
for i, raw in enumerate(lines):
    if pattern.search(raw):
        matches.append((i+1, raw))

print(f'Specific pattern matches: {len(matches)}')
for ln, raw in matches:
    print(f'  Line {ln}: {raw[:80]}')