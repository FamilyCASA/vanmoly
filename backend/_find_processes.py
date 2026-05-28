import os

backend_dir = r'D:\desktop\VANMOLY-SYS-V3.0\backend'
for root, dirs, files in os.walk(backend_dir):
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as fp:
                    for i, line in enumerate(fp):
                        if 'processes' in line:
                            print(f'{fpath}:{i+1}: {line.rstrip()}')
            except:
                pass
