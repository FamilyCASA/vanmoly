# 新建报价完整操作逻辑及PDF输出规范

# 一、新建报价整体操作流程（后台管理端）

核心路径：后台管理 → 报价管理 → 新建报价，全程按以下步骤依次操作，确保数据完整、逻辑连贯，最终生成符合规范的PDF报价表。

## 步骤1：封面美化（新建报价第一步）

两种封面设置方式，可二选一或组合使用，兼顾美观性与便捷性：

- 自定义封面元素：手动设置封面各项视觉及信息元素（贴合后续PDF封面规范），可调整布局、配色，添加必要信息标识。

- 导入封面模板：直接选用系统内已保存的封面模板，无需重复设置，可轻微修改模板内信息（如合同编号、客户信息）适配本次报价。

## 步骤2：基础信息录入

完成封面美化后，依次录入核心基础信息，建立报价基础框架：

- 客户项目资料：录入客户基本信息、项目名称、项目地址、户型信息等核心内容，作为报价关联基础。

- 关联服务人员：选择本次项目对应的乙方服务团队成员，明确责任分工，同步展示在PDF封面。

- 关联案例：关联同类项目案例（可选），增强报价可信度，无需同步至PDF，仅作为后台参考。

## 步骤3：物料与服务项目录入（核心环节）

按“房间物料 \+ 全案服务”分类录入，确保无遗漏，系统自动完成分类汇总，为后续PDF费用汇总、房间物料展示提供数据支撑：

### 3\.1 房间物料录入（按房间逐一操作）

针对每个房间，依次完成以下物料信息录入，确保每个房间的物料完整无误：

- 房间选择：明确当前录入物料对应的房间（如主卧、客厅、厨房等），后续按房间分类展示在PDF中。
插入房间名称表：
|客厅|Living Room|
|餐厅|Dining Room|
|主卧|Master Bedroom|
|次卧|Secondary Bedroom / Guest Bedroom|
|儿童房|Kids\&\#39; Room / Children\&\#39;s Bedroom|
|老人房|Elderly Room / Senior Bedroom|
|书房 / 工作间|Study / Home Office|
|中厨|Chinese Kitchen|
|西厨|Western Kitchen|
|开放式厨房|Open Kitchen|
|主卫|Master Bathroom|
|客卫|Guest Bathroom|
|公卫（住宅内）|Public Bathroom|
|公卫（公寓）|Common Bathroom|
|干湿分离卫生间|Wet\-Dry Separate Bathroom|
|玄关|Foyer / Entryway|
|入户花园|Entry Garden / Porch Garden|
|生活阳台|Service Balcony|
|休闲阳台|Leisure Balcony|
|观景阳台|View Balcony / Scenic Balcony|
|过道 / 走廊|Passageway / Corridor|
|步入式衣帽间|Walk\-in Closet|
|嵌入式衣帽间|Built\-in Closet|
|储藏室 / 杂物间|Storage Room / Utility Room|
|阁楼|Attic / Loft|
|地下室|Basement|
|影音室 / 家庭影院|Home Theater / Media Room|
|健身室 / 瑜伽室|Home Gym / Yoga Room|
|茶室 / 棋牌室|Tea Room / Chess \&amp; Card Room|
|琴房 / 画室|Music Room / Art Studio|
|保姆房|Maid\&\#39;s Room / Nanny\&\#39;s Room|
|儿童活动区|Kids\&\#39; Play Area / Children\&\#39;s Activity Zone|
|老人护理间|Elderly Care Room|
|宠物房|Pet Room|
|阳光房|Sunroom / Solarium|
|入户花厅|Entry Hall with Garden / Foyer Garden|
|空中花园|Sky Garden / Rooftop Garden|
|酒窖|Wine Cellar|
|雪茄房|Cigar Room|
|冥想室|Meditation Room|
|私人会所|Private Clubhouse|
|设备间（水电 / 空调）|Equipment Room \(Water/Electricity/Air Conditioning\)|
|店铺 / 门店|Store / Shop|
|橱窗展示区|Window Display Area|
|收银台|Cashier Desk / Checkout Counter|
|休息区|Rest Area / Lounge Area|
|试衣间 / 试戴间|Fitting Room / Trial Room|
|咖啡馆 / 奶茶店 \- 前厅|Café/Milk Tea Shop \- Front Hall|
|咖啡馆 / 奶茶店 \- 操作间|Café/Milk Tea Shop \- Preparation Area|
|咖啡馆 / 奶茶店 \- 储物间|Café/Milk Tea Shop \- Storage Room|
|餐厅 / 火锅店 \- 大堂|Restaurant/Hot Pot Restaurant \- Lobby|
|餐厅 / 火锅店 \- 包厢|Restaurant/Hot Pot Restaurant \- Private Room|
|餐厅 / 火锅店 \- 后厨|Restaurant/Hot Pot Restaurant \- Back Kitchen|
|餐厅 / 火锅店 \- 备餐间|Restaurant/Hot Pot Restaurant \- Pantry|
|美容美发店 \- 接待区|Beauty Salon \- Reception Area|
|美容美发店 \- 操作区|Beauty Salon \- Service Area|
|美容美发店 \- 烫染区|Beauty Salon \- Perm \&amp; Dye Area|
|美容美发店 \- 洗头区|Beauty Salon \- Shampoo Area|
|美甲店 / 纹绣店|Nail Salon / Embroidery Studio|
|宠物店 \- 展示区|Pet Store \- Display Area|
|宠物店 \- 洗护区|Pet Store \- Grooming \&amp; Washing Area|
|宠物店 \- 美容区|Pet Store \- Pet Grooming Area|
|宠物店 \- 寄养区|Pet Store \- Boarding Area|
|书店 / 文具店 \- 阅读区|Bookstore/Stationery Store \- Reading Area|
|书店 / 文具店 \- 售卖区|Bookstore/Stationery Store \- Sales Area|
|前台 / 接待区|Reception Desk / Reception Area|
|开放办公区|Open Office Area|
|独立办公室|Private Office|
|小型会议室|Small Meeting Room|
|中型会议室|Medium Meeting Room|
|大型会议室|Large Meeting Room|
|洽谈室|Negotiation Room / Meeting Room|
|培训室|Training Room|
|档案室 / 资料室|Archive Room / Document Room|
|茶水间|Pantry / Staff Kitchen|
|员工休息室|Staff Lounge / Rest Room|
|展厅 / 产品展示区|Exhibition Hall / Product Display Area|
|样板间|Show Flat / Model Room|
|开放工位区|Open Workstation Area|
|总监办公室|Director\&\#39;s Office|
|总经理办公室|General Manager\&\#39;s Office|
|财务室|Finance Office / Accounting Office|
|人力资源部办公室|HR Office / Human Resources Office|
|部门独立办公室|Department Private Office|
|视频会议室|Video Conference Room|
|研讨室|Seminar Room|
|多功能厅|Multi\-Functional Hall|
|员工餐厅|Staff Canteen / Employee Restaurant|
|更衣室|Locker Room / Changing Room|
|打印室 / 文印室|Printing Room / Copy Room|
|机房 / 服务器室|Server Room / IT Room|
|安保室|Security Room|
|传达室|Gate House / Reception Lodge|
|电梯厅|Elevator Lobby / Lift Hall|
|楼梯间|Stairwell / Staircase|
|小区大堂|Residential Lobby|
|写字楼大堂|Office Building Lobby|
|等候区|Waiting Area|
|公共卫生间|Public Toilet / Restroom|
|无障碍卫生间|Accessible Bathroom / Disabled Toilet|
|母婴室|Mother\-and\-Baby Room / Nursing Room|
|吸烟区|Smoking Area|
|快递柜区|Courier Cabinet Area / Parcel Locker Area|
|垃圾投放区|Garbage Disposal Area / Trash Zone|
|物业办公室|Property Management Office|
|酒吧 / 清吧 \- 吧台|Bar/Lounge \- Bar Counter|
|酒吧 / 清吧 \- 卡座|Bar/Lounge \- Booth|
|酒吧 / 清吧 \- 舞池|Bar/Lounge \- Dance Floor|
|KTV \- 包厢|KTV \- Private Room|
|健身房 \- 器械区|Gym \- Equipment Area|
|健身房 \- 有氧区|Gym \- Cardio Area|
|健身房 \- 操课室|Gym \- Group Class Studio|
|健身房 \- 淋浴间|Gym \- Shower Room|
|瑜伽馆 / 普拉提馆|Yoga Studio / Pilates Studio|
|桌游馆 / 剧本杀店 \- 游戏区|Board Game/script Murder Shop \- Game Area|
|桌游馆 / 剧本杀店 \- 换装区|Board Game/script Murder Shop \- Costume Area|
|影院 \- 放映厅|Cinema \- Auditorium / Screening Hall|
|影院 \- 售票区|Cinema \- Ticket Counter|
|影院 \- 零食区|Cinema \- Snack Bar / Concession Stand|
|诊所 \- 诊疗室|Clinic \- Consultation Room|
|诊所 \- 输液室|Clinic \- Infusion Room|
|诊所 \- 药房|Clinic \- Pharmacy|
|诊所 \- 挂号区|Clinic \- Registration Area|
|体检中心 \- 检查室|Physical Examination Center \- Examination Room|
|体检中心 \- 等候区|Physical Examination Center \- Waiting Area|
|幼儿园 \- 教室|Kindergarten \- Classroom|
|幼儿园 \- 活动室|Kindergarten \- Activity Room|
|幼儿园 \- 午睡室|Kindergarten \- Nap Room|
|幼儿园 \- 食堂|Kindergarten \- Dining Hall|
|培训机构 \- 教室|Training Institution \- Classroom|
|培训机构 \- 接待区|Training Institution \- Reception Area|
|厂房|Factory Building / Workshop|
|常温仓|Normal Temperature Warehouse|
|冷藏仓|Refrigerated Warehouse|
|操作间|Operation Room / Workshop|
|值班室|Duty Room / On\-Call Room|
|储物间|Storage Room|
|传达室|Gate House / Guard House|

- 物料筛选与选择：通过物料筛选功能，快速找到所需物料，确定商品名称、物料名称及物料类别。
- 重要：同一行实现：筛选（房间）+自定义"商品名称"+筛选物料：通过模糊搜索，下拉菜单（符合关键词的物料名称，包含物料的所有字段，可以输入大类，也可以输入品牌，花色，材料等等关键词）快读定位物料，实现物料筛选功能，自动填充物料名称及物料类别。

- 物料参数录入：必填参数包括数量、单位；可选参数（按需录入）包括定制尺寸、工艺要求；补充参数包括型号、规格、材质、品牌、物料主图、备注，确保物料信息精准可追溯。

- 重复操作：依次完成每个房间的所有物料录入，确保无遗漏（如客厅的沙发、茶几，主卧的床、衣柜等）。

### 3\.2 全案服务项目录入

录入整个户型的所有服务类项目，涵盖项目全流程服务，统一纳入费用汇总：

- 核心服务项目：安装费、配送费、清运费、保洁费、设计费、税费。

- 其他服务/费用：根据项目需求补充，如施工保证金、保险费、消防器材费、临时卫生间费、监控费、成品保护费等（同步纳入PDF“其他费用”分类）。

## 步骤4：系统自动汇总与PDF导出

- 自动分类汇总：系统根据录入的物料、服务项目，按“费用类型 \+ 房间”自动分类，计算各项金额、汇总总费用，无需手动核算。

- PDF导出：选择预设模板，系统按固定顺序生成PDF报价表（具体顺序见下文规范），支持直接下载、打印。

## 特殊说明：签字功能

当前后台管理端删除签字功能，原因如下：远程签字需微信小程序配合实现，技术层面难以单独在后台完成；后续编译成微信小程序时，再新增远程会签功能，确保签字流程合规、便捷。

# 二、报价表PDF输出顺序及详细规范

PDF整体分为4个部分：封面 → 费用分类汇总页 → 房间物料详情页 → 尾页（报价原则），各页面内容、格式严格遵循以下规范，确保专业、统一。

## 第一页：封面

核心要求：信息完整、布局美观，包含以下所有元素，添加公司logo水印（贯穿封面，不遮挡核心信息），标注保密标签：

- 核心标题：报价单（可搭配副标题，如“帝标\-设记家 全案报价单”）。

- 公司信息：中文名称（帝标\-设记家）、英文名称（DESIGNARY）。

- 基础标识：合同编号、时间戳（生成PDF的时间，格式：YYYY\-MM\-DD HH:MM:SS）。

- 项目信息：客户项目详情（客户名称、项目名称、项目地址、户型信息）。

- 服务信息：乙方服务团队（关联的服务人员姓名、岗位）。

- 其他标识：保密标签（如“保密文件，严禁外泄”）、公司logo水印（淡色，均匀分布）。

## 第二页：费用分类汇总（层级至第二层）

核心要求：层级清晰、金额准确，按以下分类展示，每个一级分类下展示所有二级分类，最后标注本案例合计费用：

1. 全案服务费用（一级分类）
        

    - 二级分类：设计费、保洁费、配送费、搬运费、安装费用、管理费用、税费、其他费用

2. 硬装材料费用（一级分类）
        

    - 二级分类：水电材料、铺装材料、木工材料、电器设备、智能设备、消防设备、空调设备、暖通设备、照明设备等

3. 硬装施工费用（一级分类）

    - 二级分类：土建、水电工、木工、泥工、瓦工、油工等

4. 全屋定制费用（一级分类）
        

    - 二级分类：柜体、柜门、五金配件、特殊工艺、石材、氛围照明电器、配送、搬运、安装

5. 成品家具费用（一级分类）


    - 二级分类：沙发、茶几、餐桌、餐椅、床、床头柜、矮柜、其他

6. 软装饰品费用（一级分类）


    - 二级分类：窗帘、轨道、智能轨道、纱、卷帘、地毯、挂画、摆件、厨具、餐具、落地灯、吊灯、台灯、其他

7. 其他费用（一级分类）
        

    - 二级分类：施工保证金、保险、消防器材、临时卫生间、监控、成品保护

8. 本案例合计费用：所有一级分类费用总和，加粗突出显示。

## 第三页——结束页：房间物料详情

核心要求：按房间分类展示，信息完整、条理清晰，每个房间单独作为一个模块，包含以下内容：

- 房间标题：大标题标注房间名称（如“主卧”“客厅”），紧跟此空间所有物料总金额（加粗，如“主卧物料总金额：XXX元”）。

- 物料列表：按表格形式展示，每一行对应一件物料，表格列顺序及显示字段内容如下：
        
编号 \+ 商品名称 \+ 物料名称 \+ 物料类别 \+ 型号 \+ 规格 \+ 材质 \+ 品牌 \+ 图片（主图，小尺寸展示） \+ 定制尺寸（有则填写，无则填“无”） \+ 单价\+数量 \+ 单位 \+ 工艺 \+ 备注（同一个商品名称下可以包含多个物料，商品名称自动合并单元格，例如：商品名称：儿童房7门衣柜，包含物料：柜体，柜门，抽屉，挂衣杆，氛围灯具，拉篮，拉手，铝合金玻璃门，烤漆工艺，实木封边拉手工艺）
      

- 排版规范：每个房间模块独立分隔，表格清晰，图片不拉伸，文字不溢出，确保可读性。标题字段的那远哥填充淡绿色，人民币单元格用”￥：55\.00“格式；

## 尾页：报价原则（单独一页）

核心要求：突出公司报价理念，深化slogan，语言正式、有公信力，排版居中或左对齐，加粗突出核心语句，内容如下：

【帝标\-设记家 报价原则】
本报价单严格遵循“预算即决算，零增项”核心承诺，所有物料、服务项目及对应费用均详细列明，无隐藏收费、无变相增项。报价有效期内，除非客户主动提出物料更换、规格调整或服务升级，否则最终结算金额与本报价单合计费用完全一致，切实保障客户权益，让每一笔消费透明、可控、放心。



# 三、补充说明

- 所有录入的物料、服务项目信息，需确保准确无误，系统自动汇总后，建议手动核对一次合计费用，避免参数录入错误导致金额偏差。

- 封面模板可提前预设，包含公司固定信息（名称、logo），减少重复操作；自定义封面时，需保持与公司品牌调性一致。

- PDF导出后，可预览检查格式、信息完整性，若需修改，返回新建报价页面调整后重新导出。

