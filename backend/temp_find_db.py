import os, sqlite3

# Check if the database file exists
paths_to_check = [
    r'D:\desktop\VANMOLY-SYS-V3.0\backend\vanmoly_v3.db',
    r'D:\desktop\VANMOLY-SYS-V3.0\backend\vanmoly.db',
]

for p in paths_to_check:
    if os.path.exists(p):
        print(f"Found: {p} ({os.path.getsize(p)} bytes)")
    else:
        print(f"Not found: {p}")

# Also check for .db files in the backend directory
backend_dir = r'D:\desktop\VANMOLY-SYS-V3.0\backend'
if os.path.exists(backend_dir):
    db_files = [f for f in os.listdir(backend_dir) if f.endswith('.db')]
    print(f"\n.db files in {backend_dir}:")
    for f in db_files:
        fp = os.path.join(backend_dir, f)
        print(f"  {f} ({os.path.getsize(fp)} bytes)")
else:
    print(f"Backend dir not found: {backend_dir}")
