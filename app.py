import os
import io
import random
import shutil
import string
import pickle
import json

from pdf2image.generators import threadsafe
from werkzeug.wrappers import response
from ocr_predictor import predictor
from flask import Flask, request, Response, jsonify, render_template, send_file
from PIL import Image
import numpy as np
from pdf2image import convert_from_path
import matplotlib.pyplot as plt

predictor_model = predictor('cpu')

app = Flask(__name__)

alphabet_set = string.ascii_letters

def create_id():
    id = ''
    for i in range(5):
        id = id + random.choice(alphabet_set)

    id = id + str(random.randrange(1000,10000))
    return id

def predictor(file,id):
    if str(file)[-6:-3] == "pdf":
        file = convert_from_path("temp/temp."+str(file)[-6:-3],fmt='jpeg')[0]
        file.save("temp/temp.jpeg")
        predictor_model.predict(np.array(file.convert('RGB')), status_path = str(id))
    else:
        predictor_model.predict(np.array(file.convert('RGB')), status_path = str(id))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/upload_annotate')
def upload_annotate():
    return render_template('upload_annotate.html')

@app.route('/annotate')
def annotate():
    return render_template('annotate.html')

# @app.route('/crop',methods = ['POST', 'GET'])
# def crop():
#     if request.method == 'POST':
#         id = create_id()
#         while True:
#             if id not in os.listdir('status'):
#                 break
#             id = create_id()

#         os.mkdir('status/'+id)
#         file = request.files['images']
#         coords = request.file['crop'] # left upper, right lower x,y
#         format = str(file)[-6:-3]
#         file.save(f"temp/temp_{id}."+format)

#         img = Image.open(file)
#         if img.mode != "RGB":
#             img = img.convert("RGB")
#         img.save(f"temp/temp_{id}.jpeg","JPEG")

#         img = Image.open(f"temp/temp_{id}.jpeg")
#         img = img.crop(tuple(coords))
#         os.remove(f"temp/temp_{id}."+format)
#         file_object = io.BytesIO()
#         img.save(file_object, 'JPEG')
#         file.close()
#         os.remove(f"temp/temp_{id}.jpeg")
#         file_object.seek(0)
#         return send_file(file_object, mimetype='image/JPEG')

@app.route('/predict',methods = ['POST', 'GET'])
def predict():
    if request.method == 'POST':
        prediction = None
        id = create_id()
        while True:
            if id not in os.listdir('status'):
                break
            id = create_id()

        os.mkdir('status/'+id)
        file = request.files['images']
        format = str(file)[-6:-3]
        file.save(f"temp/temp_{id}."+format)

        img = None 
        if format == "pdf":
            file = convert_from_path(f"temp/temp_{id}."+format,fmt='jpeg')[0]
            file.save(f"temp/temp_{id}.jpeg")

        else:
            img = Image.open(file)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(f"temp/temp_{id}.jpeg","JPEG")

        img = Image.open(f"temp/temp_{id}.jpeg")
        os.remove(f"temp/temp_{id}."+format)
        response = Response(id)
        @response.call_on_close
        def on_close():
            predictor_model.predict(np.asarray(img), status_path = str(id))

        return response

@app.route('/get_model_img',methods = ['POST', 'GET'])
def get_model_img():
    if request.method == 'POST':
        id = request.form['id']
        img = Image.open(f"temp/temp_{id}.jpeg")
        file_object = io.BytesIO()
        img.save(file_object, 'JPEG')
        os.remove(f"temp/temp_{id}.jpeg")
        shutil.rmtree(f"status/{id}")
        if f"temp_{id}.peg" in os.listdir("temp"):
            os.remove(f"temp/temp_{id}.peg")
        file_object.seek(0)
        return send_file(file_object, mimetype='image/JPEG')

@app.route('/convert_annotate',methods = ['POST', 'GET'])
def convert_annotate():
    if request.method == 'POST':
        id = create_id()
        while True:
            if id not in os.listdir('status'):
                break
            id = create_id()

        os.mkdir('status/'+id)
        file = request.files['images']
        format = str(file)[-6:-3]
        file.save(f"temp/temp_{id}."+format)

        img = None 
        if format == "pdf":
            file = convert_from_path(f"temp/temp_{id}."+format,fmt='jpeg')[0]
            file.save(f"temp/temp_{id}.jpeg")

        else:
            img = Image.open(file)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(f"temp/temp_{id}.jpeg","JPEG")

        img = Image.open(f"temp/temp_{id}.jpeg")
        os.remove(f"temp/temp_{id}."+format)
        file_object = io.BytesIO()
        img.save(file_object, 'JPEG')
        file.close()
        os.remove(f"temp/temp_{id}.jpeg")
        file_object.seek(0)
        return send_file(file_object, mimetype='image/JPEG')

@app.route('/status',methods = ['POST', 'GET'])
def status():
    if request.method == 'POST':
        id = request.form['id']
        status_len = str(len(os.listdir('status/'+id)))
        response = Response(status_len)
        return response

@app.route('/model_result',methods = ['POST', 'GET'])
def model_result():
    x = []
    id = request.form['id']
    return json.dumps(pickle.load(open('status/'+id+'/result','rb')))

if __name__ == '__main__':
   app.run(host="0.0.0.0",debug=False, port=5000, threaded=True)

