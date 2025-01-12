import time
from tkinter.constants import BOTTOM

import cv2
import numpy as np
from PIL import Image
from PIL import ImageFont, ImageDraw
# 导入中文字体，指定字号
font = ImageFont.truetype('asset/SimHei.ttf', 26)

from API_KEY import *

# 系统提示词
SYSTEM_PROMPT = '''
我即将说一句给机械臂的指令，你帮我从这句话中提取出起始物体和终止物体，并从这张图中分别找到这两个物体左上角和右下角的像素坐标，输出json数据结构。

请将结果以以下JSON格式输出：
{
 "start": "<起始物体名称>",
 "start_xyxy": [[<左上角x>, <左上角y>], [<右下角x>, <右下角y>]],
 "end": "<终止物体名称>",
 "end_xyxy": [[<左上角x>, <左上角y>], [<右下角x>, <右下角y>]]
}

注意：
1. JSON中的值请根据图片内容准确填充。
2. 输出时仅提供JSON内容，不要包含任何其它说明或解释。
3. 保证像素坐标的准确性，尽可能减小与真实位置的误差。

例如，如果我的指令是：“请帮我把红色方块放在房子简笔画上。” 输出应如下：
{
 "start": "红色方块",
 "start_xyxy": [[102, 505], [324, 860]],
 "end": "房子简笔画",
 "end_xyxy": [[300, 150], [476, 310]]
}

我现在的指令是：
'''

# Yi-Vision调用函数
import openai
from openai import OpenAI
import base64
def yi_vision_api(PROMPT, img_path='photos/vl_now.jpg'):

    '''
    零一万物大模型开放平台，yi-vision视觉语言多模态大模型API
    '''
    
    client = OpenAI(
        api_key=YI_KEY,
        base_url="https://api.lingyiwanwu.com/v1"
    )
    
    # 编码为base64数据
    with open(img_path, 'rb') as image_file:
        image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')
    
    # 向大模型发起请求
    completion = client.chat.completions.create(
      model="yi-vision",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": SYSTEM_PROMPT + PROMPT
            },
            {
              "type": "image_url",
              "image_url": {
                "url": image
              }
            }
          ]
        },
      ]
    )
    # 解析大模型返回结果
    result = eval(completion.choices[0].message.content.strip())
    print('    大模型调用成功！')
    
    return result

def post_processing_viz(result, img_path, check=False):
    
    '''
    视觉大模型输出结果后处理和可视化
    check：是否需要人工看屏幕确认可视化成功，按键继续或退出
    '''

    # 后处理
    img_bgr = cv2.imread(img_path)
    img_h = img_bgr.shape[0]
    img_w = img_bgr.shape[1]

    print(f'img_h: {img_h}, img_w: {img_w}')
    # 缩放因子
    FACTOR = 999
    # 起点物体名称
    START_NAME = result['start']
    # 终点物体名称
    END_NAME = result['end']
    # 起点，左上角像素坐标
    START_X_MIN = int(result['start_xyxy'][0][0] * img_w / FACTOR)
    START_Y_MIN = int(result['start_xyxy'][0][1] * img_h / FACTOR)
    # 起点，右下角像素坐标
    START_X_MAX = int(result['start_xyxy'][1][0] * img_w / FACTOR)
    START_Y_MAX = int(result['start_xyxy'][1][1] * img_h / FACTOR)
    # 起点，中心点像素坐标
    START_X_CENTER = int((START_X_MIN + START_X_MAX) / 2)
    START_Y_CENTER = int((START_Y_MIN + START_Y_MAX) / 2)
    # 终点，左上角像素坐标
    END_X_MIN = int(result['end_xyxy'][0][0] * img_w / FACTOR)
    END_Y_MIN = int(result['end_xyxy'][0][1] * img_h / FACTOR)
    # 终点，右下角像素坐标
    END_X_MAX = int(result['end_xyxy'][1][0] * img_w / FACTOR)
    END_Y_MAX = int(result['end_xyxy'][1][1] * img_h / FACTOR)
    # 终点，中心点像素坐标
    END_X_CENTER = int((END_X_MIN + END_X_MAX) / 2)
    END_Y_CENTER = int((END_Y_MIN + END_Y_MAX) / 2)
    '''
    # 底部点1坐标
    BOTTOM_X_1 = int(result['bottom_xyxy'][0][0] * img_w / FACTOR)
    BOTTOM_Y_1 = int(result['bottom_xyxy'][0][1] * img_h / FACTOR)
    # 底部点2坐标
    BOTTOM_X_2 = int(result['bottom_xyxy'][1][0] * img_w / FACTOR)
    BOTTOM_Y_2 = int(result['bottom_xyxy'][1][1] * img_h / FACTOR)
    '''
    
    # 可视化
    # 画起点物体框
    img_bgr = cv2.rectangle(img_bgr, (START_X_MIN, START_Y_MIN), (START_X_MAX, START_Y_MAX), [0, 0, 255], thickness=3)
    # 画起点中心点
    img_bgr = cv2.circle(img_bgr, [START_X_CENTER, START_Y_CENTER], 6, [0, 0, 255], thickness=-1)
    # 画终点物体框
    img_bgr = cv2.rectangle(img_bgr, (END_X_MIN, END_Y_MIN), (END_X_MAX, END_Y_MAX), [255, 0, 0], thickness=3)
    # 画终点中心点
    img_bgr = cv2.circle(img_bgr, [END_X_CENTER, END_Y_CENTER], 6, [255, 0, 0], thickness=-1)
    '''
    # 画出随机点
    img_bgr = cv2.circle(img_bgr, [BOTTOM_X_1, BOTTOM_Y_1], 6, [0, 255, 0], thickness=-1)
    img_bgr = cv2.circle(img_bgr, [BOTTOM_X_2, BOTTOM_Y_2], 6, [0, 255, 0], thickness=-1)
    '''
    # 写中文物体名称
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB) # BGR 转 RGB
    img_pil = Image.fromarray(img_rgb) # array 转 pil
    draw = ImageDraw.Draw(img_pil)
    # 写起点物体中文名称
    draw.text((START_X_MIN, START_Y_MIN-32), START_NAME, font=font, fill=(255, 0, 0, 1)) # 文字坐标，中文字符串，字体，rgba颜色
    # 写终点物体中文名称
    draw.text((END_X_MIN, END_Y_MIN-32), END_NAME, font=font, fill=(0, 0, 255, 1)) # 文字坐标，中文字符串，字体，rgba颜色
    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR) # RGB转BGR
    # 保存可视化效果图
    cv2.imwrite('photos/vl_new.jpg', img_bgr)

    formatted_time = time.strftime("%Y%m%d%H%M", time.localtime())
    cv2.imwrite('visualizations/{}.jpg'.format(formatted_time), img_bgr)

    # 在屏幕上展示可视化效果图
    cv2.imshow('using_vlm', img_bgr)

    return START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER #, BOTTOM_X_1, BOTTOM_Y_1, BOTTOM_X_2, BOTTOM_Y_2