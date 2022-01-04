from ntpath import join
import os
import cv2
import json
import torch
import argparse
import numpy as np
from PIL import Image
from ocr_predictor import *

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def main():
    model = predictor("cpu")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-path",
        "--path",
        help="Use relative path",
    )

    args = parser.parse_args()
    path = args.path

    if "result" not in os.listdir():
        os.mkdir("result")

    if "img_save" not in os.listdir():
        os.mkdir("img_save") #temp place to save img

    printProgressBar(0, len(os.listdir(path)), prefix = 'Progress:', suffix = 'Complete', length = 50)

    for i, each_path in enumerate(os.listdir(path)):
        img = None
        file_name = ""
        if each_path[-3:] in ['png','jpg']:
            file_name = each_path[:-4]
            img = Image.open(os.path.join(path,each_path))

        elif each_path[-4:] == "jpeg":
            file_name = each_path[:-5]
            img = Image.open(os.path.join(path,each_path)) 

        else:
            continue

        if img.mode != "RGB":
            img = img.convert("RGB")

        result = model.predict(np.asarray(img))
        
        with open(os.path.join("result/",f'{file_name}.json'), 'w') as fp:
            json.dump(result, fp)

        
        printProgressBar(i + 1, len(os.listdir()), prefix = 'Progress:', suffix = 'Complete', length = 50)


if __name__ == "__main__":
    main()

