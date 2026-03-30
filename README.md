# 📦 配送管理系统 - Railway云端版

## 🎯 方案说明

### 为什么选择Railway方案？

**您说得对！纯前端方案有并发问题：**
```
场景：A和B同时操作
10:00 - A读取：客户张三，已吃餐数=5
10:00 - B读取：客户张三，已吃餐数=5
10:01 - A修改：已吃餐数=6，保存
10:01 - B修改：已吃餐数=6，保存  ← ❌ 覆盖了A的修改！
```

**Railway方案的优势：**
- ✅ 后端排队处理请求（一次只处理一个人）
- ✅ 事务处理（保证数据一致性）
- ✅ 并发控制（防止数据冲突）
- ✅ 操作日志（记录谁做了什么）

---

## 📊 方案对比

| 项目 | 纯前端 | Railway方案 ✅ |
|------|--------|--------------|
| **并发安全** | ❌ 有风险 | ✅ 安全 |
| **费用** | ✅ 永远免费 | ✅ 免费额度够用 |
| **部署难度** | ✅ 简单 | ⚠️ 稍复杂 |
| **维护** | ✅ 无需维护 | ⚠️ 需要监控 |
| **适合人数** | 1-2人 | **3-10人** ✅ |
| **数据安全** | ⚠️ 可能冲突 | ✅ 有保障 |

---

## 📦 文件清单

### 核心文件

| 文件 | 说明 |
|------|------|
| `backend/src/main.py` | 后端主程序（FastAPI） |
| `backend/requirements.txt` | 依赖包（已简化） |
| `backend/runtime.txt` | Python版本 |
| `backend/Procfile` | 启动命令 |
| `backend/railway.json` | Railway配置 |
| `backend/config/users.json` | 用户配置 |
| `frontend/index_railway.html` | 前端页面（调用后端API） |

### 文档文件

| 文件 | 说明 |
|------|------|
| **Railway完整部署指南.md** | 详细部署步骤 ⭐ |
| **部署检查清单.md** | 逐项检查清单 ⭐ |
| 飞书配置详细教程.md | 获取飞书配置信息 |

---

## 🚀 快速开始

### 第一步：查看部署指南

👉 打开 **Railway完整部署指南.md**

### 第二步：按清单检查

👉 打开 **部署检查清单.md**

### 第三步：开始部署

按照文档步骤操作即可！

---

## 📝 部署流程概览

### 1️⃣ 后端部署到Railway

```
1. 登录 Railway（用GitHub账号）
2. 创建项目 → 从GitHub仓库部署
3. 设置根目录为 backend
4. 添加环境变量（飞书配置）
5. 部署
6. 生成域名
7. 测试：访问 https://xxx.railway.app/health
```

### 2️⃣ 前端部署到GitHub Pages

```
1. 将 index_railway.html 重命名为 index.html
2. 提交到GitHub
3. 开启 GitHub Pages
4. 访问前端地址
```

### 3️⃣ 配置前端

```
1. 打开前端页面
2. 在底部输入Railway后端地址
3. 保存配置
4. 测试连接
```

### 4️⃣ 开始使用

```
1. 登录（admin / admin123）
2. 测试各项功能
3. 分享给团队成员
```

---

## 🔧 后端API端点

### 健康检查
```
GET /health
返回：{"status": "ok", "message": "Service is running"}
```

### 用户登录
```
POST /api/login
参数：{"username": "admin", "password": "admin123"}
返回：{"success": true, "token": "...", "user": {...}}
```

### 执行工作流
```
POST /run
需要Header：Authorization: Bearer {token}
参数：{
  "workflow_type": "recalculate_eaten" | "confirm" | "recalculate_end_date" | "generate" | "update_gantt",
  "delivery_date": "2024-01-01"  // 可选
}
```

---

## 👥 用户管理

### 默认账号
```
管理员：
- 用户名：admin
- 密码：admin123

配送员：
- 用户名：user1
- 密码：user123

（还有user2, user3）
```

### 添加新用户
修改 `backend/config/users.json`：
```json
{
  "users": [
    {"username": "admin", "password": "admin123", "role": "管理员"},
    {"username": "新用户", "password": "新密码", "role": "普通用户"}
  ]
}
```

---

## 🔐 环境变量配置

在Railway的Variables标签添加：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| FEISHU_APP_ID | 飞书应用ID | cli_xxxxxxxxxxxx |
| FEISHU_APP_SECRET | 飞书应用密钥 | xxxxxxxxxxxxxxxx |
| BITABLE_APP_TOKEN | 多维表格Token | bascnXXXXXXXXXXXX |
| CUSTOMER_TABLE_ID | 客户表ID | tblXXXXXXXXXXXX |
| DELIVERY_TABLE_ID | 配送表ID | tblXXXXXXXXXXXX |
| HOLIDAY_TABLE_ID | 假期表ID | tblXXXXXXXXXXXX |
| PAUSE_TABLE_ID | 暂停表ID | tblXXXXXXXXXXXX |
| COZE_WORKSPACE_PATH | 工作目录 | /app |

---

## 💰 Railway费用说明

### 免费额度
- 每月 $5 免费额度
- 轻量级应用每月约 $2-3
- **免费额度基本够用**

### 监控
- 在Railway可以看到实时费用
- 超过额度会提醒

---

## ❓ 常见问题

### Q1: Railway部署失败？
**A:** 确保使用简化后的requirements.txt（已修复）

### Q2: 前端无法连接后端？
**A:** 
1. 测试后端健康检查
2. 确认API地址正确
3. 不要加末尾斜杠

### Q3: 登录失败？
**A:** 
1. 确认后端正常运行
2. 检查用户名密码
3. 查看Railway日志

### Q4: 多人操作会乱吗？
**A:** 不会！后端会排队处理请求，保证数据一致性。

---

## 📞 技术支持

1. 查看 **Railway完整部署指南.md**
2. 查看 **部署检查清单.md**
3. 查看Railway日志定位错误
4. 检查环境变量配置

---

## 🎉 部署成功后

### 您将拥有：

✅ **前端**：GitHub Pages（永远免费）
✅ **后端**：Railway（免费额度够用）
✅ **数据**：飞书多维表格
✅ **团队协作**：支持3-10人使用
✅ **数据安全**：无并发问题

### 访问地址：
```
前端：https://用户名.github.io/仓库名/
后端：https://xxx.railway.app
健康检查：https://xxx.railway.app/health
```

---

**祝您部署顺利！🚀**