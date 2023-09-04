import json
import argparse
import os.path
import cv2
import sys


# color palette from: https://colorswall.com/palette/171300
colors = [(47, 52, 227),
          (63, 153, 246),
          (74, 237, 255),
          (114, 193, 56),
          (181, 192, 77),
          (220, 144, 51),
          (205, 116, 101),
          (226, 97, 149),
          (155, 109, 246)]


class Image:
    def __init__(self, path):
        self.name = path.split('/')[-1]
        self.path = path
        self.image = cv2.imread(self.path)
        self.undo_stack = []
        self.class_points = {}
        self.cur_antt_class = 0


class WorkingImages:
    def __init__(self):
        self.list_imgs = []
        self.index = 0
        self.size = 0

    def append(self, path):
        img = Image(path)
        self.list_imgs.append(img)
        self.size += 1

    def cur_image(self):
        return self.list_imgs[self.index]

    def next(self):
        if self.size:
            if self.index < self.size - 1:
                self.index += 1
            else:
                self.index = 0

    def prev(self):
        if self.size:
            if self.index > 0:
                self.index -= 1
            else:
                self.index = self.size - 1

    def annotations(self):
        dict = {}
        for i in self.list_imgs:
            if len(i.class_points):
                dict[i.name] = i.class_points
        return dict


def click_event(event, x, y, flags, imgs):
    radius = 10
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cur_image = imgs.cur_image()
        cur_antt_class = cur_image.cur_antt_class
        cur_image.undo_stack.append((cur_image.image.copy(), cur_antt_class))
        cv2.circle(cur_image.image, (x, y), radius, colors[cur_antt_class], -1)
        cur_image.class_points.setdefault(cur_antt_class, []).append((x, y))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Annotate Images")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", metavar="DIRECTORY",
                        help="directory to load images", default = ".")
    group.add_argument("-p", metavar="path/to/image")
    args = parser.parse_args()

    images = WorkingImages()
    if args.p is not None:
        print("Loading " + args.p)
        images.append(args.p)
        print(images.list_imgs[0].name)
    elif args.d is not None:
        for i in os.listdir(args.d):
            if i.endswith('.jpg') or i.endswith('.png'):
                images.append(args.d + "/" + i)

    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image', click_event, images)

    while True:
        cur_image = images.cur_image()
        cv2.imshow('Image', cur_image.image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('u'):
            if cur_image.undo_stack:
                cur_image.image, old_cur_antt_class = cur_image.undo_stack.pop()
                cur_image.class_points[old_cur_antt_class].pop()
        elif key == ord('n'):
            images.next()
        elif key == ord('p'):
            images.prev()
        elif ord('1') <= key and key <= ord('9'):
            cur_image.cur_antt_class = key - 49


    print(json.dumps(images.annotations()))
    cv2.destroyAllWindows()
