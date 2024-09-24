import numpy as np
import cv2
import csv
import os
import math

def load_denorm(denorm_file):
    with open(denorm_file, 'r') as f:
        lines = f.readlines()
    denorm = np.array([float(item) for item in lines[0].split(' ')])
    return denorm

def load_calib(calib_file, denorm_path):
    with open(os.path.join(calib_file), 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=' ')
        for line, row in enumerate(reader):
            if row[0] == 'P2:':
                P2 = np.array([float(i) for i in row[1:]], dtype=np.float32).reshape(3, 4)
                K = P2[:3, :3]
            if row[0] == 'Tr_velo_to_cam:':
                Tr_velo_to_cam = np.zeros((4, 4))
                Tr_velo_to_cam[:3, :4] = np.array([float(i) for i in row[1:]]).astype(float).reshape(3,4)
                Tr_velo_to_cam[3, 3] = 1
                break
        denorm = load_denorm(denorm_path)
    return K, P2, denorm

def compute_box_3d_camera(dim, location, rotation_y, denorm):
    c, s = np.cos(rotation_y), np.sin(rotation_y)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float32)
    l, w, h = dim[2], dim[1], dim[0]
    x_corners = [l/2, l/2, -l/2, -l/2, l/2, l/2, -l/2, -l/2]
    y_corners = [0,0,0,0,-h,-h,-h,-h]
    z_corners = [w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2]

    corners = np.array([x_corners, y_corners, z_corners], dtype=np.float32)
    corners_3d = np.dot(R, corners) 

    denorm = denorm[:3]
    denorm_norm = denorm / np.sqrt(denorm[0]**2 + denorm[1]**2 + denorm[2]**2)
    ori_denorm = np.array([0.0, -1.0, 0.0])
    theta = -1 * math.acos(np.dot(denorm_norm, ori_denorm))
    n_vector = np.cross(denorm, ori_denorm)
    n_vector_norm = n_vector / np.sqrt(n_vector[0]**2 + n_vector[1]**2 + n_vector[2]**2)
    rotation_matrix, j = cv2.Rodrigues(theta * n_vector_norm)
    corners_3d = np.dot(rotation_matrix, corners_3d)
    corners_3d = corners_3d + np.array(location, dtype=np.float32).reshape(3, 1)
    return corners_3d.transpose(1, 0)

def project_to_image(pts_3d, P):
  pts_3d_homo = np.concatenate(
    [pts_3d, np.ones((pts_3d.shape[0], 1), dtype=np.float32)], axis=1)
  pts_2d = np.dot(P, pts_3d_homo.transpose(1, 0)).transpose(1, 0)
  pts_2d = pts_2d[:, :2] / pts_2d[:, 2:]
  return pts_2d

def draw_box_3d(image, corners, c=(0, 255, 0)):
  face_idx = [[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
  for ind_f in [3, 2, 1, 0]:
    f = face_idx[ind_f]
    for j in [0, 1, 2, 3]:
      cv2.line(image, (int(corners[f[j], 0]), int(corners[f[j], 1])),
               (int(corners[f[(j+1)%4], 0]), int(corners[f[(j+1)%4], 1])), c, 2, lineType=cv2.LINE_AA)
    if ind_f == 0:
      cv2.line(image, (int(corners[f[0], 0]), int(corners[f[0], 1])),
               (int(corners[f[2], 0]), int(corners[f[2], 1])), c, 1, lineType=cv2.LINE_AA)
      cv2.line(image, (int(corners[f[1], 0]), int(corners[f[1], 1])),
               (int(corners[f[3], 0]), int(corners[f[3], 1])), c, 1, lineType=cv2.LINE_AA)
  return image

# 修改成不是讀檔案畫標記，而是讀label_list
def draw_3d_box_on_image(image, label_list, P2, denorm, c=(0, 255, 0)):

    color_map = {"Car":(0, 255, 0), "Bus":(0, 255, 255), "Pedestrian":(255, 255, 0), "Cyclist":(0, 0, 255)}

    # # 原本的
    # with open(label_2_file) as f:
    #   for line in f.readlines():
    #       line_list = line.split('\n')[0].split(' ')
    #       object_type = line_list[0]
    #       if object_type not in color_map.keys(): continue
    #       dim = np.array(line_list[8:11]).astype(float)
    #       location = np.array(line_list[11:14]).astype(float)
    #       rotation_y = float(line_list[14])
    #       box_3d = compute_box_3d_camera(dim, location, rotation_y, denorm)
    #       box_2d = project_to_image(box_3d, P2)
    #       image = draw_box_3d(image, box_2d, c=color_map[object_type])
    # return image

    for obj in label_list:
        # obj: Class, Height, Width, Length, x, y, z, rotation
        object_type = obj[0]
        dim = np.array([float(obj[1]), float(obj[2]), float(obj[3])])
        location = np.array([float(obj[4]), float(obj[5]), float(obj[6])])
        rotation_y = float(obj[7])
        box_3d = compute_box_3d_camera(dim, location, rotation_y, denorm)
        box_2d = project_to_image(box_3d, P2)
        image = draw_box_3d(image, box_2d, c=color_map[object_type])
    return image


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
        
    return False

def write_kitti_in_txt(label_list, path_txt):
    # wf = open(path_txt, "w")
    new_data = []
    for line in label_list:
        obj_type = str(line[0])
        h = float(line[1])
        w = float(line[2])
        l = float(line[3])
        location_x = float(line[4])
        location_y = float(line[5])
        location_z = float(line[6])
        rotation_y = float(line[7])
        kitti_line = f"{obj_type} 0 0 0 0 0 0 0 {h:.4f} {w:.4f} {l:.4f} {location_x:.4f} {location_y:.4f} {location_z:.4f} {rotation_y:.4f}"
        new_data.append(kitti_line)
    
    with open(path_txt, 'w') as kittiFile:
        for kittiData in new_data:
            kittiFile.write(kittiData + "\n")
    # for line in pred_lines:
    #     line_string = " ".join(line) + "\n"
    #     wf.write(line_string)
    # wf.close()