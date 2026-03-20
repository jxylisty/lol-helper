# LOL 英雄数据服务器部署指南

## 混合部署架构

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   uni-app   │ ───► │  PythonAnywhere  │ ◄─── │  Local Scripts  │
│   (前端)    │      │   (Flask API)    │      │  (数据抓取)     │
└─────────────┘      └──────────────────┘      └─────────────────┘
     用户                   云端 API                本地定时运行
```

## 第一部分：本地数据更新

### 1. 安装依赖
```bash
cd server
pip install -r requirements.txt
```

### 2. 运行数据更新脚本
```bash
python update_local_data.py
```

这会：
- 从 DDragon 获取英雄列表和图片
- 从 OP.GG 抓取符文数据
- 从 OP.GG 抓取英雄出装数据
- 保存到 `data/` 目录

### 3. 定时更新（可选）
创建 Windows 任务计划程序，每天运行一次：
```
程序：python.exe
参数：update_local_data.py
起始目录：C:\Users\zzx05\Documents\HBuilderProjects\my-uniapp\server
```

## 第二部分：部署到 PythonAnywhere

### 1. 注册账户
访问 https://www.pythonanywhere.com 注册免费账户

### 2. 创建 Web 应用
1. 登录 PythonAnywhere
2. 点击 "Web" 标签
3. 点击 "Add a new web app"
4. 选择 "Flask" -> "Python 3.10"
5. 记下你的域名：`yourusername.pythonanywhere.com`

### 3. 上传代码
方法 A：使用 Git
```bash
# 在 PythonAnywhere Bash 控制台
git clone https://github.com/yourusername/my-uniapp.git
cd my-uniapp/server
```

方法 B：直接上传文件
上传以下文件到 `/home/yourusername/mysite/`:
- flask_app.py
- wsgi.py
- data/ 目录（包含所有 JSON 文件）

### 4. 配置 WSGI
1. 在 Web 标签页，点击 WSGI 文件链接
2. 替换内容为：
```python
import sys
import os

path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_APP'] = 'flask_app.py'

from flask_app import app as application
```

### 5. 配置静态文件（可选）
在 Web 标签页添加：
- URL: `/static`
- Directory: `/home/yourusername/mysite/static`

### 6. 重启应用
点击绿色 "Reload" 按钮

## 第三部分：修改前端 API 地址

修改所有前端文件中的 API 地址：
```javascript
// 从
url: 'http://localhost:3000/api/heroes'

// 改为
url: 'https://yourusername.pythonanywhere.com/api/heroes'
```

需要修改的文件：
- pages/hero/heroList.vue
- pages/hero/heroDetail.vue
- pages/hero/heroRunes.vue
- pages/hero/heroMatchups.vue

## 第四部分：数据更新流程

### 方案 A：本地更新后上传
```bash
# 本地运行
python update_local_data.py

# 上传 data/ 目录到 PythonAnywhere
# 使用 FTP 或 Git
```

### 方案 B：在 PythonAnywhere 直接运行（需要付费账户）
```bash
# 在 PythonAnywhere Bash 控制台
cd /home/yourusername/mysite
python update_local_data.py
```

## API 端点

| 端点 | 说明 | 数据来源 |
|------|------|----------|
| `/api/heroes` | 英雄列表 | data/champions.json |
| `/api/hero/<id>` | 英雄详情 | data/champions.json |
| `/api/hero/<id>/build` | 出装符文 | data/hero_<id>_build.json |
| `/api/hero/<id>/stats` | 统计数据 | data/champions.json |
| `/api/runes` | 符文数据 | data/runes.json |
| `/api/options` | 选项配置 | 硬编码 |

## 故障排查

### 1. 符文显示"未知"
- 检查 `data/runes.json` 是否存在
- 运行 `python update_local_data.py` 更新符文数据

### 2. 英雄图片不显示
- 检查 DDragon 图片 URL 是否正确
- 确保网络连接正常

### 3. API 返回 404
- 检查文件路径是否正确
- 查看 PythonAnywhere 错误日志

## 免费账户限制

- 只能访问白名单网站（OP.GG 可能不在白名单）
- CPU/内存有限制
- 域名必须是 `yourusername.pythonanywhere.com`
- 无法运行定时任务

## 升级建议

如果免费账户无法满足需求，考虑：
1. PythonAnywhere 付费账户（$5/月）
2. 其他云平台：Render, Railway, Vercel
3. 继续使用本地服务器 + 内网穿透
