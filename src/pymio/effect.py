from .image import MioImage


class MioEffect:
    """
    pyMio 的效果器基类，继承这个类可以实现自定义的效果器

    效果器可以对图像进行处理，例如添加滤镜、添加特效等

    在 MioImage 对象上调用render()方法进行渲染时，会自动遍历效果器并通过依赖注入的方式调用效果器的apply()方法
    """
    def __init__(self):
        self.effect_name: str = ""  # 特效名称

    def apply(self, image: MioImage):
        pass
