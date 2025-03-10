class MioObject:
    """
    MioObject 是一个基础图形对象类，用于存储图形对象的基本属性。
    """
    def __init__(self):
        # 坐标系属性
        # x, y 是对象的左上角（基点）坐标，width, height 是对象的宽度和高度，单位为像素（px）
        # 在OpenCV和PIL中，坐标系的原点在左上角，x轴向右，y轴向下（即第四象限）
        self.x: int = 0  # x 坐标
        self.y: int = 0  # y 坐标
        self.x_offset: int = 0  # x 偏移量，当对象被绘制到画布上时，会根据偏移量进行偏移，用于实现阴影、描边等可能影响实际位置的效果
        self.y_offset: int = 0  # y 偏移量，当对象被绘制到画布上时，会根据偏移量进行偏移，用于实现阴影、描边等可能影响实际位置的效果
        self.width: int = 0  # 坐标盒宽度
        self.height: int = 0  # 坐标盒高度
        self.full_width: int = 0  # 完整宽度
        self.full_height: int = 0  # 完整高度

        # 对象属性
        self.name: str = ""  # 对象名称，用于标识对象，设置了对象名时可以使用名称过滤器进行过滤
        self.tags: list[str] = []  # 对象标签，用于标识对象，设置了对象标签时可以使用标签过滤器进行过滤
        self.object_type: str = ""  # 对象类型，用于标识对象的类型，在子类初始化时应被设定为具体的对象类型，可以用于类型过滤器

    def get_size(self):
        """
        获取对象的坐标盒尺寸
        :return: width, height
        """
        return self.width, self.height

    def get_full_size(self):
        """
        获取对象的完整尺寸
        :return: full_width, full_height
        """
        return self.full_width, self.full_height

    def get_position(self):
        """
        获取对象的位置
        :return: x, y
        """
        return self.x, self.y

    def get_offseted_position(self):
        """
        获取对象偏移后的位置
        :return: x + x_offset, y + y_offset
        """
        return self.x + self.x_offset, self.y + self.y_offset

    def move(self, x: int, y: int):
        """
        移动对象到指定位置
        :param x: x 坐标
        :param y: y 坐标
        """
        self.x = x
        self.y = y

        return self  # 返回对象本身，以支持链式调用

    def move_up(self, step: int):
        """
        向上移动对象
        :param step: 移动的步长
        """
        self.y -= step

        return self  # 返回对象本身，以支持链式调用

    def move_down(self, step: int):
        """
        向下移动对象
        :param step: 移动的步长
        """
        self.y += step

        return self  # 返回对象本身，以支持链式调用

    def move_left(self, step: int):
        """
        向左移动对象
        :param step: 移动的步长
        """
        self.x -= step

        return self  # 返回对象本身，以支持链式调用

    def move_right(self, step: int):
        """
        向右移动对象
        :param step: 移动的步长
        """
        self.x += step

        return self  # 返回对象本身，以支持链式调用

    def get_box(self):
        """
        获取对象的边界框，即左上角和右下角的坐标
        :return: (x1, y1, x2, y2)
        """
        return self.x, self.y, self.x + self.width, self.y + self.height

    def get_left_top(self):
        """
        获取对象的左上角坐标
        :return: x, y
        """
        return self.x, self.y

    def get_left_bottom(self):
        """
        获取对象的左下角坐标
        :return: x, y
        """
        return self.x, self.y + self.height

    def get_right_top(self):
        """
        获取对象的右上角坐标
        :return: x, y
        """
        return self.x + self.width, self.y

    def get_right_bottom(self):
        """
        获取对象的右下角坐标
        :return: x, y
        """
        return self.x + self.width, self.y + self.height

    def get_offseted_box(self):
        """
        获取对象的偏移后的边界框，即左上角和右下角的坐标
        :return: (x1, y1, x2, y2)
        """
        return self.x + self.x_offset, self.y + self.y_offset, self.x + self.width + self.x_offset, self.y + self.height + self.y_offset

    def get_offseted_left_top(self):
        """
        获取对象的偏移后的左上角坐标
        :return: x, y
        """
        return self.x + self.x_offset, self.y + self.y_offset

    def get_offseted_left_bottom(self):
        """
        获取对象的偏移后的左下角坐标
        :return: x, y
        """
        return self.x + self.x_offset, self.y + self.height + self.y_offset

    def get_offseted_right_top(self):
        """
        获取对象的偏移后的右上角坐标
        :return: x, y
        """
        return self.x + self.width + self.x_offset, self.y + self.y_offset

    def get_offseted_right_bottom(self):
        """
        获取对象的偏移后的右下角坐标
        :return: x, y
        """
        return self.x + self.width + self.x_offset, self.y + self.height + self.y_offset
    