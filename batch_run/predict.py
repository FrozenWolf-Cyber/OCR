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
    parser.add_argument(
        "-MTX",
        "--MTX",
        help="Should be <Y> or <N>. If <Y> then the output will be in MTX Hacker Olympics format, if <N> then the output will be of FUND dataset format",
    )
    parser.add_argument(
        "-sr",
        "--sr",
        help="Should be <Y> or <N>. If <Y> then the output will be saved in a seperate JSON file whereas the scores for each label classification and linking will be in seperate file, if <N> then the both will be in same file",
    )


    args = parser.parse_args()
    path = args.path
    sr = args.sr
    MTX = args.MTX

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
        mtx_output = None

        if MTX == "Y":
            mtx_output = []
            for each in result["user_output"]["form"]:
                temp = {}
                temp["id"] = each["id"]
                temp["box"] = each["box"]
                temp["linking"] = each["linking"]
                mtx_output.append(temp)
            mtx_output = {"output":mtx_output}

        if sr == "Y":
            if mtx_output!=None:
                with open(os.path.join("result/",f'{file_name}_output.json'), 'w') as fp:
                    json.dump(mtx_output, fp)

                del result["user_output"]
                with open(os.path.join("result/",f'{file_name}_scores.json'), 'w') as fp:
                    json.dump(result, fp)

            else:
                with open(os.path.join("result/",f'{file_name}_output.json'), 'w') as fp:
                    json.dump(result, fp)

                del result["user_output"]
                with open(os.path.join("result/",f'{file_name}_scores.json'), 'w') as fp:
                    json.dump(result, fp)

        else:
            if mtx_output!=None:
                del result["user_output"]
                mtx_output.update(result)
                with open(os.path.join("result/",f'{file_name}_result.json'), 'w') as fp:
                    json.dump(mtx_output, fp)

            else:
                with open(os.path.join("result/",f'{file_name}_result.json'), 'w') as fp:
                    json.dump(result, fp)

        
        printProgressBar(i + 1, len(os.listdir()), prefix = 'Progress:', suffix = 'Complete', length = 50)


if __name__ == "__main__":
    main()

