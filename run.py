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
    # 在应用上下文中执行数据库操作
    with app.app_context():
        db.create_all()
        init_default_user()

    app.run(debug=True, host='0.0.0.0', port=5000)
