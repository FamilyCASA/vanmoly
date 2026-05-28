import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:8080/api/v3/public/cases/37/slide-data'
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        case_data = data.get('data', {}).get('case', {})

        print("=== case_data 关键字段 ===")
        print(f"planner: {case_data.get('planner')}")
        print(f"designer: {case_data.get('designer')}")
        print(f"responsible: {case_data.get('responsible')}")
        print(f"\nscene_tags: {case_data.get('scene_tags')}")
        print(f"scene_tag: {case_data.get('scene_tag')}")
except Exception as e:
    print(f"Error: {e}")
