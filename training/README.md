<div id="top"></div>

<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://user-images.githubusercontent.com/57902078/148179403-5510f033-b751-4ff5-92fb-1b7fe1006728.jpeg" alt="Logo" width="100" height="100">
  </a>

  <p align="center"  style="text-align:center">
    <br><br>Easy way to convert scanned documents into an editable text document,<br> classifying key-value pairs and annotating them
    <br><br>
    <a href="http://frozenwolf-ocr.westeurope.cloudapp.azure.com:5000/home">View Demo »</a>
  </p>
</div>


Table of Contents
=================
   * [Models Used](#Models-Used)
   * [Alogrthim for Complete Model](#Alogrthim-for-Complete-Model)
   * [Result](#Result)

## Models Used :
   * [CRAFT](https://github.com/FrozenWolf-Cyber/OCR/blob/master/training/craft_tesseract_demo.ipynb)
   * [Faster R-CNN](https://github.com/FrozenWolf-Cyber/OCR/blob/master/training/Faster_R-CNN.ipynb)
   * [Tesseract](https://github.com/FrozenWolf-Cyber/OCR/blob/master/training/craft_tesseract_demo.ipynb)
   * [LSTM + Siamese Neural Network](https://github.com/FrozenWolf-Cyber/OCR/blob/master/training/Siamese-NeuralNetwork.ipynb)

## Alogrthim for Complete Model :
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; First, we are feeding the image of the scanned document into the CRAFT model which returns bounding boxes for sentences. Then we feed the image again into the Faster R-CNN model which we trained before which in return will give approximate regional bounding boxes of each label category. Now we will use the bounding boxes of each sentence and compare it with the regional bounding boxes that we got from Faster R-CNN using IOU and categorize each sentence that has maximum IOU score.<br><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Now we will pass each sentence image into the Tesseract model which will give us bounding boxes of each word and translation for each word and sentence. Then we will iterate every two sentences and combine the predicted translation of each sentence with a bounding box and label classification feed into Siamese Neural Network which will give us a similarity score. We will use this similarity score to check against a threshold value and if it crosses the threshold then we will add it to the list of links for each sentence.<br>
&nbsp;&nbsp;&nbsp;&nbsp; I have explained all the training steps and what model I have choosen in details in their respective notebooks (.ipynb).<br>

## Result :
### 1.CRAFT :
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Character-Region Awareness For Text detection is to localize the individual character regions and link the detected characters to a text instance. It is also mutli-lingual which makes it easier to convert to expand the project targets to multiple languages and works very well along with Tesseract. I am using pre-trained CRAFT model and loading it using Pytorch. I am loading the scripts and pre-trained weights from ![here](https://github.com/clovaai/CRAFT-pytorch)
#### Prediction :
Individual sample : <br><br>
![CRAFT-predictions](https://user-images.githubusercontent.com/57902078/148230888-fd4ec20b-71ef-4300-952b-960f7bffe7e0.png)
<br><br>
Comparing it against ground truth :<br><br>
![craft_predictions_comparison](https://user-images.githubusercontent.com/57902078/148231055-7a98364b-35cd-4af8-9470-445d6fb636d1.png)<br>
(Prediction on the right, ground truth on the left)
<br><br>

### 2.Faster R-CNN :
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Faster R-CNN is a deep convolutional network used for object detection, that appears to the user as a single, end-to-end, unified network. The network can accurately and quickly predict the locations of different objects. I am using regional label bounding box outputs Faster R-CNN along with CRAFT bouding box to classify the labels of the sentences by calculating the maximum Intersection Over Union (IOU) value. It is normally trained to classify 4 labels accoding FUNSD dataset but the output has been restricted to 3 classes (merging header and questions into key) while running in server or for evaluation

#### Loss vs Epoch :
The model is trained for over 50 epochs.<br><br>
![faster_rcnn_loss](https://user-images.githubusercontent.com/57902078/148232074-0a8f69e4-cbd0-4df7-89f7-46d9f6e5dcb9.png)

#### Predictions :
Individual sample : <br><br>
![Faster_R-CNN_predictions](https://user-images.githubusercontent.com/57902078/148232388-23e55ec2-ca7f-4fb1-96bc-f6a029da9a6b.png)

<br><br>
Comparing it against ground truth :<br><br>
![faster_rcnn_predictions_comparison](https://user-images.githubusercontent.com/57902078/148232418-327cc729-5852-4fb2-9655-08bc37e81fc1.png)
<br>
(Prediction on the Left, ground truth on the right)
<br><br>

### 3.Tesseract :
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tesseract is an OCR engine with support for unicode and the ability to recognize more than 100 languages out of the box. It can be trained to recognize other languages. I am using it to get bounding boxes for each word in a sentence and also to get translation seperately from each sentence and it's respective words in it. Tesseract module must be first installed to use it while Pytesseract library is used to access it using Python.

#### Predictions :
![Tesseract_Word_Bounding_Box](https://user-images.githubusercontent.com/57902078/148233309-9cd488dd-29ea-4ddd-8e62-dc10e3b5cabf.png)
<br><br>

### 4.LSTM + Siamese Neural Netowrk :
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Long Short Term Memory networks – usually just called “LSTMs” – are a special kind of RNN, capable of learning long-term dependencies.LSTMs are explicitly designed to avoid the long-term dependency problem. Siamese Neural Network is a class of neural network architectures that contain two or more identical subnetworks. ‘identical’ here means, they have the same configuration with the same parameters and weights.It is used to find the similarity of the inputs by comparing its feature vectors.<br><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; I am taking a fixed size of 80 words (way over the average words in a sentence which is <30) and feeding it to pre-trained embedding layer which is loaded with GloVe word embedding weights which can be downloaded [here](https://nlp.stanford.edu/projects/glove/). The word embeddings (output dimention is (30,50)) that we get from embedding layer is passed onto a LSTM layer which will give the feature representation of each sentence (output shape 30,64) of each sentences. We are then combining these feature representation with the labels classified, bouding boxes from the Faster R-CNN and CRAFT model (Output shape : 64+4+1). Now we will find absolute difference between every two sentences and pass them to Linear layers finally giving us the similarity score. <br>

#### Model Summary :
```
==========================================================================================
Layer (type:depth-idx)                   Output Shape              Param #
==========================================================================================
siamese_multi_head                       --                        --
├─Embedding: 1-1                         [1, 30, 50]               20,000,100
├─LSTM: 1-2                              [1, 30, 64]               62,976
├─Embedding: 1-3                         [1, 30, 50]               (recursive)
├─LSTM: 1-4                              [1, 30, 64]               (recursive)
├─Linear: 1-5                            [1, 1]                    2
├─Linear: 1-6                            [1, 1]                    (recursive)
├─Linear: 1-7                            [1, 32]                   2,240
├─Linear: 1-8                            [1, 1]                    33
==========================================================================================
Total params: 20,065,351
Trainable params: 20,065,351
Non-trainable params: 0
Total mult-adds (M): 43.78
==========================================================================================
Input size (MB): 0.00
Forward/backward pass size (MB): 0.03
Params size (MB): 80.26
Estimated Total Size (MB): 80.29
==========================================================================================
```
<br><br>

#### Model Metrics :

##### 1.Loss vs Epoch :
![siamese_loss](https://user-images.githubusercontent.com/57902078/148236367-b42d6e63-8e3b-4560-88df-cc5445dcc4f8.png)
<br>
##### 2.F-Score vs Epoch :
![siamese_f_score](https://user-images.githubusercontent.com/57902078/148236510-5b7e94d2-6d1e-4880-88ea-c87419ec8fbd.png)
<br>
##### 3.Recall vs Epoch :
![siamese_recall](https://user-images.githubusercontent.com/57902078/148236540-c7cbb7fb-7bd6-495e-a801-4dff2dfc2f7b.png)

<br>
##### 4.Precision vs Epoch :
![siamese_precision](https://user-images.githubusercontent.com/57902078/148236563-98cdad00-aaa8-473b-9b9a-691b04467a95.png)
<br>
##### 5.Accuracy vs Epoch :
Best Validation Accuracy is ``` 92.1232 ``` <br><br>
![siamese_acc](https://user-images.githubusercontent.com/57902078/148236716-a554b9ab-4d00-47e4-9cdd-f11699ee3f2b.png)
<br><br>
![siamese_acc2](https://user-images.githubusercontent.com/57902078/148236790-588f56dd-2249-415c-bfea-929559de1f8c.png)

