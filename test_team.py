import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:8080/api/v3/public/cases/37/slide-data'
with urllib.request.urlopen(url, timeout=5) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    case_data = data.get('data', {}).get('case', {})

    print("=== 团队成员数据 ===")
    print(f"planner: {case_data.get('planner')}")
    print(f"designer: {case_data.get('designer')}")
    print(f"responsible: {case_data.get('responsible')}")

    print(f"\n=== scene_tags ===")
    print(f"scene_tags: {case_data.get('scene_tags')}")
