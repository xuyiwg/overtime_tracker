import sqlite3
from typing import List, Optional, Dict
from models import WorkRecord
from datetime import datetime, timedelta
from chinese_calendar import is_workday


DB_NAME = 'overtime.db'

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            clock_in TEXT,
            clock_out TEXT,
            is_leave BOOLEAN DEFAULT 0,
            overtime_hours REAL DEFAULT 0.0
        )
    ''')
    
    conn.commit()
    conn.close()

def add_work_record(record: WorkRecord) -> bool:
    """添加工作记录"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO work_records 
            (date, clock_in, clock_out, is_leave, overtime_hours)
            VALUES (?, ?, ?, ?, ?)
        ''', (record.date, None, record.clock_out, record.is_leave, record.overtime_hours))
        
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def update_work_record(record: WorkRecord) -> bool:
    """更新工作记录"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE work_records 
            SET clock_in = ?, clock_out = ?, is_leave = ?, overtime_hours = ?
            WHERE date = ?
        ''', (None, record.clock_out, record.is_leave, record.overtime_hours, record.date))
        
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_work_record(date: str) -> Optional[WorkRecord]:
    """获取指定日期的工作记录"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM work_records WHERE date = ?', (date,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return WorkRecord(
            id=row[0],
            date=row[1],
            clock_out=row[3],
            is_leave=bool(row[4]),
            overtime_hours=row[5]
        )
    return None

def get_current_month_records() -> List[WorkRecord]:
    """获取当前月份的工作记录"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 获取当前年月
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 构造月份范围查询条件
    if current_month < 10:
        date_pattern = f"{current_year}-0{current_month}-%"
    else:
        date_pattern = f"{current_year}-{current_month}-%"
    
    cursor.execute('SELECT * FROM work_records WHERE date LIKE ? ORDER BY date DESC', (date_pattern,))
    rows = cursor.fetchall()
    
    conn.close()
    
    return [
        WorkRecord(
            id=row[0],
            date=row[1],
            clock_out=row[3],
            is_leave=bool(row[4]),
            overtime_hours=row[5]
        )
        for row in rows
    ]

def get_remaining_workdays_current_month() -> int:
    """获取当前月份剩余的工作日数量（排除周末和已记录的日期）"""
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 获取当月第一天和最后一天
    first_day = datetime(current_year, current_month, 1)
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
    last_day = datetime(next_year, next_month, 1) - timedelta(days=1)
    
    # 获取已记录的日期
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if current_month < 10:
        date_pattern = f"{current_year}-0{current_month}-%"
    else:
        date_pattern = f"{current_year}-{current_month}-%"
    cursor.execute('SELECT date FROM work_records WHERE date LIKE ?', (date_pattern,))
    recorded_dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # 计算剩余工作日（含当天、调休，剔除节假日、已记录数据）
    remaining_workdays = 0
    current_date = now.date()
    
    date_to_check = current_date
    while date_to_check <= last_day.date():
        is_work_day = is_workday(date_to_check)
        if is_work_day:
            date_str = date_to_check.strftime('%Y-%m-%d')
            # 排除已记录的日期
            if date_str not in recorded_dates:
                remaining_workdays += 1
        date_to_check += timedelta(days=1)
    
    return remaining_workdays

def get_workdays_current_month() -> int:
    """获取当前月份总的工作日数量"""
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 获取当月第一天和最后一天
    first_day = datetime(current_year, current_month, 1)
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
    last_day = datetime(next_year, next_month, 1) - timedelta(days=1)

    # 计算总的工作日
    work_days = 0
    date_to_check = first_day.date()
    while date_to_check <= last_day.date():
        is_work_day = is_workday(date_to_check)
        if is_work_day:
            work_days += 1
        date_to_check += timedelta(days=1)
    
    return work_days


def get_monthly_statistics(year: int, month: int) -> Dict:
    """获取指定月份的统计信息"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 构造月份范围查询条件
    if month < 10:
        date_pattern = f"{year}-0{month}-%"
    else:
        date_pattern = f"{year}-{month}-%"
    
    cursor.execute('SELECT * FROM work_records WHERE date LIKE ? ORDER BY date', (date_pattern,))
    rows = cursor.fetchall()
    
    conn.close()
    
    records = [
        WorkRecord(
            id=row[0],
            date=row[1],
            clock_out=row[3],
            is_leave=bool(row[4]),
            overtime_hours=row[5]
        )
        for row in rows
    ]
    
    # 过滤掉请假的记录
    work_days = [record for record in records if not record.is_leave and record.clock_out]
    
    total_overtime = sum(record.overtime_hours for record in work_days)
    work_day_count = len(work_days)
    
    average_overtime = total_overtime / work_day_count if work_day_count > 0 else 0
    
    return {
        'total_overtime': round(total_overtime, 2),
        'work_day_count': work_day_count,
        'average_overtime': round(average_overtime, 2),
        'records': records,
        'year': year,
        'month': month
    }

def get_all_months_with_data() -> List[Dict]:
    """获取所有有数据的月份"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 获取所有不同的年月
    cursor.execute('''
        SELECT DISTINCT 
            strftime('%Y', date) as year,
            strftime('%m', date) as month
        FROM work_records 
        ORDER BY year DESC, month DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        year = int(row[0])
        month = int(row[1])
        stats = get_monthly_statistics(year, month)
        result.append(stats)
    
    return result

def get_statistics() -> dict:
    """获取当前月份的统计信息"""
    # 获取当前年月
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    records = get_current_month_records()
    total_work_days = get_workdays_current_month()

    leave_days = [record for record in records if record.is_leave]
    actual_work_days = total_work_days - len(leave_days)
    
    # 过滤掉请假的记录
    work_days = [record for record in records if not record.is_leave and record.clock_out]
    
    total_overtime = sum(record.overtime_hours for record in work_days)
    work_day_count = len(work_days)
    
    average_overtime = total_overtime / work_day_count if work_day_count > 0 else 0

    # 计算按当前加班时长的本月平均时长
    current_average_overtime = total_overtime / total_work_days
    
    # 计算剩余工作日
    remaining_workdays = get_remaining_workdays_current_month()
    
    # 计算达到1.5小时平均需要的额外加班时长
    target_average = 1.5
    total_workdays_needed = work_day_count + remaining_workdays
    total_overtime_needed = target_average * total_workdays_needed
    additional_overtime_needed = max(0, total_overtime_needed - total_overtime)
    
    # 计算每天需要的平均加班时长
    daily_average_needed = additional_overtime_needed / remaining_workdays if remaining_workdays > 0 else 0
    
    return {
        'total_overtime': round(total_overtime, 2),
        'work_day_count': work_day_count,
        'average_overtime': round(average_overtime, 2),
        'current_average_overtime': round(current_average_overtime, 2),
        'records': records,
        'year': current_year,
        'month': current_month,
        'total_work_days': total_work_days,
        'actual_work_days': actual_work_days,
        'remaining_workdays': remaining_workdays,
        'additional_overtime_needed': round(additional_overtime_needed, 2),
        'daily_average_needed': round(daily_average_needed, 2),
        'target_average': target_average
    }

def get_all_records() -> List[WorkRecord]:
    """获取所有工作记录"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM work_records ORDER BY date DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    return [
        WorkRecord(
            id=row[0],
            date=row[1],
            clock_out=row[3],
            is_leave=bool(row[4]),
            overtime_hours=row[5]
        )
        for row in rows
    ]

def delete_record(date: str) -> bool:
    """删除指定日期的记录"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM work_records WHERE date = ?', (date,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False
    finally:
        conn.close()