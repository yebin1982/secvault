from cryptography.fernet import Fernet
import base64
import os
from .models import db, PasswordEntry

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

def search_entries(query, user_id):
    """搜索指定用户的密码条目"""
    base_query = PasswordEntry.query.filter_by(user_id=user_id)

    if not query:
        # 返回该用户的所有条目
        return base_query.all()

    # 在该用户的基础上进行搜索
    search_term = f"%{query}%"
    entries = base_query.filter(
        db.or_(
            PasswordEntry.service_name.like(search_term),
            PasswordEntry.username.like(search_term),
            PasswordEntry.email.like(search_term),
            PasswordEntry.notes.like(search_term)
        )
    ).all()

    return entries
