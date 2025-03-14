import timeit

from pymio import const
from pymio.image import MioCutEffect, MioImage


def main():
    img = MioImage("./mio.png")
    img.add_effect(MioCutEffect([300, 300], "pil"))


if __name__ == "__main__":
    # 代码开始时间
    total = 100
    timer = timeit.Timer(stmt=main)
    execution_time = timer.timeit(number=total)  # 执行代码n次
    print(f"代码执行平均时间：{execution_time / total * 1000} ms")

    # 使用pil来resize，平均每次7.7ms
