import os
from cryptography.fernet import Fernet
# 1. 生成用于 Fernet 加密的 ENCRYPTION_KEY
# Fernet.generate_key() 返回一个 URL 安全的 base64 编码的32字节密钥
encryption_key = Fernet.generate_key().decode()
print(f"ENCRYPTION_KEY={encryption_key}")
# 2. 生成用于 Flask 的 SECRET_KEY
# os.urandom(32) 生成32个加密安全的随机字节
# .hex() 将这些字节转换为一个64个字符的十六进制字符串
secret_key = os.urandom(32).hex()
print(f"SECRET_KEY={secret_key}")