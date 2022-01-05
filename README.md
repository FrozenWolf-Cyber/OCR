<div id="top"></div>

<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://user-images.githubusercontent.com/57902078/148179403-5510f033-b751-4ff5-92fb-1b7fe1006728.jpeg" alt="Logo" width="100" height="100">
  </a>

  <p align="center"  style="text-align:center">
    <br><br>Easy way to convert scanned documents into editable text document,<br> classifying key value pairs and annotating them
    <br><br>
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Train results »</strong></a> &nbsp;&nbsp;
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo »</a>
  </p>
</div>


Table of Contents
=================
   * [About](#About)
   * [Installation](#Installation)
   * [Usage](#Usage)
   * [For developers](#for-developers)


## About
&nbsp;&nbsp;&nbsp;&nbsp;Combining CRAFT, Faster R-CNN, Tesseract and Siamese neural network model to make an Optical character recognition software which is hosted in azure cloud [here](http://frozenwolf-ocr.westeurope.cloudapp.azure.com:5000/home). The neural network models are trained with the help of pytorch on [FUND](https://guillaumejaume.github.io/FUNSD/) dataset and the server is hosted in a virtual machine in azure cloud using Flask. The frontend website consists of options for users to upload scanned document of files of formats - .png, .jpg, .jpeg, .pdf (for pdf only the first page is considered) which is in return is converted into editable text, bounding boxes for each words and sentences, classified labels for each sentences among 'other', 'question', 'answer' and 'header' and also the linked sentences. The website also provides an user friendly interface for users to modify the model predictions using annotate feature which can also be done to an document without feeding it to the model waiting for model predictions from scratch. The annotation interface is made with the help of [annotorious.js](annotorious). After the model result or after annotating the document the information can be downloaded into simple .txt format.

## Built Using :
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

## Installation :
### Dependencies :
```
tesseract-ocr
poppler-utils
```
### 1.Install server Requirements :

#### Minimal Installation through command :
Note : The libraries installed through this process is targeted for Ubuntu Python 3.9 version. Also Pytorch CPU version is installed in this case to minimize memory usuage
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
## Usage :

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
   \---images
        your_image1.png
        your_image2.png

```
#### Custom run :
Inside [batch_run](https://github.com/FrozenWolf-Cyber/OCR/tree/master/batch_run) folder run,
```shell
python predict.py -path <target folder> -MTX <Y/N> -sr <Y/N>
```

```
  -h, --help            show this help message and exit
  -path PATH, --path PATH
                        Use relative path
  -MTX MTX, --MTX MTX   Should be <Y> or <N>. If <Y> then the output will be in MTX Hacker Olympics format, if <N>
                        then the output will be of FUND dataset format
  -sr SR, --sr SR       Should be <Y> or <N>. If <Y> then the output will be saved in a seperate JSON file whereas the
                        scores for each label classification and linking will be in seperate file, if <N> then the
                        both will be in same file
```
Example : ```python predict.py -path testing_data/images -MTX Y -sr N```

![demo_batch_run](https://user-images.githubusercontent.com/57902078/148174654-5dc62519-1db4-4b97-85e2-15144bae1897.png)

Each predictions and scores are saved in result folder as a.json file together or seperate based on the custom configuration you have selected.

### 3. Website :
Note : In the website the format the model returns is that of the FUND dataset, for MTX evaluation purposes go to [batch_run](https://github.com/FrozenWolf-Cyber/OCR/tree/master/batch_run) where you can chooses the output format
#### Hosting in azure VM
![image](https://user-images.githubusercontent.com/57902078/148203059-03c23a09-d56b-440d-83fc-284f6239f1e1.png)

#### Home
There are options to annotate after model predictions or else to start annotating from scratch
![Home - OCR](https://user-images.githubusercontent.com/57902078/148220376-33fa7f34-434a-4aea-ade0-0a81e1cd2572.png)

#### Upload
You can either drag and drop the images or just select them. The images should be of form .png or .jpeg or .jpg or .pdf
Note: For .pdf files the first page alone will be considered
![Upload - OCR](https://user-images.githubusercontent.com/57902078/148220397-425ef4bb-cd02-4249-a9c5-101c875cc628.png)

#### Progress
After getting the model output user either can continue to modify their bouding box, label, translation and linking predicitions in annotations or finish it by downloading it in the form of .txt
![Result - OCR](https://user-images.githubusercontent.com/57902078/148220428-878c5015-0012-4fb7-9039-0c9865f5c1ee.png)

#### Annotate
Using annotorius.js the annotation can be now done very much easier. To modify the words you have to click any one of the corresponding sentences. After completing annotating the images user can either download the final result in the .txt form. Instead of waiting for model predictions to come user can choose to annotate from scratch too.
![Annotate - OCR](https://user-images.githubusercontent.com/57902078/148221947-7df05fd5-0312-4e39-aab6-63e9d2579d93.png)

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
