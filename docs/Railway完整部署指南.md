# 🚂 Railway完整部署指南

## 📋 目录
- [Railway简介](#railway简介)
- [部署架构](#部署架构)
- [准备工作](#准备工作)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [完整测试](#完整测试)
- [团队使用](#团队使用)
- [常见问题](#常见问题)

---

## 🎯 Railway简介

### 什么是Railway？
Railway是一个现代化的云平台，可以轻松部署后端服务。

### Railway免费额度
- **每月$5免费额度**
- **轻量级应用每月约消耗$2-3**
- **免费额度基本够用**
- **超过后需要付费**

### 为什么需要后端？

**纯前端方案的问题：**
```
时间线：
10:00 - A读取数据：客户张三，已吃餐数=5
10:00 - B读取数据：客户张三，已吃餐数=5
10:01 - A修改：已吃餐数=6，保存
10:01 - B修改：已吃餐数=6，保存  ← ❌ 覆盖了A的修改！
```

**有后端的好处：**
```
后端服务器：
✅ 排队处理请求（一次只处理一个人）
✅ 事务处理（保证数据一致性）
✅ 并发控制（防止数据冲突）
✅ 操作日志（记录谁做了什么）
```

---

## 🏗️ 部署架构

### 系统架构图：

```
┌─────────────────┐
│  团队成员       │
│  (手机/电脑)    │
└────────┬────────┘
         │
         │ 访问
         ↓
┌─────────────────┐
│  GitHub Pages   │ ← 前端（免费）
│  (HTML/JS)      │
└────────┬────────┘
         │
         │ API调用
         ↓
┌─────────────────┐
│  Railway        │ ← 后端（免费额度）
│  (Python/FastAPI)│
└────────┬────────┘
         │
         │ API调用
         ↓
┌─────────────────┐
│  飞书多维表格    │ ← 数据存储
└─────────────────┘
```

### 优势：
- ✅ **前端免费**（GitHub Pages）
- ✅ **后端免费额度**（Railway $5/月）
- ✅ **数据在飞书**（不会丢失）
- ✅ **支持多人协作**（无并发问题）

---

## 📦 准备工作

### 需要准备的东西：

#### 1. GitHub账号
- 如果没有：https://github.com 注册
- 完全免费

#### 2. Railway账号
- 访问：https://railway.app
- 可以用GitHub账号登录
- 无需信用卡

#### 3. 飞书配置
- App ID 和 App Secret
- 多维表格 Token
- 各个表的 ID

---

## 🔧 后端部署到Railway

### 第一步：准备后端代码

#### 1.1 确认文件结构
```
backend/
├── src/
│   └── main.py          ← 后端主程序
├── config/
│   └── users.json       ← 用户配置
├── requirements.txt     ← 依赖包（已简化）
├── runtime.txt          ← Python版本
├── Procfile             ← 启动命令
└── railway.json         ← Railway配置
```

#### 1.2 检查关键文件

**requirements.txt内容：**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
python-multipart==0.0.6
python-dotenv==1.0.0
```

**runtime.txt内容：**
```
3.11.4
```

**Procfile内容：**
```
web: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

---

### 第二步：创建Railway项目

#### 2.1 登录Railway
1. 访问：https://railway.app
2. 点击 **Start a New Project**
3. 选择 **Deploy from GitHub repo**

#### 2.2 授权GitHub
1. 点击 **Authorize Railway**
2. 选择您的GitHub账号
3. 允许Railway访问您的仓库

#### 2.3 选择仓库
1. 找到您的配送管理系统仓库
2. 点击选择

---

### 第三步：配置Railway

#### 3.1 设置根目录
Railway会自动检测到backend目录，但需要确认：

1. 在项目设置中，找到 **Root Directory**
2. 设置为：`backend`

#### 3.2 添加环境变量

在Railway项目中，点击 **Variables** 标签，添加以下变量：

```bash
# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BITABLE_APP_TOKEN=bascnXXXXXXXXXXXXXXXX
CUSTOMER_TABLE_ID=tblXXXXXXXXXXXX
DELIVERY_TABLE_ID=tblXXXXXXXXXXXX
HOLIDAY_TABLE_ID=tblXXXXXXXXXXXX
PAUSE_TABLE_ID=tblXXXXXXXXXXXX

# 工作目录
COZE_WORKSPACE_PATH=/app
```

**如何获取这些配置？**
- 查看：`飞书配置详细教程.md`

---

### 第四步：部署

#### 4.1 开始部署
1. 配置好环境变量后
2. Railway会自动开始部署
3. 或者点击 **Deploy** 按钮

#### 4.2 查看日志
1. 点击部署任务
2. 查看 **Build Logs**
3. 等待部署完成

#### 4.3 部署成功标志
看到以下日志表示成功：
```
✅ Build succeeded
✅ Deployment succeeded
✅ Service is running
```

---

### 第五步：获取API地址

#### 5.1 生成域名
1. 在Railway项目中
2. 点击 **Settings** 标签
3. 找到 **Domains**
4. 点击 **Generate Domain**

#### 5.2 获取地址
Railway会生成一个域名：
```
https://xxx-yyy-zzz.railway.app
```

**这就是您的后端API地址！**

#### 5.3 测试API
在浏览器访问：
```
https://您的域名.railway.app/health
```

应该看到：
```json
{"status": "ok", "message": "Service is running"}
```

---

## 🌐 前端部署到GitHub Pages

### 第一步：准备前端文件

#### 1.1 使用Railway版前端
文件：`frontend/index_railway.html`

#### 1.2 重命名文件
将 `index_railway.html` 重命名为 `index.html`

---

### 第二步：上传到GitHub

#### 2.1 提交前端文件
```bash
git add frontend/index.html
git commit -m "添加Railway版前端"
git push
```

#### 2.2 或者直接在GitHub网页上传
1. 进入GitHub仓库
2. 进入 `frontend` 目录
3. 上传 `index.html` 文件

---

### 第三步：开启GitHub Pages

#### 3.1 进入设置
1. 在GitHub仓库页面
2. 点击 **Settings**
3. 左侧菜单找到 **Pages**

#### 3.2 配置Pages
```
Source: Deploy from a branch
Branch: main
Folder: /frontend
```

#### 3.3 保存
- 点击 **Save**
- 等待1-2分钟

#### 3.4 获取访问地址
```
https://您的用户名.github.io/仓库名/
```

---

### 第四步：配置前端

#### 4.1 打开前端页面
访问您的GitHub Pages地址

#### 4.2 配置API地址
1. 在登录页面底部
2. 找到 **后端API地址配置**
3. 填入Railway后端地址：
```
https://xxx.railway.app
```
4. 点击 **保存API地址**

#### 4.3 测试连接
- 点击保存后，会自动测试连接
- 看到 **"后端连接成功！"** 表示配置正确

---

## ✅ 完整测试

### 第一步：测试登录

#### 1.1 访问前端
打开GitHub Pages地址

#### 1.2 登录系统
```
用户名：admin
密码：admin123
```

#### 1.3 检查登录状态
- 登录成功后会跳转到主页面
- 右上角显示用户信息

---

### 第二步：测试功能

#### 2.1 测试计算已吃餐数
1. 点击 **"计算初始已吃餐数"**
2. 等待执行完成
3. 查看结果

#### 2.2 测试生成配送记录
1. 选择一个日期
2. 点击 **"生成配送记录"**
3. 确认操作
4. 查看结果

#### 2.3 测试批量确认
1. 选择一个日期
2. 点击 **"批量确认送餐"**
3. 确认操作
4. 查看结果

---

### 第三步：多人测试

#### 3.1 模拟多人操作
1. 打开两个浏览器窗口
2. 分别登录不同账号
3. 同时操作同一个功能
4. 检查是否有数据冲突

#### 3.2 预期结果
- ✅ 后端会排队处理请求
- ✅ 不会出现数据覆盖
- ✅ 数据保持一致

---

## 👥 团队使用

### 给团队成员使用

#### 第一步：分享访问地址
```
前端地址：https://xxx.github.io/仓库/
```

#### 第二步：提供登录账号
```
管理员：
- 用户名：admin
- 密码：admin123

配送员：
- 用户名：user1
- 密码：user123

（还有user2, user3）
```

#### 第三步：团队成员配置
1. 打开前端地址
2. 在底部配置后端API地址
3. 保存配置
4. 登录使用

**注意：每个成员需要自己配置一次API地址**

---

## 🔧 高级配置

### 自定义域名（可选）

#### Railway自定义域名
1. 在Railway项目设置中
2. 点击 **Custom Domain**
3. 输入您的域名
4. 按提示配置DNS

#### GitHub Pages自定义域名
1. 在GitHub Pages设置中
2. 输入自定义域名
3. 配置DNS CNAME记录

---

### 监控和日志

#### 查看Railway日志
1. 进入Railway项目
2. 点击 **Deployments**
3. 查看实时日志

#### 监控资源使用
1. 在Railway项目概览页面
2. 可以看到CPU、内存使用情况
3. 以及费用预估

---

## ❓ 常见问题

### Q1: Railway部署失败？

#### 错误：error creating build plan with railpack

**原因：**
- requirements.txt包含无法安装的包
- Python版本不兼容

**解决：**
✅ 已修复！确保使用简化后的requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
python-multipart==0.0.6
python-dotenv==1.0.0
```

---

### Q2: 前端无法连接后端？

#### 错误：无法连接后端

**检查：**
1. ✅ 后端是否部署成功？
2. ✅ API地址是否正确？
3. ✅ 是否有 `/health` 端点？

**测试：**
在浏览器访问：
```
https://您的后端地址.railway.app/health
```

应该看到：
```json
{"status": "ok", "message": "Service is running"}
```

---

### Q3: 登录失败？

#### 错误：用户名或密码错误

**检查：**
1. ✅ 检查 `backend/config/users.json` 文件
2. ✅ 确认用户名密码正确

**默认账号：**
```
admin / admin123
user1 / user123
user2 / user123
user3 / user123
```

---

### Q4: 多人操作数据会乱吗？

#### 答案：不会！

**原因：**
- ✅ 后端会排队处理请求
- ✅ FastAPI支持并发控制
- ✅ 飞书API有乐观锁机制

**安全：**
- 可以放心多人同时使用
- 后端会保证数据一致性

---

### Q5: Railway费用问题？

#### 免费额度：
- 每月$5免费额度
- 轻量级应用每月约$2-3
- 基本够用

#### 监控：
- 在Railway可以看到实时费用
- 超过额度会提醒

#### 如果超出：
- 可以考虑升级付费
- 或者优化代码减少资源消耗

---

### Q6: 如何添加新用户？

#### 修改用户配置文件：
`backend/config/users.json`

```json
{
  "users": [
    {"username": "admin", "password": "admin123", "role": "管理员"},
    {"username": "user1", "password": "user123", "role": "普通用户"},
    {"username": "新用户", "password": "新密码", "role": "普通用户"}
  ],
  "session_expire_hours": 24
}
```

#### 修改后：
1. 提交到GitHub
2. Railway会自动重新部署
3. 新用户即可使用

---

### Q7: 如何查看操作日志？

#### 方法一：Railway日志
1. 进入Railway项目
2. 点击部署任务
3. 查看实时日志

#### 方法二：后端日志
后端会记录每个操作：
```
INFO: User admin logged in
INFO: Workflow recalculate_eaten started by admin
INFO: Workflow recalculate_eaten completed
```

---

## 📊 对比总结

### 纯前端 vs Railway方案

| 项目 | 纯前端 | Railway方案 |
|------|--------|------------|
| **并发安全** | ❌ 有风险 | ✅ 安全 |
| **费用** | ✅ 永远免费 | ✅ 免费额度够用 |
| **部署难度** | ✅ 简单 | ⚠️ 稍复杂 |
| **维护** | ✅ 无需维护 | ⚠️ 需要监控 |
| **适合人数** | 1-2人 | 3-10人 |
| **数据安全** | ⚠️ 可能冲突 | ✅ 有保障 |

---

## 🎯 推荐选择

### 如果您的团队：
- ✅ **3-4人使用** → **Railway方案**（推荐）
- ✅ **经常多人同时操作** → **Railway方案**
- ✅ **需要数据安全** → **Railway方案**

### 如果您：
- ✅ **只有1-2人使用** → 纯前端方案也可以
- ✅ **不经常同时操作** → 纯前端方案也可以
- ✅ **想更简单** → 纯前端方案也可以

---

## 📞 技术支持

### 遇到问题？

1. 查看本文档的常见问题部分
2. 查看Railway日志定位错误
3. 检查环境变量配置
4. 测试API端点是否正常

---

## 🎉 部署成功后

### 您将拥有：

✅ **前端**：GitHub Pages（永远免费）
✅ **后端**：Railway（免费额度够用）
✅ **数据**：飞书多维表格
✅ **团队协作**：支持多人使用
✅ **数据安全**：无并发问题

---

**祝您部署顺利！🚀**