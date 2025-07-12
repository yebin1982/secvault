// 页面加载完成后，默认加载所有密码条目
document.addEventListener('DOMContentLoaded', function() {
    performSearch();

    // 为所有密码可见性切换按钮添加事件监听器
    document.querySelectorAll('.toggle-password-btn').forEach(button => {
        button.addEventListener('click', function() {
            const targetInputId = this.getAttribute('data-target-input');
            const input = document.getElementById(targetInputId);
            
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.textContent = '隐藏';
                } else {
                    input.type = 'password';
                    this.textContent = '显示';
                }
            }
        });
    });
});

// 搜索功能
function performSearch() {
    const query = document.getElementById('searchInput').value;
    
    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('搜索失败:', error);
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '<p class="text-danger">搜索请求失败，请检查后端服务是否正常。</p>';
        });
}

// 显示搜索结果
function displaySearchResults(results) {
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = ''; // 清空旧结果
    
    if (results.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted text-center">没有找到相关记录。</p>';
        return;
    }
    
    const row = document.createElement('div');
    row.className = 'row';

    results.forEach(entry => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-4';
        
        col.innerHTML = `
            <div class="card h-100">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${escapeHTML(entry.service_name)}</h5>
                    <p class="card-text">
                        <strong>用户名:</strong> ${escapeHTML(entry.username) || 'N/A'}<br>
                        <strong>邮箱:</strong> ${escapeHTML(entry.email) || 'N/A'}<br>
                        <strong>备注:</strong> ${escapeHTML(entry.notes) || 'N/A'}
                    </p>
                    <small class="text-muted mt-auto">
                        更新于: ${entry.updated_at}
                    </small>
                    <div class="mt-3">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewPassword(${entry.id})">查看密码</button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="openEditModal(${entry.id})">��辑</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteEntry(${entry.id})">删除</button>
                    </div>
                </div>
            </div>
        `;
        row.appendChild(col);
    });
    resultsDiv.appendChild(row);
}

// 添加密码
document.getElementById('addPasswordForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/add_password', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('密码添加成功！');
            const addModal = bootstrap.Modal.getInstance(document.getElementById('addPasswordModal'));
            addModal.hide();
            this.reset();
            performSearch(); // 刷新结果
        } else {
            alert('添加失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('添加操作失败:', error);
        alert('添加失败，请重试。');
    });
});

// 打开编辑模态框并填充数据
function openEditModal(entryId) {
    fetch(`/edit_password/${entryId}`)
        .then(response => response.json())
        .then(data => {
            // 填充编辑表单
            document.getElementById('editEntryId').value = data.id;
            document.getElementById('editServiceName').value = data.service_name;
            document.getElementById('editUsername').value = data.username;
            document.getElementById('editEmail').value = data.email;
            document.getElementById('editPassword').value = ''; // 清空密码字段
            document.getElementById('editNotes').value = data.notes;
            
            // 显示编辑模态框
            const editModal = new bootstrap.Modal(document.getElementById('editPasswordModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('获取编辑数据失败:', error);
            alert('无法加载条目信息，请重试。');
        });
}

// 提交编辑表单
document.getElementById('editPasswordForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const entryId = document.getElementById('editEntryId').value;
    const formData = new FormData(this);
    
    fetch(`/edit_password/${entryId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('更新成功！');
            const editModal = bootstrap.Modal.getInstance(document.getElementById('editPasswordModal'));
            editModal.hide();
            performSearch(); // 刷新结果
        } else {
            alert('更新失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('更新操作失败:', error);
        alert('更新失败，请重试。');
    });
});

// 删除密码条目
function deleteEntry(entryId) {
    if (confirm('确定要删除这个密码条目吗？此操作不可恢复！')) {
        fetch(`/delete_password/${entryId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('删除成功！');
                performSearch(); // 刷新结果
            } else {
                alert('删除失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('删除操作失败:', error);
            alert('删除失败，请重试。');
        });
    }
}

// 查看密码
function viewPassword(entryId) {
    fetch(`/view_password/${entryId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('密码: ' + data.password);
            } else {
                alert('获取密码失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('获取密码失败:', error);
            alert('无法获取密码，请重试。');
        });
}



// 防止XSS攻击
function escapeHTML(str) {
    if (str === null || str === undefined) {
        return '';
    }
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
