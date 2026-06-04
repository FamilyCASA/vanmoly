cd D:\desktop\VANMOLY-SYS-V3.0\backend
python -c "from waitress import serve; from app import create_app; serve(create_app(), host='0.0.0.0', port=8080, threads=4)"
