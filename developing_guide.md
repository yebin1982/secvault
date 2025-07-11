# 个人密码管理 Web 应用开发指南

## 项目概述

**项目名称**: PersonalPasswordManager  
**技术栈**: Flask + MySQL + HTML + Bootstrap  
**目标用户**: 单用户（yebin817）  
**核心功能**: 密码存储、搜索、管理、重置密码  
**安全优先**: 加密存储、安全认证、密码重置

## 1. 系统环境准备

### 1.1 Ubuntu 20.04.6 LTS 系统更新

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 安装必要的系统依赖

```bash
# Python 3.8+ 和 pip
sudo apt install python3 python3-pip python3-venv -y

# MySQL 服务器
sudo apt install mysql-server mysql-client -y

# 其他依赖
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
sudo apt install pkg-config default-libmysqlclient-dev -y
```

### 1.3 MySQL 配置

```bash
# 启动 MySQL 服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql -u root -p
```

MySQL 初始化脚本：

```sql
CREATE DATABASE password_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'pm_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON password_manager.* TO 'pm_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 2. 项目结构设计

```
PersonalPasswordManager/
├── app/
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── auth.py            # 认证相关
│   ├── main.py            # 主要路由
│   ├── utils.py           # 工具函数
│   └── templates/
│       ├── base.html      # 基础模板
│       ├── login.html     # 登录页面
│       ├── dashboard.html # 主页面
│       ├── profile.html   # 个人设置
│       └── reset_password.html
├── static/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── main.js
├── migrations/            # 数据库迁移
├── config.py             # 配置文件
├── requirements.txt      # 依赖包
├── run.py               # 应用启动文件
├── .env                 # 环境变量
└── README.md
```

## 3. 开发环境搭建

### 3.1 创建项目目录和虚拟环境

```bash
# 创建项目目录
mkdir PersonalPasswordManager
cd PersonalPasswordManager

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 3.2 安装依赖包

创建 `requirements.txt`:

```txt
Flask==2.3.3
Flask-SQLAlchemy
Flask-Login==0.6.3
Flask-WTF==1.1.1
Flask-Mail==0.9.1
Flask-Migrate==4.0.5
PyMySQL==1.1.0
cryptography
bcrypt==4.0.1
python-dotenv==1.0.0
WTForms==3.0.1
email-validator==2.0.0
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 4. 核心配置文件

### 4.1 环境变量配置 (.env)

```env
# 数据库配置
DB_HOST=localhost
DB_USER=pm_user
DB_PASSWORD=your_secure_password
DB_NAME=password_manager

# 应用配置
SECRET_KEY=your_super_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# 加密密钥
ENCRYPTION_KEY=your_encryption_key_here
```

### 4.2 应用配置 (config.py)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER')}:"
        f"{os.environ.get('DB_PASSWORD')}@"
        f"{os.environ.get('DB_HOST')}/"
        f"{os.environ.get('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # 加密配置
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

    # 默认用户配置
    DEFAULT_USERNAME = 'yebin817'
    DEFAULT_PASSWORD = 'yebin817'
    DEFAULT_EMAIL = 'yebin817@gmail.com'
```

## 5. 数据模型设计

### 5.1 用户模型和密码条目模型 (app/models.py)

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """生成重置令牌"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

class PasswordEntry(db.Model):
    """密码条目模型"""
    __tablename__ = 'password_entries'

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)  # 服务名称
    username = db.Column(db.String(100), nullable=True)       # 用户名
    email = db.Column(db.String(120), nullable=True)          # 邮箱
    password_encrypted = db.Column(db.Text, nullable=False)   # 加密后的密码
    notes = db.Column(db.Text, nullable=True)                # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PasswordEntry {self.service_name}>'
```

## 6. 核心功能实现

### 6.1 加密工具 (app/utils.py)

```python
from cryptography.fernet import Fernet
import base64
import os

class PasswordEncryption:
    """密码加密解密工具"""

    def __init__(self, key=None):
        if key:
            self.key = key.encode()
        else:
            self.key = os.environ.get('ENCRYPTION_KEY').encode()
        self.cipher = Fernet(base64.urlsafe_b64encode(self.key[:32]))

    def encrypt(self, password):
        """加密密码"""
        return self.cipher.encrypt(password.encode()).decode()

    def decrypt(self, encrypted_password):
        """解密密码"""
        return self.cipher.decrypt(encrypted_password.encode()).decode()

def search_entries(query):
    """搜索密码条目"""
    if not query:
        return []

    # 搜索服务名称、用户名、邮箱
    entries = PasswordEntry.query.filter(
        db.or_(
            PasswordEntry.service_name.contains(query),
            PasswordEntry.username.contains(query),
            PasswordEntry.email.contains(query),
            PasswordEntry.notes.contains(query)
        )
    ).all()

    return entries
```

### 6.2 认证模块 (app/auth.py)

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from app.utils import send_reset_email

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('用户名或密码错误')

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """重置密码"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            token = user.generate_reset_token()
            db.session.commit()
            send_reset_email(user.email, token)
            flash('重置链接已发送到您的邮箱')
        else:
            flash('邮箱不存在')

    return render_template('reset_password.html')
```

## 7. 前端页面设计

### 7.1 基础模板 (app/templates/base.html)

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}个人密码管理器{% endblock %}</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/custom.css') }}"
    />
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="#">密码管理器</a>
        {% if current_user.is_authenticated %}
        <div class="navbar-nav ms-auto">
          <a class="nav-link" href="{{ url_for('main.dashboard') }}">主页</a>
          <a class="nav-link" href="{{ url_for('main.profile') }}">个人设置</a>
          <a class="nav-link" href="{{ url_for('auth.logout') }}">退出</a>
        </div>
        {% endif %}
      </div>
    </nav>

    <div class="container mt-4">
      {% with messages = get_flashed_messages() %} {% if messages %} {% for
      message in messages %}
      <div class="alert alert-info alert-dismissible fade show" role="alert">
        {{ message }}
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="alert"
        ></button>
      </div>
      {% endfor %} {% endif %} {% endwith %} {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
  </body>
</html>
```

### 7.2 主页面 (app/templates/dashboard.html)

```html
{% extends "base.html" %} {% block content %}
<div class="row">
  <div class="col-md-12">
    <h2>欢迎回来，{{ current_user.username }}！</h2>

    <!-- 搜索框 -->
    <div class="card mt-4">
      <div class="card-body">
        <input
          type="text"
          id="searchInput"
          class="form-control form-control-lg"
          placeholder="搜索服务名称、用户名、邮箱..."
          oninput="performSearch()"
        />
      </div>
    </div>

    <!-- 搜索结果 -->
    <div id="searchResults" class="mt-4"></div>

    <!-- 添加新密码按钮 -->
    <div class="text-center mt-4">
      <button
        class="btn btn-primary btn-lg"
        data-bs-toggle="modal"
        data-bs-target="#addPasswordModal"
      >
        添加新密码
      </button>
    </div>
  </div>
</div>

<!-- 添加密码模态框 -->
<div class="modal fade" id="addPasswordModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">添加新密码</h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
        ></button>
      </div>
      <form id="addPasswordForm">
        <div class="modal-body">
          <div class="mb-3">
            <label for="serviceName" class="form-label">服务名称</label>
            <input type="text" class="form-control" id="serviceName" required />
          </div>
          <div class="mb-3">
            <label for="username" class="form-label">用户名</label>
            <input type="text" class="form-control" id="username" />
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">邮箱</label>
            <input type="email" class="form-control" id="email" />
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">密码</label>
            <input
              type="password"
              class="form-control"
              id="password"
              required
            />
          </div>
          <div class="mb-3">
            <label for="notes" class="form-label">备注</label>
            <textarea class="form-control" id="notes"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            取消
          </button>
          <button type="submit" class="btn btn-primary">保存</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

## 8. 部署和运行

### 8.1 应用启动文件 (run.py)

```python
from app import create_app, db
from app.models import User
from config import Config

app = create_app()

def init_default_user():
    """初始化默认用户"""
    with app.app_context():
        if not User.query.filter_by(username=Config.DEFAULT_USERNAME).first():
            user = User(
                username=Config.DEFAULT_USERNAME,
                email=Config.DEFAULT_EMAIL
            )
            user.set_password(Config.DEFAULT_PASSWORD)
            db.session.add(user)
            db.session.commit()
            print(f"默认用户已创建: {Config.DEFAULT_USERNAME}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_user()

    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 8.2 运行应用

```bash
# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 运行应用
python run.py
```

## 9. 安全考虑

### 9.1 密码加密

- 使用 Fernet 对称加密存储密码
- 用户登录密码使用 bcrypt 哈希
- 环境变量存储敏感信息

### 9.2 会话管理

- 使用 Flask-Login 管理用户会话
- 设置会话超时
- CSRF 保护

### 9.3 访问控制

- 所有敏感页面需要登录
- 单用户系统，限制注册功能

## 10. 开发流程

1. **环境搭建** → 按照步骤 1-3 完成
2. **数据库设计** → 创建模型和迁移
3. **后端开发** → 实现认证和 API
4. **前端开发** → 创建页面和交互
5. **安全测试** → 验证加密和认证
6. **部署测试** → 本地测试所有功能
7. **优化改进** → 根据使用情况调整

## 11. 后续扩展

- 密码强度检查
- 自动备份功能
- 批量导入导出
- 移动端适配
- 双因素认证

---

**注意事项**：

- 定期备份数据库
- 及时更新依赖包
- 监控系统资源
- 定期更换加密密钥
