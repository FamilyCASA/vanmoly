import sys

path = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, 'rb') as f:
    data = f.read()

# Check file format
print('File size:', len(data))
print('Has CRLF:', b'\r\n' in data)
print('Has LF:', b'\n' in data)
print('Has CR:', b'\r' in data and b'\n' not in data)

# Count lines by scanning
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

print(f'Total lines (scanned): {len(lines)}')

# Show lines 279-283
for i in range(278, 284):
    if i < len(lines):
        raw = lines[i]
        dec = raw.decode('utf-8', errors='replace')
        print(f'--- Line {i+1} ({len(raw)} bytes) ---')
        for j, b in enumerate(raw[:60]):
            ch = chr(b) if 32 <= b < 127 else f'\\x{b:02x}'
            print(f'  [{j:3d}] 0x{b:02x} = {ch}')
        print(f'  decoded: {repr(dec[:80])}')
        print()

# Try compile
try:
    code = compile(data.decode('utf-8'), path, 'exec')
    print('Compiles OK - no SyntaxError')
except SyntaxError as e:
    print(f'SyntaxError at line {e.lineno}, offset {e.offset}')
    if e.lineno and e.lineno <= len(lines):
        line = lines[e.lineno - 1]
        print(f'Raw bytes: {repr(line[:80])}')