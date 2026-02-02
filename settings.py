# licensed under the MIT License.
# partly using AI code generation, but mostly hand-coded.
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml, csv
import os
import sv_ttk
from pathlib import Path
import sys

def import_csv_namelist(sa):
    """从CSV文件导入学生名单"""
    try:
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[
                ("CSV文件", "*.csv"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return  # 用户取消了选择
            
        # 读取CSV文件
        imported_names = []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # 尝试不同的分隔符
            for encoding in ['utf-8', 'gbk', 'latin-1']:
                try:
                    csvfile.seek(0)  # 重置文件指针
                    # 自动检测分隔符
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample)
                    
                    reader = csv.reader(csvfile, dialect)
                    for row in reader:
                        if row:  # 跳过空行
                            # 假设第一列是学生姓名
                            name = row[0].strip()
                            if name and name not in imported_names:
                                imported_names.append(name)
                    break  # 成功读取，跳出循环
                except (UnicodeDecodeError, csv.Error):
                    continue
        
        if not imported_names:
            messagebox.showwarning("警告", "未找到有效的学生姓名数据")
            return
            
        # 显示导入预览
        preview_text = f"找到 {len(imported_names)} 个学生:\n" + "\n".join(imported_names[:10])
        if len(imported_names) > 10:
            preview_text += f"\n... 还有 {len(imported_names) - 10} 个学生"
            
        result = messagebox.askyesno(
            "确认导入", 
            f"{preview_text}\n\n是否导入这些学生？"
        )
        
        if result:
            # 添加到现有名单（去重）
            current_list = list(sa.config["namelist"])
            for name in imported_names:
                if name not in current_list:
                    current_list.append(name)
                    
            sa.config["namelist"] = current_list
            sa.namelist_var.set(current_list)
            sa.update_stats()
            messagebox.showinfo("成功", f"成功导入 {len(imported_names)} 个学生")
            
    except Exception as e:
        messagebox.showerror("错误", f"导入CSV文件失败:\n{str(e)}")

def update_stats(sa):
    """更新统计信息显示"""
    # 确保这个方法存在并更新学生数量显示
    student_count = len(sa.config["namelist"])
    # 如果有统计标签，更新它
    # 例如: self.stats_label.config(text=f"当前学生总数: {student_count} 人")

class SettingsApp:
    def __init__(self, config_path=None):
        # 设置配置文件路径
        if config_path is None:
            self.config_path = Path.cwd() / 'bacon' / 'Setting.yml'
        else:
            self.config_path = Path(config_path)
        
        # 确保配置目录存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.import_csv_namelist = import_csv_namelist.__get__(self)
        self.config = self.load_config()
        
        # 创建主窗口并应用 sv_ttk 主题
        self.root = tk.Tk()
        self.root.title("考勤系统设置")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        self.root.minsize(500, 400)  # 设置最小尺寸，防止过小
        
        # 设置主题，从配置中读取或使用默认值
        theme = self.config.get('display', {}).get('theme', 'light')
        sv_ttk.set_theme(theme)
        
        # 尝试设置图标
        try:
            self.root.iconbitmap(default="")
        except:
            pass
        
        self.create_ui()
        
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    # 确保配置结构完整
                    return self.ensure_config_structure(config)
            else:
                return self.create_default_config()
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败: {str(e)}")
            return self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
            "points": {"_3_days": 1, "_7_days": 2.5},
            "timer": {"on": True, "morning": "7:05", "afternoon": "14:05"},
            "display": {
                "win": {
                    "row_num": 7, 
                    "font": "Microsoft YaHei UI", 
                    "font_size": 10
                },
                "md": {"column_num": 12},
                "theme": "light"
            },
            "namelist": ["sweet", "sleepy", "stupid", "sexy"],
            "project": {
                "url": "https://github.com/Jack-tendy-538/scoring-early-bird-new",
                "license": "MIT License",
                "version": "1.0.0.3"
            }
        }
        self.save_config(default_config)
        return default_config
    
    def ensure_config_structure(self, config):
        """确保配置结构完整，添加缺失的字段"""
        defaults = self.create_default_config()
        
        # 递归合并配置，确保所有默认字段都存在
        def merge_dicts(default, current):
            result = default.copy()
            for key, value in current.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_dicts(defaults, config)
    
    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            return False
    
    def create_ui(self):
        """创建用户界面"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        # 限制notebook最大高度，防止内容过少时界面变形
        notebook.bind("<Configure>", self.on_notebook_configure)
        self.create_points_tab(notebook)
        self.create_timer_tab(notebook)
        self.create_display_tab(notebook)
        self.create_namelist_tab(notebook)
        self.create_project_tab(notebook)
        # 添加按钮栏
        # 把下边距留给按钮栏，所以不放在notebook里，下边框要拉大一点
        self.create_button_bar(main_frame)
    
    def on_notebook_configure(self, event):
        """限制notebook最大高度"""
        max_height = self.root.winfo_height() - 100
        if event.height > max_height:
            event.widget.config(height=max_height)

    def create_points_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=8)
        notebook.add(tab, text="积分设置")
        
        title_label = ttk.Label(tab, text="积分规则设置", font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        points_3_frame = ttk.Frame(tab)
        points_3_frame.pack(fill=tk.X, pady=10)
        ttk.Label(points_3_frame, text="3天连续打卡积分:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.points_3_var = tk.DoubleVar(value=self.config["points"]["_3_days"])
        points_3_entry = ttk.Entry(points_3_frame, textvariable=self.points_3_var, width=10)
        points_3_entry.pack(side=tk.LEFT, padx=10)
        ttk.Label(points_3_frame, text="分").pack(side=tk.LEFT)
        
        points_7_frame = ttk.Frame(tab)
        points_7_frame.pack(fill=tk.X, pady=10)
        ttk.Label(points_7_frame, text="7天连续打卡积分:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.points_7_var = tk.DoubleVar(value=self.config["points"]["_7_days"])
        points_7_entry = ttk.Entry(points_7_frame, textvariable=self.points_7_var, width=10)
        points_7_entry.pack(side=tk.LEFT, padx=10)
        ttk.Label(points_7_frame, text="分").pack(side=tk.LEFT)
        
        # 添加积分计算示例
        example_frame = ttk.LabelFrame(tab, text="积分计算示例", padding=10)
        example_frame.pack(fill=tk.X, pady=20)
        
        example_text = (
            "示例计算:\n"
            "- 连续打卡3天: 获得3天积分\n"
            "- 连续打卡7天: 获得3天积分 + 7天积分\n"
            "- 连续打卡10天: 获得3天积分 + 7天积分 + 3天积分\n"
            f"当前设置: 3天={self.points_3_var.get()}分, 7天={self.points_7_var.get()}分\n"
            f"连续10天总分: {self.points_3_var.get() * 2 + self.points_7_var.get()}分"
        )
        example_label = ttk.Label(example_frame, text=example_text, font=("Segoe UI", 9))
        example_label.pack(anchor=tk.W)
    
    def create_timer_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="定时设置")
        
        title_label = ttk.Label(tab, text="定时提醒设置", font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        timer_frame = ttk.Frame(tab)
        timer_frame.pack(fill=tk.X, pady=10)
        ttk.Label(timer_frame, text="启用定时提醒:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.timer_on_var = tk.BooleanVar(value=self.config["timer"]["on"])
        timer_check = ttk.Checkbutton(timer_frame, variable=self.timer_on_var)
        timer_check.pack(side=tk.LEFT, padx=10)
        
        morning_frame = ttk.Frame(tab)
        morning_frame.pack(fill=tk.X, pady=10)
        ttk.Label(morning_frame, text="上午提醒时间:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.morning_var = tk.StringVar(value=self.config["timer"]["morning"])
        morning_entry = ttk.Entry(morning_frame, textvariable=self.morning_var, width=10)
        morning_entry.pack(side=tk.LEFT, padx=10)
        ttk.Label(morning_frame, text="格式: HH:MM (24小时制)").pack(side=tk.LEFT, padx=5)
        
        afternoon_frame = ttk.Frame(tab)
        afternoon_frame.pack(fill=tk.X, pady=10)
        ttk.Label(afternoon_frame, text="下午提醒时间:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.afternoon_var = tk.StringVar(value=self.config["timer"]["afternoon"])
        afternoon_entry = ttk.Entry(afternoon_frame, textvariable=self.afternoon_var, width=10)
        afternoon_entry.pack(side=tk.LEFT, padx=10)
        ttk.Label(afternoon_frame, text="格式: HH:MM (24小时制)").pack(side=tk.LEFT, padx=5)
        
        # 添加时间验证提示
        validation_frame = ttk.Frame(tab)
        validation_frame.pack(fill=tk.X, pady=10)
        validation_text = "注意: 时间格式必须为 HH:MM，如 07:05、14:30"
        validation_label = ttk.Label(validation_frame, text=validation_text, 
                                   font=("Segoe UI", 9), foreground="orange")
        validation_label.pack(anchor=tk.W)
    
    def create_display_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="显示设置")
        
        title_label = ttk.Label(tab, text="界面显示设置", font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 主题设置
        theme_frame = ttk.LabelFrame(tab, text="主题设置", padding=10)
        theme_frame.pack(fill=tk.X, pady=10)
        
        theme_inner_frame = ttk.Frame(theme_frame)
        theme_inner_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_inner_frame, text="界面主题:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.config["display"].get("theme", "light"))
        theme_combo = ttk.Combobox(theme_inner_frame, textvariable=self.theme_var,
                                  values=["light", "dark"], state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT, padx=10)
        
        # 窗口设置
        win_frame = ttk.LabelFrame(tab, text="窗口设置", padding=10)
        win_frame.pack(fill=tk.X, pady=10)
        
        row_frame = ttk.Frame(win_frame)
        row_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_frame, text="每行显示学生数:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.row_num_var = tk.IntVar(value=self.config["display"]["win"]["row_num"])
        row_spinbox = ttk.Spinbox(row_frame, from_=1, to=20, textvariable=self.row_num_var, width=10)
        row_spinbox.pack(side=tk.LEFT, padx=10)
        
        font_frame = ttk.Frame(win_frame)
        font_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_frame, text="界面字体:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.font_var = tk.StringVar(value=self.config["display"]["win"]["font"])
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var,
                                  values=["Microsoft YaHei UI", "Segoe UI", "Arial", 
                                         "SimSun", "SimHei", "KaiTi"],
                                  width=20)
        font_combo.pack(side=tk.LEFT, padx=10)
        
        font_size_frame = ttk.Frame(win_frame)
        font_size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_size_frame, text="字体大小:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.font_size_var = tk.IntVar(value=self.config["display"]["win"]["font_size"])
        font_size_spinbox = ttk.Spinbox(font_size_frame, from_=8, to=24, 
                                       textvariable=self.font_size_var, width=10)
        font_size_spinbox.pack(side=tk.LEFT, padx=10)
        
        # Markdown输出设置
        md_frame = ttk.LabelFrame(tab, text="报告输出设置", padding=10)
        md_frame.pack(fill=tk.X, pady=10)
        
        column_frame = ttk.Frame(md_frame)
        column_frame.pack(fill=tk.X, pady=5)
        ttk.Label(column_frame, text="报告表格列数:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.column_num_var = tk.IntVar(value=self.config["display"]["md"]["column_num"])
        column_spinbox = ttk.Spinbox(column_frame, from_=1, to=24, 
                                    textvariable=self.column_num_var, width=10)
        column_spinbox.pack(side=tk.LEFT, padx=10)
    
    def create_namelist_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="学生名单")
        
        title_label = ttk.Label(tab, text="学生名单管理", font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 学生名单编辑区域
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 列表标题
        header_frame = ttk.Frame(list_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(header_frame, text="学生姓名", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.namelist_var = tk.StringVar(value=self.config["namelist"])
        self.namelist_listbox = tk.Listbox(listbox_frame, listvariable=self.namelist_var,
                                           font=("Segoe UI", 10), selectmode=tk.SINGLE,
                                           height=15)
        self.namelist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.namelist_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.namelist_listbox.config(yscrollcommand=scrollbar.set)
        
        # 操作按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="添加学生", command=self.add_namelist_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编辑选中", command=self.edit_namelist_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除选中", command=self.remove_namelist_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="上移", command=self.move_namelist_item_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="下移", command=self.move_namelist_item_down).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空列表", command=self.clear_namelist).pack(side=tk.LEFT, padx=5)
        
        # 批量操作
        batch_frame = ttk.Frame(tab)
        batch_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(batch_frame, text="从csv导入", command=self.import_csv_namelist).pack(side=tk.LEFT, padx=5)
        ttk.Button(batch_frame, text="导出名单", command=self.export_namelist).pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill=tk.X, pady=10)
        student_count = len(self.config["namelist"])
        stats_label = ttk.Label(stats_frame, text=f"当前学生总数: {student_count} 人", 
                               font=("Segoe UI", 10, "bold"))
        stats_label.pack(anchor=tk.W)
    
    def create_project_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="项目信息")
        
        title_label = ttk.Label(tab, text="项目信息", font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 项目信息展示
        project_info = self.config["project"]
        
        info_text = f"""
项目名称: 考勤评分系统 (Score Early Bird)
版本: {project_info['version']}
许可证: {project_info['license']}
项目地址: {project_info['url']}

功能说明:
- 自动记录学生早晚考勤
- 智能计算连续出勤分数
- 生成详细的考勤报告
- 支持定时自动提交
- 提供暂存和补登功能
"""
        info_label = ttk.Label(info_frame, text=info_text, font=("Segoe UI", 10), justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # 操作说明
        help_frame = ttk.LabelFrame(tab, text="使用说明", padding=10)
        help_frame.pack(fill=tk.X, pady=20)
        
        help_text = """
使用流程:
1. 在"学生名单"选项卡中添加学生
2. 在"定时设置"中配置自动提交时间
3. 在"积分设置"中调整评分规则
4. 保存设置并启动主程序
5. 通过主程序进行考勤记录和报告生成
"""
        help_label = ttk.Label(help_frame, text=help_text, font=("Segoe UI", 9), justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
    
    def create_button_bar(self, parent):
        button_frame = ttk.Frame(parent, padding=0)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="保存设置", command=self.save_settings, 
                  style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="重置", command=self.reset_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="应用", command=self.apply_settings).pack(side=tk.RIGHT, padx=5)
    
    def add_namelist_item(self):
        self.show_namelist_dialog("添加学生")
    
    def edit_namelist_item(self):
        selection = self.namelist_listbox.curselection()
        if selection:
            index = selection[0]
            current_name = self.config["namelist"][index]
            self.show_namelist_dialog("编辑学生", current_name, index)
        else:
            messagebox.showwarning("警告", "请先选择一个学生")
    
    def show_namelist_dialog(self, title, current_name="", index=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="学生姓名:").pack(pady=10)
        entry_var = tk.StringVar(value=current_name)
        entry = ttk.Entry(dialog, textvariable=entry_var, width=30)
        entry.pack(pady=10)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def confirm():
            new_item = entry_var.get().strip()
            if new_item:
                current_list = list(self.config["namelist"])
                if index is not None:
                    # 编辑模式
                    current_list[index] = new_item
                else:
                    # 添加模式
                    current_list.append(new_item)
                self.config["namelist"] = current_list
                self.namelist_var.set(current_list)
                # 更新统计信息
                self.update_stats()
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "学生姓名不能为空")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="确认", command=confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键确认
        dialog.bind('<Return>', lambda e: confirm())
    
    def remove_namelist_item(self):
        selection = self.namelist_listbox.curselection()
        if selection:
            index = selection[0]
            current_list = list(self.config["namelist"])
            student_name = current_list[index]
            if messagebox.askyesno("确认", f"确定要删除学生 '{student_name}' 吗？"):
                current_list.pop(index)
                self.config["namelist"] = current_list
                self.namelist_var.set(current_list)
                self.update_stats()
        else:
            messagebox.showwarning("警告", "请先选择一个学生")
    
    def clear_namelist(self):
        if messagebox.askyesno("确认", "确定要清空整个学生名单吗？"):
            self.config["namelist"] = []
            self.namelist_var.set([])
            self.update_stats()
    
    def move_namelist_item_up(self):
        selection = self.namelist_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            current_list = list(self.config["namelist"])
            current_list[index], current_list[index-1] = current_list[index-1], current_list[index]
            self.config["namelist"] = current_list
            self.namelist_var.set(current_list)
            self.namelist_listbox.select_set(index-1)
    
    def move_namelist_item_down(self):
        selection = self.namelist_listbox.curselection()
        if selection and selection[0] < len(self.config["namelist"]) - 1:
            index = selection[0]
            current_list = list(self.config["namelist"])
            current_list[index], current_list[index+1] = current_list[index+1], current_list[index]
            self.config["namelist"] = current_list
            self.namelist_var.set(current_list)
            self.namelist_listbox.select_set(index+1)
        
    def export_namelist(self):
        # 简化的导出功能 - 实际应用中可以实现文件保存
        names = "\n".join(self.config["namelist"])
        messagebox.showinfo("学生名单", f"当前学生名单:\n\n{names}")
    
    def update_stats(self):
        """更新统计信息"""
        student_count = len(self.config["namelist"])
        # 这里可以添加更新统计标签的代码
    
    def validate_time_format(self, time_str):
        """验证时间格式"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hour = int(parts[0])
            minute = int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except ValueError:
            return False
    
    def save_settings(self):
        """保存所有设置"""
        if not self.validate_time_format(self.morning_var.get()):
            messagebox.showerror("错误", "上午时间格式不正确，请使用 HH:MM 格式")
            return
        
        if not self.validate_time_format(self.afternoon_var.get()):
            messagebox.showerror("错误", "下午时间格式不正确，请使用 HH:MM 格式")
            return
        
        # 更新配置
        self.config["points"]["_3_days"] = self.points_3_var.get()
        self.config["points"]["_7_days"] = self.points_7_var.get()
        
        self.config["timer"]["on"] = self.timer_on_var.get()
        self.config["timer"]["morning"] = self.morning_var.get()
        self.config["timer"]["afternoon"] = self.afternoon_var.get()
        
        self.config["display"]["win"]["row_num"] = self.row_num_var.get()
        self.config["display"]["win"]["font"] = self.font_var.get()
        self.config["display"]["win"]["font_size"] = self.font_size_var.get()
        
        self.config["display"]["md"]["column_num"] = self.column_num_var.get()
        self.config["display"]["theme"] = self.theme_var.get()
        
        if self.save_config():
            messagebox.showinfo("成功", "设置已保存！")
            self.root.destroy()
    
    def apply_settings(self):
        """应用设置但不关闭窗口"""
        # 类似 save_settings 但不关闭窗口
        self.config["points"]["_3_days"] = self.points_3_var.get()
        self.config["points"]["_7_days"] = self.points_7_var.get()
        
        self.config["timer"]["on"] = self.timer_on_var.get()
        self.config["timer"]["morning"] = self.morning_var.get()
        self.config["timer"]["afternoon"] = self.afternoon_var.get()
        
        self.config["display"]["win"]["row_num"] = self.row_num_var.get()
        self.config["display"]["win"]["font"] = self.font_var.get()
        self.config["display"]["win"]["font_size"] = self.font_size_var.get()
        
        self.config["display"]["md"]["column_num"] = self.column_num_var.get()
        self.config["display"]["theme"] = self.theme_var.get()
        
        if self.save_config():
            messagebox.showinfo("成功", "设置已应用！")
    
    def reset_settings(self):
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            self.config = self.create_default_config()
            self.update_ui_from_config()
            messagebox.showinfo("成功", "设置已重置为默认值")
    
    def update_ui_from_config(self):
        """从配置更新UI"""
        self.points_3_var.set(self.config["points"]["_3_days"])
        self.points_7_var.set(self.config["points"]["_7_days"])
        
        self.timer_on_var.set(self.config["timer"]["on"])
        self.morning_var.set(self.config["timer"]["morning"])
        self.afternoon_var.set(self.config["timer"]["afternoon"])
        
        self.row_num_var.set(self.config["display"]["win"]["row_num"])
        self.font_var.set(self.config["display"]["win"]["font"])
        self.font_size_var.set(self.config["display"]["win"]["font_size"])
        
        self.column_num_var.set(self.config["display"]["md"]["column_num"])
        self.theme_var.set(self.config["display"].get("theme", "light"))
        
        self.namelist_var.set(self.config["namelist"])
        self.update_stats()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # 支持命令行参数指定配置文件路径
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = SettingsApp(config_path)
    app.run()