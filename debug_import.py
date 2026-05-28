import sys; sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')
from app.models.case import *
import app.models.case as m
names = [n for n in dir(m) if not n.startswith('_')]
print("Exported names:", names)
