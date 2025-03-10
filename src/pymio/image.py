import base64
from io import BytesIO
from os import PathLike
from pathlib import Path

from numpy import ndarray

from .color import MioColor
from .const import BLACK
from .exception import MioTypeUnexpectedError
from .object import MioObject

from PIL.Image import Image, new, open
import tempfile

from .utils import cv2_image_to_pil, pil_image_to_cv2


class MioImage(MioObject):
    """
    pyMio 的智能图像对象，封装了基础图像处理的功能
    """
    def __init__(self):
        super().__init__()
        # 基本属性
        self.object_type = "image"  # 覆盖 pyMio 对象类型
        self.tags.append("image")  # 添加类型标签
        self.has_rendered = False  # 是否已经渲染过
        self.rendered_times = 0  # 渲染次数

        # 图像数据
        # 图像数据分为三层，分别对应背景、内容、前景
        # 在图像被渲染时，会依次执行效果器，并最终得到背景、内容、前景三层数据，之后合并为最终图像（合并完成后会清空三层数据以节省内存）
        self._orignal_image: Image | None = None  # 原始图像数据
        self._image_bottom: list[Image] | None = None  # 背景数据
        self._image_center: list[Image] | None = None  # 内容数据
        self._image_top: list[Image] | None = None  # 前景数据
        self._result: Image | None = None  # 图像合并结果

        self._original_image_path: Path | None = None  # 图像原始路径
        self.background_color: MioColor = BLACK  # 背景颜色，默认为黑色，这个背景颜色设定仅在不使用图层时生效
        self.rotation = 0  # 旋转角度，单位为度
        self.alpha = 255  # 透明度，默认为不透明
        self.effects = []  # 效果器

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
                self._orignal_image = open(img_path, "r")  # 打开文件
                self._original_image_path = img_path  # 记录文件路径
            except Exception as e:
                raise e
        elif isinstance(img, Image):
            # 传入了 PIL.Image 对象
            self._orignal_image = img
        elif isinstance(img, ndarray):
            # 传入了 ndarray 对象，尝试转换
            try:
                self._orignal_image = cv2_image_to_pil(img)
            except Exception as e:
                raise e
        elif isinstance(img, bytes):
            # 传入了 bytes 对象，尝试转换
            try:
                self._orignal_image = open(BytesIO(img))
            except Exception as e:
                raise e
        elif isinstance(img, BytesIO):
            # 传入了 BytesIO 对象
            self._orignal_image = open(img)
        else:
            raise MioTypeUnexpectedError("str | PathLike | Image | ndarray | bytes | BytesIO", type(img))
        return self # 返回自身，支持链式调用

    def save(self, path: str | PathLike):
        """
        保存图像数据到指定路径
        :param path: 保存路径
        :return: None
        """
        # 检查原始图像数据是否存在
        if self._orignal_image is None:
            raise ValueError("No image data to save.")
        # 保存图像
        i = self.copy().rasterisation()
        i.save(path)

    def to_bytes(self) -> bytes:
        """
        将图像数据转换为字节数据
        :return: 图像数据
        """
        # 检查图像数据是否存在
        if self._orignal_image is None:
            raise ValueError("No image data to convert.")
        # 转换
        i = self.copy().rasterisation()
        return i._orignal_image.tobytes()

    def to_base64(self) -> str:
        """
        将图像数据转换为 base64 字符串
        :return: base64 字符串
        """
        # 检查图像数据是否存在
        if self._orignal_image is None:
            raise ValueError("No image data to convert.")
        # 转换成字节数据
        i = self.copy().rasterisation()
        byte_data = i.to_bytes()
        # 编码为 base64 字符串
        return base64.b64encode(byte_data).decode("utf-8")

    def to_bytes_io(self) -> BytesIO:
        """
        将图像数据转换为 BytesIO 对象
        :return: BytesIO 对象
        """
        # 检查图像数据是否存在
        if self._orignal_image is None:
            raise ValueError("No image data to convert.")
        # 转换
        byte_io = BytesIO()
        i = self.copy().rasterisation()
        i._orignal_image.save(byte_io)
        return byte_io

    def to_image(self) -> Image:
        """
        获取图像数据
        :return: PIL.Image 对象
        """
        # 检查图像数据是否存在
        if self._orignal_image is None:
            raise ValueError("No image data to convert.")
        i = self.copy().rasterisation()
        return i._orignal_image

    def to_cv2(self) -> ndarray:
        """
        将图像数据转换为 cv2 对象
        :return: cv2 对象
        """
        # 检查图像数据是否存在
        if self._orignal_image is None:
            raise ValueError("No image data to convert.")
        # 转换
        i = self.copy().rasterisation()
        return pil_image_to_cv2(i._orignal_image)

    def get_original_path(self, enable_tmp: bool = False) -> Path | None:
        """
        获取图像完整路径
        :param enable_tmp: 默认为 False，启用后会在没有路径时生成临时文件并返回临时文件路径（临时文件位置取决于系统）
        :return: 图像完整路径
        """
        # 首先检测是否有图像数据
        if self._orignal_image is None:
            raise ValueError("No image data to get path.")
        # 如果有图像数据，检查是否有路径
        if self._original_image_path is not None:
            return self._original_image_path
        # 如果没有路径，检查是否需要临时文件
        if enable_tmp:
            # 生成临时文件
            _, temp_file_path = tempfile.mkstemp(suffix='.png')
            i = self.copy().rasterisation()
            i.save(temp_file_path)
            return Path(temp_file_path)

    def copy(self):
        """
        复制当前图像对象
        :return: 复制的图像对象
        """
        new_image = self
        return new_image

    """ 魔术方法 """
    def __add__(self, other: 'MioImage'):
        """
        重载加法运算符，将两个对象合并为一个对象
        :param other: 另一个对象
        :return: 合并后的对象
        """
        return self

    """ 图像处理 """

    """ 绘制 """
    def rasterisation(self):
        """
        栅格化图像，将图像属性全部应用到图像数据上，并重置图像属性
        :return:
        """
        # 检查图像数据是否存在
        return self

    def render(self):
        return self


