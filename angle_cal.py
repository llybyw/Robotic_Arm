import cv2
import numpy as np
import os

def angle(Image_path, color_range=((40, 40, 40), (80, 255, 255)), show_image=False, save_path="photos/angle.jpg"):
    """
    计算图像中绿色区域的旋转角度。

    Args:
        Image_path (str): 输入图像路径。
        color_range (tuple): HSV颜色范围，默认绿色。
        show_image (bool): 是否显示处理后的图像。
        save_path (str): 如果指定路径，则保存处理后的图像。

    Returns:
        dict or None: 最大绿色区域的旋转角度、面积和中心坐标。如果没有找到返回 None。
    """
    # 读取图像
    image = cv2.imread(Image_path)
    if image is None:
        raise ValueError("Image not found or unable to read!")

    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_bound, upper_bound = color_range
    mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))

    # 提取轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 如果没有找到轮廓
    if not contours:
        print("No green areas detected.")
        return None

    # 遍历轮廓，找到最大绿色区域
    max_area = 0
    result = {"angle": None, "area": None, "center": None}
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:  # 找到面积最大的绿色区域
            max_area = area
            rect = cv2.minAreaRect(contour)
            angle = rect[-1]
            if angle < -45:
                angle = 90 + angle

            # 更新结果
            result["angle"] = angle
            result["area"] = area
            result["center"] = rect[0]

            # 绘制矩形框
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(image, [box], 0, (255, 0, 0), 2)
            cv2.putText(image, f"Angle: {angle:.2f}", (int(rect[0][0]), int(rect[0][1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # 显示或保存结果
    if show_image:
        cv2.imshow("Processed Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    cv2.imwrite(save_path, image)

    return result



