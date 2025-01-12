import numpy as np
import pybullet as p

def pixel_to_world(u, v, depth, camera_config):
    # 1. 提取相机内参
    intrinsics = camera_config["intrinsics"]
    fx, fy = intrinsics[0, 0], intrinsics[1, 1]
    cx, cy = intrinsics[0, 2], intrinsics[1, 2]

    # 2. 从像素坐标转换到相机坐标
    Z_c = depth  # 深度值
    X_c = (u - cx) * Z_c / fx
    Y_c = (v - cy) * Z_c / fy
    camera_coords = np.array([X_c, Y_c, Z_c])

    # 3. 从相机坐标转换到世界坐标
    R = np.array(p.getMatrixFromQuaternion(camera_config["rotation"])).reshape(3, 3)
    T = np.array(camera_config["position"])
    world_coords = R @ camera_coords + T

    return world_coords


