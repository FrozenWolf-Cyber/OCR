from ntpath import join
import os
import json
import argparse
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from ocr_predictor import *

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

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = predictor(device)
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
    parser.add_argument(
        "-pdf",
        "--pdf",
        help="Should be <Y> or <N>. If <Y> then the target folder contains multiple .pdf documents, if <N> then the folder contains multiple .png,.jpg,.jpeg documents",
    )


    args = parser.parse_args()
    path = args.path
    sr = args.sr
    MTX = args.MTX
    pdf = args.pdf # Check if target is pdf

    if pdf == "Y":
        pdf = True
    
    else:
        pdf = False

    if "result" not in os.listdir():
        os.mkdir("result")

    if "img_save" not in os.listdir():
        os.mkdir("img_save") #temp place to save img


    if not pdf:
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
                    temp["label"]  = each["label"]
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


            printProgressBar(i + 1, len(os.listdir(path)), prefix = 'Progress:', suffix = 'Completed', length = 50)

    else:
        converted = []
        n_pages = 0
        all_docs = os.listdir(path)
        for document in all_docs:
            each_doc = []
            pages = convert_from_path(os.path.join(path,document),fmt='jpeg')
            for page in pages:
                n_pages +=1
                page.save("result/temp.jpeg")
                img = Image.open("result/temp.jpeg")

                if img.mode != "RGB":
                    img = img.convert("RGB")

                each_doc.append(np.asarray(img))

            converted.append(each_doc)

        os.remove("result/temp.jpeg")


        pdfProgressBar(0,n_pages,0,n_pages,0,len(all_docs),length=50)
        iteration = 0
        for document_idx, (doc_nam, doc_img) in enumerate(zip(all_docs, converted)):
            each_doc_output = {}
            each_doc_result = {}
            if doc_nam not in os.listdir("result"):
                os.mkdir("result/"+doc_nam)

            for page_idx, page_img in enumerate(doc_img):
                result = model.predict(page_img)
                if MTX == "Y":
                    each_doc_output[page_idx] = []
                    for each in result["user_output"]["form"]:
                        temp = {}
                        temp["id"] = each["id"]
                        temp["box"] = each["box"]
                        temp["linking"] = each["linking"]
                        temp["label"]  = each["label"]
                        each_doc_output[page_idx].append(temp)

                else :
                    each_doc_output[page_idx] = result["user_output"]

                del result["user_output"]
                each_doc_result[page_idx] = result.copy()
                iteration +=1
                pdfProgressBar(iteration,n_pages,page_idx,len(doc_img),document_idx,len(all_docs),length=50)


            if sr == "Y":
                with open(f"result/{doc_nam}/output.json", 'w') as fp:
                    json.dump(each_doc_output, fp)
                with open(f"result/{doc_nam}/result.json", 'w') as fp:
                    json.dump(each_doc_result, fp)

            else:
                with open(f"result/{doc_nam}/output_result.json", 'w') as fp:
                    json.dump({"output":each_doc_output,"result":each_doc_result}, fp)               


if __name__ == "__main__":
    main()

