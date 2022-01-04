import time

import torch
import torch.backends.cudnn as cudnn
from refinenet import RefineNet
from torch.autograd import Variable

import cv2
import numpy as np
import craft_utils
import imgproc

from craft import CRAFT

from collections import OrderedDict
def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict

def str2bool(v):
    return v.lower() in ("yes", "y", "true", "t", "1")


class word_detector():
    def __init__(self,cuda,trained_model_path,refiner_model_path):
        self.show_time = False
        self.low_text = 0.4
        self.text_threshold = 0.7
        self.link_threshold = 0.4
        self.canvas_size = 1280
        self.mag_ratio = 1.5 
        self.net = CRAFT()     # initialize
        self.cuda = cuda
        self.trained_model = trained_model_path
        self.refiner_model = refiner_model_path

        print('Loading weights from checkpoint (' + self.trained_model + ')')
        if self.cuda:
            self.net.load_state_dict(copyStateDict(torch.load(self.trained_model)))
        else:
            self.net.load_state_dict(copyStateDict(torch.load(self.trained_model, map_location='cpu')))

        if self.cuda:
            self.net = self.net.cuda()
            self.net = torch.nn.DataParallel(self.net)
            cudnn.benchmark = False

        self.net.eval()

        # LinkRefiner
        self.refine_net = RefineNet()
        print('Loading weights of refiner from checkpoint (' + self.refiner_model + ')')
        if self.cuda:
            self.refine_net.load_state_dict(copyStateDict(torch.load(self.refiner_model)))
            self.refine_net = self.refine_net.cuda()
            self.refine_net = torch.nn.DataParallel(self.refine_net)
        else:
            self.refine_net.load_state_dict(copyStateDict(torch.load(self.refiner_model, map_location='cpu')))

        self.refine_net.eval()
        self.poly = False

    def test_net(self,net, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net=None):
        t0 = time.time()

        # resize
        img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(image, self.canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=self.mag_ratio)
        ratio_h = ratio_w = 1 / target_ratio

        # preprocessing
        x = imgproc.normalizeMeanVariance(img_resized)
        x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
        x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]
        if cuda:
            x = x.cuda()

        # forward pass
        with torch.no_grad():
            y, feature = net(x)

        # make score and link map
        score_text = y[0,:,:,0].cpu().data.numpy()
        score_link = y[0,:,:,1].cpu().data.numpy()

        # refine link
        if refine_net is not None:
            with torch.no_grad():
                y_refiner = refine_net(y, feature)
            score_link = y_refiner[0,:,:,0].cpu().data.numpy()

        t0 = time.time() - t0
        t1 = time.time()

        # Post-processing
        boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

        # coordinate adjustment
        boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
        polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
        for k in range(len(polys)):
            if polys[k] is None: polys[k] = boxes[k]

        t1 = time.time() - t1

        # render results (optional)
        render_img = score_text.copy()
        render_img = np.hstack((render_img, score_link))
        ret_score_text = imgproc.cvt2HeatmapImg(render_img)

        if self.show_time : print("\ninfer/postproc time : {:.3f}/{:.3f}".format(t0, t1))

        return boxes, polys, ret_score_text

    def detect(self,image_path):
        # load data
        image = imgproc.loadImage(image_path)
        bboxes, polys, score_text = self.test_net(self.net, image, self.text_threshold, self.link_threshold, self.low_text, self.cuda, self.poly, self.refine_net)
        return bboxes, score_text

