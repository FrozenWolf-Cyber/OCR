import os
import json
import argparse
import numpy as np
from PIL import Image
from ocr_predictor import *
from sklearn.metrics import precision_recall_fscore_support

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    # percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {iteration}/{total} {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def pdfProgressBar (iteration, total,page,t_page,document,t_document, decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r"Progress:" |{bar}| {page}/{t_page} pages, {document}/{t_document} documents Converted', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def IOU(box1, box2, screen_size=(480, 640)):  # calculating IOU
    boolean_box1 = np.zeros(screen_size, dtype=bool)
    boolean_box2 = np.zeros(screen_size, dtype=bool)
    x_min, y_min, x_max, y_max = box1
    x_min, y_min, x_max, y_max = int(x_min), int(y_min), int(x_max), int(y_max)
    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            boolean_box1[y][x] = True
    x_min, y_min, x_max, y_max = box2
    x_min, y_min, x_max, y_max = int(x_min), int(y_min), int(x_max), int(y_max)
    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            boolean_box2[y][x] = True
    overlap = boolean_box1 * boolean_box2  # Logical AND
    union = boolean_box1 + boolean_box2  # Logical OR
    return overlap.sum() / float(union.sum())

def acc(y_pred, y_true):
    total = 0
    truth = 0
    for i,j in zip(y_pred, y_true):
        total+=1
        if i == j:
            truth+=1

    return truth/total

def calc_acc_precision_recall_f_score(y_pred, y_true):

    acc, true_positive, false_positive, true_negative, false_negative = 0, 0, 0, 0, 0
    for each_y_pred, each_y_true in zip(y_pred, y_true):
        if each_y_pred == 0:
            if each_y_pred == each_y_true:
                true_negative = true_negative + 1
            else :
                false_negative = false_negative + 1
            
        else :
            if each_y_pred == each_y_true:
                true_positive = true_positive + 1
            else :
                false_positive = false_positive + 1            

    acc = (true_positive + true_negative)/(true_positive + true_negative + false_positive + false_negative)

    if (true_positive + false_positive) == 0:
        precision = -1
    else:
        precision = true_positive / (true_positive + false_positive)

    if (true_positive + false_negative) == 0:
        recall = -1
    else:
        recall = true_positive / (true_positive + false_negative)
    
    if recall == -1 or precision == -1 or (precision + recall) == 0:
        fscore = -1

    else:
        fscore = (2 * precision * recall) / (precision + recall)

    return acc, precision, recall, fscore

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = predictor(device)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-img",
        "--img_path",
        help="Use relative path",
    )
    parser.add_argument(
        "-anno",
        "--anno_path",
        help="Use relative path",
    )
    parser.add_argument(
        "-sr",
        "--sr",
        help="Should be <Y> or <N>. If <Y> then the output will be saved in a seperate JSON file whereas the scores for each label classification and linking will be in seperate file, if <N> then the both will be in same file",
    )


    args = parser.parse_args()
    img_path = args.img_path
    anno_path = args.anno_path


    sr = args.sr

    if "result" not in os.listdir():
        os.mkdir("result")

    if "img_save" not in os.listdir():
        os.mkdir("img_save") #temp place to save img


    printProgressBar(0, len(os.listdir(img_path)), prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, each_path in enumerate(os.listdir(img_path)):
        img = None
        file_name = ""
        if each_path[-3:] in ['png','jpg']:
            file_name = each_path[:-4]
            img = Image.open(os.path.join(img_path,each_path))
        elif each_path[-4:] == "jpeg":
            file_name = each_path[:-5]
            img = Image.open(os.path.join(img_path,each_path)) 
        else:
            continue
        if img.mode != "RGB":
            img = img.convert("RGB")
        result = model.predict(np.asarray(img))
        mtx_output = []
        for each in result["user_output"]["form"]:
            temp = {}
            temp["id"] = each["id"]
            temp["box"] = each["box"]
            temp["label"]  = each["label"]
            temp["linking"] = each["linking"]
            mtx_output.append(temp)
        mtx_output = {"output":mtx_output}

        if sr == "Y":
            with open(os.path.join("result/",f'{file_name}_output.json'), 'w') as fp:
                json.dump(mtx_output, fp)
            del result["user_output"]
            with open(os.path.join("result/",f'{file_name}_scores.json'), 'w') as fp:
                json.dump(result, fp)
        else:
            del result["user_output"]
            mtx_output.update(result)
            with open(os.path.join("result/",f'{file_name}_result.json'), 'w') as fp:
                json.dump(mtx_output, fp)

        shape = tuple(np.asarray(img).shape[:2])
        annotation = json.load(open(os.path.join(anno_path,file_name+".json"),encoding="utf8"))['form']
        class_convertion = {"other":"other","question":"k","answer":"v","header":"k","k":"k","v":"v","key":"k","value":"v"}
        prediction_ground_iou_map = {} #[ground_truth_id:prediction_id]
        label_pred = []
        label_ground = []
        linking_pred = []
        linking_ground = []
        for each_pred_box in mtx_output["output"]:
            truth_match_score = 0;
            p_x_min, p_y_min, p_x_max, p_y_max = each_pred_box["box"]
            for each_truth_box in annotation:
                t_x_min, t_y_min, t_x_max, t_y_max = each_truth_box["box"]
                iou_score = IOU([p_x_min, p_y_min, p_x_max, p_y_max],[t_x_min, t_y_min, t_x_max, t_y_max],shape)
                if iou_score>truth_match_score:
                    truth_match_score = iou_score
                    prediction_ground_iou_map[each_truth_box["id"]] = each_pred_box["id"]
        for truth_box_idx,each_truth_box in enumerate(annotation):
            if each_truth_box["id"] in prediction_ground_iou_map.keys():
                for pred_box_idx, each_pred_box in enumerate(mtx_output["output"]):
                    if prediction_ground_iou_map[each_truth_box["id"]] == each_pred_box["id"]:
                        label_ground.append(class_convertion[each_truth_box["label"]])
                        label_pred.append(class_convertion[each_pred_box["label"]])
                        for link_truth_idx, link_truth in enumerate(each_truth_box["linking"]):
                            linking_ground.append(1)
                            for link_pred_idx,link_pred in enumerate(each_pred_box["linking"]):
                                if link_pred[1] in prediction_ground_iou_map.keys():
                                    if prediction_ground_iou_map[link_pred[1]] in link_truth:
                                        linking_pred.append(1)
                                        each_truth_box["linking"].pop(link_truth_idx)
                                        each_pred_box["linking"].pop(link_pred_idx)
                                        break
                            if len(linking_ground) != len(linking_pred):
                                linking_pred.append(0)
                        for link_pred_ in enumerate(each_pred_box["linking"]):
                            for _ in range(len(link_pred_)):
                                linking_ground.append(0)
                                linking_pred.append(1)

        result_link_metrics = calc_acc_precision_recall_f_score(linking_pred,linking_ground)
        result_label_metrics = list(precision_recall_fscore_support(label_ground,label_pred,average="weighted"))[:-1]
        result_acc = [acc(label_ground,label_pred)]
        result_label_metrics.extend(result_acc)

        result_link_metrics = {"acc":result_link_metrics[0],"precision":result_link_metrics[1],"recall":result_link_metrics[2],"f_score":result_link_metrics[3]}
        result_label_metrics = {"acc":result_label_metrics[3],"precision":result_label_metrics[0],"recall":result_label_metrics[1],"f_score":result_label_metrics[2]}
        with open(os.path.join("result/",f'{file_name}_metrics.json'), 'w') as fp:
            json.dump({"label":result_label_metrics,"linking":result_link_metrics}, fp)

        printProgressBar(i + 1, len(os.listdir(img_path)), prefix = 'Progress:', suffix = 'Completed', length = 50)
                 


if __name__ == "__main__":
    main()

