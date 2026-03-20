# PythonAnywhere WSGI 配置文件
import sys
import os

# 添加项目路径
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_APP'] = 'flask_app.py'

from flask_app import app as application
