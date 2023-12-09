import json
import argparse
import os.path
import cv2
import numpy as np

# color palette from: https://colorswall.com/palette/171300
colors = [(47,  52,  227),
          (63,  153, 246),
          (74,  237, 255),
          (114, 193, 56),
          (181, 192, 77),
          (220, 144, 51),
          (205, 116, 101),
          (226, 97,  149),
          (155, 109, 246)]


class Image:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path
        self.image = None
        self.undo_stack = []
        self.class_points = {}
        self.cur_antt_class = 0

    def load(self):
        self.image = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)


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
                for clss_pts in i.class_points:
                    if len(i.class_points[clss_pts]):
                        dict[i.name] = i.class_points
        return dict


def draw_circle(img, x, y, clss):
    radius = int(5 * (img.shape[0] / 1024))
    img = cv2.circle(img, (x, y), radius, colors[clss], -1)
    return img


def draw_stack(img, stack):
    for p in stack:
        x, y, clss = p[0:3]
        img = draw_circle(img, x, y, clss)
    return img


def event_handling(x, y, flags, imgs):
    cur_image = imgs.cur_image()
    cur_antt_class = cur_image.cur_antt_class
    cur_image.undo_stack.append((x, y, cur_antt_class))
    # draw_circle(cur_image.image, x, y, cur_antt_class)
    class_points = cur_image.class_points.setdefault(cur_antt_class, [])
    if flags & cv2.EVENT_FLAG_SHIFTKEY:
        if len(class_points) == 0:
            class_points.append([[x, y]])
        else:
            class_points[-1].append([x, y])
    else:
        class_points.append([[x, y]])


def click_event(event, x, y, flags, imgs):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        event_handling(x, y, flags, imgs)


def parser():
    parser = argparse.ArgumentParser("Annotate Images")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-i", help="input images", type=str)
    group.add_argument("-l", help="load annotations", type=str)
    parser.add_argument("--show_name",
                        help="show image names",
                        action="store_true",
                        default=False)
    return parser.parse_args()


def load_directory(dir, images):
    for i in os.listdir(dir):
        if i.endswith('.jpg') or i.endswith('.png'):
            images.append(os.path.join(dir, i))


def load_ann(images, annotations):
    for i in images.list_imgs:
        if i.name in annotations:
            for clss in annotations[i.name]:
                for point_list in annotations[i.name][clss]:
                    i.class_points.setdefault(int(clss), []).append(point_list)
                    images.index = images.list_imgs.index(i)
                    for pts in point_list:
                        i.undo_stack.append((pts[0], pts[1], int(clss)))


def main(args):
    images = WorkingImages()

    if args.i is not None:
        if os.path.isdir(args.i):
            load_directory(args.i, images)
        elif args.i.endswith('.jpg') or args.i.endswith('.png'):
            images.append(args.i)

    elif args.l is not None:
        annotations = json.load(open(args.l))
        load_directory(os.path.dirname(args.l), images)
        load_ann(images, annotations)

    if args.show_name:
        print(str(images.index) + ": " + images.cur_image().name)

    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image', click_event, images)

    while True:
        cur_image = images.cur_image()

        if cur_image.image is None:
            cur_image.load()

        img = np.copy(cur_image.image)
        img = draw_stack(img, cur_image.undo_stack)
        cv2.imshow('Image', img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('u'):
            if len(cur_image.undo_stack) > 0:
                p = cur_image.undo_stack.pop()
                cur_image.class_points[p[2]][-1].pop()
                if len(cur_image.class_points[p[2]][-1]) == 0:
                    del cur_image.class_points[p[2]][-1]

        elif key == ord('n'):
            images.next()
        elif key == ord('p'):
            images.prev()
        elif ord('1') <= key and key <= ord('9'):
            cur_image.cur_antt_class = key - 49

    print(json.dumps(images.annotations()))
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main(parser())
