import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find saveMaterials function
import re
matches = re.findall(r'(saveMaterials.*?)(?=\n\s*async|\n\s*const|\n\s*function|\n\s*<template)', content, re.DOTALL)
for i, m in enumerate(matches[:2]):
    print(f"=== Match {i+1} ===")
    print(m[:2000])
