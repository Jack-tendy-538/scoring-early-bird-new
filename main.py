# licensed under the MIT License.
# partly using AI code generation, but mostly hand-coded.
import tkinter as tk
import tkinter.messagebox as ms
import subprocess, yaml, json
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
import sv_ttk
import tkinter.ttk as ttk

# sv_ttk.set_theme('light')
class ContinuousScoring:
    """连续考勤评分系统，替代生成器的可序列化类"""
    
    def __init__(self, max_days=7):
        self.scoring = [0]  # 连续出勤天数记录
        self.history = []   # 历史出勤记录
        self.max_days = max_days
        self.current_day = 0
    
    def record_attendance(self, today_arrived):
        """记录当天考勤"""
        if today_arrived:
            self.scoring[-1] += 1
        else:
            self.scoring.append(0)
        
        self.history.append(today_arrived)
        self.current_day += 1
        
        # 只保留最近max_days*2天的记录，避免内存过度增长
        if len(self.history) > self.max_days * 2:
            self.history = self.history[-self.max_days*2:]
    
    def calculate_scores(self):
        """计算3天和7天连续出勤分数"""
        # 不使用最近max_days天的记录进行计算
#        recent_history = self.history[-self.max_days:] if len(self.history) >= self.max_days else self.history
        recent_history = self.history[:]
        # 重建连续出勤记录
        scoring = [0]
        for arrived in recent_history:
            if arrived:
                scoring[-1] += 1
            else:
                scoring.append(0)
        
        # 计算分数
        # 将 >=7 视为7天奖励，避免因 scoring 中有 >7 的值而漏计
#        _7_day = sum(1 for j in scoring if j >= 7)
#        _3_day = sum(1 for j in scoring if 3 <= j < 7)
        _3_day, _7_day = 0,0
        while scoring:
            n = scoring.pop(0)
            if n < 3:
                # 不加分
                continue
            if 3 <= n< 7:
                # 加3天的分
                _3_day+=1
                continue
            # 如果来了10天，那么既要加7天的，也要加3天的
            _7_day += 1
            scoring.append(n-7)
        return _3_day, _7_day
    
    def get_current_streak(self):
        """获取当前连续出勤天数"""
        return self.scoring[-1] if self.scoring else 0
    
    def get_total_attendance(self):
        """获取总出勤天数"""
        return sum(self.history)
    
    def get_attendance_rate(self):
        """获取出勤率"""
        if len(self.history) == 0:
            return 0
        return sum(self.history) / len(self.history)
    
    def reset_data(self):
        """重置数据，开始新的一周"""
        self.scoring = [0]
        self.history = []
        self.current_day = 0
    
    def to_dict(self):
        """转换为可序列化的字典"""
        return {
            'scoring': self.scoring,
            'history': self.history,
            'max_days': self.max_days,
            'current_day': self.current_day
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典恢复对象（包含简单校验与容错）"""
        # 解析并校验 max_days
        max_days_raw = data.get('max_days', 7)
        try:
            max_days = int(max_days_raw)
            if max_days < 1:
                max_days = 7
        except Exception:
            max_days = 7

        obj = cls(max_days)
        # 确保 scoring 为整数列表，至少包含一个元素
        raw_scoring = data.get('scoring', [0]) or [0]
        try:
            obj.scoring = [int(x) for x in raw_scoring]
        except Exception:
            obj.scoring = [0]

        # 确保 history 为布尔列表
        raw_history = data.get('history', []) or []
        try:
            obj.history = [bool(x) for x in raw_history]
        except Exception:
            obj.history = []

        # current_day 尽量与 history 长度保持一致性
        try:
            obj.current_day = int(data.get('current_day', len(obj.history)))
        except Exception:
            obj.current_day = len(obj.history)

        if not obj.scoring:
            obj.scoring = [0]

        return obj

class AttendanceSystem:
    def __init__(self):
        self.cwd = Path.cwd()
        self.setup_directories()
        self.setting = self.load_settings()
        # 支持两种 display 配置位置：display.win.* 或 display.*（向后兼容）
        display = self.setting.get('display', {}) or {}
        win_cfg = display.get('win') if isinstance(display.get('win'), dict) else {}
        font = win_cfg.get('font') or display.get('font') or 'Microsoft YaHei UI'
        font_size = win_cfg.get('font_size') or display.get('font_size') or 10
        self.font_chinese = (font, font_size)
    
    def setup_directories(self):
        """创建必要的目录"""
        if not (self.cwd/'eggs').exists():
            (self.cwd/'eggs').mkdir()
        if not (self.cwd/'bacon').exists():
            (self.cwd/'bacon').mkdir()
        if not (self.cwd/'reports').exists():
            (self.cwd/'reports').mkdir()
    
    def load_settings(self):
        """加载或创建设置文件"""
        settings_file = self.cwd/'bacon/Setting.yml'
    
        if not settings_file.exists():
            # 创建默认设置
            default_settings = {
                'points': {
                    '_3_days': 1,
                    '_7_days': 3
                },
                'timer': {
                    'on': True,
                    'morning': '7:05',
                    'afternoon': '13:05'
                },
                'display': {
                    'win': {
                        'row_num': 7,
                        'font': 'Microsoft YaHei UI',
                        'font_size': 10
                    },
                    'md': {
                        'column_num': 12
                    }
                },
                'namelist': ['sexy','stupid','sweet','sleepy']
            }
            # 将默认设置写入文件
            with open(settings_file, 'w', encoding='utf-8') as fp:
                yaml.dump(default_settings, fp, allow_unicode=True)
            return default_settings
        else:
            # 尝试不同的编码读取文件
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
            for encoding in encodings:
                try:
                    with open(settings_file, 'r', encoding=encoding) as fp:
                        return yaml.safe_load(fp)
                except (UnicodeDecodeError, yaml.YAMLError):
                    continue
        
            # 如果所有编码都失败，使用错误处理方式读取
            with open(settings_file, 'r', encoding='utf-8', errors='replace') as fp:
                return yaml.safe_load(fp)
    
    def load_student_data(self, session):
        """加载学生数据"""
        data_file = self.cwd/f'eggs/{session}_data.json'
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从字典恢复ContinuousScoring对象
            students = {}
            for name, student_data in data.items():
                students[name] = ContinuousScoring.from_dict(student_data)
            
            return students
        else:
            # 创建新的学生数据，使用配置中的 max_days（若存在）
            students = {}
            raw_max = self.setting.get('max_days', 7)
            try:
                max_days = int(raw_max)
                if max_days < 1:
                    max_days = 7
            except Exception:
                max_days = 7

            for name in self.setting['namelist']:
                students[name] = ContinuousScoring(max_days=max_days)
            
            self.save_student_data(session, students)
            return students
    
    def save_student_data(self, session, students):
        """保存学生数据"""
        data_file = self.cwd/f'eggs/{session}_data.json'
        
        # 转换为可序列化的字典
        data = {}
        for name, student in students.items():
            data[name] = student.to_dict()
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def record_attendance(self, session, present_students):
        """记录考勤"""
        students = self.load_student_data(session)
        
        # 更新每个学生的考勤记录
        for name, student in students.items():
            arrived = name in present_students
            student.record_attendance(arrived)
        
        # 保存更新后的数据
        self.save_student_data(session, students)
        
        # 计算并显示分数
        scores = {}
        for name, student in students.items():
            scores[name] = student.calculate_scores()
        
        return scores
    
    def reset_all_data(self):
        """重置所有学生的数据，开始新的一周"""
        sessions = ["morning", "afternoon"]
        for session in sessions:
            students = self.load_student_data(session)
            for student in students.values():
                student.reset_data()
            self.save_student_data(session, students)
    
    def generate_summary_report(self):
        """生成汇总报告并保存为Markdown文件，显示每个人的上午、下午分数和总分（简化版）"""
        # 加载上午和下午的数据
        morning_students = self.load_student_data("morning")
        afternoon_students = self.load_student_data("afternoon")
        
        # 获取学生列表
        students = self.setting['namelist']
        
        # 准备报告数据
        report_data = []
        
        for name in students:
            morning_student = morning_students.get(name, ContinuousScoring())
            afternoon_student = afternoon_students.get(name, ContinuousScoring())
            
            # 计算分数
            morning_3day, morning_7day = morning_student.calculate_scores()
            afternoon_3day, afternoon_7day = afternoon_student.calculate_scores()
            
            # 计算各部分分数
            morning_total = morning_3day * self.setting['points']['_3_days'] + morning_7day * self.setting['points']['_7_days']
            afternoon_total = afternoon_3day * self.setting['points']['_3_days'] + afternoon_7day * self.setting['points']['_7_days']
            total_score = morning_total + afternoon_total
            
            report_data.append({
                'name': name,
                'morning_total': morning_total,
                'afternoon_total': afternoon_total,
                'total_score': total_score
            })
        
        # 获取阶段时长
        max_day = 7  # 默认值
        if students and name in morning_students:
            max_day = len(morning_students[name].history)
        
        # 生成Markdown表格
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        md_content = f"""# 阶段性考勤汇总报告

**生成时间**: {timestamp}  
**本阶段结束，开始新的一阶段**
> 本阶段时长: {max_day}天

## 本阶段分数统计

| 姓名 | 上午分数 | 下午分数 | 总分数 |
|------|----------|----------|--------|
"""
        
        # 添加每个学生的数据行
        for data in report_data:
            md_content += f"| {data['name']} | **{data['morning_total']}** | **{data['afternoon_total']}** | **{data['total_score']}** |\n"
        
        # 添加分数说明
        md_content += f"""
## 分数说明

- 连续出勤3天及以上但不足7天: {self.setting['points']['_3_days']}分/次
- 连续出勤7天: {self.setting['points']['_7_days']}分/次

## 注意

本阶段考勤数据已重置，下一阶段将重新开始统计。
    """
        
        # 保存Markdown文件
        report_file = self.cwd / 'reports' / f'考勤汇总_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # 重置所有数据，开始新的一周
        self.reset_all_data()
        
        return report_file
    
    def load_breakpoint(self, session):
        """加载断点数据"""
        breakpoint_file = self.cwd/'eggs/breakpoint.json'
        
        if breakpoint_file.exists():
            with open(breakpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 返回指定session的暂存数据
            return data.get(session, [])
        else:
            return []
    
    def save_breakpoint(self, session, present_students):
        """保存断点数据"""
        breakpoint_file = self.cwd/'eggs/breakpoint.json'
        
        # 加载现有的断点数据
        if breakpoint_file.exists():
            with open(breakpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # 更新指定session的暂存数据
        data[session] = present_students
        
        # 保存更新后的数据
        with open(breakpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def clear_breakpoint(self, session):
        """清除指定session的断点数据"""
        breakpoint_file = self.cwd/'eggs/breakpoint.json'
        
        if breakpoint_file.exists():
            with open(breakpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 移除指定session的数据
            if session in data:
                del data[session]
            
            # 如果还有其他session的数据，保存；否则删除文件
            if data:
                with open(breakpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                breakpoint_file.unlink()

class AttendanceGUI:
    """考勤系统GUI"""
    
    def __init__(self):
        self.system = AttendanceSystem()
        self.win = tk.Tk()
        # 从设置读取主题，默认 light
        theme = self.system.setting.get('display', {}).get('theme', 'light')
        sv_ttk.set_theme(theme)  # 在创建 root 后立即设置主题

        # 全局样式配置：字体与常用控件样式
        style = ttk.Style(self.win)
        font_chinese = self.system.font_chinese
        style.configure('TLabel', font=font_chinese)
        style.configure('TButton', font=font_chinese)
        style.configure('TCheckbutton', font=font_chinese)
        style.configure('Accent.TButton', font=font_chinese)  # sv_ttk 提供的强调按钮样式
        style.configure('Countdown.TLabel', foreground='blue', font=font_chinese)

        self.setup_ui()
        self.attendance_windows = {}  # 存储考勤窗口的引用
    
    def setup_ui(self):
        """设置用户界面（使用 ttk 控件以便 sv_ttk 生效）"""
        self.win.title("考勤系统")
        self.win.geometry("300x250")

        # 使用设置中的字体（样式中已配置）
        ttk.Label(self.win, text='请选择一个操作').pack(pady=10)

        ttk.Button(self.win, text='上午考勤', command=self.append_morning, width=15).pack(pady=5)
        ttk.Button(self.win, text='下午考勤', command=self.append_afternoon, width=15).pack(pady=5)
        # 使用强调样式，视觉更突出
        ttk.Button(self.win, text='生成汇总报告', command=self.generate_summary,
                   width=15, style='Accent.TButton').pack(pady=5)

        ttk.Label(self.win, text='点击按钮记录考勤').pack(pady=10)
    
    def append_morning(self):
        """上午考勤"""
        self.take_attendance("morning", "上午")
    
    def append_afternoon(self):
        """下午考勤"""
        self.take_attendance("afternoon", "下午")
    
    def generate_summary(self):
        """生成汇总报告"""
        try:
            result = ms.askyesno("确认", "生成报告后将重置本周数据并开始新的一周，是否继续?")
            if not result:
                return
            report_file = self.system.generate_summary_report()
            ms.showinfo("报告生成成功", f"汇总报告已生成:\n{report_file}\n\n本周数据已重置，下周将重新开始统计。")
            # 尝试打开报告文件
            try:
                subprocess.Popen(['start', '', str(report_file)], shell=True)
            except:
                pass  # 如果打开失败，忽略错误
        except Exception as e:
            ms.showerror("错误", f"生成报告时出错:\n{str(e)}")
    
    def submit_attendance(self, session, session_name, attendance_win, vars, students_list):
        """提交考勤记录"""
        settings_pronoun = self.system.setting.get('display', {}).get('win', {}).get('pronoun', '同学')
        try:
            # 获取选中的学生
            present_students = [name for name, var in vars.items() if var.get()]
            
            # 从settings.yml中读取display/win/pronoun设置

            if not present_students:
                ms.showwarning("警告", "请至少选择一名%s后再提交考勤。" % settings_pronoun)
                return
            
            # 记录考勤
            scores = self.system.record_attendance(session, present_students)
            
            # 清除断点数据
            self.system.clear_breakpoint(session)
            
            # 加载学生数据用于显示
            students_data = self.system.load_student_data(session)
            
            # 显示结果
            result_text = f"{session_name}今日已签到{len(students_data)}"
            
            ms.showinfo("考勤结果", result_text)
            attendance_win.destroy()
            
            # 从窗口字典中移除
            if session in self.attendance_windows:
                del self.attendance_windows[session]
                
        except KeyError as e:
            ms.showerror("数据错误", f"{settings_pronoun}数据不完整: {str(e)}\n请检查设置文件中的{settings_pronoun}名单。")
        except Exception as e:
            ms.showerror("错误", f"提交考勤时出错:\n{str(e)}")
    
    def save_breakpoint_data(self, session, session_name, vars):
        """保存断点数据（暂存）"""
        try:
            # 获取选中的学生
            present_students = [name for name, var in vars.items() if var.get()]
            
            # 保存到断点文件
            self.system.save_breakpoint(session, present_students)
            
            ms.showinfo("暂存成功", f"{session_name}考勤数据已暂存，下次打开时会自动恢复。")
            
        except Exception as e:
            ms.showerror("错误", f"暂存数据时出错:\n{str(e)}")
    
    def parse_time_string(self, time_str):
        """解析时间字符串，返回 (小时, 分钟)"""
        try:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1])
            return hour, minute
        except (ValueError, IndexError):
            # 解析失败时返回默认值：早上(7:05)或下午(13:05)
            if "morning" in time_str:
                return 7, 5
            else:
                return 13, 5
    
    def start_auto_submit_timer(self, session, session_name, attendance_win, vars, students):
        """启动自动提交定时器"""
        # 检查是否启用定时器
        timer_enabled = self.system.setting.get('timer', {}).get('on', True)
        if not timer_enabled:
            return
        
        # 计算目标时间
        now = datetime.now()
        
        # 从设置中获取时间
        if session == "morning":
            time_str = self.system.setting.get('timer', {}).get('morning', '7:05')
        else:  # afternoon
            time_str = self.system.setting.get('timer', {}).get('afternoon', '13:05')
        
        # 解析时间字符串
        hour, minute = self.parse_time_string(time_str)
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # 如果目标时间已经过去，则设置为明天的同一时间
        if target_time < now:
            target_time += timedelta(days=1)
        
        # 计算等待时间（秒）
        wait_seconds = (target_time - now).total_seconds()
        
        # 创建定时器线程
        timer_thread = threading.Timer(wait_seconds, self.auto_submit, 
                                      [session, session_name, attendance_win, vars, students])
        timer_thread.daemon = True
        timer_thread.start()
        
        # 更新窗口标题显示自动提交时间
        time_str_display = target_time.strftime("%H:%M")
        attendance_win.title(f"{session_name}考勤 - 自动提交时间: {time_str_display}")
        
        # 添加倒计时标签
        countdown_label = tk.Label(attendance_win, text=f"自动提交倒计时: {int(wait_seconds//60)}分钟", 
                                  font=self.system.font_chinese, fg="blue")
        countdown_label.pack(pady=5)
        
        # 启动倒计时更新
        self.update_countdown(countdown_label, wait_seconds, session, session_name, 
                             attendance_win, vars, students)
    
    def update_countdown(self, label, remaining_seconds, session, session_name, 
                        attendance_win, vars, students):
        """更新倒计时显示"""
        if remaining_seconds > 0 and attendance_win.winfo_exists():
            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            label.config(text=f"自动提交倒计时: {minutes}分{seconds}秒")
            # 1秒后再次更新
            attendance_win.after(1000, self.update_countdown, label, remaining_seconds-1, 
                               session, session_name, attendance_win, vars, students)
    
    def auto_submit(self, session, session_name, attendance_win, vars, students):
        """自动提交考勤"""
        if attendance_win.winfo_exists():
            # 在主线程中执行提交
            attendance_win.after(0, self.submit_attendance, session, session_name, 
                               attendance_win, vars, students)
    
    def take_attendance(self, session, session_name):
        """执行考勤记录（改用 ttk 控件）"""
        # 创建考勤窗口
        attendance_win = tk.Toplevel(self.win)
        attendance_win.title(f"{session_name}考勤")

        # 存储窗口引用
        self.attendance_windows[session] = attendance_win

        # 获取学生列表和显示设置
        students = self.system.setting['namelist']
        display = self.system.setting.get('display', {}) or {}
        columns_per_row = display.get('win', {}).get('row_num', display.get('columns_per_row', 7))

        # 使用 ttk.Frame
        main_frame = ttk.Frame(attendance_win, padding=10)
        main_frame.pack(fill='both', expand=True)
        settings_pronoun = self.system.setting.get('display', {}).get('win', {}).get('pronoun', '他们')
        ttk.Label(main_frame, text=f"请{session_name}早到的{settings_pronoun}上来打勾:").pack(pady=(0, 10))

        # 复选框容器
        checkboxes_frame = ttk.Frame(main_frame)
        checkboxes_frame.pack(fill='both', expand=True)

        vars = {}
        checkbuttons = []

        for i, name in enumerate(students):
            row = i // columns_per_row
            col = i % columns_per_row

            vars[name] = tk.BooleanVar()
            cb = ttk.Checkbutton(checkboxes_frame, text=name, variable=vars[name])
            cb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
            checkbuttons.append(cb)

        # 加载断点数据并恢复选中状态
        breakpoint_students = self.system.load_breakpoint(session)
        for name in breakpoint_students:
            if name in vars:
                vars[name].set(True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # 暂存和提交按钮（注意用 ttk，不使用 bg 参数）
        ttk.Button(button_frame, text="暂存",
                   command=lambda: self.save_breakpoint_data(session, session_name, vars),
                   width=10).pack(side='left', padx=5)
        ttk.Button(button_frame, text="立即提交",
                   command=lambda: self.submit_attendance(session, session_name, attendance_win, vars, students),
                   width=10, style='Accent.TButton').pack(side='left', padx=5)

        # 启动自动提交定时器（倒计时标签使用自定义样式）
        self.start_auto_submit_timer(session, session_name, attendance_win, vars, students)

        attendance_win.update()
        attendance_win.minsize(attendance_win.winfo_width(), attendance_win.winfo_height())
    
    def run(self):
        """运行应用程序"""
        self.win.mainloop()

# 运行应用程序
if __name__ == "__main__":
    app = AttendanceGUI()
    app.run()
