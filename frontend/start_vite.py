import subprocess, os, sys
os.chdir(r'D:\desktop\VANMOLY-SYS-V3.0\frontend')
proc = subprocess.Popen([sys.executable, 'node_modules/vite/bin/vite.js', '--host', '0.0.0.0'])
print(f'Vite PID: {proc.pid}')