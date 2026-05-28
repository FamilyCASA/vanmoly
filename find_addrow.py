import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Fix addMatRow - missing custom_name and custom_measure
old = "color_name:'',c"
# Need to find the full addMatRow push string
old_add = "matRows.value.push({ name:'',cat1Id:'',cat2Id:'',material_name:'',material_id:null,spec:'',width:null,depth:null,height:null,quantity:1,price:null,amount:0,unit:'',calcVal:null,sku_code:'',brand:'',material:'',main_image:'',env_level:'合格',supply_chain:'直供',color_name:'',c"

# It was cut off - let me search for the end
idx = c.find("color_name:'',c")
if idx > 0:
    # Show context
    print("Found at offset:", idx)
    print("Context:", c[idx:idx+100])
