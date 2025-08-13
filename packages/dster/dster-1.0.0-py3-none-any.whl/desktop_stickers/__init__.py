"""
桌面卡通贴纸效果包
===========================

这是一个在Windows桌面上显示动态卡通贴纸的Python包。
贴纸会从屏幕中央冒出，具有真实的物理弹跳效果。

主要功能：
- 四种卡通贴纸形状：圆形、方形、三角形、星星
- 真实物理效果：重力、碰撞反弹、旋转
- 透明窗口覆盖桌面
- 自动退出功能
"""

__version__ = "1.0.0"
__author__ = "ylicen"
__email__ = "sokllmiller@gmail.com"

from .main import main, Sticker

__all__ = ['main', 'Sticker']