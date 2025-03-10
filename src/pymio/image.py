import base64
from io import BytesIO
from os import PathLike
from pathlib import Path

from numpy import ndarray

from .color import MioColor
from .const import BLACK, CV2_INTER_LINEAR
from .exception import MioTypeUnexpectedError
from .object import MioObject

from PIL.Image import Image, open
import tempfile

from .utils import cv2_image_to_pil, pil_image_to_cv2
import cv2


class MioImage(MioObject):
    """
    pyMio 的智能图像对象，封装了基础图像处理的功能
    """

    def __init__(
        self, img: str | PathLike | Image | ndarray | bytes | BytesIO | None = None
    ):
        super().__init__()
        # 基本属性
        self.object_type = "image"  # 覆盖 pyMio 对象类型
        self.tags.append("image")  # 添加类型标签
        self.has_rendered = False  # 是否已经渲染过
        self.rendered_times = 0  # 渲染次数

        # 图像数据
        # 图像数据分为三层，分别对应背景、内容、前景
        # 在图像被渲染时，会首先将原始图像数据复制到内容数据层中，然后依次执行效果器
        # 最终得到背景、内容、前景三层数据，之后合并为最终图像（合并完成后会清空三层数据以节省内存）
        self._original_image: Image | None = None  # 原始图像数据
        self.image_bottom: list[Image] | None = None  # 背景数据
        self.image_center: Image | None = None  # 内容数据
        self.image_top: list[Image] | None = None  # 前景数据
        self.result: Image | None = None  # 图像合并结果

        self._original_image_path: Path | None = None  # 图像原始路径
        self.background_color: MioColor = (
            BLACK  # 背景颜色，默认为黑色，这个背景颜色设定仅在不使用图层时生效
        )
        self.rotation = 0  # 旋转角度，单位为度
        self.alpha = 255  # 透明度，默认为不透明
        self.effects: list["MioEffect"] = []  # 效果器列表

        # 初始化时自动加载图像数据
        if img is not None:
            self.open(img)

    """ 读写操作 """

    def open(self, img: str | PathLike | Image | ndarray | bytes | BytesIO | None):
        """
        读取图像数据
        :param img: 图像数据，可以是文件路径、PIL.Image 对象、ndarray 对象（cv2读取的图像数据数组）、bytes 对象、BytesIO 对象
        :return: self
        """
        # 判断输入参数类型
        if img is None:
            return  # 无输入参数，直接返回跳过
        elif isinstance(img, str) or isinstance(img, PathLike):
            # 传入了文件路径
            img_path = Path(img)
            if not img_path.exists():
                raise FileNotFoundError(f"File not found: {img}")  # 文件不存在
            # 尝试读取文件
            try:
                self._original_image = open(img_path, "r")  # 打开文件
                self._original_image_path = img_path  # 记录文件路径
                self.width, self.height = self._original_image.size  # 更新图像尺寸
            except Exception as e:
                raise e
        elif isinstance(img, Image):
            # 传入了 PIL.Image 对象
            self._original_image = img
            self.width, self.height = self._original_image.size  # 更新图像尺寸
        elif isinstance(img, ndarray):
            # 传入了 ndarray 对象，尝试转换
            try:
                self._original_image = cv2_image_to_pil(img)
                self.width, self.height = self._original_image.size  # 更新图像尺寸
            except Exception as e:
                raise e
        elif isinstance(img, bytes):
            # 传入了 bytes 对象，尝试转换
            try:
                self._original_image = open(BytesIO(img))
                self.width, self.height = self._original_image.size  # 更新图像尺寸
            except Exception as e:
                raise e
        elif isinstance(img, BytesIO):
            # 传入了 BytesIO 对象
            self._original_image = open(img)
            self.width, self.height = self._original_image.size  # 更新图像尺寸
        else:
            raise MioTypeUnexpectedError(
                "str | PathLike | Image | ndarray | bytes | BytesIO", type(img)
            )
        return self  # 返回自身，支持链式调用

    def save(self, path: str | PathLike):
        """
        保存图像数据到指定路径
        :param path: 保存路径
        :return: None
        """
        # 检查结果是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to save.")
        # 保存图像
        self.result.save(path)

    def to_bytes(self) -> bytes:
        """
        将图像数据转换为字节数据
        :return: 图像数据
        """
        # 检查结果是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to convert.")
        # 转换成字节数据
        return self.result.tobytes()

    def to_base64(self) -> str:
        """
        将图像数据转换为 base64 字符串
        :return: base64 字符串
        """
        # 检查结果是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to convert.")
        # 转换成字节数据
        byte_data = self.to_bytes()
        # 编码为 base64 字符串
        return base64.b64encode(byte_data).decode("utf-8")

    def to_bytes_io(self) -> BytesIO:
        """
        将图像数据转换为 BytesIO 对象
        :return: BytesIO 对象
        """
        # 检查结果是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to convert.")
        # 转换
        byte_io = BytesIO()
        self.save(byte_io)  # 保存到 BytesIO 对象
        return byte_io

    def to_image(self) -> Image:
        """
        获取图像数据
        :return: PIL.Image 对象
        """
        # 检查结果是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to convert.")
        return self.result

    def to_cv2(self) -> ndarray:
        """
        将图像数据转换为 cv2 对象
        :return: cv2 对象
        """
        # 检查结果是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to convert.")
        # 转换
        return pil_image_to_cv2(self.result)

    def get_original_path(self, enable_tmp: bool = False) -> Path | None:
        """
        获取图像完整路径
        :param enable_tmp: 默认为 False，启用后会在没有路径时生成临时文件并返回临时文件路径（临时文件位置取决于系统）
        :return: 图像完整路径
        """
        # 首先检测是否有图像数据
        if self._original_image is None:
            raise ValueError("No image data to get path.")
        # 如果有图像数据，检查是否有路径
        if self._original_image_path is not None:
            return self._original_image_path
        # 如果没有路径，检查是否需要临时文件
        if enable_tmp:
            # 生成临时文件
            _, temp_file_path = tempfile.mkstemp(suffix=".png")
            self._original_image.save(temp_file_path)
            return Path(temp_file_path)

    def copy(self):
        """
        复制当前图像对象
        :return: 复制的图像对象
        """
        new_image = self
        return new_image

    def show(self):
        """
        显示图像
        """
        # 检查图像数据是否存在
        if self.result is None:
            # 尝试渲染
            self.render()
            # 检查是否渲染成功
            if self.result is None:
                raise ValueError("No image data to show.")
        # 显示图像
        self.result.show()

    """ 魔术方法 """

    def __add__(self, other: "MioImage"):
        """
        重载加法运算符，将两个对象合并为一个对象
        :param other: 另一个对象
        :return: 合并后的对象
        """
        return self

    """ 添加效果器 """

    def add_effect(self, effect: "MioEffect"):
        """
        添加任意效果器
        :param effect: 效果器对象
        :return: self
        """
        self.effects.append(effect)
        return self

    def resize(
        self,
        target: tuple[float, float] | list[float] | float | tuple[int, int] | list[int],
        interpolation: int = CV2_INTER_LINEAR,
        resize_method: str = "cv2",
    ):
        """
        通过内置的缩放效果器实现图像缩放
        :param args: 缩放参数，可以是比例、宽高
        :return: self
        """
        self.effects.append(
            MioResizeEffect(
                target,
                interpolation=interpolation,
                resize_method=resize_method,
            ),
        )  # 添加效果器
        return self

    """ 绘制 """

    def paste():
        pass

    def rasterisation(self):
        """
        栅格化图像，将图像属性全部应用到图像数据上，并重置图像属性
        :return:
        """
        # 检查图像数据是否存在
        return self

    def render(self):
        """
        渲染图像，执行这个方法后会将所有效果器应用到图像上并生成结果

        :return: self
        """
        # 复制原始图像到内容层
        assert self._original_image is not None, (
            "No image data to render."
        )  # 检查是否有图像数据

        self.image_center = self._original_image

        # 应用效果器
        for effect in self.effects:
            effect.apply(self)
        # 渲染完成后叠加三层图像
        # TODO: 叠加图像
        self.result = self.image_center
        # 清空渲染缓存
        self.image_bottom = None
        self.image_center = None
        self.image_top = None

        # 更新渲染状态
        self.has_rendered = True
        self.rendered_times += 1
        return self

    def output():
        pass


class MioEffect:
    """
    pyMio 的效果器基类，继承这个类可以实现自定义的效果器

    效果器可以对图像进行处理，例如添加滤镜、添加特效等

    在 MioImage 对象上调用render()方法进行渲染时，会自动遍历效果器并通过依赖注入的方式调用效果器的apply()方法
    """

    def __init__(self):
        self.effect_name: str = ""  # 特效名称

    def apply(self, image: MioImage) -> bool:
        pass


class MioResizeEffect(MioEffect):
    """
    pyMio 的缩放效果器，用于对图像进行缩放处理

    默认使用opencv-python的resize方法进行缩放，opencv-python的resize方法速度更快，效果更好，也可以设置pillow的resize方法
    """

    def __init__(
        self,
        target: tuple[float, float]
        | list[float]
        | float
        | tuple[int, int]
        | list[int] = 1.0,
        interpolation: int = CV2_INTER_LINEAR,
        resize_method: str = "cv2",
    ):
        super().__init__()

        self.resize_method: str = "cv2"  # 缩放方法，可选值为 cv2 或 pil
        self.is_ratio_mode: bool = True  # 是否启用按比例缩放模式
        # 目标宽度和高度
        self.target_width: int = 0  # 目标宽度
        self.target_height: int = 0  # 目标高度
        # 缩放比例，当启用按比例缩放模式时，会忽略目标宽度和高度，使用缩放比例进行缩放
        self.width_ratio: float = 1.0  # 宽度缩放比例
        self.height_ratio: float = 1.0  # 高度缩放比例
        # 其他参数
        self.interpolation: int = 0  # 插值方法，注意：cv2 和 pil 的插值方法是不同的

        # 根据传入的参数检查类型并初始化缩放效果器
        if isinstance(target, float):
            self.width_ratio = target
            self.height_ratio = target
            self.is_ratio_mode = True
        elif isinstance(target, list) or isinstance(target, tuple):
            # 检测其是否为比例模式
            if len(target) == 2:
                if isinstance(target[0], float) and isinstance(target[1], float):
                    self.width_ratio = target[0]
                    self.height_ratio = target[1]
                    self.is_ratio_mode = True
                elif isinstance(target[0], int) and isinstance(target[1], int):
                    self.target_width = target[0]
                    self.target_height = target[1]
                    self.is_ratio_mode = False  # 关闭比例模式
            elif len(target) == 1:
                raise ValueError("Invalid target value.")
        else:
            raise ValueError("Invalid target value.")

        self.interpolation = interpolation
        self.resize_method = resize_method

    def apply(self, image: MioImage) -> bool:
        if image.image_center is None:  # 图像未打开
            raise ValueError("Image not opened.")
        # 检测是否开启按比例缩放模式
        if self.is_ratio_mode:
            # 如果都是1.0，直接返回
            if self.width_ratio == 1.0 and self.height_ratio == 1.0:
                return True
            # 如果都是0.0或小于0.0，抛出异常
            elif self.width_ratio <= 0.0 or self.height_ratio <= 0.0:
                raise ValueError("Invalid ratio value.")
            if self.resize_method == "cv2":
                # 通过resize的fx和fy参数进行调整
                print(self.width_ratio, self.height_ratio)
                image.image_center = cv2_image_to_pil(
                    cv2.resize(
                        pil_image_to_cv2(image.image_center),
                        (0, 0),
                        fx=self.width_ratio,
                        fy=self.height_ratio,
                        interpolation=self.interpolation,
                    )
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            elif self.resize_method == "pil":
                # PIL库的resize方法不支持按比例缩放，需要手动计算
                # 获取当前图像尺寸
                width, height = image.image_center.size
                # 计算目标尺寸
                target_width = int(width * self.width_ratio)
                target_height = int(height * self.height_ratio)
                image.image_center = image.image_center.resize(
                    (target_width, target_height), resample=self.interpolation
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            else:
                raise ValueError("Invalid resize method.")  # 无效的缩放方法
        else:
            # 检测数值合理性
            if self.target_width <= 0 or self.target_height <= 0:
                raise ValueError("Invalid target size.")
            # 如果目标尺寸和原始尺寸一致，直接返回
            elif (
                self.target_width == image.width and self.target_height == image.height
            ):
                return True
            if self.resize_method == "cv2":
                image.image_center = cv2_image_to_pil(
                    cv2.resize(
                        pil_image_to_cv2(image.image_center),
                        (self.target_width, self.target_height),
                        interpolation=self.interpolation,
                    )
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            elif self.resize_method == "pil":
                image.image_center = image.image_center.resize(
                    (self.target_width, self.target_height),
                    resample=self.interpolation,
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            else:
                raise ValueError("Invalid resize method.")


class MioCutEffect(MioEffect):
    """
    pyMio 的裁剪效果器，用于对图像进行裁剪处理

    默认使用opencv-python的裁剪方法进行裁剪，实际上两个库的裁剪方法和速度没什么太大的区别，默认即可
    """

    def __init__(
        self,
        target: tuple[int, int] | list[int] | float | tuple[float, float] | list[float],
        cut_method: str = "cv2",  # 截取方法，可选值为 cv2 或 pil
    ):
        super().__init__()

        self.is_ratio_mode: bool = True  # 是否启用按比例缩放模式
        self.target_width: int = 0
        self.target_height: int = 0
        self.width_ratio: float = 1.0
        self.height_ratio: float = 1.0
        self.cut_method: str = "cv2"

        # 根据传入的参数检查类型并初始化缩放效果器
        if isinstance(target, float):
            self.width_ratio = target
            self.height_ratio = target
            self.is_ratio_mode = True
        elif isinstance(target, list) or isinstance(target, tuple):
            # 检测其是否为比例模式
            if len(target) == 2:
                if isinstance(target[0], float) and isinstance(target[1], float):
                    self.width_ratio = target[0]
                    self.height_ratio = target[1]
                    self.is_ratio_mode = True
                elif isinstance(target[0], int) and isinstance(target[1], int):
                    self.target_width = target[0]
                    self.target_height = target[1]
                    self.is_ratio_mode = False  # 关闭比例模式
            elif len(target) == 1:
                raise ValueError("Invalid target value.")
        else:
            raise ValueError("Invalid target value.")

        self.cut_method = cut_method

    def apply(self, image: MioImage) -> bool:
        if image.image_center is None:  # 图像未打开
            raise ValueError("Image not opened.")
        if self.is_ratio_mode:
            # 合理性判断
            if self.width_ratio == 1.0 and self.height_ratio == 1.0:
                return True
            elif (
                self.width_ratio <= 0.0
                or self.height_ratio <= 0.0
                or self.width_ratio >= 1.0
                or self.height_ratio >= 1.0
            ):
                raise ValueError("Invalid ratio value.")
            if self.cut_method == "cv2":
                cv2_img = pil_image_to_cv2(image.image_center)
                image.image_center = cv2_image_to_pil(
                    cv2_img[
                        : int(image.height * self.height_ratio),
                        : int(image.width * self.width_ratio),
                    ]
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            elif self.cut_method == "pil":
                image.image_center = image.image_center.crop(
                    (
                        0,
                        0,
                        int(image.width * self.width_ratio),
                        int(image.height * self.height_ratio),
                    )
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            else:
                raise ValueError("Invalid cut method.")
        else:
            if self.target_width <= 0 or self.target_height <= 0:
                raise ValueError("Invalid target size.")
            if self.cut_method == "cv2":
                image.image_center = cv2_image_to_pil(
                    pil_image_to_cv2(image.image_center)[
                        : self.target_height, : self.target_width
                    ]
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            elif self.cut_method == "pil":
                image.image_center = image.image_center.crop(
                    (0, 0, self.target_width, self.target_height)
                )
                image.width, image.height = image.image_center.size  # 更新图像尺寸
                return True
            else:
                raise ValueError("Invalid cut method.")


class MioExpandEffect(MioCutEffect):
    pass
