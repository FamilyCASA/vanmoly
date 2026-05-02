from waitress import serve
from app import create_app

app = create_app()
print("Starting server on http://0.0.0.0:8000")
serve(app, host='0.0.0.0', port=8000, threads=4)
