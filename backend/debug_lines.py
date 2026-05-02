path = 'D:/desktop/DESIGNARY-SYS-V3.0/backend/app/routes/case_routes.py'
with open(path, 'rb') as f:
    data = f.read()

# Split lines by CRLF
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

# Check lines 293 (0-indexed) and 326
for idx in [293, 326]:
    raw = lines[idx]
    print(f'=== Line {idx+1} ===')
    print('Raw bytes:', repr(raw))
    # Show all bytes
    for j, b in enumerate(raw):
        if 32 <= b < 127:
            print(f'  [{j:3d}] 0x{b:02x} = {chr(b)}')
        else:
            print(f'  [{j:3d}] 0x{b:02x} = \\x{b:02x}')
    # Try decoding
    try:
        u = raw.decode('utf-8')
        print('UTF-8:', repr(u))
    except:
        pass
    try:
        g = raw.decode('gbk')
        print('GBK:', repr(g))
    except:
        pass
    print()