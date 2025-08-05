from flask import Flask, render_template, request, jsonify
from datetime import datetime
from database import init_database, add_work_record, get_work_record, get_statistics, delete_record, update_work_record, get_current_month_records, get_remaining_workdays_current_month, get_all_months_with_data
from models import WorkRecord

app = Flask(__name__)

# 初始化数据库
init_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/record', methods=['POST'])
def add_record():
    try:
        data = request.get_json()
        date = data.get('date')
        clock_out = data.get('clock_out')
        is_leave = data.get('is_leave', False)
        
        # 验证数据
        if not date:
            return jsonify({'success': False, 'message': '请选择日期'})
        
        # 创建工作记录
        record = WorkRecord(
            id=None,
            date=date,
            clock_out=clock_out if not is_leave else None,
            is_leave=is_leave,
            overtime_hours=0.0
        )
        
        # 如果不是请假，计算加班时长
        if not is_leave and clock_out:
            record.calculate_overtime()
        
        # 保存到数据库
        if add_work_record(record):
            return jsonify({'success': True, 'message': '记录保存成功'})
        else:
            return jsonify({'success': False, 'message': '保存失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'发生错误: {str(e)}'})

@app.route('/api/record/<date>', methods=['PUT'])
def update_record(date):
    try:
        data = request.get_json()
        clock_out = data.get('clock_out')
        is_leave = data.get('is_leave', False)
        
        # 创建工作记录
        record = WorkRecord(
            id=None,
            date=date,
            clock_out=clock_out if not is_leave else None,
            is_leave=is_leave,
            overtime_hours=0.0
        )
        
        # 如果不是请假，计算加班时长
        if not is_leave and clock_out:
            record.calculate_overtime()
        
        # 更新数据库
        if update_work_record(record):
            return jsonify({'success': True, 'message': '记录更新成功'})
        else:
            return jsonify({'success': False, 'message': '更新失败，记录不存在'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'发生错误: {str(e)}'})

@app.route('/api/records')
def get_records():
    # 只返回当前月份的统计数据
    stats = get_statistics()
    return jsonify(stats)

@app.route('/api/history')
def get_history():
    # 返回历史月份统计数据
    history_data = get_all_months_with_data()
    return jsonify({'history': history_data})

@app.route('/api/record/<date>', methods=['DELETE'])
def delete_record_api(date):
    if delete_record(date):
        return jsonify({'success': True, 'message': '记录删除成功'})
    else:
        return jsonify({'success': False, 'message': '删除失败'})

@app.route('/api/record/<date>')
def get_record(date):
    record = get_work_record(date)
    if record:
        return jsonify({
            'success': True,
            'data': {
                'date': record.date,
                'clock_out': record.clock_out,
                'is_leave': record.is_leave,
                'overtime_hours': record.overtime_hours
            }
        })
    else:
        return jsonify({'success': False, 'message': '记录不存在'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)