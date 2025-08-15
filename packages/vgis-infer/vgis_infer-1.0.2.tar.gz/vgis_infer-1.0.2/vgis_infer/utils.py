"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :vgis_python_package
@File    :utils.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2025/8/1 14:17
@Descr:
"""
import base64
import json
import os
import re
import time
from io import BytesIO
import cv2
import requests
from toollib.guid import SnowFlake
from PIL import Image

@staticmethod
def get_ai_service_token(RS_AI_SERVICE_URL):
    url = "{}/user/loginWithForce/".format(RS_AI_SERVICE_URL)

    payload = json.dumps({
        "username": "admin",
        "password": "admin",
        "verifcation": "42FF8F",
        "client_time": int(time.time() * 1000)
    })
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'sessionid=k22jiy8ktaqh13ddbdu5tfdp8dgizr6w'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return json.loads(response.text)["token"]

# 调用AI服务
@staticmethod
def toggle_ai_service(url, pay_json):
    
    headers = {
        # 'Authorization': 'Token {}'.format(token_value),
        'Content-Type': 'application/json',
        'Cookie': 'sessionid=k22jiy8ktaqh13ddbdu5tfdp8dgizr6w'
    }
    payload = json.dumps(pay_json)
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)

# 上传文件
@staticmethod
def upload_file_service(upload_url, file_path):
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f)}
        response = requests.post(upload_url, files=files)
        # 返回JSON响应
    if "file_path" in response.json():
        return response.json()["file_path"]
    else:
        assert "图片上传失败"

# 获取唯一码：雪花ID
@staticmethod
def snowflakeId():
    # worker_id  = 0,
    # datacenter_id = 0,
    snow = SnowFlake(worker_id_bits=0,datacenter_id_bits=0)
    return snow.gen_uid()

# 将base64字符串保存为图片
@staticmethod
def save_base64_image(base64_str: str, output_path: str):
    """
    将Base64图像数据保存到本地文件，自动从Base64字符串中提取图像类型

    参数:
    base64_str: 包含MIME类型前缀的Base64字符串
    output_path: 输出文件路径（可以带或不带扩展名）

    返回:
    实际保存的文件路径
    """
    try:
        # 提取MIME类型（如"image/jpeg"）
        mime_match = re.search(r'data:(image/[^;]+);base64', base64_str)
        if not mime_match:
            raise ValueError("无效的Base64图像格式，缺少MIME类型信息")

        mime_type = mime_match.group(1)
        # 提取纯Base64数据（移除前缀）
        base64_data = base64_str.split(",")[1]

        # 将MIME类型映射到文件扩展名
        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
            "image/tiff": ".tiff",
            "image/svg+xml": ".svg"
        }

        # 获取文件扩展名
        file_ext = mime_to_ext.get(mime_type.lower())
        if not file_ext:
            # 对于未知类型，使用MIME类型中的最后部分作为扩展名
            file_ext = "." + mime_type.split("/")[-1]
            print(f"警告: 未知的图像类型 '{mime_type}', 使用扩展名 '{file_ext}'")

        # 确保输出路径有正确的扩展名
        filename, orig_ext = os.path.splitext(output_path)
        if not orig_ext or orig_ext.lower() != file_ext:
            output_path = filename + file_ext

        # 解码并保存图像
        image_data = base64.b64decode(base64_data)
        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"图片已保存至: {output_path} (类型: {mime_type})")
        return output_path

    except (ValueError, IndexError) as e:
        print(f"Base64格式错误: {e}")
    except base64.binascii.Error as e:
        print(f"Base64解码失败: {e}")
    except IOError as e:
        print(f"文件写入失败: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    return None

@staticmethod
def get_size_of_image(image_path):
    # 打开图像文件
    img = Image.open(image_path)
    # 获取图像尺寸 (宽度, 高度)
    return img.size

@staticmethod
def get_size_of_url_image_type(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img.size


@staticmethod
def get_video_info(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    # 获取宽度（分辨率）
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 获取总帧数和帧率
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 计算时长（秒）
    duration = total_frames / fps if fps > 0 else 0

    cap.release()
    return {
        "width": width,  # 视频宽度（像素）
        "height": height,  # 视频高度（像素）
        "duration": duration,  # 视频时长（秒）
        "fps": fps  # 帧率（可选）
    }

@staticmethod
def get_predict_cname_by_ename(ename):
    if ename=="storagetank":
        return "储油罐"



