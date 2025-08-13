# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import cv2
import numpy as np
from typing import Union
from pathlib import Path

"""
图像的高频信息、低频信息
低频信息：代表着图像中亮度/灰度值/颜色变化很缓慢的区域，描述了图像的主要部分，是对整幅图像强度的综合度量
高频信息：对应着图像变化剧烈的部分，也就是图像的边缘/轮廓、噪声以及细节部分，主要是对图像边缘/轮廓的度量，而人眼对高频分量比较敏感
"""


def read(img_path: Union[str, Path], bg_to_white=False) -> np.ndarray:
    """
    读图片-兼容图片路径包含中文
    :param img_path:
    :param bg_to_white: 是否将图片的透明背景转成白色背景
    :return: np.ndarray
    """
    if isinstance(img_path, str):
        img_path = Path(img_path)
    if isinstance(img_path, Path):
        if bg_to_white:
            img_path = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if img_path is not None and img_path.shape[2] == 4:
                alpha_channel = img_path[:, :, 3]
                if cv2.countNonZero(alpha_channel) < alpha_channel.size:
                    b_channel, g_channel, r_channel, a_channel = cv2.split(img_path)
                    white_background = np.ones_like(a_channel) * 255
                    a_channel = a_channel / 255.0
                    r_channel = r_channel * a_channel + white_background * (1 - a_channel)
                    g_channel = g_channel * a_channel + white_background * (1 - a_channel)
                    b_channel = b_channel * a_channel + white_background * (1 - a_channel)
                    img_path = cv2.merge((b_channel, g_channel, r_channel))
        else:
            img_path = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)
    return img_path


def write(image: np.ndarray, img_write_path: Path):
    """
    写图片-兼容图片路径包含中文
    :param image:
    :param img_write_path:
    :return:
    """
    cv2.imencode(img_write_path.suffix, image[:, :, ::-1])[1].tofile(str(img_write_path))


def is_transparent(img_path: Path):
    """
    判断图片是否透明背景
    :param img_path:
    :return:
    """
    img = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img is not None and img.shape[2] == 4:
        alpha_channel = img[:, :, 3]
        if cv2.countNonZero(alpha_channel) < alpha_channel.size:
            return True
    return False


def transparent_bg_to_white(img_path: Path, save_path: Path = None):
    """
    图片透明背景转成白色背景
    :param img_path:
    :param save_path:
    :return:
    """
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img is not None and img.shape[2] == 4:
        alpha_channel = img[:, :, 3]
        if cv2.countNonZero(alpha_channel) < alpha_channel.size:
            b_channel, g_channel, r_channel, a_channel = cv2.split(img)
            white_background = np.ones_like(a_channel) * 255
            a_channel = a_channel / 255.0
            r_channel = r_channel * a_channel + white_background * (1 - a_channel)
            g_channel = g_channel * a_channel + white_background * (1 - a_channel)
            b_channel = b_channel * a_channel + white_background * (1 - a_channel)
            result = cv2.merge((b_channel, g_channel, r_channel))
            if save_path is not None:
                write(result, save_path)
            return result
    return img


def is_pure_color(image: Union[str, Path, np.ndarray]):
    """
    判断图片是否为纯色
    :param image: 可以是图片路径或numpy数组
    :type image: Union[str, Path, np.ndarray]
    :return: bool
    """
    if not isinstance(image, np.ndarray):
        image = read(image, bg_to_white=False)
    if image.ndim == 2:  # 灰度图
        return np.all(image[0, 0] == image)
    elif image.ndim == 3:  # 彩色图
        return np.all(image[0] == image)
    else:
        return False


def get_image_colors(image: Union[str, Path, np.ndarray]):
    """
    获取图片的颜色数量
    :param image: 可以是图片路径或numpy数组
    :type image: Union[str, Path, np.ndarray]
    :return: int
    """
    image_arr = read(image, False)
    if image_arr.ndim == 2:  # 灰度图
        return len(np.unique(image_arr))
    elif image_arr.ndim == 3:  # 彩色图
        colors = np.unique(image_arr.reshape(-1, image_arr.shape[-1]), axis=0)
        return len(colors)
    else:
        return 0

