# OCR
&nbsp;&nbsp;&nbsp;&nbsp;Combining CRAFT, Faster R-CNN, Tesseract and Siamese neural network model to make an Optical character recognition software which is hosted in azure cloud [here](http://frozenwolf-ocr.westeurope.cloudapp.azure.com:5000/home). The neural network models are trained with the help of pytorch on [FUND](https://guillaumejaume.github.io/FUNSD/) dataset and the server is hosted in a virtual machine in azure cloud using Flask. The frontend website consists of options for users to upload scanned document of files of formats - .png, .jpg, .jpeg, .pdf (for pdf only the first page is considered) which is in return is converted into editable text, bounding boxes for each words and sentences, classified labels for each sentences among 'other', 'question', 'answer' and 'header' and also the linked sentences. The website also provides an user friendly interface for users to modify the model predictions using annotate feature which can also be done to an document without feeding it to the model waiting for model predictions from scratch. The annotation interface is made with the help of [annotorious.js](annotorious). After the model result or after annotating the document the information can be downloaded into simple .txt format.

# Alogrthim for Complete Model :
&nbsp;&nbsp;&nbsp;&nbsp;First, we are feeding the image of the scanned document into the CRAFT model which returns bounding boxes for sentences. Then we feed the image again into the Faster R-CNN model which we trained before which in return will give approximate regional bounding boxes of each label category. Now we will use the bounding boxes of each sentence and compare it with the regional bounding boxes that we got from Faster R-CNN using IOU and categorize each sentence that has maximum IOU score.<br><br>
&nbsp;&nbsp;&nbsp;&nbsp;Now we will pass each sentence image into the Tesseract model which will give us bounding boxes of each word and translation for each word and sentence. Then we will iterate every two sentences and combine the predicted translation of each sentence with a bounding box and label classification feed into Siamese Neural Network which will give us a similarity score. We will use this similarity score to check against a threshold value and if it crosses the threshold then we will add it to the list of links for each sentence.<br>


![OCR_flowchart](https://user-images.githubusercontent.com/57902078/148105380-bbc69ff0-0a55-48d1-a711-13fb2f0f76ef.png)

## Quick start :
### 1. Server Install Requirements :
#### Libraries Used :
```
Flask
pickle-mixin
numpy
Pillow
regex
pdf2image
opencv-python
scikit-image
torch
torchvision
pytesseract
```
#### Additional Tools :
```
tesseract-ocr
poppler-utils
```
#### Minimal Installation through command :
Note : The libraries installed through this process is targeted for Ubuntu Python 3.9 version. Also Pytorch CPU version is installed in this case to minimize memory usuage
```shell
pip install -r requirements.txt
```
### 2.Additional Training Install Requirements :
Note : This is required only if you want to run the .ipynb training notebooks in [training](https://github.com/FrozenWolf-Cyber/OCR/tree/master/training) folder
```
matplotlib
seaborn
nltk
torchinfo
albumentations
```
## Usage :

### 1.Starting the server :

### 2.How to use the website ? :

### 3.Predicting mutliple files offline :



