import cv2
from ocr_predictor import predictor
from flask import Flask, request
from PIL import Image
import numpy as np

predictor_model = predictor('cpu')

app = Flask(__name__)

@app.route('/predict',methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        prediction = predictor_model.predict(np.array(Image.open(request.files['image']).convert('RGB')))
        print(prediction,flush=True)

        return prediction

if __name__ == '__main__':
   app.run(debug=True,host='0.0.0.0', port=5000)
