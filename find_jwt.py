import sys; sys.stdout.reconfigure(encoding='utf-8')
import re

# Search for jwt_required_v2 definition
import os
for root, dirs, files in os.walk(r'D:\desktop\VANMOLY-SYS-V3.0\backend'):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            try:
                with open(fp, encoding='utf-8') as fh:
                    c = fh.read()
                if 'jwt_required_v2' in c and ('def jwt_required_v2' in c or 'jwt_required_v2 =' in c):
                    print(f"Defined in: {fp}")
                    idx = c.find('jwt_required_v2')
                    print(c[max(0,idx-50):idx+200][:300])
            except:
                pass
