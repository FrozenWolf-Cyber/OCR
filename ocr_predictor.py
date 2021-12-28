import cv2
import os
import re
import pytesseract
import torch
import torch.nn as nn
import torch.nn.functional as F
import pickle
import torchvision
import torchvision.transforms as T
from pytesseract import Output
from word_Detection import *
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

class predictor():
    def __init__(self,device):
        class siamese_multi_head(nn.Module):
            def __init__(self,device,hidden_size,n_layer,embedding_size):
                super().__init__()
                if 'embs_npa.npy' in os.listdir('saved_models/'):
                    embs_npa = np.load('saved_models/embs_npa.npy')
                
                self.device = device
                self.n_layer = n_layer
                self.hidden_size = hidden_size
        
                # Sentence embeddings
                self.embedding_layer = nn.Embedding.from_pretrained(torch.from_numpy(embs_npa).float(),freeze=False)
                self.lstm_layer = nn.LSTM(embedding_size,hidden_size,n_layer,batch_first = True)
        
                #label layer
                self.label_l = nn.Linear(1,1)
                # combined
                self.l1 = nn.Linear(hidden_size+1+4,32)
                self.l2 = nn.Linear(32,1)
        
            def forward(self,x_words, x_labels, x_box):
                x_words_1 = self.embedding_layer(x_words[0])
                _ , (x_words_1,__) = self.lstm_layer(x_words_1)
                x_words_1 = F.relu(x_words_1[-1])
        
                x_words_2 = self.embedding_layer(x_words[1])
                _ , (x_words_2,__) = self.lstm_layer(x_words_2)
                x_words_2 = F.relu(x_words_2[-1])
        
                x_labels_1 = self.label_l(x_labels[0])
                x_labels_2 = self.label_l(x_labels[1])
        
                x_words = torch.abs(x_words_1-x_words_2)
                x_labels = torch.abs(x_labels_1-x_labels_2)
                x_box = torch.abs(x_box[0]-x_box[1])
        
                x = torch.cat([x_labels,x_box,x_words],dim=1)
                x = F.relu(self.l1(x))
                x = torch.sigmoid(self.l2(x))
        
                return x
        
        self.classes = ['other', 'question', 'answer', 'header']
        self.device = device

        self.similarity_model = siamese_multi_head(device,hidden_size = 64,n_layer= 2,embedding_size = 50).to(self.device)
        self.similarity_model.load_state_dict(torch.load("saved_models/siamese_multi_head.pth",map_location=self.device))

        self.model_sentence_detector = word_detector(False,"saved_models/craft_mlt_25k.pth","saved_models/craft_refiner_CTW1500.pth")

        self.model_label_classifier = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False)
        num_classes = len(self.classes)+1
        in_features = self.model_label_classifier.roi_heads.box_predictor.cls_score.in_features
        self.model_label_classifier.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
        self.model_label_classifier.load_state_dict(torch.load(f'saved_models/faster_rcnn_sgd.pth'))
        self.model_label_classifier.eval()

        self.vocab = pickle.load(open("saved_models/vocab",'rb'))
        self.transforms = T.Compose([T.ToTensor()])
        self.save_img_path = "img_save/"

    def IOU(self,box1, box2, screen_size=(480, 640)):  # calculating IOU
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

    def padding(self,img,size):
        old_image_height, old_image_width, channels = img.shape
        new_image_width = size[0]
        new_image_height = size[1]
        color = (255,255,255)
        result = np.full((new_image_height,new_image_width, 3), color, dtype=np.uint8)

        # compute center offset
        x_center = (new_image_width - old_image_width) // 2
        y_center = (new_image_height - old_image_height) // 2

        # copy img image into center of result image
        result[y_center:y_center+old_image_height, 
               x_center:x_center+old_image_width] = img

        return result

    def preprocess_string(self,s):
        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", '', s)
        # Replace all runs of whitespaces with no space
        s = re.sub(r"\s+", '', s)
        # replace digits with no space
        s = re.sub(r"\d", '', s)

        return s

    def tockenize(self,x_train,vocab=None):
        final_list_train = []
        for sent in x_train:
            for word in sent.lower().split():
                if self.preprocess_string(word) in vocab.keys():
                    final_list_train.append([vocab[self.preprocess_string(word)]])
                try:
                    float(word)
                    final_list_train.append([1]) # digits are 1
                except ValueError:
                    pass

        return np.array(final_list_train).reshape(1,-1)

    def sentence_padding(self,sentences, seq_len):
        padded_sentences = []

        for sentence in sentences:
            sentence = np.array(sentence)
            size = sentence.shape[0]
            sentence = sentence.reshape((size,))
            if size >seq_len:
                padded_sentences.append(sentence[:seq_len])
            else:
                padding = np.zeros((seq_len-sentence.shape[0]))
                padded_sentences.append(np.append(padding,sentence))

        return np.array(padded_sentences).reshape((len(sentences),seq_len))

    def predict(self,img):
        file_name = str(len(os.listdir(self.save_img_path)))+'.png'
        path = self.save_img_path+file_name
        cv2.imwrite(path, img)
        boxxes = self.model_sentence_detector.detect(path).astype(np.int32)
        
        prediction = self.model_label_classifier(self.transforms(img).unsqueeze(0))[0]

        shape = img.shape[:2]
        iou_label = []
        for  bounding_boxes in boxxes:
            iou_label.append(1)  # 1 for others
            temp_iou = 0
            x_min, y_min = tuple(bounding_boxes[0])
            x_max, y_max = tuple(bounding_boxes[2])

            for labels, label_boxes, scores in zip(prediction['labels'], prediction['boxes'], prediction['scores']):
                scores = scores.detach().numpy()
                if scores<0.5:
                    continue
                labels = labels.detach().numpy()
                label_boxes = label_boxes.detach().numpy().astype(np.int32)   
                iou = self.IOU([label_boxes[0], label_boxes[1], label_boxes[2], label_boxes[3]],[x_min, y_min, x_max, y_max],shape)    # xmin y min xmax y max
                if iou>temp_iou:
                    temp_iou = iou
                    iou_label[-1] = int(labels)

        output_img =  np.copy(img)
        each_sentence = []
        each_word = []
        each_word_coord = []
        
        for  bounding_boxes, each_label in zip(boxxes, iou_label):
            x_min, y_min = tuple(bounding_boxes[0])
            x_max, y_max = tuple(bounding_boxes[2])

            strip_img = img[y_min:y_max,x_min:x_max]
            h, w, c = strip_img.shape
            each_sentence.append(pytesseract.image_to_string(strip_img))
            d = pytesseract.image_to_data(strip_img, output_type=Output.DICT)
            n_boxes = len(d['text'])

            temp_each_word_coord = []
            temp_each_word = []
            for i in range(n_boxes):
                if float(d['conf'][i]) > 0:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    if w == 0 or h == 0:
                        continue
                    temp_each_word_coord.append([(x_min+x, y_min+y), (x_min+x + w, y_min+y + h)])
                    temp_each_word.append(pytesseract.image_to_string(self.padding(img[y_min+y:y_min+y+h, x_min+x:x_min+x+w],img.shape[:2])))

            each_word_coord.append(temp_each_word_coord)
            each_word.append(temp_each_word)       

        for idx, (whole, sep) in enumerate(zip(each_sentence,each_word)):
            for w_idx,word in enumerate(sep):
                each_word[idx][w_idx] = word.strip()

            each_sentence[idx] = each_sentence[idx].strip()
            if whole.strip() == "":
                each_sentence[idx] = " ".join(each_word[idx])

        linked_dict = {}

        for ref1 , (sentence1, sentence_coord1,label1) in enumerate(zip(each_sentence,boxxes,iou_label)):
            if ref1 not in linked_dict.keys():
                linked_dict[ref1] = []

            sentence1 = torch.LongTensor(self.sentence_padding(self.tockenize([sentence1],vocab=self.vocab),seq_len=50))

            sentence_coord1 = torch.FloatTensor([[sentence_coord1[0][0],sentence_coord1[0][1],sentence_coord1[2][0],sentence_coord1[2][1]]])
            label1 = torch.FloatTensor([label1]).unsqueeze(0)

            for ref2 , (sentence2, sentence_coord2,label2) in enumerate(zip(each_sentence,boxxes,iou_label)):
                if ref2 == ref1:
                    continue
                if ref2 not in linked_dict.keys():
                    linked_dict[ref2] = []

                sentence2 = torch.LongTensor(self.sentence_padding(self.tockenize([sentence2],vocab=self.vocab),seq_len=50))
                sentence_coord2 = torch.FloatTensor([[sentence_coord2[0][0],sentence_coord2[0][1],sentence_coord2[2][0],sentence_coord2[2][1]]])
                label2 = torch.FloatTensor([label2]).unsqueeze(0)
                similarity = float(self.similarity_model([sentence1,sentence2],[label1,label2],[sentence_coord1,sentence_coord2]).detach().numpy()[0])
                if similarity>=0.5:
                    if ref2 not in linked_dict[ref1]:
                        linked_dict[ref1].append(ref2)

                    if ref1 not in linked_dict[ref2]:
                        linked_dict[ref2].append(ref1)

        final_output = {'form':[]}
        for idx, (nth_label, nth_sentence, nth_words, nth_sentence_bounding_boxes, nth_word_bounding_boxes) in enumerate(zip(iou_label,each_sentence,each_word,boxxes,each_word_coord)):
            temp = {}
            temp['id'] = int(idx)
            temp['label'] = self.classes[nth_label-1]
            temp['box'] = np.array([nth_sentence_bounding_boxes[0][0],nth_sentence_bounding_boxes[0][1],nth_sentence_bounding_boxes[2][0],nth_sentence_bounding_boxes[2][1]],dtype=int).tolist()
            temp['text'] = nth_sentence
            temp['words'] = []
            temp['linking'] = []

            for i,i_coord in zip(nth_words,nth_word_bounding_boxes):
                temp_ = {}
                i_coord[0] = list(i_coord[0])
                i_coord[0].extend(list(i_coord[1]))
                temp_['box'] = np.array(i_coord[0],dtype=int).tolist()
                temp_['text'] = i
                temp['words'].append(temp_)

            for i in linked_dict[idx]:
                temp['linking'].append([int(idx),int(i)])

            final_output['form'].append(temp)

        return final_output
