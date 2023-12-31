from streetview import search_panoramas, get_panorama_meta, get_panorama
from tqdm import tqdm
import os.path
import csv
import random
import argparse
import os.path


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
            continue
        print("downloading: " + id + ".jpg")
        image = get_panorama(id, quality)
        # o motivo dessas operações: https://medium.com/@nocomputer/creating-point-clouds-with-google-street-view-185faad9d4ee
        actual_w = 2**quality * 416 
        actual_h = 2**(quality - 1) * 416 

        image = image.crop((0, 0, actual_w, actual_h)).resize((512 * 2**quality,
                                                               512 * 2**(quality - 1)))
        image.save(os.path.join(path, id + ".jpg"), "jpeg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--api_key", help="your GOOGLE API key",
                        required=True)
    parser.add_argument("-r", metavar="coord", type=float, nargs=4,
                        help="defines the boundery rectangle for search",
                        # Região Metropolitana de Porto Alegre
                        default=[-30.001798, -51.207466,  # top-left corner
                                 -30.088726, -51.184806]) # bottom right
    parser.add_argument("-d", metavar="Directory",
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
    parser.add_argument("-m", "--metadata",
                        help="download from metadata file",
                        type=str)
    parser.add_argument("-p", "--panorama",
                        help="downloads an image based on an panorama_id")

    args = parser.parse_args()

    if args.metadata is not None:
        ids = []
        fn = csv.DictReader(open(args.metadata))
        i = 1
        for row in fn:
            meta = {}
            pano_id = row['pano_id']
            if pano_id + ".jpg" in os.listdir(os.path.split(args.metadata)[0]):
                print(f"{pano_id} found")
                i = i + 1
                continue
            meta[pano_id] = get_panorama_meta(pano_id=pano_id,
                                              api_key=args.api_key)
            print(f"retrieving metadata {pano_id} ({i})")
            download_images(meta,
                            os.path.dirname(args.metadata),
                            args.quality)
            i = i + 1
    elif args.panorama is not None:
        pano_id = args.panorama
        meta = {}
        meta[pano_id] = get_panorama_meta(pano_id=pano_id,
                                          api_key=args.api_key)
        download_images(meta, args.d, args.quality)
    else:
        path = os.path.join(args.d, "")
        if os.path.isdir(path) is False:
            os.mkdir(path)

        print(f"Searching inside {args.r}")
        meta = get_panoramas_info(args.r, args.n, args.api_key, args.year)
        save_metadata(path + "metadata", meta)
        download_images(meta, path, args.quality)
