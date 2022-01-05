<div id="top"></div>

<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://user-images.githubusercontent.com/57902078/148179403-5510f033-b751-4ff5-92fb-1b7fe1006728.jpeg" alt="Logo" width="30%" height="30%">
  </a>

  <p align="center"  style="text-align:center">
    <br><br>Easy way to convert scanned documents into an editable text document,<br> classifying key-value pairs and annotating them
    <br><br>
    <a href="https://github.com/FrozenWolf-Cyber/OCR/tree/master/training"><strong>Train results »</strong></a> &nbsp;&nbsp;
    <a href="http://frozenwolf-ocr.westeurope.cloudapp.azure.com:5000/home">View Demo »</a>
  </p>
</div>


Table of Contents
=================
   * [About](#About)
   * [Installation](#Installation)
   * [Usage](#Usage)

## About
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Combining CRAFT, Faster R-CNN, Tesseract and Siamese neural network model to make an Optical character recognition software which is hosted in azure cloud [here](http://frozenwolf-ocr.westeurope.cloudapp.azure.com:5000/home). The neural network models are trained with the help of PyTorch on [FUND](https://guillaumejaume.github.io/FUNSD/) dataset and the server is hosted in a virtual machine in azure cloud using Flask. The frontend website consists of options for users to upload a scanned document of files of formats - .png, .jpg, .jpeg, .pdf (for pdf only the first page is considered) which is in return is converted into editable text, bounding boxes for each word and sentences, classified labels for each sentence among 'other', 'question', 'answer' and 'header' and also the linked sentences. The website also provides a user-friendly interface for users to modify the model predictions using annotate features which can also be done to a document without feeding it to the model waiting for model predictions from scratch.<br> <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The annotation interface is made with the help of [annotorious.js](annotorious). After the model result or after annotating the document the information can be downloaded into simple .txt format. There are also options to run the model offline so that multiple images can be fed to the images at once and it is also an option to decide if the output should be of MTX format or FUND dataset format.<br><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I am running the models in Azure VM because of the requirement of Tesseract and Popper. I am using Standard B2s (2 vcpus, 4 GiB memory) in Azure VM with Linux (ubuntu 18.04) as the operating system. I have added the videos and images of accessing the website which has been hosted through Azure VM but currently, I am unable to keep the VM open all the time due to interruption when the SSH connection is closed (I start the server in Azure VM using PuTTY to through SSH connection). But the same result can still be achieved by following the server installation and starting setup given [below](#Usage). I will be leaving the server open for as long as possible in a whole day so it might so the link might sometimes work.<br><br>
&nbsp;&nbsp;&nbsp;&nbsp; Most of the model training is done with the help of Pytorch. I have explained the training steps and the metrics to analyze the models in [training](https://github.com/FrozenWolf-Cyber/OCR/tree/master/training)


## Built Using
Python :
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
Javascript :
```
bootstrap
annotorious
```

## Installation
### Dependencies :
```
tesseract-ocr
poppler-utils
```
### 1.Install server Requirements :

#### Minimal Installation through command :
Note: The libraries installed through this process are targeted for Ubuntu Python 3.6 version. Also, the Pytorch CPU version is installed in this case to minimize memory usage
```shell
pip install -r requirements.txt
```
### Additional Training Install Requirements (Optional) :
Note : This is required only if you want to run the .ipynb training notebooks in [training](https://github.com/FrozenWolf-Cyber/OCR/tree/master/training) folder
```
matplotlib
seaborn
nltk
torchinfo
albumentations
```
Finally after installing requirements,
clone the repo
```
git clone https://github.com/FrozenWolf-Cyber/OCR.git
```
## Usage

### 1.Starting the server :
Project structure :

```
server:
|   app.py
|   craft.py
|   craft_utils.py
|   imgproc.py
|   ocr_predictor.py
|   refinenet.py
|   word_Detection.py
|   
+---basenet
|   |   vgg16_bn.py
|   |   
|   \---__pycache__
|           vgg16_bn.cpython-39.pyc
|                      
+---img_save
|       requirements.txt
|       
+---saved_models
|       craft_mlt_25k.pth
|       craft_refiner_CTW1500.pth
|       embs_npa.npy
|       faster_rcnn_sgd.pth
|       siamese_multi_head.pth
|       vocab
|       
+---static
|   \---assets
|       +---bootstrap
|       |   +---css
|       |   |       bootstrap.min.css
|       |   |       
|       |   \---js
|       |           bootstrap.min.js
|       |           
|       +---css
|       |       animated-textbox-1.css
|       |       animated-textbox.css
|       |       annotorious.min.css
|       |       Codeblock.css
|       |       custom.css
|       |       custom_annotate.css
|       |       Drag--Drop-Upload-Form.css
|       |       Features-Blue.css
|       |       Footer-Basic.css
|       |       Navigation-Clean.css
|       |       PJansari---Horizontal-Stepper.css
|       |       steps-progressbar.css
|       |       
|       +---fonts
|       |       ionicons.eot
|       |       ionicons.min.css
|       |       ionicons.svg
|       |       ionicons.ttf
|       |       ionicons.woff
|       |       material-icons.min.css
|       |       MaterialIcons-Regular.eot
|       |       MaterialIcons-Regular.svg
|       |       MaterialIcons-Regular.ttf
|       |       MaterialIcons-Regular.woff
|       |       MaterialIcons-Regular.woff2
|       |       
|       +---img
|       |       bg-masthead.jpg
|       |       bg-showcase-2.jpg
|       |       bg-showcase-3.jpg
|       |       
|       \---js
|               annotate.js
|               annotorious.min.js
|               annotorious.umd.js.map
|               bs-init.js
|               navigator.js
|               recogito-polyfills.js
|               result.js
|               upload.js
|               
+---status
|       requirements.txt
|       
+---temp
|       requirements.txt
|       
+---templates
       annotate.html
       home.html
       result.html
       upload.html
       upload_annotate.html

```
To start the server run the app.py inside the server folder
```shell
python app.py
```

### 2.Predicting mutliple scanned documents offline :
To run this program minimal installation is enough
#### Project structure
```
batch_run
|   app.py
|   craft.py
|   craft_utils.py
|   demo_batch_run.png
|   imgproc.py
|   ocr_predictor.py
|   predict.py
|   refinenet.py
|   tree.txt
|   word_Detection.py
|   
+---basenet
|   |   vgg16_bn.py
|   |   
|   \---__pycache__
|           vgg16_bn.cpython-39.pyc
|           
+---img_save
|       
+---result
|       
+---saved_models
|       craft_mlt_25k.pth
|       craft_refiner_CTW1500.pth
|       embs_npa.npy
|       faster_rcnn_sgd.pth
|       siamese_multi_head.pth
|       vocab
|       
+---testing_data
   +---documents
   |       your_pdf1.pdf
   |       your_pdf2.pdf
   |       your_pdf3.pdf
   \---images
        your_image1.png
        your_image2.png

```
#### Custom run :
Inside [batch_run](https://github.com/FrozenWolf-Cyber/OCR/tree/master/batch_run) folder run,
```shell
python predict.py -path <target folder> -MTX <Y/N> -sr <Y/N> -pdf <Y/N>
```

```
usage: predict.py [-h] [-path PATH] [-MTX MTX] [-sr SR] [-pdf PDF]

optional arguments:
  -h, --help            show this help message and exit
  -path PATH, --path PATH
                        Use relative path
  -MTX MTX, --MTX MTX   Should be <Y> or <N>. If <Y> then the output will be in MTX Hacker Olympics format, if <N>
                        then the output will be of FUND dataset format
  -sr SR, --sr SR       Should be <Y> or <N>. If <Y> then the output will be saved in a seperate JSON file whereas the
                        scores for each label classification and linking will be in seperate file, if <N> then the
                        both will be in same file
  -pdf PDF, --pdf PDF   Should be <Y> or <N>. If <Y> then the target folder contains multiple .pdf documents, if <N>
                        then the folder contains multiple .png,.jpg,.jpeg documents
```
Example :<br>
```python predict.py -path testing_data/images -MTX Y -sr N -pdf N```<br>
```python predict.py -path testing_data/documents -MTX Y -sr N -pdf Y```<br>

![image](https://user-images.githubusercontent.com/57902078/148266764-3430e302-85f8-4770-81df-02c64b15817d.png)

<br>

![image](https://user-images.githubusercontent.com/57902078/148270237-984a629b-b4ee-49b5-a1e5-3dc59a306c69.png)

<br>
Each prediction and score are saved in the result folder as a .json file together or separate based on the custom configuration you have selected.

### 3. Website :
Note : In the website the format the model returns is that of the FUND dataset, for MTX evaluation purposes go to [batch_run](https://github.com/FrozenWolf-Cyber/OCR/tree/master/batch_run) where you can choose the output format
#### Hosting in azure VM
![image](https://user-images.githubusercontent.com/57902078/148203059-03c23a09-d56b-440d-83fc-284f6239f1e1.png)
![OCR-VM](https://user-images.githubusercontent.com/57902078/148226726-ff8b5730-a80a-4871-b359-d57256facc45.png)

#### Home
There are options to annotate after model predictions or else to start annotating from scratch
<br><br>
![Home - OCR](https://user-images.githubusercontent.com/57902078/148220376-33fa7f34-434a-4aea-ade0-0a81e1cd2572.png)
<br><br>
#### Upload
You can either drag and drop the images or just select them. The images should be of form .png or .jpeg or .jpg or .pdf
Note: For .pdf files, the first page alone will be considered
<br><br>
![Upload - OCR](https://user-images.githubusercontent.com/57902078/148220397-425ef4bb-cd02-4249-a9c5-101c875cc628.png)
<br><br>
#### Progress
After getting the model output using either can continue to modify their bounding box, label, translation, and linking predictions in annotations or finish it by downloading it in the form of a .txt
<br><br>
![Result - OCR](https://user-images.githubusercontent.com/57902078/148220428-878c5015-0012-4fb7-9039-0c9865f5c1ee.png)
<br><br>
#### Annotate
Using annotorius.js the annotation can be now done very much easier. To modify the words you have to click any one of the corresponding sentences. After completing annotating the images used can either download the final result in the .txt form. Instead of waiting for model predictions to come, users can choose to annotate from scratch too.
<br><br>
![Annotate - OCR](https://user-images.githubusercontent.com/57902078/148221947-7df05fd5-0312-4e39-aab6-63e9d2579d93.png)
<br><br>
<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

