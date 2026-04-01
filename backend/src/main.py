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
app = FastAPI(title="配送管理系统API V3.1", version="3.1.0")

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

# 辅助函数：提取富文本内容
def extract_text(value: Any) -> str:
    """提取富文本字段中的纯文本"""
    if not value:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        texts = []
        for item in value:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
            elif isinstance(item, str):
                texts.append(item)
        return ''.join(texts).strip()
    return str(value).strip()

# 辅助函数：日期转时间戳（毫秒）
def date_to_timestamp(date_value) -> int:
    """将日期转换为飞书时间戳（毫秒）"""
    if isinstance(date_value, datetime):
        return int(date_value.timestamp() * 1000)
    elif isinstance(date_value, str):
        dt = datetime.strptime(date_value, "%Y-%m-%d")
        return int(dt.timestamp() * 1000)
    elif isinstance(date_value, (int, float)):
        return int(date_value)
    return 0

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
        logger.info(f"正在更新记录 {record_id}")
        response = requests.put(url, headers=headers, json=body, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 更新成功")
            return True, None
        else:
            error_msg = result.get('msg', '未知错误')
            error_code = result.get('code', '无错误码')
            logger.error(f"❌ 更新失败: code={error_code}, msg={error_msg}")
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
        logger.info(f"正在创建记录")
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

# 辅助函数：获取客户暂停日期列表
def get_customer_pause_dates(customer_name: str, pause_records_all: List[Dict]) -> List[datetime]:
    """获取指定客户的暂停日期列表"""
    pause_dates = []
    
    for record in pause_records_all:
        fields = record.get('fields', {})
        record_customer = extract_text(fields.get('客户姓名'))
        
        if record_customer != customer_name:
            continue
        
        # 处理暂停单天字段
        pause_day_fields = []
        for field_name in fields.keys():
            if '暂停单天' in field_name or '暂停单日' in field_name:
                pause_day_fields.append(field_name)
        
        for field_name in pause_day_fields:
            pause_day = fields.get(field_name)
            if pause_day:
                pause_date = parse_date(pause_day)
                if pause_date:
                    pause_dates.append(pause_date)
        
        # 处理暂停区间字段
        j = 1
        while True:
            start_date = (
                fields.get(f'暂停区间{j}开始') or 
                fields.get(f'暂停区间 {j}开始') or
                fields.get(f'暂停区间{j} 开始') or
                fields.get(f'暂停区间 {j} 开始')
            )
            end_date = (
                fields.get(f'暂停区间{j}结束') or 
                fields.get(f'暂停区间 {j}结束') or
                fields.get(f'暂停区间{j} 结束') or
                fields.get(f'暂停区间 {j} 结束')
            )
            
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

# 🔴 核心函数：生成吃餐日历
def generate_meal_calendar(
    customer_name: str,
    start_date: datetime,
    end_date: Optional[datetime],
    pause_dates: List[datetime],
    holiday_dates: List[datetime],
    existing_calendar: Optional[Dict] = None
) -> Dict:
    """
    生成吃餐日历
    
    结构：
    {
        "2026-03-27": {"qty": 1, "status": "delivered", "source": "calendar"},
        "2026-03-28": {"qty": 0, "status": "paused", "source": "system"},
        "2026-03-29": {"qty": 0, "status": "holiday", "source": "system"},
        ...
    }
    
    status: delivered(已配送), paused(暂停), holiday(假期), pending(待确认)
    source: calendar(日历设置), delivery(配送记录), system(系统自动)
    """
    calendar = {}
    
    if not end_date:
        # 如果没有结束日期，默认生成到起送日期后90天
        end_date = start_date + timedelta(days=90)
    
    current = start_date
    yesterday = datetime.now() - timedelta(days=1)
    
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        
        # 检查是否已有记录
        if existing_calendar and date_str in existing_calendar:
            calendar[date_str] = existing_calendar[date_str]
        else:
            # 判断状态
            is_pause = any(p.date() == current.date() for p in pause_dates)
            is_holiday = any(h.date() == current.date() for h in holiday_dates)
            
            if is_pause:
                calendar[date_str] = {"qty": 0, "status": "paused", "source": "system"}
            elif is_holiday:
                calendar[date_str] = {"qty": 0, "status": "holiday", "source": "system"}
            elif current <= yesterday:
                # 过去的日期，默认为已配送
                calendar[date_str] = {"qty": 1, "status": "delivered", "source": "calendar"}
            else:
                # 今天及未来，待确认
                calendar[date_str] = {"qty": 0, "status": "pending", "source": "system"}
        
        current += timedelta(days=1)
    
    return calendar

# 🔴 核心函数：计算已吃餐数（基于吃餐日历）
def calculate_eaten_meals_from_calendar(calendar: Dict) -> int:
    """从吃餐日历计算已吃餐数"""
    total = 0
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for date_str, record in calendar.items():
        # 只统计今天之前且已配送的记录
        if date_str <= yesterday and record.get("status") == "delivered":
            total += record.get("qty", 0)
    
    return total

# 🔴 核心函数：同步配送记录到吃餐日历
def sync_delivery_to_calendar(
    customer_name: str,
    calendar: Dict,
    delivery_records: List[Dict]
) -> Dict:
    """将配送记录表的确认状态同步到吃餐日历"""
    
    for record in delivery_records:
        fields = record.get('fields', {})
        record_customer = extract_text(fields.get('客户姓名'))
        
        if record_customer != customer_name:
            continue
        
        delivery_date_ts = fields.get('配送日期')
        if not delivery_date_ts:
            continue
        
        delivery_date = parse_date(delivery_date_ts)
        if not delivery_date:
            continue
        
        date_str = delivery_date.strftime("%Y-%m-%d")
        
        # 检查确认状态
        confirm_status = fields.get('确认状态', '')
        if isinstance(confirm_status, dict):
            status_text = confirm_status.get('text', '')
        else:
            status_text = extract_text(confirm_status)
        
        if status_text == "已确认":
            delivery_qty = fields.get('配送数量', 1)
            calendar[date_str] = {
                "qty": delivery_qty if isinstance(delivery_qty, int) else 1,
                "status": "delivered",
                "source": "delivery"
            }
    
    return calendar

# API接口
@app.get("/")
async def root():
    return {"message": "配送管理系统API V3.1运行中", "version": "3.1.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Service is running"}

@app.get("/api/diagnose")
async def diagnose():
    """诊断接口"""
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "version": "3.1.0",
        "calculation_logic": {
            "已吃餐数": "吃餐日历中过去日期的配送数量总和",
            "吃餐日历": {
                "说明": "记录每个客户每天的配送数量",
                "过去日期": "默认为1，可在日历中手动修改",
                "今天及未来": "通过配送记录表确认后自动同步"
            },
            "同步机制": "配送记录表确认后自动同步到吃餐日历"
        },
        "workflow": {
            "新客户流程": [
                "1. 设置起送日期、总餐数",
                "2. 系统自动生成吃餐日历（过去日期默认为1）",
                "3. 每日生成配送记录 → 批量确认",
                "4. 确认后自动同步到吃餐日历"
            ],
            "老客户录入": [
                "方案1: 在吃餐日历中手动设置过去的配送数量",
                "方案2: 补录配送记录表（设为已确认状态）"
            ],
            "日常操作": [
                "1. 生成明天配送记录",
                "2. 批量确认昨天的配送记录（自动同步到日历）",
                "3. 修改历史数据：在吃餐日历中修改"
            ]
        },
        "env_config": {
            "FEISHU_APP_ID": "已配置" if FEISHU_APP_ID else "❌ 未配置",
            "FEISHU_APP_SECRET": "已配置" if FEISHU_APP_SECRET else "❌ 未配置",
            "BITABLE_APP_TOKEN": "已配置" if BITABLE_APP_TOKEN else "❌ 未配置",
            "CUSTOMER_TABLE_ID": "已配置" if CUSTOMER_TABLE_ID else "❌ 未配置",
            "DELIVERY_TABLE_ID": "已配置" if DELIVERY_TABLE_ID else "❌ 未配置",
            "HOLIDAY_TABLE_ID": "已配置" if HOLIDAY_TABLE_ID else "❌ 未配置",
            "PAUSE_TABLE_ID": "已配置" if PAUSE_TABLE_ID else "❌ 未配置"
        }
    }
    
    token = get_feishu_token()
    if token:
        diagnosis["tests"] = {"feishu_token": "✅ 成功"}
        
        if CUSTOMER_TABLE_ID:
            customers = query_bitable_records(CUSTOMER_TABLE_ID)
            if customers:
                diagnosis["tests"]["customer_table"] = f"✅ 查询到 {len(customers)} 个客户"
    
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
        
        return {
            "success": True,
            "token": token,
            "user": {"username": username, "role": user_info['role']}
        }
    except Exception as e:
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
        record_id = data.get('record_id')
        
        # 🆕 新增：修改吃餐日历
        calendar_updates = data.get('calendar_updates')  # {客户名: {日期: 数量}}
        
        logger.info(f"🚀 工作流 {workflow_type} 开始执行 (用户: {session['username']})")
        
        if workflow_type == 'recalculate_eaten':
            return await recalculate_eaten_meals()
        elif workflow_type == 'confirm':
            result = await confirm_delivery(delivery_date)
            # 确认后自动重新计算
            await recalculate_eaten_meals()
            await recalculate_end_date()
            return result
        elif workflow_type == 'recalculate_end_date':
            return await recalculate_end_date()
        elif workflow_type == 'generate':
            return await generate_delivery_records(delivery_date)
        elif workflow_type == 'update_calendar':
            return await update_meal_calendar(calendar_updates)
        elif workflow_type == 'generate_calendar':
            return await generate_customer_calendar()
        elif workflow_type == 'run_all':
            return await run_all_operations()
        else:
            return {"success": False, "message": f"未知的工作流类型: {workflow_type}"}
    
    except Exception as e:
        logger.error(f"❌ 工作流执行失败: {e}", exc_info=True)
        return {"success": False, "message": f"执行失败: {str(e)}"}

async def generate_customer_calendar():
    """为所有客户生成吃餐日历"""
    try:
        logger.info("=" * 60)
        logger.info("开始生成客户吃餐日历...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "查询客户数据失败"}
        
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        holiday_dates = get_holiday_dates()
        delivery_records_all = query_bitable_records(DELIVERY_TABLE_ID)
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = extract_text(fields.get('客户姓名'))
            
            if not customer_name:
                continue
            
            start_date = parse_date(fields.get('起送日期'))
            end_date = parse_date(fields.get('预计结束日期'))
            
            if not start_date:
                debug_info.append(f"⚠️ {customer_name}: 起送日期未填写，跳过")
                continue
            
            # 获取暂停日期
            pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
            
            # 获取已有日历数据
            existing_calendar_str = fields.get('吃餐日历', '{}')
            try:
                existing_calendar = json.loads(existing_calendar_str) if isinstance(existing_calendar_str, str) else existing_calendar_str
            except:
                existing_calendar = {}
            
            # 生成新日历
            calendar = generate_meal_calendar(
                customer_name, start_date, end_date,
                pause_dates, holiday_dates, existing_calendar
            )
            
            # 同步配送记录
            calendar = sync_delivery_to_calendar(customer_name, calendar, delivery_records_all)
            
            # 更新到客户表
            update_success, error_msg = update_bitable_record(
                CUSTOMER_TABLE_ID, record_id,
                {"吃餐日历": json.dumps(calendar, ensure_ascii=False)}
            )
            
            if update_success:
                # 计算已吃餐数
                eaten_count = calculate_eaten_meals_from_calendar(calendar)
                update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"已吃餐数": eaten_count})
                
                debug_info.append(f"✅ {customer_name}: 生成日历（已吃{eaten_count}餐）")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已为 {updated_count} 个客户生成吃餐日历",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"生成失败: {str(e)}"}

async def update_meal_calendar(calendar_updates: Dict):
    """修改客户的吃餐日历"""
    try:
        if not calendar_updates:
            return {"success": False, "message": "未提供日历更新数据"}
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        holiday_dates = get_holiday_dates()
        
        debug_info = []
        updated_count = 0
        
        for customer_name, updates in calendar_updates.items():
            # 查找客户记录
            customer_record = None
            for c in customers:
                if extract_text(c.get('fields', {}).get('客户姓名')) == customer_name:
                    customer_record = c
                    break
            
            if not customer_record:
                debug_info.append(f"❌ {customer_name}: 找不到客户记录")
                continue
            
            fields = customer_record.get('fields', {})
            record_id = customer_record.get('record_id')
            
            # 获取现有日历
            existing_calendar_str = fields.get('吃餐日历', '{}')
            try:
                calendar = json.loads(existing_calendar_str) if isinstance(existing_calendar_str, str) else existing_calendar_str
            except:
                calendar = {}
            
            # 应用更新
            for date_str, qty in updates.items():
                calendar[date_str] = {
                    "qty": qty,
                    "status": "delivered" if qty > 0 else "paused",
                    "source": "calendar"
                }
            
            # 更新日历
            update_success, error_msg = update_bitable_record(
                CUSTOMER_TABLE_ID, record_id,
                {"吃餐日历": json.dumps(calendar, ensure_ascii=False)}
            )
            
            if update_success:
                # 重新计算已吃餐数
                eaten_count = calculate_eaten_meals_from_calendar(calendar)
                update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"已吃餐数": eaten_count})
                
                # 重新计算预计结束日期
                await recalculate_end_date_for_customer(record_id, customer_name, fields, calendar)
                
                debug_info.append(f"✅ {customer_name}: 更新日历成功，已吃{eaten_count}餐")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已更新 {updated_count} 个客户的吃餐日历",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def recalculate_end_date_for_customer(record_id: str, customer_name: str, fields: Dict, calendar: Dict):
    """为单个客户重新计算预计结束日期"""
    try:
        total_meals = fields.get('总餐数', 0)
        eaten_count = calculate_eaten_meals_from_calendar(calendar)
        remaining = total_meals - eaten_count
        
        if remaining <= 0:
            return
        
        start_date = parse_date(fields.get('起送日期'))
        pause_dates = get_customer_pause_dates(customer_name, [])
        holiday_dates = get_holiday_dates()
        
        current = datetime.now()
        days_counted = 0
        
        while days_counted < remaining:
            is_pause = any(p.date() == current.date() for p in pause_dates)
            is_holiday = any(h.date() == current.date() for h in holiday_dates)
            
            if not is_pause and not is_holiday:
                days_counted += 1
            
            if days_counted < remaining:
                current += timedelta(days=1)
        
        end_timestamp = date_to_timestamp(current)
        update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"预计结束日期": end_timestamp})
    except Exception as e:
        logger.error(f"计算结束日期失败: {e}")

async def recalculate_eaten_meals():
    """重新计算已吃餐数（基于吃餐日历）"""
    try:
        logger.info("=" * 60)
        logger.info("开始计算已吃餐数...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "查询客户数据失败"}
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = extract_text(fields.get('客户姓名'))
            
            if not customer_name:
                continue
            
            # 检查"等信息通知"
            waiting = extract_text(fields.get('等信息通知', ''))
            if waiting:
                debug_info.append(f"⏸️ {customer_name}: 等信息通知，跳过")
                continue
            
            # 获取吃餐日历
            calendar_str = fields.get('吃餐日历', '{}')
            try:
                calendar = json.loads(calendar_str) if isinstance(calendar_str, str) else calendar_str
            except:
                calendar = {}
            
            if not calendar:
                debug_info.append(f"⚠️ {customer_name}: 吃餐日历为空，请先生成")
                continue
            
            # 计算已吃餐数
            eaten_count = calculate_eaten_meals_from_calendar(calendar)
            
            # 更新
            update_success, error_msg = update_bitable_record(
                CUSTOMER_TABLE_ID, record_id,
                {"已吃餐数": eaten_count}
            )
            
            if update_success:
                debug_info.append(f"✅ {customer_name}: 已吃{eaten_count}餐")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的已吃餐数",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def recalculate_end_date():
    """重新计算预计结束日期"""
    try:
        logger.info("=" * 60)
        logger.info("开始计算预计结束日期...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "查询客户数据失败"}
        
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        holiday_dates = get_holiday_dates()
        
        debug_info = []
        updated_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = extract_text(fields.get('客户姓名'))
            
            if not customer_name:
                continue
            
            waiting = extract_text(fields.get('等信息通知', ''))
            if waiting:
                continue
            
            total_meals = fields.get('总餐数', 0)
            eaten_count = fields.get('已吃餐数', 0)
            start_date = parse_date(fields.get('起送日期'))
            
            if not start_date or total_meals <= 0:
                continue
            
            remaining = total_meals - eaten_count
            if remaining <= 0:
                continue
            
            pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
            
            current = datetime.now()
            days_counted = 0
            
            while days_counted < remaining:
                is_pause = any(p.date() == current.date() for p in pause_dates)
                is_holiday = any(h.date() == current.date() for h in holiday_dates)
                
                if not is_pause and not is_holiday:
                    days_counted += 1
                
                if days_counted < remaining:
                    current += timedelta(days=1)
            
            end_timestamp = date_to_timestamp(current)
            
            update_success, error_msg = update_bitable_record(
                CUSTOMER_TABLE_ID, record_id,
                {"预计结束日期": end_timestamp}
            )
            
            if update_success:
                debug_info.append(f"✅ {customer_name}: 剩余{remaining}餐 → 结束{current.strftime('%Y-%m-%d')}")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已计算 {updated_count} 个客户的预计结束日期",
            "data": {"debug_info": debug_info}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def confirm_delivery(delivery_date: str):
    """批量确认配送记录"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请选择配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始确认配送: {delivery_date}")
        
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
                "data": {"debug_info": [f"⚠️ 未找到配送记录"]}
            }
        
        debug_info = []
        confirmed_count = 0
        
        for record in records:
            fields = record.get('fields', {})
            record_id = record.get('record_id')
            customer_name = extract_text(fields.get('客户姓名'))
            
            confirm_status = fields.get('确认状态', '')
            if isinstance(confirm_status, dict):
                status_text = confirm_status.get('text', '')
            else:
                status_text = extract_text(confirm_status)
            
            if status_text == "已确认":
                debug_info.append(f"⏭️ {customer_name}: 已确认过")
                continue
            
            delivery_qty = fields.get('配送数量', 1)
            
            update_success, error_msg = update_bitable_record(
                DELIVERY_TABLE_ID, record_id,
                {"确认状态": "已确认"}
            )
            
            if update_success:
                debug_info.append(f"✅ {customer_name}: 确认配送{delivery_qty}份")
                confirmed_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 确认失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已确认 {confirmed_count} 条配送记录",
            "data": {
                "debug_info": debug_info,
                "confirmed_count": confirmed_count
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
        
        # 删除旧记录
        filter_condition = {
            "conditions": [{
                "field_name": "配送日期",
                "operator": "is",
                "value": [delivery_date]
            }]
        }
        old_records = query_bitable_records(DELIVERY_TABLE_ID, filter_condition)
        
        if old_records:
            old_ids = [r.get('record_id') for r in old_records]
            delete_bitable_records(DELIVERY_TABLE_ID, old_ids)
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "客户表为空"}
        
        holiday_dates = get_holiday_dates()
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        selected_date = datetime.strptime(delivery_date, "%Y-%m-%d")
        tomorrow = selected_date + timedelta(days=1)
        
        debug_info = []
        created_count = 0
        skipped_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            customer_name = extract_text(fields.get('客户姓名'))
            
            if not customer_name:
                continue
            
            waiting = extract_text(fields.get('等信息通知', ''))
            if waiting:
                debug_info.append(f"⏸️ {customer_name}: 等信息通知")
                continue
            
            start_date = parse_date(fields.get('起送日期'))
            end_date = parse_date(fields.get('预计结束日期'))
            total_meals = fields.get('总餐数', 0)
            eaten_count = fields.get('已吃餐数', 0)
            
            if not start_date:
                continue
            
            skip_reason = None
            
            if selected_date.date() < start_date.date():
                skip_reason = "未到起送日期"
            elif end_date and selected_date.date() > end_date.date():
                skip_reason = "已过结束日期"
            elif eaten_count >= total_meals:
                skip_reason = "已吃完所有餐数"
            
            if skip_reason:
                debug_info.append(f"⏭️ {customer_name}: {skip_reason}")
                skipped_count += 1
                continue
            
            is_holiday = any(h.date() == selected_date.date() for h in holiday_dates)
            pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
            is_pause = any(p.date() == selected_date.date() for p in pause_dates)
            
            if is_holiday:
                debug_info.append(f"📅 {customer_name}: 假期")
                skipped_count += 1
                continue
            
            if is_pause:
                debug_info.append(f"⏸️ {customer_name}: 暂停日")
                skipped_count += 1
                continue
            
            is_last_day = end_date and tomorrow.date() > end_date.date()
            
            delivery_fields = {
                "配送日期": date_to_timestamp(delivery_date),
                "客户姓名": customer_name,
                "手机号": extract_text(fields.get('手机号')),
                "配送地址": extract_text(fields.get('配送地址')),
                "忌口": extract_text(fields.get('忌口')),
                "加量": extract_text(fields.get('加量')),
                "备注": extract_text(fields.get('备注')),
                "配送数量": 1,
                "明天是否最后一天": is_last_day,
                "确认状态": "未确认"
            }
            
            success, error_msg = create_bitable_record(DELIVERY_TABLE_ID, delivery_fields)
            
            if success:
                debug_info.append(f"✅ {customer_name}: 生成配送记录")
                created_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 创建失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已生成 {created_count} 条配送记录（跳过 {skipped_count} 条）",
            "data": {"debug_info": debug_info, "created_count": created_count}
        }
    except Exception as e:
        logger.error(f"❌ 生成失败: {e}", exc_info=True)
        return {"success": False, "message": f"生成失败: {str(e)}"}

async def run_all_operations():
    """一键执行所有操作"""
    try:
        results = []
        
        result1 = await generate_customer_calendar()
        results.append(f"1️⃣ 生成吃餐日历: {result1['message']}")
        
        result2 = await recalculate_eaten_meals()
        results.append(f"2️⃣ 计算已吃餐数: {result2['message']}")
        
        result3 = await recalculate_end_date()
        results.append(f"3️⃣ 计算结束日期: {result3['message']}")
        
        return {
            "success": True,
            "message": "所有操作已完成",
            "data": {"debug_info": results}
        }
    except Exception as e:
        return {"success": False, "message": f"执行失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
