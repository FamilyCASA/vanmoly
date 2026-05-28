# -*- coding: utf-8 -*-
import urllib.request
import json

url = 'http://localhost:8080/api/v3/frontend/themes/active'
try:
    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode('utf-8'))
    theme = data['data']
    print(f"Theme: {theme.get('theme_name')} / {theme.get('theme_key')}")
    print(f"Active: {theme.get('is_active')}")
    print(f"Colors count: {len(theme.get('colors', {}))}")
    sc = theme.get('section_configs', {})
    print(f"Section configs: {json.dumps(sc, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f'Error: {e}')
