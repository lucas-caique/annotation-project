from streetview import search_panoramas, get_panorama_meta, get_panorama
from tqdm import tqdm
import os.path
import csv
import random
import argparse


def get_random_point(pts):
    random.seed()
    return [round(random.uniform(pts[0], pts[2]), 6),
            round(random.uniform(pts[1], pts[3]), 6)]


def get_panoramas_info(pts, n, api_key, year):
    panos = {}
    i = 1
    print("Searching panoramas...")
    with tqdm(total=n, unit='panorama') as pbar:
        while i <= n:
            p = get_random_point(pts)
            tmp = search_panoramas(lat=p[0], lon=p[1])
            # print(f"{p} found panoramas: {len(tmp)}")

            if len(tmp) != 0:
                for pano in tmp:
                    if pano.date is None:
                        pano.date = get_panorama_meta(tmp[0].pano_id,
                                                      api_key).date
                    # Define ano mínimo do panorama
                    if int(pano.date.split('-')[0]) >= year:
                        if pano.pano_id not in panos.keys():
                            # print(f"pano_id: {pano.pano_id} added (found {i} of {n})")
                            panos[pano.pano_id] = pano
                            i += 1
                            pbar.update(1)
                            break
    return panos


def save_metadata(fname, meta):
    if os.path.isfile(fname) is False:
        f = open(fname, 'w', newline='')
        csv.writer(f).writerow(['pano_id',
                                'lat',
                                'lon',
                                'heading',
                                'pitch',
                                'roll',
                                'date'])
    f = open(fname, 'a', newline='')
    l = list(meta.values())
    for pano in l:
        data = []
        for j in pano:
            data.append(j[1])
        csv.writer(f).writerow(data)
    f.close()


def download_images(meta, path, quality):
    print("\nDownloading to: " + path)
    for id in meta:
        if os.path.isfile(path+id+".jpg"):
            print(id+".jpg ja existe")
            break
        print("downloading: " + id + ".jpg")
        image = get_panorama(id, quality)
        # o motivo dessas operações: https://medium.com/@nocomputer/creating-point-clouds-with-google-street-view-185faad9d4ee
        actual_w = 2**quality * 416 
        actual_h = 2**(quality - 1) * 416 

        image = image.crop((0, 0, actual_w, actual_h)).resize((512 * 2**quality,
                                                               512 * 2**(quality - 1)))
        image.save(path + id + ".jpg", "jpeg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--api_key", help="your GOOGLE API key", required=True)
    parser.add_argument("-r", metavar="coord", type=float, nargs=4,
                        help="defines the boundery rectangle for search",
                        default=[-30.001798, -51.207466, -30.088726, -51.184806], # Região Metropolitana de Porto Alegre
                        required=False)
    parser.add_argument("-d", metavar="DIRECTORY",
                        help="directory to save images",
                        default=".")
    parser.add_argument("-n",
                        help="number of panoramas to download",
                        type=int, default=1)
    parser.add_argument("-q", "--quality",
                        help="quality of panoramas (highest = 5)",
                        type=int, choices=[1, 2, 3, 4, 5], default=1)
    parser.add_argument("-y", "--year",
                        help="only allows panoramas taken in \'year\' or later",
                        type=int, default=0)

    args = parser.parse_args()
    path = args.d
    if os.path.isdir(path) is False:
        os.mkdir(path)

    if path[-1] != '/':
        path += '/'

    print(args.r)
    meta = get_panoramas_info(args.r, args.n, args.api_key, args.year)
    save_metadata(path + "metadata", meta)
    download_images(meta, path, args.quality)
