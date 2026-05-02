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

# Target replacements (byte-level)
replacements = [
    # 已发布 missing closing quote
    (b"case.status = '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83", b"case.status = '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83'"),
    # 已下架 missing closing quote
    (b"case.status = '\\xe5\\xae\\xb8\\xe8\\xb9\\xad\\xe7\\xac\\x85\\xe9\\x8f\\x8b", b"case.status = '\\xe5\\xae\\xb8\\xe8\\xb9\\xad\\xe7\\xac\\x85\\xe9\\x8f\\x8b'"),
    # status filter missing closing quote
    (b"CaseStudy.status == '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83,'", b"CaseStudy.status == '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83',"),
    (b"CaseStudy.status == '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83,\"", b"CaseStudy.status == '\\xe5\\xb7\\xb2\\xe5\\x8f\\x91\\xe5\\xb8\\x83',"),
]

# Apply replacements
fixed_count = 0
for i in range(len(lines)):
    for old, new in replacements:
        if old in lines[i]:
            print(f'Line {i+1}: replacing')
            print(f'  Before: {repr(lines[i][:80])}')
            lines[i] = lines[i].replace(old, new)
            print(f'  After:  {repr(lines[i][:80])}')
            fixed_count += 1
            break

print(f'\nFixed {fixed_count} lines')

# Build output
output = b'\r\n'.join(lines)
# Preserve trailing newline if original had one
has_nl = data.endswith(b'\r\n') or data.endswith(b'\n')
if has_nl:
    if b'\r\n' in data:
        output += b'\r\n'
    else:
        output += b'\n'

# Verify
try:
    compiled = compile(output.decode('utf-8'), path, 'exec')
    print('Fixed code compiles OK!')
except SyntaxError as e:
    print(f'Still has SyntaxError at line {e.lineno}, offset {e.offset}: {e}')
    lines_raw = output.decode('utf-8', errors='replace').split('\n')
    if e.lineno and e.lineno <= len(lines_raw):
        print(f'Problem line: {repr(lines_raw[e.lineno-1])}')

# Backup
backup = path + '.broken'
with open(backup, 'wb') as f:
    f.write(data)
print(f'Backup: {backup}')

# Save
with open(path, 'wb') as f:
    f.write(output)
print(f'Saved. Original: {len(data)} bytes, Fixed: {len(output)} bytes')