import cv2
import os.path
import sys


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
        if fp.endswith('.png') or fp.endswith('.jpg'):
            imgs.append(os.path.join(sys.argv[1], fp))
elif os.path.isfile(sys.argv[1]):
    imgs.append(sys.argv[1])


for fp in imgs:
    print(f"Processing: {fp}")
    img = cv2.imread(fp, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            img2[i][j] = colors[img[i][j]]

    fn, ext = os.path.splitext(fp.split('/')[-1])
    cv2.imwrite(os.path.join(os.path.dirname(fp), fn) + "_visualization" + ext,
                img2)
