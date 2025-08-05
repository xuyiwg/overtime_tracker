// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
    
    // 设置默认值为"否"
    document.getElementById('is_leave').value = 'false';
    
    // 加载当前月份记录
    loadRecords();
    
    // 加载历史统计
    loadHistoryRecords();
    
    // 表单提交事件
    document.getElementById('recordForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveRecord();
    });
    
    // 请假下拉框事件
    document.getElementById('is_leave').addEventListener('change', function() {
        const isLeave = this.value === 'true';
        document.getElementById('clock_out').disabled = isLeave;
    });
    
    // 取消编辑按钮事件
    document.getElementById('cancelBtn').addEventListener('click', cancelEdit);
    
    // 日期变化事件
    document.getElementById('date').addEventListener('change', function() {
        const isEditMode = document.getElementById('is_edit_mode').value === 'true';
        if (isEditMode) {
            const originalDate = document.getElementById('original_date') ? 
                document.getElementById('original_date').value : null;
            
            if (originalDate && this.value !== originalDate) {
                // 如果在编辑模式下更改了日期，询问用户意图
                const userChoice = confirm(
                    `您正在编辑 ${originalDate} 的记录，现在选择的日期是 ${this.value}。\n` +
                    `点击"确定"将加载 ${this.value} 的记录进行编辑。\n` +
                    `点击"取消"将退出编辑模式并保持 ${this.value} 作为新记录的日期。`
                );
                
                if (userChoice) {
                    // 加载新日期的记录进行编辑
                    editRecord(this.value);
                } else {
                    // 退出编辑模式，保持新日期用于添加新记录
                    resetForm();
                    document.getElementById('date').value = this.value;
                }
            }
        }
    });
});

// 加载记录和统计信息（只加载当前月份）
function loadRecords() {
    // 加载统计信息
    fetch('/api/records')
        .then(response => response.json())
        .then(data => {
            // 更新统计显示
            document.getElementById('workDays').textContent = data.work_day_count;
            document.getElementById('totalOvertime').textContent = data.total_overtime;
            document.getElementById('averageOvertime').textContent = data.average_overtime;
            
            // 更新月份显示
            const monthDisplay = `${data.year}年${data.month}月`;
            document.querySelectorAll('[id^="current_month_display"]').forEach(element => {
                element.textContent = monthDisplay;
            });
            
            // 更新记录数量显示
            document.getElementById('record_count_display').textContent = `共 ${data.records.length} 条记录`;
            
            // 更新目标进度显示
            updateTargetProgress(data);
            
            // 加载记录列表
            loadRecordList(data.records);
            
            // 重新加载历史统计（因为可能有新数据）
            loadHistoryRecords();
        })
        .catch(error => {
            showToast('danger', '错误', '加载数据失败: ' + error.message);
        });
}

// 加载历史统计
function loadHistoryRecords() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            loadHistoryList(data.history);
            // 更新历史记录数量显示
            document.getElementById('history_count_display').textContent = `共 ${data.history.length} 个月份`;
        })
        .catch(error => {
            console.error('加载历史数据失败:', error);
            // 即使历史数据加载失败，也不影响主要功能
        });
}

// 更新目标进度显示
function updateTargetProgress(data) {
    // 显示或隐藏目标进度卡片
    const targetProgress = document.getElementById('targetProgress');
    if (data.remaining_workdays > 0) {
        targetProgress.style.display = 'block';
        
        // 更新各个数值
        document.getElementById('remainingWorkdays').textContent = data.remaining_workdays;
        document.getElementById('additionalOvertimeNeeded').textContent = data.additional_overtime_needed;
        document.getElementById('dailyAverageNeeded').textContent = data.daily_average_needed;
        document.getElementById('targetAverage').textContent = data.target_average;
        
        // 更新进度条
        const currentProgress = data.average_overtime;
        const targetProgressPercent = Math.min(100, (currentProgress / data.target_average) * 100);
        document.getElementById('progressBar').style.width = targetProgressPercent + '%';
        document.getElementById('progressText').textContent = Math.round(targetProgressPercent) + '%';
        
        // 更新进度描述
        document.getElementById('dailyNeededText').textContent = data.daily_average_needed;
        
        // 根据进度改变进度条颜色
        const progressBar = document.getElementById('progressBar');
        if (currentProgress >= data.target_average) {
            progressBar.className = 'progress-bar bg-success';
        } else if (currentProgress >= data.target_average * 0.8) {
            progressBar.className = 'progress-bar bg-warning';
        } else {
            progressBar.className = 'progress-bar bg-danger';
        }
    } else {
        targetProgress.style.display = 'none';
    }
}

// 加载记录列表
function loadRecordList(records) {
    const tbody = document.getElementById('recordsBody');
    tbody.innerHTML = '';
    
    if (records.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6" class="text-center">暂无数据</td>';
        tbody.appendChild(row);
        return;
    }
    
    records.forEach(record => {
        const row = document.createElement('tr');
        
        // 计算星期
        const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        const dateObj = new Date(record.date);
        const weekDay = weekDays[dateObj.getDay()];
        
        // 状态显示
        let statusHtml = '';
        let overtimeHtml = '';
        
        if (record.is_leave) {
            statusHtml = '<span class="badge bg-secondary">请假</span>';
            overtimeHtml = '-';
        } else if (record.clock_out) {
            statusHtml = '<span class="badge bg-success">工作日</span>';
            overtimeHtml = `<span class="${record.overtime_hours > 0 ? 'text-danger fw-bold' : ''}">${record.overtime_hours} 小时</span>`;
        } else {
            statusHtml = '<span class="badge bg-light text-dark">未记录</span>';
            overtimeHtml = '-';
        }
        
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${weekDay}</td>
            <td>${record.clock_out || '-'}</td>
            <td>${statusHtml}</td>
            <td>${overtimeHtml}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="editRecord('${record.date}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRecord('${record.date}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// 加载历史统计列表
function loadHistoryList(historyData) {
    const tbody = document.getElementById('historyBody');
    tbody.innerHTML = '';
    
    if (historyData.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">暂无历史数据</td>';
        tbody.appendChild(row);
        return;
    }
    
    historyData.forEach(monthData => {
        const row = document.createElement('tr');
        
        // 格式化年月显示
        const yearMonth = `${monthData.year}年${monthData.month}月`;
        
        // 目标达成状态
        let targetStatus = '';
        const targetAverage = 1.5;
        if (monthData.work_day_count === 0) {
            targetStatus = '<span class="badge bg-light text-dark">无数据</span>';
        } else if (monthData.average_overtime >= targetAverage) {
            targetStatus = '<span class="badge bg-success">达成</span>';
        } else {
            targetStatus = '<span class="badge bg-warning">未达成</span>';
        }
        
        // 格式化数值显示
        const totalOvertime = monthData.total_overtime > 0 ? 
            `<span class="${monthData.total_overtime > 10 ? 'text-danger fw-bold' : ''}">${monthData.total_overtime}</span>` : 
            monthData.total_overtime;
            
        const averageOvertime = monthData.average_overtime > 0 ? 
            `<span class="${monthData.average_overtime >= targetAverage ? 'text-success' : 'text-warning'} fw-bold">${monthData.average_overtime}</span>` : 
            monthData.average_overtime;
        
        row.innerHTML = `
            <td>${yearMonth}</td>
            <td>${monthData.work_day_count}</td>
            <td>${totalOvertime} 小时</td>
            <td>${averageOvertime} 小时</td>
            <td>${targetStatus}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// 保存记录
function saveRecord() {
    const isEditMode = document.getElementById('is_edit_mode').value === 'true';
    const date = document.getElementById('date').value;
    
    const formData = {
        date: date,
        clock_out: document.getElementById('clock_out').value,
        is_leave: document.getElementById('is_leave').value === 'true'
    };
    
    const method = isEditMode ? 'PUT' : 'POST';
    const url = isEditMode ? `/api/record/${date}` : '/api/record';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        showToast(data.success ? 'success' : 'danger', '提示', data.message);
        if (data.success) {
            resetForm();
            // 重新加载当前月份数据
            loadRecords();
        }
    })
    .catch(error => {
        showToast('danger', '错误', '网络错误: ' + error.message);
    });
}

// 编辑记录
function editRecord(date) {
    fetch(`/api/record/${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const record = data.data;
                
                // 保存原始日期用于取消时恢复
                if (!document.getElementById('original_date')) {
                    const originalDateInput = document.createElement('input');
                    originalDateInput.type = 'hidden';
                    originalDateInput.id = 'original_date';
                    originalDateInput.value = record.date;
                    document.getElementById('recordForm').appendChild(originalDateInput);
                } else {
                    document.getElementById('original_date').value = record.date;
                }
                
                document.getElementById('date').value = record.date;
                document.getElementById('is_leave').value = record.is_leave ? 'true' : 'false';
                document.getElementById('clock_out').value = record.clock_out || '17:00';
                
                document.getElementById('is_edit_mode').value = 'true';
                document.getElementById('submitBtn').innerHTML = '<i class="fas fa-edit"></i>';
                document.getElementById('cancelBtn').style.display = 'block';
                
                document.getElementById('clock_out').disabled = record.is_leave;
                
                document.getElementById('recordForm').scrollIntoView({ behavior: 'smooth' });
            } else {
                showToast('danger', '错误', data.message);
            }
        })
        .catch(error => {
            showToast('danger', '错误', '加载记录失败: ' + error.message);
        });
}

// 删除记录
function deleteRecord(date) {
    if (confirm('确定要删除 ' + date + ' 的记录吗？')) {
        fetch(`/api/record/${date}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            showToast(data.success ? 'success' : 'danger', '提示', data.message);
            if (data.success) {
                // 重新加载当前月份数据
                loadRecords();
            }
        })
        .catch(error => {
            showToast('danger', '错误', '删除失败: ' + error.message);
        });
    }
}

// 重置表单函数
function resetForm() {
    document.getElementById('recordForm').reset();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
    document.getElementById('is_leave').value = 'false'; // 重置为默认值"否"
    document.getElementById('is_edit_mode').value = 'false';
    document.getElementById('submitBtn').innerHTML = '<i class="fas fa-save"></i>';
    document.getElementById('cancelBtn').style.display = 'none';
    document.getElementById('clock_out').disabled = false;
    
    // 移除原始日期存储
    const originalDateInput = document.getElementById('original_date');
    if (originalDateInput) {
        originalDateInput.remove();
    }
}

// 取消编辑函数
function cancelEdit() {
    resetForm();
}

// 显示提示信息
function showToast(type, title, message) {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    // 移除之前的背景类
    toast.className = 'toast';
    
    toast.classList.add('show', 'bg-' + type);
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    // 自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}