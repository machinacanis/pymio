import numpy
import cv2

from PIL import Image


def pil_image_to_cv2(image: Image.Image) -> numpy.ndarray:
    """
    将PIL的图像对象转换为OpenCV的图像对象
    :param image:
    :return:
    """
    return cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGBA2BGRA)  # 注意是将RGBA转换为BGRA的格式，这样才能正常保存透明度数据

def cv2_image_to_pil(image: numpy.ndarray) -> Image:
    """
    将OpenCV的图像对象转换为PIL的图像对象
    :param image:
    :return:
    """
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))  # 注意是将BGRA转换为RGBA的格式，这样才能正常保存透明度数据
