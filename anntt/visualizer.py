import cv2
import os.path
import sys
import numpy as np


colors = [(0,   0,     0),
          (47,  52,  227),
          (63,  153, 246),
          (74,  237, 255),
          (114, 193,  56),
          (181, 192,  77),
          (220, 144,  51),
          (205, 116, 101),
          (226, 97,  149),
          (155, 109, 246)]

imgs = []
if os.path.isdir(sys.argv[1]):
    for fp in os.listdir(sys.argv[1]):
        if fp.endswith(".npy"):
            imgs.append(os.path.join(sys.argv[1], fp))
elif os.path.isfile(sys.argv[1]):
    imgs.append(sys.argv[1])


for fp in imgs:
    print(f"Processing: {fp}")
    img = np.load(fp)
    img2 = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            # print(img[i][j][0])
            img2[i][j] = colors[img[i][j][0]]

    fn, _ = os.path.splitext(os.path.basename(fp))
    cv2.imwrite(os.path.join(os.path.dirname(fp), fn) + ".png", img2)
