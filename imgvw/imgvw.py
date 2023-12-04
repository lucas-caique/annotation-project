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
        self.image = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)
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
                for clss_pts in i.class_points:
                    if len(i.class_points[clss_pts]):
                        dict[i.name] = i.class_points
        return dict


def draw_circle(img, x, y, clss):
    radius = int(5 * (img.image.shape[1] / 1024))
    cv2.circle(img.image, (x, y), radius, colors[clss], -1)


def event_handling(x, y, flags, imgs):
    cur_image = imgs.cur_image()
    cur_antt_class = cur_image.cur_antt_class
    cur_image.undo_stack.append((cur_image.image.copy(),
                                 cur_antt_class))
    draw_circle(cur_image, x, y, cur_antt_class)
    class_points = cur_image.class_points.setdefault(cur_antt_class, [])
    if flags & cv2.EVENT_FLAG_SHIFTKEY:
        if len(class_points) == 0:
            class_points.append([x, y])
        elif len(class_points) == 1:
            class_points[-1] = [class_points[-1], [x, y]]
        else:
            class_points[-1].append([x, y])
    else:
        class_points.append([x, y])


def click_event(event, x, y, flags, imgs):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        event_handling(x, y, flags, imgs)


def parser():
    parser = argparse.ArgumentParser("Annotate Images")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-p", help="path to images", type=str)
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


def load_ann(annotations, images):
    for i in images.list_imgs:
        if i.name in annotations:
            for clss in annotations[i.name]:
                for pts in annotations[i.name][clss]:
                    i.undo_stack.append((i.image.copy(), int(clss)))
                    draw_circle(i, pts[0], pts[1], int(clss))
                    i.class_points.setdefault(int(clss), []).append(pts)


def main(args):
    images = WorkingImages()

    if args.p is not None:
        if os.path.isdir(args.p):
            load_directory(args.p, images)
        elif args.p.endswith('.jpg') or args.p.endswith('.png'):
            images.append(args.p)

    elif args.l is not None:
        annotations = json.load(open(os.path.join(args.l, "ann")))
        load_directory(args.l, images)
        load_ann(annotations, images)

    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image', click_event, images)

    if args.show_name:
        print(str(images.index) + ": " + images.cur_image().name)

    while True:
        cur_image = images.cur_image()
        cv2.imshow('Image', cur_image.image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('u'):
            if cur_image.undo_stack:
                cur_image.image, old_antt_clss = cur_image.undo_stack.pop()
                cur_image.class_points[old_antt_clss].pop()
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
