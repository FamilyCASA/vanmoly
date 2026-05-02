#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复案例编辑模块的时间轴节点功能"""

# 1. 添加后端API - 获取workflow nodes列表
backend_code = '''
# 添加到 case_routes.py 的末尾

@case_bp.route('/workflow/nodes', methods=['GET'])
@jwt_required_v2
def get_workflow_nodes(current_user):
    """获取流程节点模板列表"""
    try:
        nodes = WorkflowNode.query.filter_by(
            is_enabled=True
        ).order_by(WorkflowNode.phase_order, WorkflowNode.sort_order).all()
        
        return api_response(data={
            'items': [{
                'id': n.id,
                'node_code': n.node_code,
                'node_name': n.node_name,
                'phase': n.phase,
                'phase_order': n.phase_order,
                'sort_order': n.sort_order,
                'description': n.description or ''
            } for n in nodes]
        })
    except Exception as e:
        return api_response(code=500, message=str(e))
'''

print("=== 1. 后端API代码（添加到 case_routes.py）===")
print(backend_code)

# 2. 前端修复说明
print("\n=== 2. 前端修复步骤 ===")
print("""
步骤A：添加API函数到 frontend/src/api/case.js

export function getWorkflowNodes() {
  return request.get('/workflow/nodes')
}

步骤B：修改 CaseEdit.vue

1. 在 script setup 中添加：
   - 导入 getWorkflowNodes API
   - 添加 workflowNodes ref
   - 在 onMounted 中调用获取nodes列表

2. 修改"添加节点"按钮点击事件：
   从: @click="showTimelineDialog = true"
   到:   @click="openAddTimelineDialog()"

3. 添加 openAddTimelineDialog 函数：
   const openAddTimelineDialog = () => {
     editingTimeline.value = null
     timelineForm.node_time = new Date()  // 初始化为当前时间
     timelineForm.title = ''
     timelineForm.content = ''
     timelineForm.media_urls = ''
     timelineMediaList.value = []
     showTimelineDialog.value = true
   }

4. 修改节点标题字段：
   从: <el-input v-model="timelineForm.title" placeholder="如：开工大吉" />
   到: <el-select 
         v-model="timelineForm.title" 
         filterable 
         allow-create
         placeholder="选择或输入节点标题"
         style="width: 100%"
       >
         <el-option 
           v-for="node in workflowNodes" 
           :key="node.id" 
           :label="node.node_name" 
           :value="node.node_name"
         />
       </el-select>
""")

print("\n修复完成！")
