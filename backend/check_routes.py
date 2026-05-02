from app import create_app

app = create_app()
with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.endpoint:
            methods = '|'.join(rule.methods - {'OPTIONS', 'HEAD'})
            routes.append(f'{rule.rule} [{methods}]')
    for r in sorted(routes):
        if '/api/v3' in r:
            print(r)
