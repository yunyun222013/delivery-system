# 🚀 快速开始指南

## 📦 这个包里有什么？

```
github_upload_package/
├── README.md                    ← 总体说明（先看这个）
├── QUICK_START.md               ← 快速开始（你正在看）
├── .gitignore                   ← Git忽略文件
│
├── backend/                     ← 后端代码（部署到Railway）
│   ├── src/
│   │   └── main.py             ← FastAPI主程序
│   ├── config/
│   │   └── users.json          ← 用户账号配置
│   ├── requirements.txt         ← Python依赖包
│   ├── runtime.txt             ← Python版本
│   ├── Procfile                ← 启动命令
│   ├── railway.json            ← Railway配置
│   └── .env.example            ← 环境变量示例
│
├── frontend/                    ← 前端代码（部署到GitHub Pages）
│   └── index.html              ← 前端页面
│
└── docs/                        ← 文档
    ├── Railway完整部署指南.md   ← 详细部署步骤
    ├── 部署检查清单.md          ← 逐项检查
    └── 飞书配置详细教程.md      ← 获取飞书配置
```

---

## ⚡ 5分钟快速部署

### 第一步：上传到GitHub（2分钟）

#### 方法一：创建新仓库
1. 登录 GitHub
2. 创建新仓库：`delivery-system`
3. 上传 **整个** `github_upload_package` 文件夹的内容
4. 确保 backend/ 和 frontend/ 目录都上传了

#### 方法二：直接拖拽上传
1. 在GitHub创建空仓库
2. 把 `github_upload_package` 文件夹里的所有内容拖进去
3. 提交

---

### 第二步：部署后端到Railway（2分钟）

#### 2.1 登录Railway
1. 访问：https://railway.app
2. 点击 **Start a New Project**
3. 选择 **Deploy from GitHub repo**
4. 选择刚才创建的仓库

#### 2.2 配置项目
1. 设置 Root Directory：`backend`
2. 添加环境变量（在 Variables 标签）：

```
FEISHU_APP_ID=你的App_ID
FEISHU_APP_SECRET=你的App_Secret
BITABLE_APP_TOKEN=你的表格Token
CUSTOMER_TABLE_ID=客户表ID
DELIVERY_TABLE_ID=配送表ID
HOLIDAY_TABLE_ID=假期表ID
PAUSE_TABLE_ID=暂停表ID
COZE_WORKSPACE_PATH=/app
```

#### 2.3 部署
1. 点击 **Deploy**
2. 等待部署完成（约1-2分钟）
3. 在 Settings → Domains 生成域名
4. 复制域名（例如：https://xxx.railway.app）

#### 2.4 测试
在浏览器访问：
```
https://你的域名/health
```
应该看到：
```json
{"status":"ok","message":"Service is running"}
```

---

### 第三步：部署前端到GitHub Pages（1分钟）

#### 3.1 开启Pages
1. 在GitHub仓库，点击 **Settings**
2. 左侧菜单找到 **Pages**
3. 配置：
   - Source: Deploy from a branch
   - Branch: main
   - Folder: / (root)
4. 点击 **Save**

#### 3.2 等待部署
- 等待1-2分钟
- 页面会显示访问地址

#### 3.3 访问测试
```
https://你的用户名.github.io/delivery-system/
```

---

### 第四步：配置前端（30秒）

#### 4.1 打开前端页面
访问GitHub Pages地址

#### 4.2 配置API地址
1. 在登录页面底部找到 **"后端API地址配置"**
2. 输入Railway后端地址：`https://xxx.railway.app`
3. 点击 **保存API地址**
4. 看到 "后端连接成功！"

#### 4.3 登录测试
```
用户名：admin
密码：admin123
```

---

## ✅ 完成！

### 您现在可以：

1. ✅ 访问系统
2. ✅ 登录使用
3. ✅ 分享给团队成员

### 默认账号：
```
管理员：admin / admin123
配送员：user1 / user123
配送员：user2 / user123
配送员：user3 / user123
```

---

## 📚 详细文档

如果遇到问题，查看：

1. **docs/Railway完整部署指南.md** - 详细步骤
2. **docs/部署检查清单.md** - 逐项检查
3. **docs/飞书配置详细教程.md** - 获取飞书配置

---

## 🆘 常见问题

### Q: Railway部署失败？
**A:** 确保使用了正确的 requirements.txt（这个包里已经是正确的）

### Q: 前端无法连接后端？
**A:** 
1. 测试后端：访问 `https://后端地址/health`
2. 确认地址正确，不要加末尾斜杠

### Q: 登录失败？
**A:** 
1. 确认后端正常运行
2. 检查用户名密码：admin / admin123

---

## 🎯 下一步

### 团队成员使用：

1. 把前端地址发给他们
2. 提供登录账号
3. 告知需要配置后端API地址（一次性）

---

**祝您部署顺利！🚀**