from fastsam import FastSAM, FastSAMPrompt
import cv2
import os.path
import argparse
import json
from matplotlib import pyplot as plt
import numpy as np
from skimage.measure import label


def getLargestCC(segmentation):
    labels = label(segmentation)
    if (labels.max() != 0):
        largestCC = labels == np.argmax(np.bincount(labels.flat)[1:])+1
        return largestCC
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path",
                        type=str,
                        help="path to model",
                        default="./weights/FastSAM-x.pt")
    parser.add_argument("-i",
                        "--img_path",
                        type=str,
                        help="path to image",
                        required=True)
    parser.add_argument("-o",
                        "--output",
                        type=str,
                        help="path to save image ",
                        required=True)
    parser.add_argument("-p",
                        "--points",
                        type=json.loads,
                        help="points prompt",
                        required=True)
    parser.add_argument("--show_masks",
                        action="store_true",
                        help="show masks for each point",
                        default=False)
    args = parser.parse_args()

    annotations = args.points
    model = FastSAM(args.model_path)
    DEVICE = 'cpu'
    IMAGE_PATH = args.img_path

    for fn in annotations.keys():
        if os.path.isdir(args.img_path):
            IMAGE_PATH = os.path.join(args.img_path, fn)
        elif args.img_path.split('/')[-1] != fn:
            continue

        print(f"processing: {IMAGE_PATH}")
        everything_results = model(IMAGE_PATH,
                                   device=DEVICE,
                                   retina_masks=True,
                                   conf=0.4,
                                   iou=0.9,)
        prompt_process = FastSAMPrompt(IMAGE_PATH,
                                       everything_results,
                                       device=DEVICE)

        masks = []
        for clss in annotations[fn]:
            for pts in annotations[fn][clss]:
                print(f"{pts}: {clss}")
                ann = prompt_process.point_prompt(points=[pts],
                                                  pointlabel=[1])
                largestCC = getLargestCC(ann[0])
                if largestCC is not None:
                    masks.append((int(clss)+1)*largestCC)
                    if args.show_masks:
                        plt.imshow(largestCC)
                        plt.show()
            print('')

        if os.path.isdir(args.output) is False:
            os.mkdir(args.output)

        n, e = os.path.splitext(fn)
        np.save(args.output + n, masks)
        cv2.imwrite(args.output + n + "_masks.png", sum(masks))
