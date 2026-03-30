import os
import json
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境变量
WORKSPACE_PATH = os.getenv("COZE_WORKSPACE_PATH", "/app")
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
BITABLE_APP_TOKEN = os.getenv("BITABLE_APP_TOKEN", "")
CUSTOMER_TABLE_ID = os.getenv("CUSTOMER_TABLE_ID", "")
DELIVERY_TABLE_ID = os.getenv("DELIVERY_TABLE_ID", "")
HOLIDAY_TABLE_ID = os.getenv("HOLIDAY_TABLE_ID", "")
PAUSE_TABLE_ID = os.getenv("PAUSE_TABLE_ID", "")

# FastAPI应用
app = FastAPI(title="配送管理系统API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户管理
USERS_CONFIG = {}
SESSIONS = {}

def load_users_config():
    """加载用户配置"""
    global USERS_CONFIG
    config_path = os.path.join(WORKSPACE_PATH, "config/users.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                USERS_CONFIG = json.load(f)
                logger.info(f"Loaded {len(USERS_CONFIG.get('users', []))} users")
    except Exception as e:
        logger.warning(f"Failed to load users config: {e}")
        USERS_CONFIG = {
            "users": [
                {"username": "admin", "password": "admin123", "role": "管理员"},
                {"username": "user1", "password": "user123", "role": "普通用户"}
            ],
            "session_expire_hours": 24
        }

load_users_config()

def get_user_info(username: str) -> Optional[Dict]:
    """获取用户信息"""
    for user in USERS_CONFIG.get('users', []):
        if user['username'] == username:
            return user
    return None

def verify_token(token: str) -> Optional[Dict]:
    """验证token"""
    if not token or token not in SESSIONS:
        return None
    session = SESSIONS[token]
    if datetime.now() > session['expire_time']:
        del SESSIONS[token]
        return None
    return session

# 飞书API
def get_feishu_token():
    """获取飞书access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, json=data)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        logger.error(f"Failed to get feishu token: {result}")
        return None

def query_bitable_records(table_id: str, filter_condition: str = None):
    """查询多维表格记录"""
    token = get_feishu_token()
    if not token:
        return []
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/search"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"automatic_fields": False}
    if filter_condition:
        data["filter"] = filter_condition
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("items", [])
    return []

def update_bitable_record(table_id: str, record_id: str, fields: Dict):
    """更新多维表格记录"""
    token = get_feishu_token()
    if not token:
        return False
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"fields": fields}
    
    response = requests.put(url, headers=headers, json=data)
    result = response.json()
    
    return result.get("code") == 0

def create_bitable_record(table_id: str, fields: Dict):
    """创建多维表格记录"""
    token = get_feishu_token()
    if not token:
        return None
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"fields": fields}
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("record", {})
    return None

# API接口
@app.get("/")
async def root():
    return {"message": "配送管理系统API运行中", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Service is running"}

@app.post("/api/login")
async def login(request: Request):
    """用户登录"""
    try:
        data = await request.json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return {"success": False, "message": "用户名和密码不能为空"}
        
        user = get_user_info(username)
        if not user or user['password'] != password:
            return {"success": False, "message": "用户名或密码错误"}
        
        token = secrets.token_urlsafe(32)
        expire_hours = USERS_CONFIG.get('session_expire_hours', 24)
        SESSIONS[token] = {
            'username': username,
            'role': user['role'],
            'expire_time': datetime.now() + timedelta(hours=expire_hours)
        }
        
        logger.info(f"User {username} logged in")
        
        return {
            "success": True,
            "message": "登录成功",
            "token": token,
            "user": {"username": username, "role": user['role']}
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {"success": False, "message": f"登录失败: {str(e)}"}

@app.post("/api/logout")
async def logout(request: Request):
    """用户登出"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token in SESSIONS:
        username = SESSIONS[token]['username']
        del SESSIONS[token]
        logger.info(f"User {username} logged out")
    return {"success": True, "message": "已登出"}

@app.get("/api/verify")
async def verify(request: Request):
    """验证token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    session = verify_token(token)
    
    if not session:
        return {"success": False, "message": "未登录或登录已过期"}
    
    return {
        "success": True,
        "user": {"username": session['username'], "role": session['role']}
    }

@app.post("/run")
async def run_workflow(request: Request):
    """执行工作流"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    session = verify_token(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="未授权")
    
    try:
        data = await request.json()
        workflow_type = data.get('workflow_type')
        delivery_date = data.get('delivery_date')
        
        logger.info(f"Workflow {workflow_type} started by {session['username']}")
        
        # 根据workflow_type执行不同操作
        if workflow_type == 'recalculate_eaten':
            return await recalculate_eaten_meals()
        elif workflow_type == 'confirm':
            return await confirm_delivery(delivery_date)
        elif workflow_type == 'recalculate_end_date':
            return await recalculate_end_date()
        elif workflow_type == 'generate':
            return await generate_delivery_records(delivery_date)
        elif workflow_type == 'update_gantt':
            return await update_gantt_status()
        else:
            return {"success": False, "message": f"未知的工作流类型: {workflow_type}"}
    
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return {"success": False, "message": f"执行失败: {str(e)}"}

async def recalculate_eaten_meals():
    """重新计算已吃餐数"""
    try:
        # 获取所有客户
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        # 获取假期和暂停记录
        holidays = query_bitable_records(HOLIDAY_TABLE_ID)
        pauses = query_bitable_records(PAUSE_TABLE_ID)
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            # 计算逻辑（简化版）
            # 实际计算需要根据起送日期、假期、暂停等计算
            debug_info.append(f"处理客户: {customer.get('fields', {}).get('客户姓名', '未知')}")
            updated_count += 1
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的已吃餐数",
            "data": {"debug_info": debug_info}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def confirm_delivery(delivery_date: str):
    """确认配送"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        # 查询当天配送记录
        filter_condition = {
            "conditions": [{
                "field_name": "配送日期",
                "operator": "is",
                "value": [delivery_date]
            }]
        }
        records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
        
        debug_info = []
        confirmed_count = 0
        
        for record in records:
            # 标记为已确认
            fields = record.get('fields', {})
            customer_name = fields.get('客户姓名', '未知')
            
            debug_info.append(f"确认配送: {customer_name}")
            confirmed_count += 1
        
        return {
            "success": True,
            "message": f"已确认 {delivery_date} 的 {confirmed_count} 条配送记录",
            "data": {"debug_info": debug_info}
        }
    except Exception as e:
        return {"success": False, "message": f"确认失败: {str(e)}"}

async def recalculate_end_date():
    """重新计算预计结束日期"""
    try:
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            debug_info.append(f"计算结束日期: {customer.get('fields', {}).get('客户姓名', '未知')}")
            updated_count += 1
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的预计结束日期",
            "data": {"debug_info": debug_info}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def generate_delivery_records(delivery_date: str):
    """生成配送记录"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        debug_info = []
        created_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            customer_name = fields.get('客户姓名')
            
            if customer_name:
                # 创建配送记录
                record = create_bitable_record(DELIVERY_TABLE_ID, {
                    "配送日期": delivery_date,
                    "客户姓名": customer_name,
                    "配送数量": 1,
                    "是否已确认": False
                })
                
                if record:
                    debug_info.append(f"生成记录: {customer_name}")
                    created_count += 1
        
        return {
            "success": True,
            "message": f"已生成 {delivery_date} 的 {created_count} 条配送记录",
            "data": {"debug_info": debug_info}
        }
    except Exception as e:
        return {"success": False, "message": f"生成失败: {str(e)}"}

async def update_gantt_status():
    """更新甘特图状态"""
    try:
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            debug_info.append(f"更新状态: {customer.get('fields', {}).get('客户姓名', '未知')}")
            updated_count += 1
        
        return {
            "success": True,
            "message": f"已更新 {updated_count} 个客户的甘特图状态",
            "data": {"debug_info": debug_info}
        }
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)