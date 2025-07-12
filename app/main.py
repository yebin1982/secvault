from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import PasswordEntry, db
from app.utils import PasswordEncryption, search_entries

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    """主页面"""
    return render_template('dashboard.html')

# ============ 添加功能 ============
@main.route('/add_password', methods=['POST'])
@login_required
def add_password():
    """添加新密码条目"""
    try:
        # 获取表单数据
        service_name = request.form.get('service_name')
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password')
        notes = request.form.get('notes', '')
        
        # 验证必填字段
        if not service_name or not password:
            return jsonify({'success': False, 'message': '服务名称和密码不能为空'})
        
        # 加密密码
        encryption = PasswordEncryption()
        encrypted_password = encryption.encrypt(password)
        
        # 创建密码条目
        entry = PasswordEntry(
            service_name=service_name,
            username=username,
            email=email,
            password_encrypted=encrypted_password,
            notes=notes
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '密码添加成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

# ============ 修改功能 ============
@main.route('/edit_password/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_password(entry_id):
    """编辑密码条目"""
    entry = PasswordEntry.query.get_or_404(entry_id)
    
    if request.method == 'GET':
        # 返回编辑表单数据（包含解密后的密码）
        encryption = PasswordEncryption()
        try:
            decrypted_password = encryption.decrypt(entry.password_encrypted)
        except Exception:
            decrypted_password = "无法解密！密钥可能已更改。"

        return jsonify({
            'id': entry.id,
            'service_name': entry.service_name,
            'username': entry.username or '',
            'email': entry.email or '',
            'notes': entry.notes or '',
            'password': decrypted_password
        })
    
    elif request.method == 'POST':
        try:
            # 更新数据
            entry.service_name = request.form.get('service_name')
            entry.username = request.form.get('username', '')
            entry.email = request.form.get('email', '')
            entry.notes = request.form.get('notes', '')
            
            # 如果密码有变化，重新加密
            new_password = request.form.get('password')
            if new_password:
                encryption = PasswordEncryption()
                entry.password_encrypted = encryption.encrypt(new_password)
            
            db.session.commit()
            return jsonify({'success': True, 'message': '修改成功'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'修改失败: {str(e)}'})

# ============ 删除功能 ============
@main.route('/delete_password/<int:entry_id>', methods=['POST'])
@login_required
def delete_password(entry_id):
    """删除密码条目"""
    try:
        entry = PasswordEntry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# ============ 查看密码功能 ============
@main.route('/view_password/<int:entry_id>')
@login_required
def view_password(entry_id):
    """查看密码（解密显示）"""
    try:
        entry = PasswordEntry.query.get_or_404(entry_id)
        encryption = PasswordEncryption()
        decrypted_password = encryption.decrypt(entry.password_encrypted)
        
        return jsonify({
            'success': True,
            'password': decrypted_password
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取密码失败: {str(e)}'})

# ============ 搜索功能 ============
@main.route('/search')
@login_required
def search():
    """搜索密码条目"""
    query = request.args.get('q', '')
    entries = search_entries(query)
    
    results = []
    for entry in entries:
        results.append({
            'id': entry.id,
            'service_name': entry.service_name,
            'username': entry.username or '',
            'email': entry.email or '',
            'notes': entry.notes or '',
            'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': entry.updated_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'results': results})
