with open('D:/desktop/DESIGNARY-SYS-V3.0/backend/app/routes/case_routes.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
for i in [293, 294, 295, 326, 327, 328]:
    print(f'Line {i+1}: {repr(lines[i][:100])}')