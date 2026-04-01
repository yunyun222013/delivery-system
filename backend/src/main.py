import os
import json
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 环境变量
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
BITABLE_APP_TOKEN = os.getenv("BITABLE_APP_TOKEN", "")
CUSTOMER_TABLE_ID = os.getenv("CUSTOMER_TABLE_ID", "")
DELIVERY_TABLE_ID = os.getenv("DELIVERY_TABLE_ID", "")
HOLIDAY_TABLE_ID = os.getenv("HOLIDAY_TABLE_ID", "")
PAUSE_TABLE_ID = os.getenv("PAUSE_TABLE_ID", "")

# FastAPI应用
app = FastAPI(title="配送管理系统API V2.6", version="2.6.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户管理
USERS_CONFIG = {
    "users": [
        {"username": "admin", "password": "admin123", "role": "管理员"},
        {"username": "user1", "password": "user123", "role": "普通用户"},
        {"username": "user2", "password": "user123", "role": "普通用户"},
        {"username": "user3", "password": "user123", "role": "普通用户"}
    ],
    "session_expire_hours": 24
}
SESSIONS = {}

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
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        logger.error("❌ 飞书配置缺失")
        return None
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            token = result.get("tenant_access_token")
            logger.info(f"✅ 成功获取飞书token")
            return token
        else:
            logger.error(f"❌ 获取飞书token失败: {result}")
            return None
    except Exception as e:
        logger.error(f"❌ 获取飞书token异常: {e}")
        return None

def query_bitable_records(table_id: str, filter_condition: Dict = None):
    """查询多维表格记录"""
    if not BITABLE_APP_TOKEN or not table_id:
        logger.error(f"❌ 配置缺失")
        return []
    
    token = get_feishu_token()
    if not token:
        return []
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {}
    if filter_condition:
        body["filter"] = filter_condition
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        result = response.json()
        
        if result.get("code") == 0:
            items = result.get("data", {}).get("items", [])
            logger.info(f"✅ 查询成功，获取 {len(items)} 条记录")
            return items
        else:
            logger.error(f"❌ 查询失败: {result}")
            return []
    except Exception as e:
        logger.error(f"❌ 查询异常: {e}")
        return []

def update_bitable_record(table_id: str, record_id: str, fields: Dict) -> tuple:
    """更新多维表格记录，返回 (是否成功, 错误信息)"""
    if not BITABLE_APP_TOKEN or not table_id or not record_id:
        return False, "配置缺失"
    
    token = get_feishu_token()
    if not token:
        return False, "无法获取飞书token"
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"fields": fields}
    
    try:
        logger.info(f"正在更新记录 {record_id}: {fields}")
        response = requests.put(url, headers=headers, json=body, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 更新成功")
            return True, None
        else:
            error_msg = result.get('msg', '未知错误')
            error_code = result.get('code', '无错误码')
            logger.error(f"❌ 更新失败: code={error_code}, msg={error_msg}, fields={fields}")
            return False, f"错误码{error_code}: {error_msg}"
    except Exception as e:
        logger.error(f"❌ 更新异常: {e}")
        return False, str(e)

def create_bitable_record(table_id: str, fields: Dict) -> tuple:
    """创建多维表格记录，返回 (是否成功, 错误信息)"""
    if not BITABLE_APP_TOKEN or not table_id:
        return False, "配置缺失"
    
    token = get_feishu_token()
    if not token:
        return False, "无法获取飞书token"
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"fields": fields}
    
    try:
        logger.info(f"正在创建记录: {fields}")
        response = requests.post(url, headers=headers, json=body, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 创建成功")
            return True, None
        else:
            error_msg = result.get('msg', '未知错误')
            error_code = result.get('code', '无错误码')
            logger.error(f"❌ 创建失败: code={error_code}, msg={error_msg}")
            return False, f"错误码{error_code}: {error_msg}"
    except Exception as e:
        logger.error(f"❌ 创建异常: {e}")
        return False, str(e)

def delete_bitable_records(table_id: str, record_ids: List[str]) -> bool:
    """批量删除多维表格记录"""
    if not BITABLE_APP_TOKEN or not table_id or not record_ids:
        return False
    
    token = get_feishu_token()
    if not token:
        return False
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/batch_delete"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"records": record_ids}
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 删除成功")
            return True
        else:
            logger.error(f"❌ 删除失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 删除异常: {e}")
        return False

# 辅助函数：解析日期
def parse_date(date_value) -> Optional[datetime]:
    """解析飞书日期字段"""
    if not date_value:
        return None
    
    try:
        if isinstance(date_value, (int, float)):
            return datetime.fromtimestamp(date_value / 1000)
        elif isinstance(date_value, str):
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                try:
                    return datetime.strptime(date_value, fmt)
                except:
                    continue
        return None
    except Exception as e:
        logger.error(f"日期解析失败: {date_value}, {e}")
        return None

# 辅助函数：获取客户暂停日期列表
def get_customer_pause_dates(customer_name: str) -> List[datetime]:
    """获取指定客户的暂停日期列表"""
    filter_condition = {
        "conditions": [{
            "field_name": "客户姓名",
            "operator": "is",
            "value": [customer_name]
        }]
    }
    
    pause_records = query_bitable_records(PAUSE_TABLE_ID, filter_condition)
    pause_dates = []
    
    for record in pause_records:
        fields = record.get('fields', {})
        
        # 处理暂停单日（暂停单日1、暂停单日2、...）
        i = 1
        while True:
            pause_day = fields.get(f'暂停单日{i}')
            if not pause_day:
                break
            pause_date = parse_date(pause_day)
            if pause_date:
                pause_dates.append(pause_date)
            i += 1
        
        # 处理暂停区间（暂停区间1开始、暂停区间1结束、...）
        j = 1
        while True:
            start_date = fields.get(f'暂停区间{j}开始')
            end_date = fields.get(f'暂停区间{j}结束')
            
            if not start_date or not end_date:
                break
            
            start = parse_date(start_date)
            end = parse_date(end_date)
            
            if start and end:
                current = start
                while current <= end:
                    pause_dates.append(current)
                    current += timedelta(days=1)
            
            j += 1
    
    return pause_dates

# 辅助函数：获取公共假期列表
def get_holiday_dates() -> List[datetime]:
    """获取公共假期列表"""
    holiday_records = query_bitable_records(HOLIDAY_TABLE_ID)
    holiday_dates = []
    
    for record in holiday_records:
        fields = record.get('fields', {})
        holiday_date = parse_date(fields.get('日期'))
        if holiday_date:
            holiday_dates.append(holiday_date)
    
    return holiday_dates

# 辅助函数：获取客户已确认的配送记录累计
def get_customer_confirmed_delivery_count(customer_name: str) -> int:
    """
    获取客户历史已确认配送记录的累计配送数量
    确认状态是单选，可能是"已确认"/"未确认"或其他值
    """
    # 先查询所有该客户的配送记录
    filter_condition = {
        "conditions": [{
            "field_name": "客户姓名",
            "operator": "is",
            "value": [customer_name]
        }]
    }
    
    delivery_records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
    total_count = 0
    
    for record in delivery_records:
        fields = record.get('fields', {})
        confirm_status = fields.get('确认状态', '')
        
        # 判断是否已确认（可能是"已确认"、True、或"是"）
        is_confirmed = (
            confirm_status == "已确认" or 
            confirm_status == True or 
            confirm_status == "是" or
            str(confirm_status).lower() in ["true", "yes", "1"]
        )
        
        if is_confirmed:
            delivery_count = fields.get('配送数量', 1)
            if isinstance(delivery_count, (int, float)):
                total_count += int(delivery_count)
            else:
                total_count += 1
    
    return total_count

# 辅助函数：计算日期范围内的有效配送天数
def calculate_valid_delivery_days(start_date: datetime, end_date: datetime, 
                                  pause_dates: List[datetime], holiday_dates: List[datetime]) -> int:
    """计算从start_date到end_date的有效配送天数"""
    current_date = start_date
    valid_days = 0
    
    while current_date <= end_date:
        is_pause = any(pause.date() == current_date.date() for pause in pause_dates)
        is_holiday = any(holiday.date() == current_date.date() for holiday in holiday_dates)
        
        if not is_pause and not is_holiday:
            valid_days += 1
        
        current_date += timedelta(days=1)
    
    return valid_days

# 辅助函数：计算结束日期
def calculate_end_date_with_history(start_date: datetime, total_meals: int, 
                                   confirmed_count: int, pause_dates: List[datetime], 
                                   holiday_dates: List[datetime]) -> datetime:
    """计算预计结束日期"""
    remaining_meals = total_meals - confirmed_count
    
    if remaining_meals <= 0:
        return datetime.now()
    
    current_date = datetime.now()
    delivered_days = 0
    
    while delivered_days < remaining_meals:
        is_pause = any(pause.date() == current_date.date() for pause in pause_dates)
        is_holiday = any(holiday.date() == current_date.date() for holiday in holiday_dates)
        
        if not is_pause and not is_holiday:
            delivered_days += 1
        
        if delivered_days < remaining_meals:
            current_date += timedelta(days=1)
    
    return current_date

# API接口
@app.get("/")
async def root():
    return {"message": "配送管理系统API V2.6运行中", "version": "2.6.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Service is running"}

@app.get("/api/diagnose")
async def diagnose():
    """诊断接口 - 显示所有字段名和数据样例"""
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "version": "2.6.0",
        "env_config": {
            "FEISHU_APP_ID": "已配置" if FEISHU_APP_ID else "❌ 未配置",
            "FEISHU_APP_SECRET": "已配置" if FEISHU_APP_SECRET else "❌ 未配置",
            "BITABLE_APP_TOKEN": "已配置" if BITABLE_APP_TOKEN else "❌ 未配置",
            "CUSTOMER_TABLE_ID": "已配置" if CUSTOMER_TABLE_ID else "❌ 未配置",
            "DELIVERY_TABLE_ID": "已配置" if DELIVERY_TABLE_ID else "❌ 未配置",
            "HOLIDAY_TABLE_ID": "已配置" if HOLIDAY_TABLE_ID else "❌ 未配置",
            "PAUSE_TABLE_ID": "已配置" if PAUSE_TABLE_ID else "❌ 未配置"
        },
        "tests": {}
    }
    
    token = get_feishu_token()
    diagnosis["tests"]["feishu_token"] = "✅ 成功" if token else "❌ 失败"
    
    if token and CUSTOMER_TABLE_ID:
        try:
            customers = query_bitable_records(CUSTOMER_TABLE_ID)
            diagnosis["tests"]["customer_table"] = f"✅ 成功查询到 {len(customers)} 个客户"
            
            if customers:
                first_customer = customers[0].get('fields', {})
                diagnosis["tests"]["customer_fields"] = list(first_customer.keys())
                diagnosis["tests"]["customer_sample"] = {
                    k: str(v)[:100] for k, v in first_customer.items()
                }
        except Exception as e:
            diagnosis["tests"]["customer_table"] = f"❌ 查询失败: {str(e)}"
    
    if token and DELIVERY_TABLE_ID:
        try:
            deliveries = query_bitable_records(DELIVERY_TABLE_ID)
            diagnosis["tests"]["delivery_table"] = f"✅ 成功查询到 {len(deliveries)} 条配送记录"
            
            if deliveries:
                first_delivery = deliveries[0].get('fields', {})
                diagnosis["tests"]["delivery_fields"] = list(first_delivery.keys())
                diagnosis["tests"]["delivery_sample"] = {
                    k: str(v)[:100] for k, v in first_delivery.items()
                }
        except Exception as e:
            diagnosis["tests"]["delivery_table"] = f"❌ 查询失败: {str(e)}"
    
    if token and HOLIDAY_TABLE_ID:
        try:
            holidays = query_bitable_records(HOLIDAY_TABLE_ID)
            diagnosis["tests"]["holiday_table"] = f"✅ 成功查询到 {len(holidays)} 条假期记录"
            
            if holidays:
                first_holiday = holidays[0].get('fields', {})
                diagnosis["tests"]["holiday_fields"] = list(first_holiday.keys())
        except Exception as e:
            diagnosis["tests"]["holiday_table"] = f"❌ 查询失败: {str(e)}"
    
    if token and PAUSE_TABLE_ID:
        try:
            pauses = query_bitable_records(PAUSE_TABLE_ID)
            diagnosis["tests"]["pause_table"] = f"✅ 成功查询到 {len(pauses)} 条暂停记录"
            
            if pauses:
                first_pause = pauses[0].get('fields', {})
                diagnosis["tests"]["pause_fields"] = list(first_pause.keys())
        except Exception as e:
            diagnosis["tests"]["pause_table"] = f"❌ 查询失败: {str(e)}"
    
    return diagnosis

@app.post("/api/login")
async def login(request: Request):
    """用户登录"""
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {"success": False, "message": "请输入用户名和密码"}
        
        user_info = get_user_info(username)
        if not user_info:
            return {"success": False, "message": "用户名不存在"}
        
        if user_info['password'] != password:
            return {"success": False, "message": "密码错误"}
        
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = {
            'username': username,
            'role': user_info['role'],
            'expire_time': datetime.now() + timedelta(hours=24)
        }
        
        logger.info(f"✅ 用户登录成功: {username}")
        
        return {
            "success": True,
            "token": token,
            "user": {
                "username": username,
                "role": user_info['role']
            }
        }
    except Exception as e:
        logger.error(f"❌ 登录失败: {e}")
        return {"success": False, "message": f"登录失败: {str(e)}"}

@app.post("/api/logout")
async def logout(request: Request):
    """用户登出"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token in SESSIONS:
        del SESSIONS[token]
    return {"success": True, "message": "已退出登录"}

@app.get("/api/verify")
async def verify(request: Request):
    """验证token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    session = verify_token(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="未授权")
    
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
        delivery_count = data.get('delivery_count', 1)
        record_id = data.get('record_id')
        
        logger.info(f"🚀 工作流 {workflow_type} 开始执行 (用户: {session['username']})")
        
        if workflow_type == 'recalculate_eaten':
            return await recalculate_eaten_meals()
        elif workflow_type == 'confirm':
            return await confirm_delivery(delivery_date)
        elif workflow_type == 'recalculate_end_date':
            return await recalculate_end_date()
        elif workflow_type == 'generate':
            return await generate_delivery_records(delivery_date)
        elif workflow_type == 'update_delivery_count':
            return await update_delivery_count(record_id, delivery_count)
        elif workflow_type == 'update_gantt':
            return await update_gantt_status()
        elif workflow_type == 'run_all':
            return await run_all_operations()
        else:
            return {"success": False, "message": f"未知的工作流类型: {workflow_type}"}
    
    except Exception as e:
        logger.error(f"❌ 工作流执行失败: {e}", exc_info=True)
        return {"success": False, "message": f"执行失败: {str(e)}"}

async def recalculate_eaten_meals():
    """重新计算已吃餐数"""
    try:
        logger.info("=" * 60)
        logger.info("开始计算已吃餐数...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {
                "success": False,
                "message": "查询客户数据失败"
            }
        
        holiday_dates = get_holiday_dates()
        debug_info = []
        updated_count = 0
        error_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = fields.get('客户姓名', '未知')
            
            try:
                total_meals = fields.get('总餐数', 0)
                start_date = parse_date(fields.get('起送日期'))
                
                if not start_date:
                    debug_info.append(f"❌ {customer_name}: 起送日期未填写")
                    error_count += 1
                    continue
                
                pause_dates = get_customer_pause_dates(customer_name)
                
                # 基础天数（起送日期到昨天）
                yesterday = datetime.now() - timedelta(days=1)
                base_days = calculate_valid_delivery_days(start_date, yesterday, pause_dates, holiday_dates)
                
                # 历史已确认配送数量
                history_confirmed = get_customer_confirmed_delivery_count(customer_name)
                
                # 总已吃餐数
                total_eaten = base_days + history_confirmed
                
                if total_eaten > total_meals:
                    total_eaten = total_meals
                
                # 更新记录
                update_success, error_msg = update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"已吃餐数": total_eaten})
                
                if update_success:
                    debug_info.append(f"✅ {customer_name}: 基础{base_days}天 + 历史{history_confirmed}餐 = 已吃{total_eaten}餐")
                    updated_count += 1
                else:
                    debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
                    error_count += 1
                    
            except Exception as e:
                debug_info.append(f"❌ {customer_name}: 处理失败 - {str(e)}")
                error_count += 1
        
        logger.info(f"✅ 完成：成功 {updated_count} 个，失败 {error_count} 个")
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的已吃餐数（失败 {error_count} 个）",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        logger.error(f"❌ 计算失败: {e}", exc_info=True)
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def recalculate_end_date():
    """重新计算预计结束日期"""
    try:
        logger.info("=" * 60)
        logger.info("开始重新计算预计结束日期...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "查询客户数据失败"}
        
        holiday_dates = get_holiday_dates()
        debug_info = []
        updated_count = 0
        error_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = fields.get('客户姓名', '未知')
            
            try:
                total_meals = fields.get('总餐数', 0)
                start_date = parse_date(fields.get('起送日期'))
                
                if not start_date:
                    debug_info.append(f"❌ {customer_name}: 起送日期未填写")
                    error_count += 1
                    continue
                
                if total_meals <= 0:
                    debug_info.append(f"❌ {customer_name}: 总餐数无效")
                    error_count += 1
                    continue
                
                pause_dates = get_customer_pause_dates(customer_name)
                confirmed_count = get_customer_confirmed_delivery_count(customer_name)
                
                end_date = calculate_end_date_with_history(
                    start_date, total_meals, confirmed_count, pause_dates, holiday_dates
                )
                
                update_success, error_msg = update_bitable_record(
                    CUSTOMER_TABLE_ID, record_id, 
                    {"预计结束日期": end_date.strftime("%Y-%m-%d")}
                )
                
                if update_success:
                    remaining = total_meals - confirmed_count
                    debug_info.append(
                        f"✅ {customer_name}: 总{total_meals}餐 - 已确认{confirmed_count}餐 = 剩余{remaining}餐 → 结束{end_date.strftime('%Y-%m-%d')}"
                    )
                    updated_count += 1
                else:
                    debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
                    error_count += 1
                    
            except Exception as e:
                debug_info.append(f"❌ {customer_name}: 处理失败 - {str(e)}")
                error_count += 1
        
        logger.info(f"✅ 完成：成功 {updated_count} 个，失败 {error_count} 个")
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的预计结束日期",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def update_delivery_count(record_id: str, delivery_count: int):
    """修改配送数量"""
    try:
        if not record_id:
            return {"success": False, "message": "缺少配送记录ID"}
        
        delivery_records = query_bitable_records(DELIVERY_TABLE_ID)
        target_record = None
        
        for record in delivery_records:
            if record.get('record_id') == record_id:
                target_record = record
                break
        
        if not target_record:
            return {"success": False, "message": "配送记录不存在"}
        
        fields = target_record.get('fields', {})
        is_confirmed = fields.get('确认状态', '')
        
        if is_confirmed == "已确认":
            return {
                "success": False,
                "message": "该配送记录已确认，无法修改配送数量"
            }
        
        update_success, error_msg = update_bitable_record(DELIVERY_TABLE_ID, record_id, {"配送数量": delivery_count})
        
        if update_success:
            return {
                "success": True,
                "message": f"配送数量已更新为 {delivery_count}"
            }
        else:
            return {"success": False, "message": f"更新失败: {error_msg}"}
            
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def confirm_delivery(delivery_date: str):
    """批量确认配送记录"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始确认配送日期: {delivery_date}")
        
        filter_condition = {
            "conditions": [{
                "field_name": "配送日期",
                "operator": "is",
                "value": [delivery_date]
            }]
        }
        records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
        
        if not records:
            return {
                "success": False,
                "message": f"{delivery_date} 没有配送记录",
                "data": {
                    "debug_info": [f"⚠️ 未找到 {delivery_date} 的配送记录"],
                    "tips": ["请先使用'生成配送记录'功能生成该日期的记录"]
                }
            }
        
        debug_info = []
        confirmed_count = 0
        skipped_count = 0
        
        for record in records:
            fields = record.get('fields', {})
            record_id = record.get('record_id')
            customer_name = fields.get('客户姓名', '未知')
            is_confirmed = fields.get('确认状态', '')
            delivery_qty = fields.get('配送数量', 1)
            
            if is_confirmed == "已确认":
                debug_info.append(f"⏭️ {customer_name}: 已确认过（配送{delivery_qty}份），跳过")
                skipped_count += 1
                continue
            
            # 更新确认状态
            update_success, error_msg = update_bitable_record(DELIVERY_TABLE_ID, record_id, {"确认状态": "已确认"})
            
            if update_success:
                customer_records = query_bitable_records(CUSTOMER_TABLE_ID, {
                    "conditions": [{
                        "field_name": "客户姓名",
                        "operator": "is",
                        "value": [customer_name]
                    }]
                })
                
                if customer_records:
                    customer_record = customer_records[0]
                    customer_fields = customer_record.get('fields', {})
                    customer_record_id = customer_record.get('record_id')
                    current_eaten = customer_fields.get('已吃餐数', 0)
                    
                    update_bitable_record(
                        CUSTOMER_TABLE_ID,
                        customer_record_id,
                        {"已吃餐数": current_eaten + delivery_qty}
                    )
                    
                    debug_info.append(
                        f"✅ {customer_name}: 确认配送 {delivery_qty} 份，已吃餐数 {current_eaten} → {current_eaten + delivery_qty}"
                    )
                    confirmed_count += 1
                else:
                    debug_info.append(f"⚠️ {customer_name}: 确认成功但找不到客户记录")
                    confirmed_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 确认失败 - {error_msg}")
        
        logger.info(f"✅ 完成：确认 {confirmed_count} 个，跳过 {skipped_count} 个")
        
        return {
            "success": True,
            "message": f"已确认 {delivery_date} 的 {confirmed_count} 条配送记录",
            "data": {
                "debug_info": debug_info,
                "confirmed_count": confirmed_count,
                "skipped_count": skipped_count
            }
        }
    except Exception as e:
        return {"success": False, "message": f"确认失败: {str(e)}"}

async def generate_delivery_records(delivery_date: str):
    """生成配送记录"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始生成配送记录: {delivery_date}")
        
        # 删除该日期的旧记录
        filter_condition = {
            "conditions": [{
                "field_name": "配送日期",
                "operator": "is",
                "value": [delivery_date]
            }]
        }
        old_records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
        
        if old_records:
            old_record_ids = [r.get('record_id') for r in old_records]
            delete_bitable_records(DELIVERY_TABLE_ID, old_record_ids)
            logger.info(f"已删除 {len(old_records)} 条旧记录")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        if not customers:
            return {"success": False, "message": "客户表为空，无法生成配送记录"}
        
        holiday_dates = get_holiday_dates()
        selected_date = datetime.strptime(delivery_date, "%Y-%m-%d")
        tomorrow = selected_date + timedelta(days=1)
        
        debug_info = []
        created_count = 0
        skipped_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            customer_name = fields.get('客户姓名')
            start_date = parse_date(fields.get('起送日期'))
            end_date = parse_date(fields.get('预计结束日期'))
            total_meals = fields.get('总餐数', 0)
            eaten_meals = fields.get('已吃餐数', 0)
            
            # 从客户表读取其他字段
            phone = fields.get('手机号', '')
            address = fields.get('配送地址', '')
            taboo = fields.get('忌口', '')
            extra = fields.get('加量', '')
            remark = fields.get('备注', '')
            
            if not customer_name:
                continue
            
            should_deliver = True
            skip_reason = ""
            
            if start_date and selected_date.date() < start_date.date():
                skip_reason = "未到起送日期"
                should_deliver = False
            
            if end_date and selected_date.date() > end_date.date():
                skip_reason = "已过结束日期"
                should_deliver = False
            
            if eaten_meals >= total_meals:
                skip_reason = "已吃完所有餐数"
                should_deliver = False
            
            if should_deliver:
                is_holiday = any(h.date() == selected_date.date() for h in holiday_dates)
                pause_dates = get_customer_pause_dates(customer_name)
                is_pause = any(p.date() == selected_date.date() for p in pause_dates)
                
                if is_holiday:
                    skip_reason = "该日期是假期"
                    skipped_count += 1
                elif is_pause:
                    skip_reason = "该日期是暂停日"
                    skipped_count += 1
                else:
                    # 判断明天是否是最后一天
                    is_last_day = False
                    if end_date and tomorrow.date() > end_date.date():
                        is_last_day = True
                    
                    # 创建配送记录（复选框字段需要布尔值）
                    delivery_fields = {
                        "配送日期": delivery_date,
                        "客户姓名": customer_name,
                        "手机号": phone,
                        "配送地址": address,
                        "忌口": taboo,
                        "加量": extra,
                        "备注": remark,
                        "配送数量": 1,
                        "明天是否是最后一天": is_last_day,  # 布尔值
                        "确认状态": "未确认"
                    }
                    
                    success, error_msg = create_bitable_record(DELIVERY_TABLE_ID, delivery_fields)
                    
                    if success:
                        debug_info.append(f"✅ {customer_name}: 生成配送记录（默认1份）")
                        created_count += 1
                    else:
                        debug_info.append(f"❌ {customer_name}: 创建失败 - {error_msg}")
                        skipped_count += 1
            else:
                debug_info.append(f"⏭️ {customer_name}: {skip_reason}")
                skipped_count += 1
        
        logger.info(f"✅ 完成：生成 {created_count} 条，跳过 {skipped_count} 条")
        
        return {
            "success": True,
            "message": f"已生成 {delivery_date} 的 {created_count} 条配送记录",
            "data": {
                "debug_info": debug_info,
                "created_count": created_count,
                "skipped_count": skipped_count,
                "tips": [
                    "📋 配送记录已生成，默认配送数量为1",
                    "✏️ 如需修改配送数量，请直接在飞书表格中修改",
                    "✅ 修改完成后，点击'批量确认'锁定配送数量"
                ]
            }
        }
    except Exception as e:
        logger.error(f"❌ 生成失败: {e}", exc_info=True)
        return {"success": False, "message": f"生成失败: {str(e)}"}

async def update_gantt_status():
    """更新甘特图状态"""
    try:
        logger.info("=" * 60)
        logger.info("开始更新甘特图状态...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "客户表为空"}
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = fields.get('客户姓名')
            start_date = parse_date(fields.get('起送日期'))
            end_date = parse_date(fields.get('预计结束日期'))
            
            if not customer_name or not start_date:
                continue
            
            pause_dates = get_customer_pause_dates(customer_name)
            holiday_dates = get_holiday_dates()
            
            gantt_data = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",
                "pause_dates": [p.strftime("%Y-%m-%d") for p in pause_dates],
                "holiday_dates": [h.strftime("%Y-%m-%d") for h in holiday_dates],
                "daily_details": []
            }
            
            if end_date:
                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    filter_condition = {
                        "conditions": [{
                            "field_name": "配送日期",
                            "operator": "is",
                            "value": [date_str]
                        }]
                    }
                    delivery_records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
                    
                    delivery_info = {
                        "date": date_str,
                        "is_pause": any(p.date() == current_date.date() for p in pause_dates),
                        "is_holiday": any(h.date() == current_date.date() for h in holiday_dates),
                        "delivery_count": 0,
                        "is_confirmed": False
                    }
                    
                    for record in delivery_records:
                        r_fields = record.get('fields', {})
                        if r_fields.get('客户姓名') == customer_name:
                            delivery_info["delivery_count"] = r_fields.get('配送数量', 0)
                            delivery_info["is_confirmed"] = r_fields.get('确认状态', '') == "已确认"
                            break
                    
                    gantt_data["daily_details"].append(delivery_info)
                    current_date += timedelta(days=1)
            
            update_success, error_msg = update_bitable_record(
                CUSTOMER_TABLE_ID, record_id,
                {"甘特图数据": json.dumps(gantt_data, ensure_ascii=False)}
            )
            
            if update_success:
                debug_info.append(f"✅ {customer_name}: 甘特图数据已更新")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已更新 {updated_count} 个客户的甘特图数据",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def run_all_operations():
    """一键执行所有操作"""
    try:
        results = []
        
        result1 = await recalculate_eaten_meals()
        results.append(f"1️⃣ 计算已吃餐数: {result1['message']}")
        
        result2 = await recalculate_end_date()
        results.append(f"2️⃣ 计算结束日期: {result2['message']}")
        
        result3 = await update_gantt_status()
        results.append(f"3️⃣ 更新甘特图: {result3['message']}")
        
        return {
            "success": True,
            "message": "所有操作已完成",
            "data": {
                "debug_info": results,
                "tips": ["建议每周一早上运行一次，全面更新所有数据"]
            }
        }
    except Exception as e:
        return {"success": False, "message": f"执行失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
