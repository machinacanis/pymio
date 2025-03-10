from .color import MioColor
from .const import BLACK
from .object import MioObject


class MioLayer:
    """
    MioLayer类用于表示一个图层，就像Photoshop的图层一样，每个图层都可以包含多个图形对象

    图层没有坐标属性，但是有尺寸属性，通过设置dynamic属性可以让图层自动调整尺寸（自动尺寸图层无法组合）
    """

    def __init__(self):
        # 图层属性
        self.name = "layer"  # 图层名称
        self.dynamic: bool = False  # 是否启用动态尺寸，启用后图层会自动调整尺寸
        self.width: int = 0  # 图层宽度
        self.height: int = 0  # 图层高度
        self.background_color: MioColor = BLACK  # 背景颜色
        self.alpha: int = 255  # 图层透明度

        # 图层对象
        self.objects: list[
            MioObject
        ] = []  # 存储所有的图形对象，渲染时会按照添加的顺序由后往前渲染
