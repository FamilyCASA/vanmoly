@echo off
chcp 65001 >nul
cd /d D:\desktop\VANMOLY-SYS-V3.0\backend
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
start /B python run_waitress.py >nul 2>&1
timeout /t 5 /nobreak >nul

echo === Testing workflow phase filters ===
python -c "
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')
base = 'http://localhost:8080/api/v3'
tests = [('designing','提案阶段'),('construction','施工中'),('soft_service','软装服务'),('after_sales','售后服务')]
for progress, label in tests:
    url = f'{base}/public/cases?progress={progress}&page_size=5'
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        data = json.loads(resp.read())
        inner = data.get('data', data)
        total = inner.get('total', 0)
        print(f'{label}: {total} cases')
    except Exception as e:
        print(f'{label}: ERROR - {e}')

print()
url2 = f'{base}/cases/options'
try:
    resp2 = urllib.request.urlopen(url2, timeout=5)
    data2 = json.loads(resp2.read())
    opts = data2.get('data', data2).get('progress_options', [])
    for o in opts:
        print(f'  {o.get(\"key\")}: {o.get(\"label\")} ({o.get(\"count\")})')
except Exception as e:
    print(f'options ERROR: {e}')
"

echo Done.