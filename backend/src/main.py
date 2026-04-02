import os
import json
import secrets
import logging
from datetime import datetime, timedelta, date
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
app = FastAPI(title="配送管理系统API V3.3", version="3.3.0")

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

# 辅助函数：提取多选字段选项列表
def extract_multi_select(value: Any) -> List[str]:
    """提取多选字段中的选项列表"""
    if not value:
        return []
    
    # 如果是列表
    if isinstance(value, list):
        options = []
        for item in value:
            if isinstance(item, dict) and 'text' in item:
                options.append(item['text'])
            elif isinstance(item, str):
                options.append(item)
        return options
    
    # 如果是字符串，按逗号分割
    if isinstance(value, str):
        return [v.strip() for v in value.split(',') if v.strip()]
    
    return []

# 辅助函数：提取单选字段值
def extract_single_select(value: Any) -> str:
    """提取单选字段中的选项值"""
    if not value:
        return ""
    
    if isinstance(value, str):
        return value.strip()
    
    if isinstance(value, dict):
        return value.get('text', '') or value.get('name', '') or ''
    
    return str(value).strip()

# 辅助函数：日期转时间戳（毫秒）
def date_to_timestamp(date_value) -> int:
    """将日期转换为飞书时间戳（毫秒）- 使用本地时间"""
    if isinstance(date_value, datetime):
        return int(date_value.timestamp() * 1000)
    elif isinstance(date_value, str):
        dt = datetime.strptime(date_value, "%Y-%m-%d")
        return int(dt.timestamp() * 1000)
    elif isinstance(date_value, (int, float)):
        return int(date_value)
    return 0

# 辅助函数：解析日期（修复时区问题 - 使用本地时间）
def parse_date(date_value) -> Optional[date]:
    """解析飞书日期字段，返回date对象"""
    if not date_value:
        return None
    
    try:
        if isinstance(date_value, (int, float)):
            # 飞书时间戳是毫秒，转换为秒
            ts = date_value / 1000
            # 使用本地时间（不再使用UTC）
            dt = datetime.fromtimestamp(ts)
            logger.info(f"解析时间戳 {date_value} -> {dt.date()}")
            return dt.date()
        elif isinstance(date_value, str):
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.date()
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
    
    body = {"automatic_fields": False}
    if filter_condition:
        body["filter"] = filter_condition
    
    all_records = []
    has_more = True
    page_token = None
    
    while has_more:
        if page_token:
            body["page_token"] = page_token
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                records = data.get("items", [])
                all_records.extend(records)
                has_more = data.get("has_more", False)
                page_token = data.get("page_token")
            else:
                logger.error(f"❌ 查询失败: {result}")
                break
        except Exception as e:
            logger.error(f"❌ 查询异常: {e}")
            break
    
    logger.info(f"✅ 查询到 {len(all_records)} 条记录")
    return all_records

def update_bitable_record(table_id: str, record_id: str, fields: Dict) -> tuple:
    """更新多维表格记录"""
    if not BITABLE_APP_TOKEN or not table_id or not record_id:
        return False, "配置缺失"
    
    token = get_feishu_token()
    if not token:
        return False, "获取token失败"
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"fields": fields}
    
    try:
        response = requests.put(url, headers=headers, json=body, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 更新成功")
            return True, ""
        else:
            error_msg = f"错误码{result.get('code')}: {result.get('msg')}"
            logger.error(f"❌ 更新失败: {error_msg}")
            return False, error_msg
    except Exception as e:
        logger.error(f"❌ 更新异常: {e}")
        return False, str(e)

def create_bitable_record(table_id: str, fields: Dict) -> tuple:
    """创建多维表格记录"""
    if not BITABLE_APP_TOKEN or not table_id:
        return False, "配置缺失"
    
    token = get_feishu_token()
    if not token:
        return False, "获取token失败"
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"fields": fields}
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"✅ 创建成功")
            return True, ""
        else:
            error_msg = f"错误码{result.get('code')}: {result.get('msg')}"
            logger.error(f"❌ 创建失败: {error_msg}")
            return False, error_msg
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
def get_customer_pause_dates(customer_name: str, pause_records_all: List[Dict]) -> List[date]:
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
def get_holiday_dates() -> List[date]:
    """获取公共假期列表"""
    holiday_records = query_bitable_records(HOLIDAY_TABLE_ID)
    holiday_dates = []
    
    for record in holiday_records:
        fields = record.get('fields', {})
        holiday_date = parse_date(fields.get('日期'))
        if holiday_date:
            logger.info(f"假期日期: {holiday_date}")
            holiday_dates.append(holiday_date)
    
    return holiday_dates

# 🔴 核心函数：生成吃餐日历
def generate_meal_calendar(
    customer_name: str,
    start_date: date,
    end_date: Optional[date],
    pause_dates: List[date],
    holiday_dates: List[date],
    existing_calendar: Optional[Dict] = None
) -> Dict:
    """
    生成吃餐日历
    
    规则：
    1. 从起送日期当天开始计算
    2. 过去的日期 = 昨天及以前（不包含今天）
    3. 暂停日和假期不配送
    """
    calendar = {}
    
    if not end_date:
        # 如果没有结束日期，默认生成到起送日期后90天
        end_date = start_date + timedelta(days=90)
    
    # 今天日期（不含时间）
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    logger.info(f"生成日历: {customer_name}, 起送={start_date}, 结束={end_date}, 今天={today}")
    
    # 从起送日期开始，到结束日期
    current = start_date
    
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        
        # 检查是否已有记录（保留用户手动修改的数据）
        if existing_calendar and date_str in existing_calendar:
            existing_info = existing_calendar[date_str]
            # 只保留手动修改的数据（source为calendar）
            if existing_info.get('source') == 'calendar':
                calendar[date_str] = existing_info
                current += timedelta(days=1)
                continue
        
        # 判断状态
        is_pause = current in pause_dates
        is_holiday = current in holiday_dates
        
        if is_pause:
            calendar[date_str] = {"qty": 0, "status": "paused", "source": "system"}
        elif is_holiday:
            calendar[date_str] = {"qty": 0, "status": "holiday", "source": "system"}
        elif current <= yesterday:
            # 过去的日期（昨天及以前），默认为已配送数量1
            calendar[date_str] = {"qty": 1, "status": "delivered", "source": "system"}
        else:
            # 今天及未来，待确认
            calendar[date_str] = {"qty": 1, "status": "pending", "source": "system"}
        
        current += timedelta(days=1)
    
    return calendar

# 辅助函数：同步配送记录到吃餐日历
def sync_delivery_to_calendar(customer_name: str, calendar: Dict, delivery_records_all: List[Dict]) -> Dict:
    """将配送记录表的确认状态同步到吃餐日历"""
    
    for record in delivery_records_all:
        fields = record.get('fields', {})
        record_customer = extract_text(fields.get('客户姓名'))
        
        if record_customer != customer_name:
            continue
        
        # 解析配送日期
        delivery_date = parse_date(fields.get('配送日期'))
        if not delivery_date:
            continue
        
        date_str = delivery_date.strftime("%Y-%m-%d")
        
        # 检查确认状态
        confirm_status = fields.get('确认状态', '')
        if isinstance(confirm_status, dict):
            status_text = confirm_status.get('text', '')
        else:
            status_text = extract_text(confirm_status)
        
        # 只有已确认的记录才同步
        if status_text == '已确认':
            delivery_qty = fields.get('配送数量', 1)
            calendar[date_str] = {
                "qty": delivery_qty,
                "status": "delivered",
                "source": "delivery"
            }
    
    return calendar

# 辅助函数：从日历计算已吃餐数
def calculate_eaten_meals_from_calendar(calendar: Dict) -> int:
    """从吃餐日历计算已吃餐数（昨天及以前的配送数量总和）"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    eaten = 0
    for date_str, info in calendar.items():
        try:
            record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            # 只统计昨天及以前的
            if record_date <= yesterday:
                eaten += info.get('qty', 0)
        except:
            continue
    
    return eaten

# ==================== API路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "配送管理系统API V3.3",
        "features": [
            "修复日期时区问题",
            "修复单选字段格式问题",
            "删除预计结束日期计算"
        ]
    }

@app.post("/api/login")
async def login(request: Request):
    """用户登录"""
    try:
        data = await request.json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        user_info = get_user_info(username)
        if not user_info or user_info['password'] != password:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = {
            'username': username,
            'role': user_info['role'],
            'expire_time': datetime.now() + timedelta(hours=USERS_CONFIG['session_expire_hours'])
        }
        
        return {"success": True, "token": token, "role": user_info['role']}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logout")
async def logout(request: Request):
    """用户登出"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header else ''
    if token in SESSIONS:
        del SESSIONS[token]
    return {"success": True}

@app.get("/api/verify")
async def verify(request: Request):
    """验证token"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header else ''
    session = verify_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="无效的token")
    return {"success": True, "username": session['username'], "role": session['role']}

@app.post("/run")
async def run_workflow(request: Request):
    """执行工作流"""
    try:
        data = await request.json()
        workflow_type = data.get('workflow_type')
        
        if workflow_type == 'generate_calendar':
            return await generate_customer_calendar()
        elif workflow_type == 'generate_delivery':
            delivery_date = data.get('delivery_date')
            return await generate_delivery_records(delivery_date)
        elif workflow_type == 'confirm_delivery':
            delivery_date = data.get('delivery_date')
            return await confirm_delivery_records(delivery_date)
        elif workflow_type == 'recalculate_eaten':
            return await recalculate_eaten_meals()
        elif workflow_type == 'update_gantt':
            return await update_gantt_status()
        elif workflow_type == 'update_single_calendar':
            return await update_single_customer_calendar(data)
        elif workflow_type == 'sync_all':
            return await sync_all_operations()
        elif workflow_type == 'get_customers':
            return await get_customers_list()
        elif workflow_type == 'get_customer_calendar':
            return await get_customer_calendar_data(data.get('customer_name'))
        else:
            return {"success": False, "message": f"未知的工作流类型: {workflow_type}"}
    
    except Exception as e:
        logger.error(f"❌ 工作流执行失败: {e}", exc_info=True)
        return {"success": False, "message": f"执行失败: {str(e)}"}

async def sync_all_operations():
    """一键同步所有数据"""
    try:
        results = []
        
        result1 = await generate_customer_calendar()
        results.append(f"1️⃣ 生成吃餐日历: {result1['message']}")
        
        result2 = await recalculate_eaten_meals()
        results.append(f"2️⃣ 计算已吃餐数: {result2['message']}")
        
        return {
            "success": True,
            "message": "同步完成",
            "data": {"debug_info": results}
        }
    except Exception as e:
        return {"success": False, "message": f"同步失败: {str(e)}"}

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
            
            if not start_date:
                debug_info.append(f"⚠️ {customer_name}: 起送日期未填写，跳过")
                continue
            
            # 获取暂停日期
            pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
            logger.info(f"{customer_name}: 起送={start_date}, 暂停={pause_dates}")
            
            # 获取已有日历数据
            existing_calendar_str = fields.get('吃餐日历', '{}')
            try:
                existing_calendar = json.loads(existing_calendar_str) if isinstance(existing_calendar_str, str) else existing_calendar_str
            except:
                existing_calendar = {}
            
            # 生成新日历（不传结束日期，由系统自动计算）
            calendar = generate_meal_calendar(
                customer_name, start_date, None,
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
                
                debug_info.append(f"✅ {customer_name}: 起送{start_date}, 已吃{eaten_count}餐")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已为 {updated_count} 个客户生成吃餐日历",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        logger.error(f"❌ 生成失败: {e}", exc_info=True)
        return {"success": False, "message": f"生成失败: {str(e)}"}

async def update_single_customer_calendar(data: Dict):
    """修改单个客户的吃餐日历"""
    try:
        customer_name = data.get('customer_name')
        calendar_updates = data.get('calendar_updates', {})
        
        if not customer_name:
            return {"success": False, "message": "请提供客户姓名"}
        
        if not calendar_updates:
            return {"success": False, "message": "请提供日历更新数据"}
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        customer_record = None
        
        for c in customers:
            if extract_text(c.get('fields', {}).get('客户姓名')) == customer_name:
                customer_record = c
                break
        
        if not customer_record:
            return {"success": False, "message": f"找不到客户: {customer_name}"}
        
        fields = customer_record.get('fields', {})
        record_id = customer_record.get('record_id')
        
        existing_calendar_str = fields.get('吃餐日历', '{}')
        try:
            calendar = json.loads(existing_calendar_str) if isinstance(existing_calendar_str, str) else existing_calendar_str
        except:
            calendar = {}
        
        today = date.today()
        for date_str, qty in calendar_updates.items():
            try:
                record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                continue
            
            if record_date >= today:
                continue
            
            calendar[date_str] = {
                "qty": qty,
                "status": "delivered" if qty > 0 else "paused",
                "source": "calendar"
            }
        
        update_success, error_msg = update_bitable_record(
            CUSTOMER_TABLE_ID, record_id,
            {"吃餐日历": json.dumps(calendar, ensure_ascii=False)}
        )
        
        if update_success:
            eaten_count = calculate_eaten_meals_from_calendar(calendar)
            update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"已吃餐数": eaten_count})
            
            return {
                "success": True,
                "message": f"已更新 {customer_name} 的吃餐日历",
                "data": {"eaten_count": eaten_count}
            }
        else:
            return {"success": False, "message": f"更新失败: {error_msg}"}
    
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def recalculate_eaten_meals():
    """重新计算所有客户的已吃餐数"""
    try:
        logger.info("=" * 60)
        logger.info("开始重新计算已吃餐数...")
        
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
            
            calendar_str = fields.get('吃餐日历', '{}')
            try:
                calendar = json.loads(calendar_str) if isinstance(calendar_str, str) else calendar_str
            except:
                calendar = {}
            
            if not calendar:
                continue
            
            eaten_count = calculate_eaten_meals_from_calendar(calendar)
            
            current_eaten = fields.get('已吃餐数', 0)
            if eaten_count != current_eaten:
                update_success, error_msg = update_bitable_record(
                    CUSTOMER_TABLE_ID, record_id,
                    {"已吃餐数": eaten_count}
                )
                
                if update_success:
                    debug_info.append(f"✅ {customer_name}: {current_eaten} → {eaten_count}")
                    updated_count += 1
                else:
                    debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已更新 {updated_count} 个客户的已吃餐数",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"计算失败: {str(e)}"}

async def generate_delivery_records(delivery_date: str):
    """生成配送记录"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请提供配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始生成配送记录: {delivery_date}")
        
        try:
            selected_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
            tomorrow = selected_date + timedelta(days=1)
        except:
            return {"success": False, "message": "日期格式错误，请使用 YYYY-MM-DD 格式"}
        
        # 删除该日期的旧记录
        old_records = query_bitable_records(DELIVERY_TABLE_ID)
        to_delete = []
        
        for record in old_records:
            fields = record.get('fields', {})
            record_date = parse_date(fields.get('配送日期'))
            if record_date == selected_date:
                to_delete.append(record.get('record_id'))
        
        if to_delete:
            delete_bitable_records(DELIVERY_TABLE_ID, to_delete)
            logger.info(f"✅ 删除 {len(to_delete)} 条旧记录")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        holiday_dates = get_holiday_dates()
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        
        debug_info = []
        created_count = 0
        skipped_count = 0
        
        for customer in customers:
            fields = customer.get('fields', {})
            customer_name = extract_text(fields.get('客户姓名'))
            
            if not customer_name:
                continue
            
            start_date = parse_date(fields.get('起送日期'))
            total_meals = fields.get('总餐数', 0)
            eaten_count = fields.get('已吃餐数', 0)
            
            if not start_date:
                continue
            
            skip_reason = None
            
            if selected_date < start_date:
                skip_reason = "未到起送日期"
            elif eaten_count >= total_meals:
                skip_reason = "已吃完所有餐数"
            
            if skip_reason:
                debug_info.append(f"⏭️ {customer_name}: {skip_reason}")
                skipped_count += 1
                continue
            
            is_holiday = selected_date in holiday_dates
            pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
            is_pause = selected_date in pause_dates
            
            if is_holiday:
                debug_info.append(f"📅 {customer_name}: 假期")
                skipped_count += 1
                continue
            
            if is_pause:
                debug_info.append(f"⏸️ {customer_name}: 暂停日")
                skipped_count += 1
                continue
            
            # 提取字段值 - 修复单选/多选字段格式
            # 忌口：可能是多选或文本
            jikou_raw = fields.get('忌口')
            if jikou_raw:
                jikou_list = extract_multi_select(jikou_raw)
                jikou_value = jikou_list if jikou_list else extract_text(jikou_raw)
            else:
                jikou_value = ""
            
            # 加量：单选或文本
            jialiang_raw = fields.get('加量')
            jialiang_value = extract_single_select(jialiang_raw) if jialiang_raw else ""
            
            # 备注：文本
            beizhu_value = extract_text(fields.get('备注')) if fields.get('备注') else ""
            
            delivery_fields = {
                "配送日期": date_to_timestamp(delivery_date),
                "客户姓名": customer_name,
                "手机号": extract_text(fields.get('手机号')),
                "配送地址": extract_text(fields.get('配送地址')),
                "忌口": jikou_value,
                "加量": jialiang_value,
                "备注": beizhu_value,
                "配送数量": 1,
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

async def confirm_delivery_records(delivery_date: str):
    """批量确认配送记录"""
    try:
        if not delivery_date:
            return {"success": False, "message": "请提供配送日期"}
        
        logger.info("=" * 60)
        logger.info(f"开始确认配送记录: {delivery_date}")
        
        try:
            selected_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
        except:
            return {"success": False, "message": "日期格式错误"}
        
        delivery_records = query_bitable_records(DELIVERY_TABLE_ID)
        
        debug_info = []
        confirmed_count = 0
        customers_to_update = {}
        
        for record in delivery_records:
            fields = record.get('fields', {})
            record_id = record.get('record_id')
            
            record_date = parse_date(fields.get('配送日期'))
            if record_date != selected_date:
                continue
            
            customer_name = extract_text(fields.get('客户姓名'))
            if not customer_name:
                continue
            
            confirm_status = fields.get('确认状态', '')
            if isinstance(confirm_status, dict):
                status_text = confirm_status.get('text', '')
            else:
                status_text = extract_text(confirm_status)
            
            if status_text == '已确认':
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
                
                if customer_name not in customers_to_update:
                    customers_to_update[customer_name] = 0
                customers_to_update[customer_name] += delivery_qty
            else:
                debug_info.append(f"❌ {customer_name}: 确认失败 - {error_msg}")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = extract_text(fields.get('客户姓名'))
            
            if customer_name not in customers_to_update:
                continue
            
            calendar_str = fields.get('吃餐日历', '{}')
            try:
                calendar = json.loads(calendar_str) if isinstance(calendar_str, str) else calendar_str
            except:
                calendar = {}
            
            date_str = selected_date.strftime("%Y-%m-%d")
            calendar[date_str] = {
                "qty": customers_to_update[customer_name],
                "status": "delivered",
                "source": "delivery"
            }
            
            update_bitable_record(CUSTOMER_TABLE_ID, record_id, {
                "吃餐日历": json.dumps(calendar, ensure_ascii=False)
            })
            
            eaten_count = calculate_eaten_meals_from_calendar(calendar)
            update_bitable_record(CUSTOMER_TABLE_ID, record_id, {"已吃餐数": eaten_count})
        
        return {
            "success": True,
            "message": f"已确认 {confirmed_count} 条配送记录",
            "data": {"debug_info": debug_info, "confirmed_count": confirmed_count}
        }
    except Exception as e:
        return {"success": False, "message": f"确认失败: {str(e)}"}

async def update_gantt_status():
    """更新甘特图状态"""
    try:
        logger.info("=" * 60)
        logger.info("开始更新甘特图状态...")
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        
        debug_info = []
        updated_count = 0
        
        today = date.today()
        
        for customer in customers:
            fields = customer.get('fields', {})
            record_id = customer.get('record_id')
            customer_name = extract_text(fields.get('客户姓名'))
            
            if not customer_name:
                continue
            
            start_date = parse_date(fields.get('起送日期'))
            total_meals = fields.get('总餐数', 0)
            eaten_count = fields.get('已吃餐数', 0)
            
            if not start_date:
                continue
            
            if eaten_count >= total_meals:
                status = "已结束"
            elif today < start_date:
                status = "未开始"
            else:
                status = "配送中"
            
            pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
            pause_dates_str = [str(d) for d in pause_dates]
            
            update_success, error_msg = update_bitable_record(
                CUSTOMER_TABLE_ID, record_id,
                {
                    "配送状态": status,
                    "暂停日期": ", ".join(pause_dates_str) if pause_dates_str else ""
                }
            )
            
            if update_success:
                debug_info.append(f"✅ {customer_name}: {status}")
                updated_count += 1
            else:
                debug_info.append(f"❌ {customer_name}: 更新失败 - {error_msg}")
        
        return {
            "success": True,
            "message": f"已更新 {updated_count} 个客户的甘特图状态",
            "data": {"debug_info": debug_info, "updated_count": updated_count}
        }
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}

async def get_customers_list():
    """获取客户列表"""
    try:
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        if not customers:
            return {"success": False, "message": "查询客户数据失败"}
        
        customer_list = []
        for customer in customers:
            fields = customer.get('fields', {})
            customer_name = extract_text(fields.get('客户姓名'))
            if customer_name:
                customer_list.append({
                    "name": customer_name,
                    "start_date": str(parse_date(fields.get('起送日期'))) if parse_date(fields.get('起送日期')) else None,
                    "total_meals": fields.get('总餐数', 0),
                    "eaten_count": fields.get('已吃餐数', 0)
                })
        
        return {
            "success": True,
            "message": f"获取到 {len(customer_list)} 个客户",
            "data": {"customers": customer_list}
        }
    except Exception as e:
        return {"success": False, "message": f"获取失败: {str(e)}"}

async def get_customer_calendar_data(customer_name: str):
    """获取单个客户的日历数据"""
    try:
        if not customer_name:
            return {"success": False, "message": "请提供客户姓名"}
        
        customers = query_bitable_records(CUSTOMER_TABLE_ID)
        pause_records_all = query_bitable_records(PAUSE_TABLE_ID)
        holiday_dates = get_holiday_dates()
        
        customer_record = None
        for c in customers:
            if extract_text(c.get('fields', {}).get('客户姓名')) == customer_name:
                customer_record = c
                break
        
        if not customer_record:
            return {"success": False, "message": f"找不到客户: {customer_name}"}
        
        fields = customer_record.get('fields', {})
        
        calendar_str = fields.get('吃餐日历', '{}')
        try:
            calendar = json.loads(calendar_str) if isinstance(calendar_str, str) else calendar_str
        except:
            calendar = {}
        
        pause_dates = get_customer_pause_dates(customer_name, pause_records_all)
        pause_dates_str = [str(d) for d in pause_dates]
        
        holiday_dates_str = [str(d) for d in holiday_dates]
        
        return {
            "success": True,
            "message": "获取成功",
            "data": {
                "customer_name": customer_name,
                "start_date": str(parse_date(fields.get('起送日期'))) if parse_date(fields.get('起送日期')) else None,
                "total_meals": fields.get('总餐数', 0),
                "eaten_count": fields.get('已吃餐数', 0),
                "calendar": calendar,
                "pause_dates": pause_dates_str,
                "holiday_dates": holiday_dates_str
            }
        }
    except Exception as e:
        return {"success": False, "message": f"获取失败: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
