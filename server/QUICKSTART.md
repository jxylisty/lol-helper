# 快速开始 - 混合部署

## 本地测试 Flask 服务器

### 1. 启动 Flask 服务器
```bash
cd server
python flask_app.py
```

服务器会在 http://localhost:5000 启动

### 2. 测试 API
访问以下地址测试：
- http://localhost:5000/api/heroes
- http://localhost:5000/api/runes
- http://localhost:5000/api/options

### 3. 更新数据
```bash
python update_local_data.py
```

## 部署到 PythonAnywhere

### 1. 注册并创建应用
1. 访问 https://www.pythonanywhere.com
2. 注册免费账户
3. 点击 "Web" -> "Add a new web app"
4. 选择 "Flask" -> "Python 3.10"

### 2. 上传文件
上传到 `/home/yourusername/mysite/`:
- flask_app.py
- wsgi.py
- data/ (整个目录)

### 3. 配置 WSGI
编辑 WSGI 文件，替换 `yourusername` 为你的用户名

### 4. 修改前端 API 地址
将所有前端文件中的：
```javascript
http://localhost:3000
```
改为：
```javascript
https://yourusername.pythonanywhere.com
```

需要修改的文件：
- pages/hero/heroList.vue
- pages/hero/heroDetail.vue
- pages/hero/heroRunes.vue
- pages/hero/heroMatchups.vue

## 数据更新流程

### 每周更新一次（推荐）
```bash
# 本地运行
python update_local_data.py

# 上传 data/ 到 PythonAnywhere
# 使用网页文件管理器或 FTP
```

## 优势

✅ 前端免费托管（uni-app）
✅ 后端免费托管（PythonAnywhere 免费层）
✅ 数据更新灵活（本地运行 Python 脚本）
✅ 无需担心服务器维护

## 注意事项

⚠️ PythonAnywhere 免费账户限制：
- 只能访问白名单网站
- CPU/内存有限制
- 域名：yourusername.pythonanywhere.com

⚠️ 数据需要定期手动更新并上传
