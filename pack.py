import shutil
import os
import subprocess
from pathlib import Path

def delete_prev_pack():
    """删除之前的打包文件"""
    for folder in ['build', 'dist']:
        shutil.rmtree(folder, ignore_errors=True)
        print(f"已删除 {folder} 目录")

def create_spec_file(script_name, exe_name, icon_file='favicon.ico'):
    """创建 spec 文件"""
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_name}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['sv_ttk','yaml'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='{icon_file}' if os.path.exists('{icon_file}') else None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    spec_filename = f'{script_name.replace(".py", "")}.spec'
    with open(spec_filename, 'w', encoding='utf-8') as fp:
        fp.write(spec_content)
    return spec_filename

def run_pyinstaller(spec_file):
    """运行 PyInstaller"""
    try:
        # 使用 run 替代 Popen，更安全
        result = subprocess.run(
            ['pyinstaller', spec_file], 
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"成功打包: {spec_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败 {spec_file}: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 未找到 pyinstaller，请先安装")
        return False

def pack_software():
    """打包软件"""
    # 定义要打包的脚本配置
    packages = [
        {'script': 'main.py', 'exe_name': 'seab'},
        {'script': 'settings.py', 'exe_name': 'seab-settings'}
    ]
    
    spec_files = []
    
    for pkg in packages:
        if not os.path.exists(pkg['script']):
            print(f"警告: 未找到脚本文件 {pkg['script']}")
            continue
            
        spec_file = create_spec_file(pkg['script'], pkg['exe_name'])
        spec_files.append(spec_file)
        
        if not run_pyinstaller(spec_file):
            print(f"{pkg['script']} 打包失败，中止流程")
            break
    
    # 清理临时文件
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            os.unlink(spec_file)
            print(f"已删除临时文件: {spec_file}")

def check_requirements():
    """检查必要的文件是否存在"""
    required_files = ['main.py', 'settings.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("错误: 缺少必要的文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    if not os.path.exists('favicon.ico'):
        print("警告: 未找到图标文件 favicon.ico，将使用默认图标")
    
    return True

def main():
    """主函数"""
    print("开始打包过程...")
    
    # 检查必要文件
    if not check_requirements():
        return
    
    # 删除旧包
    delete_prev_pack()
    
    # 打包软件
    pack_software()
    
    print("打包完成！")
    
    # 显示输出信息
    dist_path = Path('dist')
    if dist_path.exists():
        print("\n生成的可执行文件:")
        for exe_file in dist_path.glob('*.exe'):
            print(f"  - {exe_file}")

if __name__ == '__main__':
    main()
