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
                        help="path to save image ",)
    parser.add_argument("-a",
                        "--annotation",
                        type=str,
                        help="path to the annotation file")
    parser.add_argument("--show_masks",
                        action="store_true",
                        help="show masks for each point",
                        default=False)
    parser.add_argument("--imgsz",
                        type=int,
                        help="size of the image",
                        default=1024)
    parser.add_argument("--overlay",
                        action="store_true",
                        help="save overlay",
                        default=False)
    args = parser.parse_args()

    if args.output is None:
        args.output = os.path.join(args.img_path, "output")
        if os.path.isdir(args.output) is False:
            os.mkdir(args.output)

    if args.annotation is None:
        args.annotation = os.path.join(args.img_path, "ann")

    assert os.path.isfile(args.annotation) is True, "Annotation file invalid"
    annotations = json.load(open(args.annotation))

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
                                   imgsz=args.imgsz,
                                   conf=0.4,
                                   iou=0.9,)
        prompt_process = FastSAMPrompt(IMAGE_PATH,
                                       everything_results,
                                       device=DEVICE)

        masks = []
        p = []
        for clss in annotations[fn]:
            count = 1
            for pts in annotations[fn][clss]:
                p.append(pts)
                print(f"{pts}: {clss}")
                ann = prompt_process.point_prompt(points=[pts],
                                                  pointlabel=[1])
                largestCC = getLargestCC(ann[0])
                if largestCC is not None:
                    chn1 = largestCC.astype(np.uint8) * (int(clss) + 1)
                    chn2 = largestCC.astype(np.uint8) * count
                    masks.append(np.stack((chn1, chn2), axis=-1))
                    count += 1
                    if args.show_masks:
                        plt.imshow(largestCC)
                        plt.show()
            print('')

        n, e = os.path.splitext(fn)
        output_path = os.path.join(args.output, n)

        if len(masks):
            out = np.zeros(masks[0].shape, dtype=np.uint8)
            for i in range(0, out.shape[0]):
                for j in range(0, out.shape[1]):
                    for z in range(0, len(masks)):
                        if masks[z][i][j][0] != 0:
                            out[i][j] = masks[z][i][j]
                            break

                with open(output_path + '.npy', 'wb') as f:
                    np.save(f, out)

            if args.overlay is True:
                ann = prompt_process.point_prompt(points=p,
                                                  pointlabel=[1]*len(p))
                prompt_process.plot(annotations=ann,
                                    withContours=False,
                                    mask_random_color=False,
                                    better_quality=True,
                                    output_path=output_path + '.png')
