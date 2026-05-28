import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find the input table area
idx = c.find('addMatRow')
if idx > 0:
    # Search backwards for the table header
    search_start = max(0, idx - 3000)
    block = c[search_start:idx+500]
    # Find the last <th before addMatRow
    th_pos = block.rfind('<th')
    # Find the first <th in the table
    first_th = block.find('<th')
    if first_th >= 0:
        # Find the table start
        table_start = block.rfind('<table', 0, first_th)
        table_end = block.find('</table>', th_pos)
        if table_start >= 0 and table_end >= 0:
            table_block = block[table_start:table_end+8]
            print(table_block[:2000])
