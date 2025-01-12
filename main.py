from constants import WORKSPACE_LIMITS, IMAGE_SIZE
from environment_sim import Environment
from scipy.spatial.transform import Rotation as R_
from utils_vlm import *
from utils_agent import *
from photo2truth import *
from angle_cal import *
import pybullet as p
import time
import numpy as np
import cv2

order = '请把绿色立方体放到奶龙上'

prompt_text = AGENT_SYS_PROMPT + order
messages = [{
    'role': 'user',
    'content': [
        {
            'text': prompt_text
        },
    ]
}]

generated_text = generate_plan(messages)
print(generated_text)

while True:
    value = input("请输入 'continue' 以继续：")
    if value == "continue":
        print("程序继续运行...")
        break
    else:
        print("输入错误，请重新输入！")

camera_config = {
    "position": np.array([0.5, 0, 0.5]),  # 相机位置 (x, y, z)
    "rotation": p.getQuaternionFromEuler([0, np.pi, np.pi]),  # 相机旋转 (四元数)
    "intrinsics": np.array([[500, 0, 320], [0, 500, 240], [0, 0, 1]]),  # 内参矩阵
    "image_size": (480, 640),  # 图像分辨率 (height, width)
    "zrange": (0.01, 10.0),  # 深度范围
    "noise": False,  # 是否添加噪声
}


env = Environment()
env.reset()


# 加载 URDF 文件
platform1 = p.loadURDF("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\platform.urdf",basePosition = [0.5, -0.05, 0])
platform2 = p.loadURDF("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\platform.urdf",basePosition = [0.5, -0.18, 0])
platform3 = p.loadURDF("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\platform.urdf",basePosition = [0.5, 0.05, 0])
platform4 = p.loadURDF("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\platform.urdf",basePosition = [0.5, 0.18, 0])

cube = p.loadURDF("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\cube.urdf",basePosition = [0.35, 0.11, 0.03])
# 手动加载纹理
texture_id1 = p.loadTexture("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\LiYunlong.jpg")
texture_id2 = p.loadTexture("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\NaiLong.jpg")
texture_id3 = p.loadTexture("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\DingDongji.jpg")
texture_id4 = p.loadTexture("D:\\Anaconda\\envs\\Pybullet\\Lib\\site-packages\\pybullet_data\\assets\\simplified_objects\\PeiQi.jpg")
p.changeVisualShape(platform1, -1, textureUniqueId=texture_id1)  # 应用纹理
p.changeVisualShape(platform2, -1, textureUniqueId=texture_id2)  # 应用纹理
p.changeVisualShape(platform3, -1, textureUniqueId=texture_id3)  # 应用纹理
p.changeVisualShape(platform4, -1, textureUniqueId=texture_id4)  # 应用纹理

# env.add_object_push_from_file3("object.txt", workspace_limits=WORKSPACE_LIMITS)
env.add_object_push_from_file4("object.txt", workspace_limits=WORKSPACE_LIMITS)

width, height, color, depth, segm = env.render_camera(camera_config)
rgb_image = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)  # BGR 转 RGB
cv2.imwrite("photos/vl_now.jpg", rgb_image)

'''
grasp_pose1 = [[0.4, 0.2, 0.1], [0, 0, 0, 1]]
grasp_pose2 = [[0.8, 0.8, 0.2], [0, 0, 0, 1]]

env.go_home()
env.move_ee_pose(grasp_pose1, speed=0.0005)
print('move successfully')
'''
# while not success:

result1 = yi_vision_api(order)
START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER = post_processing_viz(result1, img_path = "photos/vl_now.jpg", check=True)

result_angle = angle("photos/vl_now.jpg", show_image=True)
ang = result_angle["angle"]
print(f'angle:', ang)

theta =  np.radians(ang)

START_Y_CENTER = int(result_angle["center"][1])
START_X_CENTER = int(result_angle["center"][0])
# test
depth_value_start = depth[START_Y_CENTER, START_X_CENTER]  # 从深度图中提取深度值
world_coords_start = pixel_to_world(START_X_CENTER, START_Y_CENTER, depth_value_start, camera_config)
print("起始世界坐标: ", world_coords_start)

depth_value_end = depth[END_Y_CENTER, END_X_CENTER]
world_coords_end = pixel_to_world(END_X_CENTER, END_Y_CENTER, depth_value_end, camera_config)
world_coords_end[2] = 0.01
print("终点世界坐标: ", world_coords_end)

'''
_, pos, ort = env.get_true_object_pose(1)
pose1 = np.array(pos + ort)
print("pose1: ", pose1)
env.move_ee_pose(pose1, speed=0.005)
env.go_home()
'''
[a, b, c] = world_coords_start.tolist()
pose_start = [a, b, c, theta, 0, 0]

[a1, b1, c1] = world_coords_end.tolist()
pose_end = [[a1, b1, c1+0.2], [0, 1, 0, 0]]

pose_end2 = [[a1, b1, c1+0.2], [0, 0, np.pi]]



'''
pose1 = [a, b, c, 0, 0, np.sin(theta/2), np.cos(theta/2)]
pose2 = [[a, b, c], theta, 0, 0]
pose3 = [[a, b, c], 0, 0, np.sin(theta/2), np.cos(theta/2)]
print("pose1: ", pose1)
print("pose2: ", pose2)
print("pose3: ", pose3)
'''


env.go_home()
# env.grasp(pose_test, speed=0.0005)
success, _, _ = env.grasp(pose=pose_start, pose2=pose_end2, speed=0.0005)
# env.go_home
# env.move_ee_pose([[0.499, -0.21799969, 0.01],[3.14159265, 0, 0]], speed=0.0005)
env.go_home()



while True:
    p.stepSimulation()  # 维持仿真循环


'''
# 显示彩色图像
cv2.imshow("RGB Image", cv2.cvtColor(color, cv2.COLOR_RGB2BGR))
cv2.waitKey(0)
# 显示深度图像
plt.imshow(depth, cmap="hot")
plt.colorbar()
plt.title("Depth Image")
plt.show()
# 显示分割图像
plt.imshow(segm, cmap="jet")
plt.colorbar()
plt.title("Segmentation Image")
plt.show()
'''

