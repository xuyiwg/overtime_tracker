from datetime import timedelta, datetime, date
from chinese_calendar import is_holiday, is_workday




def get_remaining_workdays_current_month() -> int:
    """获取当前月份剩余的工作日数量（排除周末和已记录的日期）"""
    now = date(2025, 10, 13)
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

    recorded_dates = ['2025-10-12']
    
    # 计算剩余工作日（周一到周五，排除已记录和周末）
    remaining_workdays = 0
    
    date_to_check = now 
    while date_to_check <= last_day.date():
        work_day = is_workday(date_to_check)
        if work_day:
            date_str = date_to_check.strftime('%Y-%m-%d')
            # 排除已记录的日期
            if date_str not in recorded_dates:
                remaining_workdays += 1
        date_to_check += timedelta(days=1)
    
    return remaining_workdays


workdays = get_remaining_workdays_current_month()
print(f"当前月份剩余工作日数量: {workdays}")