from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkRecord:
    id: Optional[int]
    date: str  # YYYY-MM-DD
    clock_out: str  # HH:MM 格式
    is_leave: bool  # 是否请假
    overtime_hours: float  # 加班时长（小时）
    
    def __post_init__(self):
        if self.overtime_hours is None and self.clock_out and not self.is_leave:
            self.calculate_overtime()
    
    def calculate_overtime(self):
        """计算加班时长"""
        if self.is_leave:
            self.overtime_hours = 0.0
            return
            
        # 标准下班时间 17:00
        standard_end = datetime.strptime("17:00", "%H:%M")
        
        try:
            clock_out_time = datetime.strptime(self.clock_out, "%H:%M")
            if clock_out_time > standard_end:
                # 计算加班时长（小时）
                overtime_delta = clock_out_time - standard_end
                self.overtime_hours = overtime_delta.total_seconds() / 3600
            else:
                self.overtime_hours = 0.0
        except ValueError:
            self.overtime_hours = 0.0