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

from .utils import cv2_image_to_pil, pil_image_to_cv2


class MioImage(MioObject):
    """
    pyMio 的基础图像对象，封装了基础图像处理的功能
    """
    def __init__(self):
        super().__init__()
        # 基本属性
        self.object_type = "image"  # 覆盖 pyMio 对象类型
        self.tags.append("image")  # 添加类型标签

        # 图像数据
        self.image_data: Image | None = None  # 图像数据
        self._image_path: Path | None = None  # 图像完整路径
        self.background_color: MioColor = BLACK  # 背景颜色，默认为黑色，这个背景颜色设定仅在不使用图层时生效
        self.rotation = 0  # 旋转角度，单位为度
        self.alpha = 255  # 透明度，默认为不透明

    """ 读写操作相关 """
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
                self.image_data = open(img_path, "r")  # 打开文件
                self._image_path = img_path  # 记录文件路径
            except Exception as e:
                raise e
        elif isinstance(img, Image):
            # 传入了 PIL.Image 对象
            self.image_data = img
        elif isinstance(img, ndarray):
            # 传入了 ndarray 对象，尝试转换
            try:
                self.image_data = cv2_image_to_pil(img)
            except Exception as e:
                raise e
        elif isinstance(img, bytes):
            # 传入了 bytes 对象，尝试转换
            try:
                self.image_data = open(BytesIO(img))
            except Exception as e:
                raise e
        elif isinstance(img, BytesIO):
            # 传入了 BytesIO 对象
            self.image_data = open(img)
        else:
            raise MioTypeUnexpectedError("str | PathLike | Image | ndarray | bytes | BytesIO", type(img))
        return self # 返回自身，支持链式调用

    def save(self, path: str | PathLike):
        """
        保存图像数据到指定路径
        :param path: 保存路径
        :return: None
        """
        # 检查图像数据是否存在
        if self.image_data is None:
            raise ValueError("No image data to save.")
        # 保存图像
        self.image_data.save(path)

    def to_bytes(self) -> bytes:
        """
        将图像数据转换为字节数据
        :return: 图像数据
        """
        # 检查图像数据是否存在
        if self.image_data is None:
            raise ValueError("No image data to convert.")
        # 转换
        return self.image_data.tobytes()

    def to_base64(self) -> str:
        """
        将图像数据转换为 base64 字符串
        :return: base64 字符串
        """
        # 检查图像数据是否存在
        if self.image_data is None:
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
        # 检查图像数据是否存在
        if self.image_data is None:
            raise ValueError("No image data to convert.")
        # 转换
        byte_io = BytesIO()
        self.image_data.save(byte_io)
        return byte_io

    def to_image(self) -> Image:
        """
        获取图像数据
        :return: PIL.Image 对象
        """
        # 检查图像数据是否存在
        if self.image_data is None:
            raise ValueError("No image data to convert.")
        return self.image_data

    def to_cv2(self) -> ndarray:
        """
        将图像数据转换为 cv2 对象
        :return: cv2 对象
        """
        # 检查图像数据是否存在
        if self.image_data is None:
            raise ValueError("No image data to convert.")
        # 转换
        return pil_image_to_cv2(self.image_data)

    def full_path(self, enable_tmp: bool) -> str:
        pass

