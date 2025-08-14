#!/usr/bin/env python3
"""
MCP服务器，提供schema和SQL查询工具
基于原始的FastAPI服务封装为MCP协议
"""

import json
import requests
import asyncio
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import chardet
import re
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from pydantic import BaseModel, Field

# 加载环境变量
load_dotenv()


# 配置信息
DEFAULT_USER_SCHEMA = "jackylzhou"

DEFAULT_BUSINESS_ID_SCHEMA = "102580"

DEFAULT_USER_SQL = "jackylzhou"
DEFAULT_BUSINESS_ID_SQL = "102403"


# API URLs - 从环境变量获取
QUERY_API_URL = os.getenv("QUERY_API_URL", "")




# Token配置 - 从环境变量获取
SCHEMA_TOKEN = os.getenv("SCHEMA_TOKEN")
SQL_TOKEN = os.getenv("SQL_TOKEN")

# 创建MCP服务器实例 - 使用无状态HTTP模式，配置端口和主机
mcp = FastMCP(
    "Schema and SQL Query Server"
)


def sanitize_string(text: str) -> str:
    """清理字符串中的无效Unicode代理对并处理编码问题"""
    if not text:
        return text
    
    # 尝试检测编码
    try:
        detected = chardet.detect(text.encode('latin1'))
        if detected['encoding'] == 'GB2312' or detected['encoding'] == 'GBK':
            text = text.encode('latin1').decode('gbk')
    except:
        pass
    
    # 替换无效Unicode代理对
    return re.sub(r'[\ud800-\udfff]', '', text)




async def make_api_request(url: str, headers: dict, payload: dict) -> dict:
    """发送HTTP请求的异步函数"""
    try:
        # 使用同步requests，在实际生产环境中建议使用httpx等异步库
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"请求失败: {str(e)}")


@mcp.tool()
async def get_sql_schema(
    query: str, 
    document_id: Optional[str] = None,
    extra_result_params: Optional[List[str]] = None
) -> dict:
    """
    获取SQL数据口径信息。根据用户需求，分析需要用到的数据表、字段、枚举值、关联方式和易错点等信息

    Args:
        query: 用户需要提取的数据需求，比如'查询理财通2025年6月1日的保有量'或'统计理财通2025年6月1日的股混申购金额'
    
    Returns:
        dict:   包含schema分析结果的JSON对象
    """
    # 记录请求日志
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_query = sanitize_string(query)
    
    print(json.dumps({
        "timestamp": current_time,
        "tool": "get_sql_schema",
        "query": safe_query
    }, ensure_ascii=False))
    
    if not SCHEMA_TOKEN:
        return {
            "success": False,
            "data": "SCHEMA_TOKEN环境变量未设置"
        }
    
    headers = {
        "Authorization": f"Bearer {SCHEMA_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "data": {
            "user": DEFAULT_USER_SCHEMA,
            "useSession": True,
            "businessId": DEFAULT_BUSINESS_ID_SCHEMA,
            "query": query,
            "extra": {"documentId": document_id or "588"},
            "extraResultParams": extra_result_params or []
        }
    }

    try:
        result = await make_api_request(QUERY_API_URL, headers, payload)
        
        if "error" in result:
            return {
            "success": False,
            "data": answer
        }
        
        # 提取答案，移除<answer>标签
        answer = result['data']['answer'].split("<answer>")[0]
        
        return {
            "success": True,
            "data": answer
        }
        
    except Exception as e:
        return {
            "success": True,
            "data": answer
        }

@mcp.tool()
async def execute_sql_query(
    query: str,
    document_id: Optional[str] = None,
    extra_result_params: Optional[List[str]] = None
) -> dict:
    """
    可执行理财通相关的SQL代码，获取数据结果

    Args:
        query: 要执行的SQL代码，比如'select * from user_table where date = '2025-06-01' limit 10'
    
    Returns:
        dict: 包含查询结果的JSON对象
    """
    # 记录请求日志
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(json.dumps({
        "timestamp": current_time,
        "tool": "execute_sql_query",
        "sql_length": len(query)
    }, ensure_ascii=False))
    
    if not SQL_TOKEN:
        return {
            "success": False,
            "data": "SQL_TOKEN环境变量未设置"
        }
    
    headers = {
        "Authorization": f"Bearer {SQL_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "data": {
            "user": DEFAULT_USER_SQL,
            "useSession": True,
            "businessId": DEFAULT_BUSINESS_ID_SQL,
            "query": query,
            "extra": {"documentId": document_id or "588"},
            "extraResultParams": extra_result_params or []
        }
    }

    try:
        result = await make_api_request(QUERY_API_URL, headers, payload)
        
        # 记录查询日志
        log_entry = {
            "query": query,
            "answer": result['data']['answer'],
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        # 写入日志文件
        try:
            with open("sql_query_log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as log_error:
            print(f"日志写入失败: {log_error}")
        
        # 检查是否有错误信息
        if "error" in result or "message" in str(result):
            return {
            "success": False,
            "data": result['data']['answer']
        }
        
        return {
            "success": True,
            "data": result['data']['answer']
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": e
        }


@mcp.tool()
async def check_server_status() -> Dict[str, Any]:
    """
    检查目标服务器的状态
    
    Returns:
        Dict[str, Any]: 服务器状态信息
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(json.dumps({
        "timestamp": current_time,
        "tool": "check_server_status"
    }, ensure_ascii=False))
    
    try:
        # 测试API端点连接
        import socket
        host = "11.168.42.59"
        port = 13699
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            status = "healthy"
            message = "API服务器连接正常"
        else:
            status = "unhealthy"
            message = f"无法连接到API服务器 {host}:{port}"
        
        return {
            "status": status,
            "message": message,
            "timestamp": current_time,
            "api_endpoint": QUERY_API_URL,
            "mcp_server": "running"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"状态检查失败: {str(e)}",
            "timestamp": current_time,
            "api_endpoint": QUERY_API_URL,
            "mcp_server": "running"
        }


@mcp.tool()
async def get_current_time() -> Dict[str, str]:
    """
    获取当前系统时间，返回yyyyMMdd HH:mm:SS格式，对于用户涉及"今天"，"昨天"，"近xx天"、"上个月"等模糊时间描述时，建议先调用本工具获取当前时间，再由AI推算出具体的日期范围后用于SQL查询
    
    Returns:
        Dict[str, str]: 包含当前时间的多种格式
    """
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    print(json.dumps({
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "tool": "get_current_time"
    }, ensure_ascii=False))
    
    # 计算常用的时间点
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)
    last_month = now.replace(month=now.month-1 if now.month > 1 else 12, 
                           year=now.year if now.month > 1 else now.year-1)
    
    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S")
    }


@mcp.resource("health://status")
def get_health_status() -> str:
    """获取服务健康状态"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps({
        "status": "healthy",
        "service": "schema-sql-mcp-service",
        "timestamp": current_time,
        "endpoints": {
            "get_sql_schema": "获取SQL数据口径信息",
            "execute_sql_query": "执行理财通SQL查询",
            "check_server_status": "检查服务器状态",
            "get_current_time": "获取当前系统时间"
        }
    }, ensure_ascii=False, indent=2)


@mcp.resource("config://settings")
def get_configuration() -> str:
    """获取服务配置信息"""
    config = {
        "service_name": "Schema and SQL Query MCP Server",
        "version": "1.0.0",
        "api_url": QUERY_API_URL,
        "default_users": {
            "schema": DEFAULT_USER_SCHEMA,
            "sql": DEFAULT_USER_SQL
        },
        "business_ids": {
            "schema": DEFAULT_BUSINESS_ID_SCHEMA,
            "sql": DEFAULT_BUSINESS_ID_SQL
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


@mcp.prompt()
def schema_analysis_prompt(data_requirement: str) -> str:
    """生成schema分析提示"""
    return f"""请帮我分析以下数据需求对应的schema信息：

数据需求：{data_requirement}

请使用get_sql_schema工具来获取相关的数据库表结构、字段信息、枚举值、关联方式和易错点等信息。你需要提供：
1. query参数：描述你的数据需求（比如'查询理财通2025年6月1日的保有量'） 

例如：
get_sql_schema(query="{data_requirement}")
"""


@mcp.prompt()
def sql_execution_prompt(sql_query: str) -> str:
    """生成SQL执行提示"""
    return f"""请执行以下理财通相关的SQL查询：

SQL代码：
```sql
{sql_query}
```

请使用execute_sql_query工具来执行这个SQL查询。你需要提供：
1. query参数：要执行的SQL代码

例如：
execute_sql_query(query="{sql_query}")

注意：如果涉及模糊时间描述（如"今天"、"昨天"、"近7天"等），建议先使用get_current_time工具获取当前时间，再计算具体的日期范围。
"""


def main():
    """运行MCP服务器"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
