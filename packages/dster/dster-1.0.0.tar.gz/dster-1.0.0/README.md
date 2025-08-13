# 桌面卡通贴纸效果程序

一个在Windows桌面上显示动态卡通贴纸的Python程序。贴纸会从屏幕中央冒出，具有真实的物理弹跳效果，并自动消失。程序以透明窗口形式覆盖在桌面上，不会干扰正常使用。

## 功能特点

- 🎈 **四种卡通贴纸形状**：圆形、方形、三角形、星星
- ⚙️ **真实物理效果**：重力、碰撞反弹、旋转
- 🖥️ **透明窗口覆盖桌面**：不干扰正常使用
- ⏱️ **可配置运行时间**：默认10秒自动退出
- 🚀 **命令行界面**：支持参数配置
- 📦 **一键安装**：通过PyPI轻松安装

## 安装方式

### 方法1：通过PyPI安装（推荐）

```bash
pip install dster
```

### 方法2：从源码安装

```bash
git clone https://github.com/yourusername/desktop-stickers.git
cd desktop-stickers
pip install -e .
```

## 使用方法

### 命令行使用

安装后，可以直接在命令行中使用：

```bash
# 使用默认设置运行（10秒，20个贴纸）
dster

# 自定义运行时间（30秒）
dster --duration 30

# 自定义贴纸数量（50个）
dster --number 50

# 查看帮助信息
dster --help

# 查看版本信息
dster --version
```

### Python代码中使用

```python
import desktop_stickers

# 使用默认参数
desktop_stickers.main()

# 自定义参数
desktop_stickers.main(duration=15, initial_stickers=30)
```

## 操作说明

- **ESC键**：手动退出程序
- **空格键**：添加10个新贴纸
- **自动退出**：达到指定时间后自动结束

## 系统要求

- **操作系统**：Windows 7/10/11
- **Python版本**：3.7或更高版本
- **依赖库**：pygame >= 2.0.0

## 技术原理

- 使用Pygame创建透明窗口
- 调用Windows API实现真正透明效果
- 物理引擎模拟重力、碰撞和旋转
- 支持命令行参数配置

## 自定义选项

程序支持以下配置参数：

- `duration`：运行时长（秒）
- `initial_stickers`：初始贴纸数量

## 开发相关

### 本地开发环境搭建

```bash
# 克隆代码
git clone https://github.com/yourusername/desktop-stickers.git
cd desktop-stickers

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
pip install -e .

# 运行测试
desktop-stickers
```

### 构建发布包

```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build

# 上传到PyPI
twine upload dist/*
```

## 许可证

本项目使用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎贡献代码！请先阅读贡献指南。

## 问题反馈

如果您遇到任何问题，请在 [GitHub Issues](https://github.com/yourusername/desktop-stickers/issues) 中提交。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持四种贴纸形状
- 物理引擎和透明窗口
- 命令行界面
- PyPI发布

## 注意事项

- 仅支持Windows系统
- 首次运行可能需要允许防火墙权限
- 确保已安装Python和pygame库
- 运行期间可能会占用一定的CPU资源