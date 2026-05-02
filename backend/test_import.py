# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\desktop\DESIGNARY-SYS-V3.0\backend')

# Test import
try:
    from app.routes import case_routes
    print('SUCCESS: case_routes imported')
except SyntaxError as e:
    print(f'SYNTAX ERROR: {e}')
    # Show the problematic line
    import traceback
    tb = traceback.extract_tb(sys.exc_info()[2])
    if tb:
        filename, lineno, _, line = tb[-1]
        print(f'File: {filename}, Line: {lineno}')
        print(f'Line content: {line!r}')
except Exception as e:
    print(f'ERROR: {e}')