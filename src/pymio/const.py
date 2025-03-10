from pymio.color import MioColor

"""
颜色常量
"""
WHITE = MioColor(255, 255, 255, 255)
BLACK = MioColor(0, 0, 0, 255)
RED = MioColor(255, 0, 0, 255)
GREEN = MioColor(0, 255, 0, 255)
BLUE = MioColor(0, 0, 255, 255)
YELLOW = MioColor(255, 255, 0, 255)
CYAN = MioColor(0, 255, 255, 255)
MAGENTA = MioColor(255, 0, 255, 255)
TRANSPARENT = MioColor(0, 0, 0, 0)

"""
插值方法快捷方式，和OpenCV中的枚举值对应
"""
INTER_NEAREST = 0  # 最近邻插值
INTER_LINEAR = 1  # 线性插值
INTER_CUBIC = 2  # 三次插值
INTER_AREA = 3  # 区域插值
INTER_LANCZOS4 = 4  # Lanczos4插值
INTER_LINEAR_EXACT = 5  # 精确线性插值
INTER_NEAREST_EXACT = 6  # 精确最近邻插值