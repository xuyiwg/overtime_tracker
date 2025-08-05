## 加班时长统计
基于 Flask 的加班时长统计系统，用于记录和统计加班情况

### 功能特性

- 🗓️ 支持记录每日上下班时间
- 🏖️ 支持标记请假日期（请假不计入统计）
- 📊 实时统计总加班时长、工作日数、平均加班时长
- 📊 实时统计本月剩余工作及为达标所需工时
- 📱 响应式 Web 界面

### 项目结构

```bash
overtime_tracker/
├── app.py                 # Flask 主程序
├── database.py            # 数据库操作模块
├── models.py              # 数据模型
├── requirements.txt       # 项目依赖
├── templates/
│   └── index.html         # 主页面模板
├── static/
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── script.js      # JavaScript 文件
└── overtime.db            # SQLite 数据库文件（自动生成）

```
## 快速开始

### 使用 uv 创建虚拟环境

```bash
# 安装 uv（如果还没有安装）
pip install uv

# 克隆项目
git clone <repository-url>
cd overtime_tracker

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

uv pip install -r requirements.txt

```

### 启动应用

```bash
python app.py
```

应用将在 http://localhost:5000 启动

## 使用说明
### 添加工作记录
1.选择日期
2.如果是请假日期，勾选"请假"复选框
3.输入上班时间和下班时间（请假时会自动禁用）
4.点击"保存"按钮

### 统计计算规则

- 标准下班时间：17:00
- 加班时长计算：下班时间 - 17:00
- 请假日期：不计入工作日统计和加班时长统计
- 平均加班时长：总加班时长 ÷ 实际工作日数

### 数据库结构

数据库文件：`overtime.db`
表结构：

```sql
CREATE TABLE work_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    clock_in TEXT,
    clock_out TEXT,
    is_leave BOOLEAN DEFAULT 0,
    overtime_hours REAL DEFAULT 0.0
);
```

## 部署建议

### 生产环境部署

```bash
# 设置生产环境变量
export FLASK_ENV=production
export FLASK_DEBUG=False

# 使用 gunicorn 部署（需要安装）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

