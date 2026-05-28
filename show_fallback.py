import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Show context around the two fallback dicts at offset 89388 and 104579
for offset in [89350, 104540]:
    print(f"\n--- offset {offset} ---")
    print(c[offset:offset+300])
