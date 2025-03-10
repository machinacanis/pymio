import sys
import time

from PIL import Image
import cv2
import timeit

from pymio.image import MioImage
from pymio.utils import cv2_image_to_pil, pil_image_to_cv2


def main():
    # im = Image.open("../mio.png")
    # ci = pil_image_to_cv2(im)
    # cv2.resize(ci, (350, 350), cv2.INTER_LINEAR)
    # im = Image.open("../mio.png")
    # im.resize((350, 350))
    i = MioImage().open(1)

if __name__ == "__main__":
    # 代码开始时间
    total = 1
    timer = timeit.Timer(stmt=main)
    execution_time = timer.timeit(number=total)  # 执行代码100次
    print(f"代码执行平均时间：{execution_time / total * 1000} ms")

    # 使用pil来resize，平均每次7.7ms