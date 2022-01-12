## Predicting mutliple scanned documents offline :
To run this program minimal installation is enough.
### Project structure
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
### Custom run :
##### Prediction :
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

```python predict.py -path testing_data/images -MTX Y -sr N -pdf N```

<br>

![image](https://user-images.githubusercontent.com/57902078/148266764-3430e302-85f8-4770-81df-02c64b15817d.png)

<br>

```python predict.py -path testing_data/documents -MTX Y -sr N -pdf Y```

<br>

![image](https://user-images.githubusercontent.com/57902078/148270237-984a629b-b4ee-49b5-a1e5-3dc59a306c69.png)

<br>

##### Evalution :
Inside [batch_run](https://github.com/FrozenWolf-Cyber/OCR/tree/master/batch_run) folder run,

```shell
python evaluate.py -img <Image folder> -anno <Annotations folder> -sr <Y/N>
```

<br>

```
optional arguments:
  -h, --help            show this help message and exit
  -img IMG_PATH, --img_path IMG_PATH
                        Use relative path
  -anno ANNO_PATH, --anno_path ANNO_PATH
                        Use relative path
  -sr SR, --sr SR       Should be <Y> or <N>. If <Y> then the output will be saved in a seperate JSON file whereas the
                        scores for each label classification and linking will be in seperate file, if <N> then the
                        both will be in same file
```

<br>

Example :

<br>

```
python evaluate.py -img testing_data/images -anno testing_data/annotations -sr Y
```

<br>

![image](https://user-images.githubusercontent.com/57902078/149166663-b399f2d1-8033-492c-898f-358543d20547.png)

<br>

Each prediction and score are saved in the result folder as a .json file together or separate based on the custom configuration you have selected. In case of evaluation additional metrics.json file is saved, it contains label and linking accuracy, f_score, precision and recall value of each image seperately.

