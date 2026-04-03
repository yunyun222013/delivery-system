<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍱 配送管理系统 V3.3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        
        /* 登录页面 */
        .login-body { 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 20px; 
        }
        .login-container { 
            background: white; 
            border-radius: 20px; 
            padding: 40px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
            max-width: 420px; 
            width: 100%; 
        }
        .login-header { text-align: center; margin-bottom: 30px; }
        .login-header h1 { font-size: 2em; color: #667eea; margin-bottom: 10px; }
        .login-header p { color: #666; font-size: 0.95em; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .form-group input { 
            width: 100%; 
            padding: 12px 15px; 
            border: 2px solid #e0e0e0; 
            border-radius: 8px; 
            font-size: 1em; 
        }
        .form-group input:focus { 
            outline: none; 
            border-color: #667eea; 
        }
        .login-btn { 
            width: 100%; 
            padding: 14px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            border-radius: 8px; 
            font-size: 1.1em; 
            font-weight: 600; 
            cursor: pointer; 
            transition: transform 0.2s; 
        }
        .login-btn:hover { transform: translateY(-2px); }
        .login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .config-section { 
            margin-top: 20px; 
            padding-top: 20px; 
            border-top: 1px solid #eee; 
        }
        .config-section h3 { 
            font-size: 0.9em; 
            color: #999; 
            margin-bottom: 10px; 
        }
        .config-section input { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 6px; 
            margin-bottom: 10px; 
        }
        .config-btn { 
            width: 100%; 
            padding: 10px; 
            background: #f0f0f0; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
        }
        .config-btn:hover { background: #e0e0e0; }
        
        /* 主页面 */
        .user-info {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .user-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        .logout-btn {
            margin-left: auto;
            padding: 8px 16px;
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .logout-btn:hover { background: #dc2626; }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 80px 20px 20px; 
        }
        header { 
            text-align: center; 
            margin-bottom: 30px; 
            color: white; 
        }
        header h1 { 
            font-size: 2.2em; 
            margin-bottom: 8px; 
            text-shadow: 0 2px 4px rgba(0,0,0,0.2); 
        }
        header p { 
            font-size: 1.1em; 
            opacity: 0.9; 
        }
        
        .section-divider {
            text-align: center;
            margin: 25px 0;
            position: relative;
        }
        .section-divider::before {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            top: 50%;
            height: 1px;
            background: rgba(255,255,255,0.3);
        }
        .section-divider span {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 8px 20px;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            position: relative;
            z-index: 1;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 16px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card p {
            color: #666;
            margin-bottom: 16px;
            line-height: 1.6;
        }
        .step-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 0.9em;
            font-weight: 600;
        }
        
        .input-group {
            margin-bottom: 16px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .input-group input, .input-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }
        .input-group input:focus, .input-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .tip-box {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        .tip-box span {
            font-size: 1.2em;
        }
        .tip-box.info {
            background: #e0f2fe;
            color: #0369a1;
        }
        .tip-box.warning {
            background: #fef3c7;
            color: #92400e;
        }
        .tip-box.danger {
            background: #fee2e2;
            color: #991b1b;
        }
        .tip-box.success {
            background: #dcfce7;
            color: #166534;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-primary:hover { background: #2563eb; }
        .btn-success { background: #22c55e; color: white; }
        .btn-success:hover { background: #16a34a; }
        .btn-warning { background: #f59e0b; color: white; }
        .btn-warning:hover { background: #d97706; }
        .btn-info { background: #8b5cf6; color: white; }
        .btn-info:hover { background: #7c3aed; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-danger:hover { background: #dc2626; }
        
        .result {
            margin-top: 16px;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.9em;
            display: none;
        }
        .result.success {
            display: block;
            background: #dcfce7;
            color: #166534;
        }
        .result.error {
            display: block;
            background: #fee2e2;
            color: #991b1b;
        }
        .result.loading {
            display: block;
            background: #f0f9ff;
            color: #0369a1;
        }
        
        /* 日历视图样式 */
        .calendar-container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-top: 20px;
        }
        .calendar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .calendar-header h3 {
            font-size: 1.5em;
            color: #333;
        }
        .calendar-nav {
            display: flex;
            gap: 10px;
        }
        .calendar-nav button {
            padding: 8px 16px;
            background: #f0f0f0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        .calendar-nav button:hover { background: #e0e0e0; }
        
        .calendar-info {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8fafc;
            border-radius: 10px;
        }
        .calendar-info-item {
            text-align: center;
        }
        .calendar-info-item .label {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }
        .calendar-info-item .value {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
        }
        
        .calendar-legend {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85em;
            color: #666;
        }
        .legend-dot {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75em;
            font-weight: 600;
        }
        .legend-dot.start { background: #22c55e; color: white; }
        .legend-dot.pause { background: #f59e0b; color: white; }
        .legend-dot.holiday { background: #ef4444; color: white; }
        .legend-dot.delivered { background: #3b82f6; color: white; }
        .legend-dot.pending { background: #9ca3af; color: white; }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 6px;
        }
        .calendar-day-header {
            text-align: center;
            padding: 10px;
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
        }
        .calendar-day {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 6px;
            min-height: 65px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
        }
        .calendar-day:hover { 
            background: #f0f9ff; 
            border-color: #3b82f6;
        }
        .calendar-day.empty {
            background: #f9fafb;
            cursor: default;
        }
        .calendar-day.empty:hover {
            background: #f9fafb;
            border-color: #e0e0e0;
        }
        .calendar-day.today {
            border-color: #3b82f6;
            border-width: 2px;
            box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
        }
        .calendar-day .day-number {
            font-weight: 600;
            color: #333;
            font-size: 0.9em;
            margin-bottom: 4px;
        }
        .calendar-day .day-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            text-align: center;
            margin-top: auto;
        }
        .calendar-day .day-badge.start { background: #22c55e; color: white; }
        .calendar-day .day-badge.pause { background: #f59e0b; color: white; }
        .calendar-day .day-badge.holiday { background: #ef4444; color: white; }
        .calendar-day .day-badge.delivered { background: #3b82f6; color: white; }
        .calendar-day .day-badge.pending { background: #9ca3af; color: white; }
        
        .calendar-edit {
            margin-top: 20px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 10px;
            display: none;
        }
        .calendar-edit.active { display: block; }
        .calendar-edit h4 {
            margin-bottom: 15px;
            color: #333;
        }
        .calendar-edit-row {
            display: flex;
            gap: 15px;
            align-items: flex-end;
            flex-wrap: wrap;
        }
        .calendar-edit-row .input-group {
            margin-bottom: 0;
            flex: 1;
            min-width: 150px;
        }
        
        /* 甘特图样式 */
        .gantt-container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-top: 20px;
            overflow-x: auto;
        }
        .gantt-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .gantt-header h3 {
            font-size: 1.3em;
            color: #333;
        }
        
        .gantt-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }
        .gantt-table th, .gantt-table td {
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }
        .gantt-table th {
            background: #f8fafc;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
        }
        .gantt-table th.customer-col {
            position: sticky;
            left: 0;
            z-index: 2;
            background: #f8fafc;
            min-width: 100px;
        }
        .gantt-table td.customer-col {
            position: sticky;
            left: 0;
            z-index: 1;
            background: white;
            text-align: left;
            font-weight: 600;
            min-width: 100px;
        }
        .gantt-table th.info-col {
            min-width: 60px;
        }
        .gantt-table td.info-col {
            font-weight: 600;
        }
        .gantt-table td.today-col {
            background: #eff6ff;
            border-left: 2px solid #3b82f6;
            border-right: 2px solid #3b82f6;
        }
        
        .gantt-day {
            width: 28px;
            height: 28px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.85em;
        }
        .gantt-day.start { background: #22c55e; color: white; }
        .gantt-day.pause { background: #f59e0b; color: white; }
        .gantt-day.holiday { background: #ef4444; color: white; }
        .gantt-day.delivered { background: #3b82f6; color: white; }
        .gantt-day.pending { background: #9ca3af; color: white; }
        .gantt-day.empty { background: #f3f4f6; color: #9ca3af; }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .status-badge.active { background: #dcfce7; color: #166534; }
        .status-badge.pending { background: #fef3c7; color: #92400e; }
        .status-badge.ended { background: #fee2e2; color: #991b1b; }
        
        /* 流程卡片 */
        .workflow-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .workflow-card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        .flow-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .flow-step {
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        .flow-step-number {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .flow-step h3 {
            color: #333;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .flow-step p {
            color: #666;
            font-size: 0.95em;
            line-height: 1.5;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.8);
        }
        .footer p {
            margin-bottom: 8px;
        }
        
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .calendar-info { grid-template-columns: repeat(2, 1fr); }
            .calendar-edit-row { flex-direction: column; }
            .calendar-edit-row .input-group { width: 100%; }
        }
    </style>
</head>
<body class="login-body">
    <!-- 登录页面 -->
    <div class="login-container" id="loginPage">
        <div class="login-header">
            <h1>🍱 配送管理系统</h1>
            <p>V3.3 修复版</p>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" placeholder="请输入用户名" required autocomplete="username">
            </div>
            
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" placeholder="请输入密码" required autocomplete="current-password">
            </div>
            
            <button type="submit" class="login-btn" id="loginBtn">登录</button>
        </form>
        
        <div class="config-section" id="configSection">
            <h3>⚙️ API配置</h3>
            <input type="text" id="apiUrlInput" placeholder="例如：https://your-api.render.com">
            <button class="config-btn" onclick="saveApiUrl()">保存API地址</button>
            <p style="font-size: 0.85em; color: #999; margin-top: 10px;">当前地址: <span id="currentApiUrl"></span></p>
        </div>
    </div>
    
    <!-- 主页面 -->
    <div id="mainPage" style="display: none;">
        <div class="user-info" id="userInfo">
            <span class="status-indicator online"></span>
            <div class="user-avatar" id="userAvatar">A</div>
            <div>
                <div style="font-weight: 600;" id="userName">管理员</div>
                <div style="font-size: 0.85em; color: #666;" id="userRole">管理员</div>
            </div>
            <button class="logout-btn" onclick="logout()">登出</button>
        </div>

        <div class="container">
            <header>
                <h1>🍱 配送管理系统 V3.3</h1>
                <p>修复版 · 日期计算准确</p>
            </header>
            
            <div class="section-divider">
                <span>👇 功能操作区</span>
            </div>
            
            <div class="grid">
                <!-- 一键同步 -->
                <div class="card">
                    <h2><span class="step-badge">🔄</span> 一键同步数据</h2>
                    <p>同步暂停表、假期表，重新生成所有客户的吃餐日历，并重新计算统计数据。</p>
                    <div class="tip-box warning">
                        <span>📌</span>
                        <div>
                            <strong>点击时机：</strong><br>
                            • 修改了暂停表（新增/删除暂停日期）<br>
                            • 修改了假期表（新增/删除假期）<br>
                            • 新增客户后初始化
                        </div>
                    </div>
                    <button class="btn-warning" onclick="syncAll()">🔄 一键同步所有数据</button>
                    <div id="syncResult" class="result"></div>
                </div>
                
                <!-- 查看甘特图 -->
                <div class="card">
                    <h2><span class="step-badge">📊</span> 查看甘特图</h2>
                    <p>查看所有客户的配送状态，一目了然。显示起送日、暂停日、假期、配送数量等。</p>
                    <button class="btn-info" onclick="loadGantt()">📊 查看甘特图</button>
                    <div id="ganttResult" class="result"></div>
                </div>
                
                <!-- 日历视图 -->
                <div class="card">
                    <h2><span class="step-badge">📅</span> 查看客户日历</h2>
                    <p>查看单个客户的吃餐日历，可视化展示配送情况，可修改过去的配送数量。</p>
                    <div class="input-group">
                        <label for="calendarCustomer">👤 选择客户：</label>
                        <select id="calendarCustomer">
                            <option value="">-- 请选择客户 --</option>
                        </select>
                    </div>
                    <button class="btn-primary" onclick="loadCustomerCalendar()">📅 查看日历</button>
                    <div id="calendarViewResult" class="result"></div>
                </div>
                
                <!-- 生成配送记录 -->
                <div class="card">
                    <h2><span class="step-badge">1</span> 生成配送记录</h2>
                    <p>为指定日期生成配送记录，系统会自动删除旧记录并生成新记录。</p>
                    <div class="input-group">
                        <label for="generateDate">📅 配送日期：</label>
                        <input type="date" id="generateDate" value="">
                    </div>
                    <button class="btn-primary" onclick="generateRecords()">📋 生成配送记录</button>
                    <div id="generateResult" class="result"></div>
                </div>
                
                <!-- 批量确认 -->
                <div class="card">
                    <h2><span class="step-badge">2</span> 批量确认配送</h2>
                    <p>确认指定日期的所有配送记录，确认后自动同步到吃餐日历。</p>
                    <div class="input-group">
                        <label for="confirmDate">📅 配送日期：</label>
                        <input type="date" id="confirmDate" value="">
                    </div>
                    <button class="btn-success" onclick="confirmDelivery()">✅ 批量确认配送</button>
                    <div id="confirmResult" class="result"></div>
                </div>
            </div>
            
            <!-- 甘特图容器 -->
            <div id="ganttContainer" class="gantt-container" style="display: none;">
                <div class="gantt-header">
                    <h3>📊 客户配送甘特图</h3>
                    <div>
                        <button onclick="refreshGantt()">🔄 刷新</button>
                        <button onclick="closeGantt()" style="background: #f0f0f0; color: #333;">✕ 关闭</button>
                    </div>
                </div>
                
                <div class="calendar-legend" style="margin-bottom: 15px;">
                    <div class="legend-item"><div class="legend-dot start">🚀</div> 起送日</div>
                    <div class="legend-item"><div class="legend-dot pause">⏸</div> 暂停日</div>
                    <div class="legend-item"><div class="legend-dot holiday">🎉</div> 假期</div>
                    <div class="legend-item"><div class="legend-dot delivered">1</div> 已配送</div>
                    <div class="legend-item"><div class="legend-dot pending">1?</div> 待确认</div>
                </div>
                
                <div id="ganttTable" style="overflow-x: auto;">
                    <!-- 甘特图内容动态生成 -->
                </div>
            </div>
            
            <!-- 日历视图容器 -->
            <div id="calendarContainer" class="calendar-container" style="display: none;">
                <div class="calendar-header">
                    <h3 id="calendarTitle">客户日历</h3>
                    <div class="calendar-nav">
                        <button onclick="prevMonth()">◀ 上月</button>
                        <button onclick="nextMonth()">下月 ▶</button>
                        <button onclick="closeCalendar()">✕ 关闭</button>
                    </div>
                </div>
                
                <div class="calendar-info">
                    <div class="calendar-info-item">
                        <div class="label">起送日期</div>
                        <div class="value" id="infoStartDate">-</div>
                    </div>
                    <div class="calendar-info-item">
                        <div class="label">已吃/总餐</div>
                        <div class="value" id="infoEaten">-</div>
                    </div>
                    <div class="calendar-info-item">
                        <div class="label">剩余餐数</div>
                        <div class="value" id="infoRemaining">-</div>
                    </div>
                </div>
                
                <div class="calendar-legend">
                    <div class="legend-item"><div class="legend-dot start">🚀</div> 起送日</div>
                    <div class="legend-item"><div class="legend-dot pause">⏸</div> 暂停日</div>
                    <div class="legend-item"><div class="legend-dot holiday">🎉</div> 假期</div>
                    <div class="legend-item"><div class="legend-dot delivered">1</div> 已确认</div>
                    <div class="legend-item"><div class="legend-dot pending">1?</div> 待确认</div>
                </div>
                
                <div class="calendar-grid" id="calendarGrid">
                    <!-- 日历内容动态生成 -->
                </div>
                
                <div class="calendar-edit" id="calendarEdit">
                    <h4>📝 修改配送数量（仅限过去的日期）</h4>
                    <div class="calendar-edit-row">
                        <div class="input-group">
                            <label>日期</label>
                            <input type="date" id="editDate" readonly>
                        </div>
                        <div class="input-group">
                            <label>配送数量</label>
                            <input type="number" id="editQty" value="1" min="0" max="10">
                        </div>
                        <button class="btn-warning" onclick="saveCalendarEdit()">💾 保存修改</button>
                        <button class="btn-info" onclick="cancelCalendarEdit()">取消</button>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>💡 <strong>提示：</strong>修改暂停表/假期表后，请点击"一键同步"</p>
                <p>📞 <strong>技术支持：</strong>遇到问题请联系管理员</p>
            </div>
        </div>
    </div>
    
    <script>
        // ==================== 配置 ====================
        const DEFAULT_API_URL = 'https://delivery-system-production-984a.up.railway.app';
        
        // ==================== 全局变量 ====================
        let API_URL = localStorage.getItem('delivery_api_url') || DEFAULT_API_URL;
        let TOKEN = localStorage.getItem('delivery_token') || '';
        let currentCustomerData = null;
        let currentCalendarMonth = new Date();
        let ganttData = null;
        
        // ==================== 初始化 ====================
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('loginForm').addEventListener('submit', handleLogin);
            document.getElementById('apiUrlInput').value = API_URL;
            document.getElementById('currentApiUrl').textContent = API_URL;
            
            checkAuth();
        });
        
        async function checkAuth() {
            if (!TOKEN) return;
            
            try {
                const response = await fetch(`${API_URL}/api/verify`, {
                    headers: { 'Authorization': `Bearer ${TOKEN}` }
                });
                const data = await response.json();
                
                if (data.success) {
                    showMainPage(data.username, data.role);
                }
            } catch (e) {
                console.log('Token验证失败');
            }
        }
        
        function showMainPage(username, role) {
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('mainPage').style.display = 'block';
            document.body.classList.remove('login-body');
            
            document.getElementById('userName').textContent = username;
            document.getElementById('userRole').textContent = role;
            document.getElementById('userAvatar').textContent = username.charAt(0).toUpperCase();
            
            setDefaultDates();
            loadCustomerList();
        }
        
        function setDefaultDates() {
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            document.getElementById('generateDate').value = tomorrow.toISOString().split('T')[0];
            document.getElementById('confirmDate').value = today.toISOString().split('T')[0];
        }
        
        async function loadCustomerList() {
            try {
                const response = await fetch(`${API_URL}/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${TOKEN}`
                    },
                    body: JSON.stringify({ workflow_type: 'get_customers' })
                });
                
                const data = await response.json();
                if (data.success && data.data && data.data.customers) {
                    const select = document.getElementById('calendarCustomer');
                    select.innerHTML = '<option value="">-- 请选择客户 --</option>';
                    
                    data.data.customers.forEach(c => {
                        const option = document.createElement('option');
                        option.value = c.name;
                        option.textContent = `${c.name} (剩余${c.remaining}餐)`;
                        select.appendChild(option);
                    });
                }
            } catch (e) {
                console.log('加载客户列表失败');
            }
        }
        
        // ==================== 登录相关 ====================
        async function handleLogin(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                alert('请输入用户名和密码');
                return;
            }
            
            document.getElementById('loginBtn').disabled = true;
            
            try {
                const response = await fetch(`${API_URL}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    TOKEN = data.token;
                    localStorage.setItem('delivery_token', TOKEN);
                    showMainPage(username, data.role);
                } else {
                    alert(data.detail || '登录失败');
                }
            } catch (error) {
                alert('登录失败: ' + error.message);
            } finally {
                document.getElementById('loginBtn').disabled = false;
            }
        }
        
        function saveApiUrl() {
            const url = document.getElementById('apiUrlInput').value.trim();
            if (!url) {
                alert('请输入API地址');
                return;
            }
            
            let cleanUrl = url.replace(/\/$/, '');
            if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
                cleanUrl = 'https://' + cleanUrl;
            }
            
            localStorage.setItem('delivery_api_url', cleanUrl);
            API_URL = cleanUrl;
            
            document.getElementById('currentApiUrl').textContent = cleanUrl;
            document.getElementById('apiUrlInput').value = cleanUrl;
            alert('✅ API地址已保存: ' + cleanUrl);
        }
        
        function logout() {
            fetch(`${API_URL}/api/logout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${TOKEN}` }
            }).catch(e => console.log('Logout error:', e));
            
            localStorage.removeItem('delivery_token');
            TOKEN = '';
            
            document.getElementById('loginPage').style.display = 'block';
            document.getElementById('mainPage').style.display = 'none';
            document.body.classList.add('login-body');
        }
        
        // ==================== 工作流调用 ====================
        async function callWorkflow(type, extraData = {}) {
            const response = await fetch(`${API_URL}/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${TOKEN}`
                },
                body: JSON.stringify({ workflow_type: type, ...extraData })
            });
            
            return await response.json();
        }
        
        function showLoading(elementId) {
            const el = document.getElementById(elementId);
            el.className = 'result loading';
            el.textContent = '⏳ 处理中...';
        }
        
        function showResult(elementId, data) {
            const el = document.getElementById(elementId);
            if (data.success) {
                el.className = 'result success';
                el.innerHTML = `<strong>✅ ${data.message}</strong>`;
                if (data.data && data.data.debug_info) {
                    el.innerHTML += `<br><small>${data.data.debug_info.slice(0, 3).join('<br>')}</small>`;
                }
            } else {
                el.className = 'result error';
                el.innerHTML = `<strong>❌ ${data.message}</strong>`;
            }
        }
        
        // ==================== 业务功能 ====================
        async function syncAll() {
            if (!confirm('确认同步所有数据吗？这将重新生成所有客户的吃餐日历。')) return;
            
            showLoading('syncResult');
            
            try {
                const results = [];
                
                results.push('1️⃣ 生成吃餐日历...');
                const r1 = await callWorkflow('generate_calendar');
                results.push(r1.success ? '✅ 完成' : '❌ 失败');
                
                results.push('2️⃣ 计算已吃餐数...');
                const r2 = await callWorkflow('recalculate_eaten');
                results.push(r2.success ? '✅ 完成' : '❌ 失败');
                
                const div = document.getElementById('syncResult');
                div.className = 'result success';
                div.innerHTML = `<strong>✅ 同步完成</strong><br>${results.join('<br>')}`;
                
                loadCustomerList();
            } catch (error) {
                document.getElementById('syncResult').className = 'result error';
                document.getElementById('syncResult').textContent = '❌ 错误: ' + error.message;
            }
        }
        
        async function generateRecords() {
            const date = document.getElementById('generateDate').value;
            if (!date) {
                alert('请选择配送日期');
                return;
            }
            
            showLoading('generateResult');
            
            try {
                const result = await callWorkflow('generate_delivery', { delivery_date: date });
                showResult('generateResult', result);
            } catch (error) {
                document.getElementById('generateResult').className = 'result error';
                document.getElementById('generateResult').textContent = '❌ 错误: ' + error.message;
            }
        }
        
        async function confirmDelivery() {
            const date = document.getElementById('confirmDate').value;
            if (!date) {
                alert('请选择配送日期');
                return;
            }
            
            if (!confirm(`确认 ${date} 的所有配送记录吗？`)) return;
            
            showLoading('confirmResult');
            
            try {
                const result = await callWorkflow('confirm_delivery', { delivery_date: date });
                showResult('confirmResult', result);
            } catch (error) {
                document.getElementById('confirmResult').className = 'result error';
                document.getElementById('confirmResult').textContent = '❌ 错误: ' + error.message;
            }
        }
        
        // ==================== 甘特图功能 ====================
        async function loadGantt() {
            showLoading('ganttResult');
            
            try {
                const result = await callWorkflow('get_gantt_data');
                
                if (result.success) {
                    ganttData = result.data;
                    renderGantt();
                    document.getElementById('ganttContainer').style.display = 'block';
                    document.getElementById('calendarContainer').style.display = 'none';
                    
                    const resultEl = document.getElementById('ganttResult');
                    resultEl.className = 'result success';
                    resultEl.textContent = '✅ 甘特图已加载';
                } else {
                    showResult('ganttResult', result);
                }
            } catch (error) {
                document.getElementById('ganttResult').className = 'result error';
                document.getElementById('ganttResult').textContent = '❌ 错误: ' + error.message;
            }
        }
        
        function renderGantt() {
            if (!ganttData || !ganttData.gantt_data) return;
            
            const container = document.getElementById('ganttTable');
            
            // 找到日期范围
            let allDates = [];
            ganttData.gantt_data.forEach(customer => {
                if (customer.daily_details) {
                    customer.daily_details.forEach(day => {
                        if (!allDates.includes(day.date)) {
                            allDates.push(day.date);
                        }
                    });
                }
            });
            allDates.sort();
            
            // 只显示最近30天
            const today = new Date();
            const displayDates = [];
            for (let i = -10; i <= 20; i++) {
                const d = new Date(today);
                d.setDate(d.getDate() + i);
                displayDates.push(d.toISOString().split('T')[0]);
            }
            
            // 生成表格
            let html = '<table class="gantt-table"><thead><tr>';
            html += '<th class="customer-col">客户</th>';
            html += '<th class="info-col">总餐</th>';
            html += '<th class="info-col">剩余</th>';
            html += '<th class="info-col">状态</th>';
            
            // 日期表头
            displayDates.forEach(dateStr => {
                const d = new Date(dateStr);
                const weekday = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()];
                const isToday = dateStr === ganttData.today;
                const isWeekend = d.getDay() === 0 || d.getDay() === 6;
                html += `<th class="${isToday ? 'today-col' : ''}" style="${isWeekend ? 'background: #fef3c7;' : ''}">${d.getDate()}<br><small>${weekday}</small></th>`;
            });
            html += '</tr></thead><tbody>';
            
            // 数据行
            ganttData.gantt_data.forEach(customer => {
                // 状态样式
                let statusClass = 'active';
                let statusText = customer.delivery_status;
                if (statusText === '已结束') {
                    statusClass = 'ended';
                } else if (statusText === '未开始') {
                    statusClass = 'pending';
                }
                
                html += '<tr>';
                html += `<td class="customer-col">${customer.customer_name}</td>`;
                html += `<td class="info-col">${customer.total_meals}</td>`;
                html += `<td class="info-col">${customer.remaining}</td>`;
                html += `<td class="info-col"><span class="status-badge ${statusClass}">${statusText}</span></td>`;
                
                // 每日数据
                displayDates.forEach(dateStr => {
                    const isToday = dateStr === ganttData.today;
                    const dayInfo = customer.daily_details ? customer.daily_details.find(d => d.date === dateStr) : null;
                    
                    let cellClass = isToday ? 'today-col' : '';
                    let dayHtml = '';
                    
                    if (dayInfo) {
                        let dayClass = 'empty';
                        let dayText = '';
                        
                        if (dayInfo.is_start) {
                            dayClass = 'start';
                            dayText = '🚀';
                        } else if (dayInfo.is_pause) {
                            dayClass = 'pause';
                            dayText = '⏸';
                        } else if (dayInfo.is_holiday) {
                            dayClass = 'holiday';
                            dayText = '🎉';
                        } else if (dayInfo.qty > 0) {
                            if (dayInfo.is_past) {
                                dayClass = 'delivered';
                                dayText = dayInfo.qty;
                            } else {
                                dayClass = 'pending';
                                dayText = dayInfo.qty + '?';
                            }
                        } else {
                            dayText = '-';
                        }
                        
                        dayHtml = `<span class="gantt-day ${dayClass}">${dayText}</span>`;
                    }
                    
                    html += `<td class="${cellClass}">${dayHtml}</td>`;
                });
                
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        function refreshGantt() {
            loadGantt();
        }
        
        function closeGantt() {
            document.getElementById('ganttContainer').style.display = 'none';
        }
        
        // ==================== 日历视图功能 ====================
        async function loadCustomerCalendar() {
            const customerName = document.getElementById('calendarCustomer').value;
            if (!customerName) {
                alert('请选择客户');
                return;
            }
            
            showLoading('calendarViewResult');
            
            try {
                const response = await fetch(`${API_URL}/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${TOKEN}`
                    },
                    body: JSON.stringify({
                        workflow_type: 'get_customer_calendar',
                        customer_name: customerName
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentCustomerData = data.data;
                    currentCalendarMonth = new Date();
                    
                    document.getElementById('calendarTitle').textContent = `${customerName} 的吃餐日历`;
                    document.getElementById('calendarContainer').style.display = 'block';
                    document.getElementById('ganttContainer').style.display = 'none';
                    
                    document.getElementById('infoStartDate').textContent = currentCustomerData.start_date || '-';
                    document.getElementById('infoEaten').textContent = 
                        `${currentCustomerData.eaten_count || 0}/${currentCustomerData.total_meals || 0}`;
                    document.getElementById('infoRemaining').textContent = 
                        currentCustomerData.remaining || 0;
                    
                    renderCalendar();
                    
                    const resultEl = document.getElementById('calendarViewResult');
                    resultEl.className = 'result success';
                    resultEl.textContent = '✅ 日历已加载';
                } else {
                    showResult('calendarViewResult', data);
                }
            } catch (error) {
                document.getElementById('calendarViewResult').className = 'result error';
                document.getElementById('calendarViewResult').textContent = '❌ 错误: ' + error.message;
            }
        }
        
        function renderCalendar() {
            if (!currentCustomerData) return;
            
            const grid = document.getElementById('calendarGrid');
            grid.innerHTML = '';
            
            const year = currentCalendarMonth.getFullYear();
            const month = currentCalendarMonth.getMonth();
            
            document.getElementById('calendarTitle').textContent = 
                `${currentCustomerData.customer_name} 的吃餐日历 - ${year}年${month + 1}月`;
            
            const weekdays = ['一', '二', '三', '四', '五', '六', '日'];
            weekdays.forEach(day => {
                const header = document.createElement('div');
                header.className = 'calendar-day-header';
                header.textContent = day;
                grid.appendChild(header);
            });
            
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const startDayOfWeek = (firstDay.getDay() + 6) % 7;
            
            for (let i = 0; i < startDayOfWeek; i++) {
                const emptyDay = document.createElement('div');
                emptyDay.className = 'calendar-day empty';
                grid.appendChild(emptyDay);
            }
            
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            for (let day = 1; day <= lastDay.getDate(); day++) {
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                const currentDate = new Date(year, month, day);
                currentDate.setHours(0, 0, 0, 0);
                
                const dayEl = document.createElement('div');
                dayEl.className = 'calendar-day';
                
                if (currentDate.getTime() === today.getTime()) {
                    dayEl.classList.add('today');
                }
                
                const dayNumber = document.createElement('div');
                dayNumber.className = 'day-number';
                dayNumber.textContent = day;
                dayEl.appendChild(dayNumber);
                
                const dayBadge = document.createElement('div');
                dayBadge.className = 'day-badge';
                
                let hasBadge = false;
                let badgeText = '';
                let badgeClass = '';
                let currentQty = 1;
                
                if (currentCustomerData.start_date === dateStr) {
                    badgeText = '🚀 起送';
                    badgeClass = 'start';
                    hasBadge = true;
                }
                else if (currentCustomerData.pause_dates && currentCustomerData.pause_dates.includes(dateStr)) {
                    badgeText = '⏸ 暂停';
                    badgeClass = 'pause';
                    hasBadge = true;
                    currentQty = 0;
                }
                else if (currentCustomerData.holiday_dates && currentCustomerData.holiday_dates.includes(dateStr)) {
                    badgeText = '🎉 假期';
                    badgeClass = 'holiday';
                    hasBadge = true;
                    currentQty = 0;
                }
                else if (currentCustomerData.calendar && currentCustomerData.calendar[dateStr]) {
                    const info = currentCustomerData.calendar[dateStr];
                    const qty = info.qty || 0;
                    currentQty = qty;
                    
                    if (currentDate < today) {
                        badgeText = qty;
                        badgeClass = 'delivered';
                        hasBadge = true;
                    } else {
                        badgeText = qty + '?';
                        badgeClass = 'pending';
                        hasBadge = true;
                    }
                }
                else if (currentDate >= today && currentCustomerData.start_date && dateStr >= currentCustomerData.start_date) {
                    badgeText = '1?';
                    badgeClass = 'pending';
                    hasBadge = true;
                    currentQty = 1;
                }
                
                if (hasBadge) {
                    dayBadge.classList.add(badgeClass);
                    dayBadge.textContent = badgeText;
                    dayEl.appendChild(dayBadge);
                }
                
                if (currentDate < today && currentQty > 0) {
                    dayEl.onclick = () => selectDateForEdit(dateStr, currentQty);
                    dayEl.style.cursor = 'pointer';
                } else {
                    dayEl.style.cursor = 'default';
                }
                
                grid.appendChild(dayEl);
            }
        }
        
        function prevMonth() {
            currentCalendarMonth.setMonth(currentCalendarMonth.getMonth() - 1);
            renderCalendar();
        }
        
        function nextMonth() {
            currentCalendarMonth.setMonth(currentCalendarMonth.getMonth() + 1);
            renderCalendar();
        }
        
        function closeCalendar() {
            document.getElementById('calendarContainer').style.display = 'none';
        }
        
        function selectDateForEdit(dateStr, currentQty) {
            document.getElementById('editDate').value = dateStr;
            document.getElementById('editQty').value = currentQty || 1;
            document.getElementById('calendarEdit').classList.add('active');
        }
        
        function cancelCalendarEdit() {
            document.getElementById('calendarEdit').classList.remove('active');
        }
        
        async function saveCalendarEdit() {
            const dateStr = document.getElementById('editDate').value;
            const qty = parseInt(document.getElementById('editQty').value) || 1;
            const customerName = currentCustomerData.customer_name;
            
            if (!confirm(`确认修改 ${customerName} 在 ${dateStr} 的配送数量为 ${qty} 份？`)) {
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${TOKEN}`
                    },
                    body: JSON.stringify({
                        workflow_type: 'update_single_calendar',
                        customer_name: customerName,
                        calendar_updates: { [dateStr]: qty }
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('✅ 修改成功！已吃餐数已更新。');
                    
                    if (!currentCustomerData.calendar) {
                        currentCustomerData.calendar = {};
                    }
                    currentCustomerData.calendar[dateStr] = {
                        qty: qty,
                        status: qty > 0 ? 'delivered' : 'paused',
                        source: 'calendar'
                    };
                    currentCustomerData.eaten_count = data.data.eaten_count;
                    currentCustomerData.remaining = currentCustomerData.total_meals - data.data.eaten_count;
                    
                    document.getElementById('infoEaten').textContent = 
                        `${currentCustomerData.eaten_count}/${currentCustomerData.total_meals}`;
                    document.getElementById('infoRemaining').textContent = currentCustomerData.remaining;
                    
                    renderCalendar();
                    cancelCalendarEdit();
                    loadCustomerList();
                } else {
                    alert('❌ 修改失败: ' + data.message);
                }
            } catch (error) {
                alert('❌ 修改失败: ' + error.message);
            }
        }
    </script>
</body>
</html>
