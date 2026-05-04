"""
Doubao (火山引擎) AI 工具封装
用于楼盘信息智能总结、数据提取等
"""
import requests
import json
import logging

logger = logging.getLogger(__name__)

# 豆包 Seed 2.0 Pro 配置
DOUBAO_API_KEY = "06393f55-d0d3-4b88-a47f-926547e6bc93"
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DOUBAO_MODEL = "doubao-seed-2-0-pro-260215"


def call_doubao(messages: list, temperature: float = 0.3, timeout: int = 30) -> str:
    """
    调用豆包大模型
    :param messages: OpenAI 格式消息列表
    :param temperature: 温度
    :param timeout: 超时秒数
    :return: AI 回复文本
    """
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": DOUBAO_MODEL,
        "messages": messages,
        "temperature": temperature
    }

    try:
        resp = requests.post(DOUBAO_API_URL, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        logger.error("AI API timeout")
        return ""
    except requests.exceptions.HTTPError as e:
        logger.error(f"AI API HTTP error: {e.response.status_code} {e.response.text[:200]}")
        return ""
    except Exception as e:
        logger.error(f"AI API error: {str(e)}")
        return ""


def ai_summarize_building(raw_text: str) -> dict:
    """
    AI 总结楼盘信息，返回结构化字段
    输入：用户输入的楼盘原始文本（如从网页复制的杂乱信息）
    输出：自动填表用的结构化数据
    """
    messages = [
        {
            "role": "system",
            "content": (
                "你是楼盘数据整理专员。从用户提供的楼盘原始信息中提取结构化数据。"
                "必须以JSON格式返回，包含以下字段（无法提取的填null）：\n"
                "name: 楼盘名称\n"
                "alias: 别名\n"
                "province: 省\n"
                "city: 市\n"
                "district: 区/县\n"
                "address: 详细地址\n"
                "developer: 开发商\n"
                "property_company: 物业公司\n"
                "build_year: 建成年份(整数)\n"
                "total_houses: 总户数(整数)\n"
                "property_type: 物业类型(residential/villa/apartment/commercial/mixed)\n"
                "remark: 备注摘要\n"
                "只输出JSON，不要输出其他内容。"
            )
        },
        {
            "role": "user",
            "content": raw_text
        }
    ]

    result = call_doubao(messages, temperature=0.1)
    if not result:
        return {}

    # 尝试解析 JSON
    try:
        # 去掉可能的 markdown 代码块标记
        if result.startswith("```"):
            lines = result.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            result = "\n".join(lines)
        return json.loads(result)
    except json.JSONDecodeError:
        logger.warning(f"AI返回非JSON: {result[:200]}")
        return {"raw_summary": result}


def ai_extract_customers(raw_text: str) -> list:
    """
    AI 从文本中提取客户/业主信息
    输入：Excel中读取的原始行数据或手动输入的文本
    输出：[{name, phone, room, building_no, unit_no, house_type, house_area}, ...]
    """
    messages = [
        {
            "role": "system",
            "content": (
                "你是客户信息提取专员。从提供的文本中提取所有业主/客户信息。"
                "必须以JSON数组格式返回，每个元素包含以下字段（无法提取的填null）：\n"
                "name: 姓名\n"
                "phone: 手机号\n"
                "room: 房号\n"
                "building_no: 楼栋号\n"
                "unit_no: 单元号\n"
                "house_type: 户型(如3室2厅)\n"
                "house_area: 面积(数字)\n"
                "只输出JSON数组，不要输出其他内容。"
            )
        },
        {
            "role": "user",
            "content": raw_text
        }
    ]

    result = call_doubao(messages, temperature=0.1)
    if not result:
        return []

    try:
        if result.startswith("```"):
            lines = result.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            result = "\n".join(lines)
        return json.loads(result)
    except json.JSONDecodeError:
        logger.warning(f"AI客户提取返回非JSON: {result[:200]}")
        return []


def ai_analyze_excel_row(row_data: dict) -> dict:
    """
    AI 分析单条 Excel 行数据，智能映射到系统字段
    """
    messages = [
        {
            "role": "system",
            "content": (
                "你是数据映射专员。将Excel行数据映射到楼盘客户系统字段。"
                "必须以JSON格式返回，包含以下字段（无法提取的填null）：\n"
                "name: 客户姓名\n"
                "phone: 手机号\n"
                "building_no: 楼栋号\n"
                "unit_no: 单元号\n"
                "room_no: 房号\n"
                "floor: 楼层(整数)\n"
                "house_type: 户型\n"
                "house_area: 面积(数字)\n"
                "decoration_status: 装修状态(not_started/decorating/completed)\n"
                "owner_type: 业主类型(owner/tenant/investor)\n"
                "remark: 备注\n"
                "只输出JSON，不要输出其他内容。"
            )
        },
        {
            "role": "user",
            "content": json.dumps(row_data, ensure_ascii=False)
        }
    ]

    result = call_doubao(messages, temperature=0.1)
    if not result:
        return row_data

    try:
        if result.startswith("```"):
            lines = result.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            result = "\n".join(lines)
        return json.loads(result)
    except json.JSONDecodeError:
        return row_data
