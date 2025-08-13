import pygame
import sys
import random
import math
import time
import ctypes


def get_screen_info():
    """获取屏幕信息"""
    screen_info = pygame.display.Info()
    return screen_info.current_w, screen_info.current_h


def setup_transparent_window(screen_width, screen_height):
    """设置透明窗口"""
    # 创建透明无边框窗口（覆盖桌面）
    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        pygame.NOFRAME | pygame.SRCALPHA
    )
    pygame.display.set_caption("桌面贴纸效果")
    
    # 获取窗口句柄并设置透明属性
    hwnd = pygame.display.get_wm_info()["window"]
    
    # 设置窗口为分层窗口
    ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ex_style |= 0x00080000  # WS_EX_LAYERED
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, ex_style)
    
    # 设置黑色为透明色
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x00000000, 0, 0x00000001)
    
    return screen


# 贴纸类
class Sticker:
    """卡通贴纸类"""
    
    # 颜色配置
    COLORS = [
        (255, 105, 180),  # 热粉
        (255, 215, 0),    # 金黄
        (50, 205, 50),    # 酸橙绿
        (70, 130, 180),   # 钢蓝
        (255, 165, 0),    # 橙色
    ]
    
    def __init__(self, x, y, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = x
        self.y = y
        self.size = random.randint(30, 70)
        self.color = random.choice(self.COLORS)
        self.shape = random.choice(["circle", "square", "triangle", "star"])
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, -1)
        self.gravity = 0.2
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        
    def update(self):
        """更新贴纸状态"""
        # 应用重力
        self.vy += self.gravity
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        
        # 更新旋转
        self.rotation += self.rotation_speed
        
        # 边界检查
        if self.x < 0 or self.x > self.screen_width:
            self.vx *= -0.8  # 反弹并损失能量
        if self.y > self.screen_height:
            self.vy *= -0.7  # 反弹并损失能量
            self.y = self.screen_height - 5
            
    def draw(self, surface):
        """绘制贴纸"""
        if self.shape == "circle":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size//2)
            # 添加装饰性眼睛
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x)-self.size//4, int(self.y)-self.size//6), self.size//8)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x)+self.size//4, int(self.y)-self.size//6), self.size//8)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x)-self.size//4, int(self.y)-self.size//6), self.size//16)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x)+self.size//4, int(self.y)-self.size//6), self.size//16)
            # 添加微笑
            pygame.draw.arc(surface, (0, 0, 0), 
                           [self.x-self.size//3, self.y-self.size//6, self.size*2//3, self.size*2//3],
                           0, math.pi, 2)
            
        elif self.shape == "square":
            rect = pygame.Rect(self.x-self.size//2, self.y-self.size//2, self.size, self.size)
            pygame.draw.rect(surface, self.color, rect)
            # 添加装饰性图案
            pygame.draw.rect(surface, (255, 255, 255), 
                            (self.x-self.size//4, self.y-self.size//4, self.size//2, self.size//2), 2)
            
        elif self.shape == "triangle":
            points = [
                (self.x, self.y - self.size//2),
                (self.x - self.size//2, self.y + self.size//2),
                (self.x + self.size//2, self.y + self.size//2)
            ]
            pygame.draw.polygon(surface, self.color, points)
            # 添加装饰性线条
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            
        elif self.shape == "star":
            points = []
            for i in range(5):
                # 外点
                outer_x = self.x + self.size//2 * math.cos(math.radians(self.rotation + i*72))
                outer_y = self.y + self.size//2 * math.sin(math.radians(self.rotation + i*72))
                points.append((outer_x, outer_y))
                # 内点
                inner_x = self.x + self.size//4 * math.cos(math.radians(self.rotation + 36 + i*72))
                inner_y = self.y + self.size//4 * math.sin(math.radians(self.rotation + 36 + i*72))
                points.append((inner_x, inner_y))
            pygame.draw.polygon(surface, self.color, points)


def main(duration=10, initial_stickers=20):
    """
    主程序函数
    
    Args:
        duration (int): 运行时长（秒），默认10秒
        initial_stickers (int): 初始贴纸数量，默认20个
    """
    # 初始化pygame
    pygame.init()
    
    try:
        # 获取屏幕尺寸
        screen_width, screen_height = get_screen_info()
        
        # 设置透明窗口
        screen = setup_transparent_window(screen_width, screen_height)
        
        # 设置背景为黑色（将作为透明色）
        BACKGROUND = (0, 0, 0)
        
        # 创建初始贴纸
        stickers = []
        for _ in range(initial_stickers):
            stickers.append(Sticker(screen_width//2, screen_height//2, screen_width, screen_height))
        
        # 记录启动时间
        start_time = time.time()
        
        # 主循环
        clock = pygame.time.Clock()
        running = True
        while running:
            # 检查是否超过指定时间
            if time.time() - start_time > duration:
                running = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # 空格键添加更多贴纸
                        for _ in range(10):
                            stickers.append(Sticker(screen_width//2, screen_height//2, screen_width, screen_height))
            
            # 更新贴纸
            for sticker in stickers:
                sticker.update()
            
            # 绘制
            screen.fill(BACKGROUND)
            for sticker in stickers:
                sticker.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
    
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()