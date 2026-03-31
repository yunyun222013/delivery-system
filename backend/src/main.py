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
app = FastAPI(title="配送管理系统API V2.1", version="2.1.0")

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
        logger.error("❌ 配置缺失")
        return []
    
    token = get_feishu_token()
    if not token:
        return []
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/search"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"automatic_fields": False}
    if filter_condition:
        data["filter"] = filter_condition
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            items = result.get("data", {}).get("items", [])
            logger.info(f"✅ 查询成功，返回 {len(items)} 条记录")
            return items
        else:
            logger.error(f"❌ 查询失败: {result}")
            return []
    except Exception as e:
        logger.error(f"❌ 查询异常: {e}")
        return []

def update_bitable_record(table_id: str, record_id: str, fields: Dict):
    """更新多维表格记录"""
    token = get_feishu_token()
    if not token:
        return False
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"fields": fields}
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 更新记录成功")
            return True
        else:
            logger.error(f"❌ 更新记录失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 更新记录异常: {e}")
        return False

def create_bitable_record(table_id: str, fields: Dict):
    """创建多维表格记录"""
    token = get_feishu_token()
    if not token:
        return None
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"fields": fields}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            record = result.get("data", {}).get("record", {})
            logger.info(f"✅ 创建记录成功")
            return record
        else:
            logger.error(f"❌ 创建记录失败: {result}")
            return None
    except Exception as e:
        logger.error(f"❌ 创建记录异常: {e}")
        return None

def delete_bitable_records(table_id: str, record_ids: List[str]):
    """批量删除多维表格记录"""
    if not record_ids:
        return True
    
    token = get_feishu_token()
    if not token:
        return False
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/batch_delete"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"records": record_ids}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 删除 {len(record_ids)} 条记录成功")
            return True
        else:
            logger.error(f"❌ 删除记录失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 删除记录异常: {e}")
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
    pause_records = query_bitable_records(PAUSE_TABLE_ID)
    pause_dates = []
    
    for record in pause_records:
        fields = record.get('fields', {})
        if fields.get('客户姓名') == customer_name:
            pause_date = parse_date(fields.get('暂停日期'))
            if pause_date:
                pause_dates.append(pause_date)
    
    return pause_dates

# 辅助函数：获取公共假期列表
def get_holiday_dates() -> List[datetime]:
    """获取公共假期列表"""
    holiday_records = query_bitable_records(HOLIDAY_TABLE_ID)
    holiday_dates = []
    
    for record in holiday_records:
        fields = record.get('fields', {})
        holiday_date = parse_date(fields.get('假期日期'))
        if holiday_date:
            holiday_dates.append(holiday_date)
    
    return holiday_dates

# 辅助函数：获取客户已确认的配送记录累计
def get_customer_confirmed_delivery_count(customer_name: str) -> int:
    """获取客户历史已确认配送记录的累计配送数量"""
    filter_condition = {
        "conjunction": "and",
        "conditions": [
            {
                "field_name": "客户姓名",
                "operator": "is",
                "value": [customer_name]
            },
            {
                "field_name": "是否已确认",
                "operator": "is",
                "value": [True]
            }
        ]
    }
    
    delivery_records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
    total_count = 0
    
    for record in delivery_records:
        fields = record.get('fields', {})
        delivery_count = fields.get('配送数量', 1)
        total_count += delivery_count
    
    return total_count

# 辅助函数：计算日期范围内的有效配送天数
def calculate_valid_delivery_days(start_date: datetime, end_date: datetime, 
                                  pause_dates: List[datetime], holiday_dates: List[datetime]) -> int:
    """计算从start_date到end_date的有效配送天数（排除暂停和假期）"""
    current_date = start_date
    valid_days = 0
    
    while current_date <= end_date:
        is_pause = any(pause.date() == current_date.date() for pause in pause_dates)
        is_holiday = any(holiday.date() == current_date.date() for holiday in holiday_dates)
        
        if not is_pause and not is_holiday:
            valid_days += 1
        
        current_date += timedelta(days=1)
    
    return valid_days

# 辅助函数：计算结束日期（修正版）
def calculate_end_date_with_history(start_date: datetime, total_meals: int, 
                                   confirmed_count: int, pause_dates: List[datetime], 
                                   holiday_dates: List[datetime]) -> datetime:
    """
    计算预计结束日期（考虑历史已确认配送数量）
    
    逻辑：
    1. 剩余餐数 = 总餐数 - 历史已确认配送数量
    2. 从今天开始，逐日累加，跳过暂停和假期，直到达到剩余餐数
    """
    # 剩余需要配送的餐数
    remaining_meals = total_meals - confirmed_count
    
    if remaining_meals <= 0:
        # 如果已经吃完或超出，返回今天
        return datetime.now()
    
    # 从今天开始计算
    current_date = datetime.now()
    delivered_days = 0
    
    while delivered_days < remaining_meals:
        # 检查是否是暂停日
        is_pause = any(pause.date() == current_date.date() for pause in pause_dates)
        # 检查是否是假期
        is_holiday = any(holiday.date() == current_date.date() for holiday in holiday_dates)
        
        if not is_pause and not is_holiday:
            delivered_days += 1
        
        if delivered_days < remaining_meals:
            current_date += timedelta(days=1)
    
    return current_date

# API接口
@app.get("/")
async def root():
    return {"message": "配送管理系统API V2.1运行中", "version": "2.1.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Service is running"}

@app.get("/api/diagnose")
async def diagnose():
    """诊断接口"""
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "env_config": {
            "FEISHU_APP_ID": "已配置" if FEISHU_APP_ID else "❌ 未配置",
            "FEISHU_APP_SECRET": "已配置" if FEISHU_APP_SECRET else "❌ 未配置",
            "BITABLE_APP_TOKEN": BITABLE_APP_TOKEN if BITABLE_APP_TOKEN else "❌ 未配置",
            "CUSTOMER_TABLE_ID": CUSTOMER_TABLE_ID if CUSTOMER_TABLE_ID else "❌ 未配置",
            "DELIVERY_TABLE_ID": DELIVERY_TABLE_ID if DELIVERY_TABLE_ID else "❌ 未配置",
            "HOLIDAY_TABLE_ID": HOLIDAY_TABLE_ID if HOLIDAY_TABLE_ID else "❌ 未配置",
            "PAUSE_TABLE_ID": PAUSE_TABLE_ID if PAUSE_TABLE_ID else "❌ 未配置"
        }
    }
    
    token = get_feishu_token()
    diagnosis["feishu_connection"] = {
        "status": "✅ 成功" if token else "❌ 失败",
        "token_obtained": bool(token)
    }
    
    return diagnosis

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
        
        return {
            "success": True,
            "message": "登录成功",
            "token": token,
            "user": {"username": username, "role": user['role']}
        }
    except Exception as e:
        return {"success": False, "message": f"登录失败: {str(e)}"}

@app.post("/api/logout")
async def logout(request: Request):
    """用户登出"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token in SESSIONS:
        del SESSIONS[token]
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
        delivery_count = data.get('delivery_count', 1)  # 配送数量，默认为1
        record_id = data.get('record_id')  # 配送记录ID
        
        logger.info(f"🚀 工作流 {workflow_type} 开始执行")
        
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
    """
    重新计算已吃餐数
    算法：
    1. 基础天数 = 从起送日期到昨天（排除暂停和假期）
    2. 历史累计 = 已确认配送记录的配送数量总和
    3. 已吃餐数 = 基础天数 + 历史累计
    """
    try:
        logger.info("=" * 60)
        logger.info("开始计算初始已吃餐数...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": True, "message": "客户表为空", "data": {"debug_info": ["⚠️ 客户表为空"]}}
        
        holiday_dates = get_holiday_dates()
        today = datetime.now().date()
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
                
                # 获取客户暂停日期
                pause_dates = get_customer_pause_dates(customer_name)
                
                # 1. 计算基础天数（起送日期到昨天）
                yesterday = datetime.now() - timedelta(days=1)
                base_days = calculate_valid_delivery_days(start_date, yesterday, pause_dates, holiday_dates)
                
                # 2. 获取历史已确认配送记录累计
                history_confirmed = get_customer_confirmed_delivery_count(customer_name)
                
                # 3. 计算总已吃餐数
                total_eaten = base_days + history_confirmed
                
                # 不能超过总餐数
                if total_eaten > total_meals:
                    total_eaten = total_meals
                
                # 更新记录
                update_success = update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"已吃餐数": total_eaten})
                
                if update_success:
                    debug_info.append(f"✅ {customer_name}: 基础{base_days}天 + 历史{history_confirmed}餐 = 已吃{total_eaten}餐")
                    updated_count += 1
                else:
                    debug_info.append(f"❌ {customer_name}: 更新失败")
                    error_count += 1
                    
            except Exception as e:
                debug_info.append(f"❌ {customer_name}: 处理失败 - {str(e)}")
                error_count += 1
        
        logger.info(f"✅ 完成：成功 {updated_count} 个，失败 {error_count} 个")
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的已吃餐数",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def recalculate_end_date():
    """
    重新计算预计结束日期（修正版）
    算法：
    1. 剩余餐数 = 总餐数 - 历史已确认配送数量累计
    2. 从今天开始，逐日累加，跳过暂停和假期，直到达到剩余餐数
    """
    try:
        logger.info("=" * 60)
        logger.info("开始重新计算预计结束日期...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": True, "message": "客户表为空", "data": {"debug_info": ["⚠️ 客户表为空"]}}
        
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
                
                # 获取客户暂停日期
                pause_dates = get_customer_pause_dates(customer_name)
                
                # 获取历史已确认配送数量累计
                confirmed_count = get_customer_confirmed_delivery_count(customer_name)
                
                # 计算结束日期（考虑历史已确认配送数量）
                end_date = calculate_end_date_with_history(
                    start_date, total_meals, confirmed_count, pause_dates, holiday_dates
                )
                
                # 更新记录
                update_success = update_bitable_record(
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
                    debug_info.append(f"❌ {customer_name}: 更新失败")
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
    """
    修改配送数量（仅限未确认的记录）
    """
    try:
        if not record_id:
            return {"success": False, "message": "缺少配送记录ID"}
        
        # 查询配送记录
        delivery_records = query_bitable_records(DELIVERY_TABLE_ID)
        target_record = None
        
        for record in delivery_records:
            if record.get('record_id') == record_id:
                target_record = record
                break
        
        if not target_record:
            return {"success": False, "message": "配送记录不存在"}
        
        fields = target_record.get('fields', {})
        is_confirmed = fields.get('是否已确认', False)
        
        if is_confirmed:
            return {
                "success": False,
                "message": "该配送记录已确认，无法修改配送数量",
                "data": {"debug_info": ["⚠️ 已确认的记录不可修改"]}
            }
        
        # 更新配送数量
        update_success = update_bitable_record(DELIVERY_TABLE_ID, record_id, {"配送数量": delivery_count})
        
        if update_success:
            return {
                "success": True,
                "message": f"配送数量已更新为 {delivery_count}",
                "data": {"debug_info": [f"✅ 配送数量更新成功"]}
            }
        else:
            return {"success": False, "message": "更新失败"}
            
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def confirm_delivery(delivery_date: str):
    """
    批量确认配送记录
    强制执行：
    1. 必须有配送记录才能确认
    2. 确认后无法修改配送数量
    3. 确认后自动累加已吃餐数
    """
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始确认配送日期: {delivery_date}")
        
        # 查询该日期的配送记录
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
                "message": f"{delivery_date} 没有配送记录，请先生成配送记录",
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
            is_confirmed = fields.get('是否已确认', False)
            delivery_qty = fields.get('配送数量', 1)
            
            # 跳过已确认的记录
            if is_confirmed:
                debug_info.append(f"⏭️ {customer_name}: 已确认过（配送{delivery_qty}份），跳过")
                skipped_count += 1
                continue
            
            # 确认配送记录
            update_success = update_bitable_record(DELIVERY_TABLE_ID, record_id, {"是否已确认": True})
            
            if update_success:
                # 累加客户的已吃餐数
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
                debug_info.append(f"❌ {customer_name}: 确认失败")
        
        logger.info(f"✅ 完成：确认 {confirmed_count} 个，跳过 {skipped_count} 个")
        
        return {
            "success": True,
            "message": f"已确认 {delivery_date} 的 {confirmed_count} 条配送记录（跳过 {skipped_count} 条已确认）",
            "data": {
                "debug_info": debug_info,
                "confirmed_count": confirmed_count,
                "skipped_count": skipped_count
            }
        }
    except Exception as e:
        return {"success": False, "message": f"确认失败: {str(e)}"}

async def generate_delivery_records(delivery_date: str):
    """
    生成配送记录
    特点：
    1. 支持任意日期（未来或过去）
    2. 每个日期独立生成
    3. 自动删除该日期的旧记录
    4. 默认配送数量为1
    """
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始生成配送记录: {delivery_date}")
        
        # 1. 查询该日期已有的配送记录并删除
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
        
        # 2. 查询所有客户
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        if not customers:
            return {"success": False, "message": "客户表为空，无法生成配送记录"}
        
        # 获取公共假期和暂停日期
        holiday_dates = get_holiday_dates()
        selected_date = datetime.strptime(delivery_date, "%Y-%m-%d")
        
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
            
            if not customer_name:
                continue
            
            # 检查是否在配送范围内
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
                # 检查是否是假期
                is_holiday = any(h.date() == selected_date.date() for h in holiday_dates)
                
                # 检查是否是暂停日
                pause_dates = get_customer_pause_dates(customer_name)
                is_pause = any(p.date() == selected_date.date() for p in pause_dates)
                
                if is_holiday:
                    skip_reason = "该日期是假期"
                    skipped_count += 1
                elif is_pause:
                    skip_reason = "该日期是暂停日"
                    skipped_count += 1
                else:
                    # 生成配送记录，默认配送数量为1
                    record = create_bitable_record(DELIVERY_TABLE_ID, {
                        "配送日期": delivery_date,
                        "客户姓名": customer_name,
                        "配送数量": 1,  # 默认为1
                        "是否已确认": False
                    })
                    
                    if record:
                        debug_info.append(f"✅ {customer_name}: 生成配送记录（配送数量默认为1，确认前可修改）")
                        created_count += 1
                    else:
                        debug_info.append(f"❌ {customer_name}: 生成失败")
            else:
                debug_info.append(f"⏭️ {customer_name}: {skip_reason}，跳过")
                skipped_count += 1
        
        logger.info(f"✅ 完成：生成 {created_count} 条，跳过 {skipped_count} 个")
        
        return {
            "success": True,
            "message": f"已生成 {delivery_date} 的 {created_count} 条配送记录（跳过 {skipped_count} 个客户）",
            "data": {
                "debug_info": debug_info,
                "created_count": created_count,
                "skipped_count": skipped_count,
                "tips": [
                    "💡 配送数量默认为1",
                    "💡 确认前可在飞书多维表格中修改配送数量",
                    "💡 确认后配送数量将无法修改"
                ]
            }
        }
    except Exception as e:
        return {"success": False, "message": f"生成失败: {str(e)}"}

async def update_gantt_status():
    """
    更新甘特图状态数据
    包含完整的时间线信息：
    - 起送日期到结束日期
    - 暂停日期详情
    - 假期日期详情
    - 每日配送记录
    """
    try:
        logger.info("=" * 60)
        logger.info("开始更新甘特图状态...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        if not customers:
            return {"success": True, "message": "客户表为空", "data": {"debug_info": ["⚠️ 客户表为空"]}}
        
        # 获取所有假期
        all_holidays = get_holiday_dates()
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = fields.get('客户姓名', '未知')
            
            # 获取客户暂停日期
            pause_dates = get_customer_pause_dates(customer_name)
            
            # 获取配送记录
            delivery_records = query_bitable_records(DELIVERY_TABLE_ID, {
                "conditions": [{
                    "field_name": "客户姓名",
                    "operator": "is",
                    "value": [customer_name]
                }]
            })
            
            # 构建完整的甘特图数据
            gantt_data = {
                "customer_name": customer_name,
                "start_date": fields.get('起送日期'),
                "end_date": fields.get('预计结束日期'),
                "total_meals": fields.get('总餐数'),
                "eaten_meals": fields.get('已吃餐数'),
                "pause_dates": [p.strftime("%Y-%m-%d") for p in pause_dates],  # 暂停日期列表
                "holiday_dates": [h.strftime("%Y-%m-%d") for h in all_holidays],  # 假期日期列表
                "delivery_records": []
            }
            
            # 整理配送记录
            for record in delivery_records:
                delivery_fields = record.get('fields', {})
                delivery_date = delivery_fields.get('配送日期')
                
                # 解析配送日期
                if isinstance(delivery_date, (int, float)):
                    delivery_date_str = datetime.fromtimestamp(delivery_date / 1000).strftime("%Y-%m-%d")
                else:
                    delivery_date_str = delivery_date
                
                gantt_data["delivery_records"].append({
                    "date": delivery_date_str,
                    "count": delivery_fields.get('配送数量', 1),
                    "confirmed": delivery_fields.get('是否已确认', False)
                })
            
            # 按日期排序配送记录
            gantt_data["delivery_records"].sort(key=lambda x: x["date"])
            
            # 更新甘特图字段
            update_success = update_bitable_record(
                CUSTOMER_TABLE_ID,
                record_id,
                {"甘特图数据": json.dumps(gantt_data, ensure_ascii=False)}
            )
            
            if update_success:
                debug_info.append(
                    f"✅ {customer_name}: 甘特图数据已更新（含{len(pause_dates)}个暂停日，{len(gantt_data['delivery_records'])}条配送记录）"
                )
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败")
        
        logger.info(f"✅ 完成：更新 {updated_count} 个客户")
        
        return {
            "success": True,
            "message": f"已更新 {updated_count} 个客户的甘特图状态",
            "data": {
                "debug_info": debug_info,
                "updated_count": updated_count
            }
        }
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def run_all_operations():
    """一键执行所有操作"""
    try:
        logger.info("=" * 60)
        logger.info("开始一键执行所有操作...")
        
        results = []
        
        # 1. 计算初始已吃餐数
        result1 = await recalculate_eaten_meals()
        results.append(f"1️⃣ 计算已吃餐数: {result1['message']}")
        
        # 2. 重新计算结束日期
        result2 = await recalculate_end_date()
        results.append(f"2️⃣ 计算结束日期: {result2['message']}")
        
        # 3. 更新甘特图
        result3 = await update_gantt_status()
        results.append(f"3️⃣ 更新甘特图: {result3['message']}")
        
        return {
            "success": True,
            "message": "一键执行所有操作完成",
            "data": {
                "debug_info": results,
                "results": {
                    "recalculate_eaten": result1,
                    "recalculate_end_date": result2,
                    "update_gantt": result3
                }
            }
        }
    except Exception as e:
        return {"success": False, "message": f"一键执行失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
