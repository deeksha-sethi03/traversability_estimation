# -*- coding: utf-8 -*-
"""plots.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cAt0_7YpBKAcaTbVy3mxuzmQwauWyjaA
"""

import cv2 as cv
import numpy as np
import torch
import torchvision
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torch.optim as optim
import matplotlib.pyplot as plt

import os
import re
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset, SubsetRandomSampler
import math
from matplotlib.colors import ListedColormap
from tqdm import tqdm
from sklearn.model_selection import KFold


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

file_path = './Results/3D FCN/Epoch Wise/train_mIOU.npy'

# Load data from the .npy file
attention = np.load(file_path)

file_path = './Results/FCN/Epoch Wise/train_mIOU.npy'

# Load data from the .npy file
baseline = np.load(file_path)

# Plot the first line
plt.plot(baseline, label='Baseline FCN', color='blue', linewidth = 0.5)

# Plot the second line
plt.plot(attention, label='Attention FCN', color='red', linewidth = 0.5)

# Add labels and legend
plt.xlabel('Epochs')
plt.ylabel('Mean IOU')
plt.title('Training Mean IOU (Baseline FCN versus Attention FCN)')
plt.legend()
plt.tight_layout()

# Show the plot
plt.show()

attention

baseline

test_loader = torch.load('/content/drive/MyDrive/DL Project/test_loader_CMUYamaha.pth')

train_loader = torch.load('/content/drive/MyDrive/DL Project/train_loader_CMUYamaha.pth')

class AttentionBlock(nn.Module):
    def __init__(self, f_g, f_l, f_int):
        super().__init__()

        self.w_g = nn.Sequential(
                                nn.Conv2d(f_g, f_int,
                                         kernel_size=1, stride=1,
                                         padding=0, bias=True),
                                nn.BatchNorm2d(f_int)
        )

        self.w_x = nn.Sequential(
                                nn.Conv2d(f_l, f_int,
                                         kernel_size=1, stride=1,
                                         padding=0, bias=True),
                                nn.BatchNorm2d(f_int)
        )

        self.psi = nn.Sequential(
                                nn.Conv2d(f_int, 1,
                                         kernel_size=1, stride=1,
                                         padding=0,  bias=True),
                                nn.BatchNorm2d(1),
                                nn.Sigmoid(),
        )

        self.relu = nn.ReLU(inplace=True)

    def forward(self, g, x):
        g1 = self.w_g(g)
        x1 = self.w_x(x)
        psi = self.relu(g1+x1)
        psi = self.psi(psi)

        return psi*x



class SegNetAttn(nn.Module):
  def __init__(self):
    super(SegNetAttn, self).__init__()


    self.conv1 = nn.Conv2d(in_channels = 3, out_channels = 96, kernel_size = 7, stride = 2, padding = 80, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu1 = nn.ReLU()
    self.norm1 = nn.LocalResponseNorm(size = 5, alpha=0.0001, beta=0.75, k=1.0)
    self.pool1 = nn.MaxPool2d(kernel_size = 3, stride = 3, padding = 0, dilation = 1)
    self.nin_pool1 = nn.Conv2d(in_channels=96, out_channels=8, kernel_size=1, stride=1, padding=0, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.drop_nin_pool1 = nn.Dropout(p=0.2)
    self.crop_nin_pool1 = nn.ZeroPad2d((-17, -18, -17, -18))
    self.nin_conv1 = nn.Conv2d(in_channels=96, out_channels=8, kernel_size=1, stride=1, padding=0, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.crop_nin_conv1 = nn.ZeroPad2d((-53, -54, -53, -54))


    self.conv2 = nn.Conv2d(in_channels = 96, out_channels = 256, kernel_size = 5, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu2 = nn.ReLU()
    self.pool2 = nn.MaxPool2d(kernel_size = 2, stride = 2, padding = 0, dilation = 1)


    self.conv3 = nn.Conv2d(in_channels = 256, out_channels = 512, kernel_size = 3, stride = 1, padding = 1, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu3 = nn.ReLU()


    self.conv4 = nn.Conv2d(in_channels = 512, out_channels = 512, kernel_size = 3, stride = 1, padding = 1, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu4 = nn.ReLU()


    self.conv5 = nn.Conv2d(in_channels = 512, out_channels = 512, kernel_size = 3, stride = 1, padding = 1, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu5 = nn.ReLU()
    self.pool5 = nn.MaxPool2d(kernel_size = 3, stride = 3, padding = 0, dilation = 1)
    self.crop_conv5 = nn.ZeroPad2d((-8, -7, -8, -7))
    self.nin_crop_conv5 =  nn.Conv2d(in_channels = 512, out_channels = 8, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')


    self.conv_fc6 = nn.Conv2d(in_channels = 512, out_channels = 4096, kernel_size = 6, stride = 1, padding = 2, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu6 = nn.ReLU()
    self.drop6 = nn.Dropout(p = 0.2)


    self.conv_fc7 = nn.Conv2d(in_channels = 4096, out_channels = 4096, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu7 = nn.ReLU()
    self.drop7 = nn.Dropout(p = 0.2)
    self.nin_fc7 = nn.Conv2d(in_channels = 4096, out_channels = 8, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu_nin7 = nn.ReLU()


    self.up1 = nn.ConvTranspose2d(in_channels = 8, out_channels = 8, kernel_size = 4, stride = 2, padding = 1, output_padding = 0, groups = 1, bias = True, dilation = 1)
    self.relu_up1 = nn.ReLU()


    self.up2 = nn.ConvTranspose2d(in_channels=8, out_channels=8, kernel_size=4, stride=2, padding=1, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.relu_up2 = nn.ReLU()



    self.up3 = nn.ConvTranspose2d(in_channels=8, out_channels=8, kernel_size=5, stride=3, padding=1, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.relu_up3 = nn.ReLU()



    self.nin6 = nn.Conv2d(in_channels = 8, out_channels = 6, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.conv6 = nn.ConvTranspose2d(in_channels=6, out_channels=6, kernel_size= 2, stride=3, padding=60, dilation=2, groups=1,  bias = True, padding_mode = 'zeros')


    self.conv7 = nn.ConvTranspose2d(in_channels=6, out_channels=6, kernel_size=16, stride=1, padding=0, dilation=4, groups=1,  bias = True, padding_mode = 'zeros')


    self.att5 = AttentionBlock(8, 8, 8)
    self.att2 = AttentionBlock(8, 8, 8)
    self.att1 = AttentionBlock(8, 8, 8)



  def forward(self, x):
    conv1 = self.conv1(x)
    relu1 = self.relu1(conv1) # Has a skip connection
    norm1 = self.norm1(relu1)
    pool1 = self.pool1(norm1) # Has a skip connection


    conv2 = self.conv2(pool1)
    relu2 = self.relu2(conv2)
    pool2 = self.pool2(relu2)


    conv3 = self.conv3(pool2)
    relu3 = self.relu3(conv3)


    conv4 = self.conv4(relu3)
    relu4 = self.relu4(conv4)


    conv5 = self.conv5(relu4)
    relu5 = self.relu5(conv5) # Has a skip connection
    pool5 = self.pool5(relu5)


    conv_fc6 = self.conv_fc6(pool5)
    relu6 = self.relu6(conv_fc6)
    drop6 = self.drop6(relu6)


    conv_fc7 = self.conv_fc7(drop6)
    relu7 = self.relu7(conv_fc7)
    drop7 = self.drop7(relu7)
    nin_fc7 = self.nin_fc7(drop7)
    relu_nin7 = self.relu_nin7(nin_fc7)


    up1 = self.up1(relu_nin7)
    relu_up1 = self.relu_up1(up1)


    crop_conv5 = self.crop_conv5(relu5)
    nin_crop_conv5 = self.nin_crop_conv5(crop_conv5)
    att5 = self.att5(g = relu_up1, x = nin_crop_conv5)


    fuse1 = torch.add(att5, relu_up1)


    up2 = self.up2(fuse1)
    relu_up2 = self.relu_up2(up2)


    nin_pool1 = self.nin_pool1(pool1)
    drop_nin_pool1 = self.drop_nin_pool1(nin_pool1)
    crop_nin_pool1 = self.crop_nin_pool1(drop_nin_pool1)
    att2 = self.att2(g = relu_up2, x = crop_nin_pool1)


    fuse2 = torch.add(att2, relu_up2)


    up3 = self.up3(fuse2)
    relu_up3 = self.relu_up3(up3)


    nin_conv1 = self.nin_conv1(conv1)
    crop_nin_conv1 = self.crop_nin_conv1(nin_conv1)
    att1 = self.att1(g = relu_up3, x = crop_nin_conv1)


    fuse3 = torch.add(att1, relu_up3)


    nin6= self.nin6(fuse3)
    conv6= self.conv6(nin6)


    conv7= self.conv7(conv6)

    return conv7

class SegNet(nn.Module):
  def __init__(self):
    super(SegNet, self).__init__()
    # d=0.5
    self.conv1 = nn.Conv2d(in_channels = 3, out_channels = 96, kernel_size = 7, stride = 2, padding = 80, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu1 = nn.ReLU()
    self.norm1 = nn.LocalResponseNorm(size = 5, alpha=0.0001, beta=0.75, k=1.0)
    self.pool1 = nn.MaxPool2d(kernel_size = 3, stride = 3, padding = 0, dilation = 1)
    self.conv2 = nn.Conv2d(in_channels = 96, out_channels = 256, kernel_size = 5, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu2 = nn.ReLU()
    self.pool2 = nn.MaxPool2d(kernel_size = 2, stride = 2, padding = 0, dilation = 1)
    self.conv3 = nn.Conv2d(in_channels = 256, out_channels = 512, kernel_size = 3, stride = 1, padding = 1, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu3 = nn.ReLU()
    self.conv4 = nn.Conv2d(in_channels = 512, out_channels = 512, kernel_size = 3, stride = 1, padding = 1, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu4 = nn.ReLU()
    self.conv5 = nn.Conv2d(in_channels = 512, out_channels = 512, kernel_size = 3, stride = 1, padding = 1, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu5 = nn.ReLU()
    self.pool5 = nn.MaxPool2d(kernel_size = 3, stride = 3, padding = 0, dilation = 1)
    self.conv_fc6 = nn.Conv2d(in_channels = 512, out_channels = 4096, kernel_size = 6, stride = 1, padding = 2, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu6 = nn.ReLU()
    self.drop6 = nn.Dropout(p = 0.2)
    self.conv_fc7 = nn.Conv2d(in_channels = 4096, out_channels = 4096, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu7 = nn.ReLU()
    self.drop7 = nn.Dropout(p = 0.2)
    self.nin_fc7 = nn.Conv2d(in_channels = 4096, out_channels = 8, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.relu_nin7 = nn.ReLU()
    self.up1 = nn.ConvTranspose2d(in_channels = 8, out_channels = 8, kernel_size = 4, stride = 2, padding = 1, output_padding = 0, groups = 1, bias = True, dilation = 1)
    self.relu_up1 = nn.ReLU()
    self.crop_conv5 = nn.ZeroPad2d((-8, -7, -8, -7))
    self.nin_crop_conv5 =  nn.Conv2d(in_channels = 512, out_channels = 8, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.up2 = nn.ConvTranspose2d(in_channels=8, out_channels=8, kernel_size=4, stride=2, padding=1, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.relu_up2 = nn.ReLU()
    self.nin_pool1 = nn.Conv2d(in_channels=96, out_channels=8, kernel_size=1, stride=1, padding=0, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.drop_nin_pool1 = nn.Dropout(p=0.2)
    self.crop_nin_pool1 = nn.ZeroPad2d((-17, -18, -17, -18))
    self.up3 = nn.ConvTranspose2d(in_channels=8, out_channels=8, kernel_size=5, stride=3, padding=1, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.relu_up3 = nn.ReLU()
    self.nin_conv1 = nn.Conv2d(in_channels=96, out_channels=8, kernel_size=1, stride=1, padding=0, dilation=1, groups=1,  bias = True, padding_mode = 'zeros')
    self.crop_nin_conv1 = nn.ZeroPad2d((-53, -54, -53, -54))
    self.nin6 = nn.Conv2d(in_channels = 8, out_channels = 6, kernel_size = 1, stride = 1, padding = 0, dilation = 1, groups = 1, bias = True, padding_mode = 'zeros')
    self.conv6 = nn.ConvTranspose2d(in_channels=6, out_channels=6, kernel_size= 2, stride=3, padding=60, dilation=2, groups=1,  bias = True, padding_mode = 'zeros')
    self.conv7 = nn.ConvTranspose2d(in_channels=6, out_channels=6, kernel_size=16, stride=1, padding=0, dilation=4, groups=1,  bias = True, padding_mode = 'zeros')


  def forward(self, x):
    conv1 = self.conv1(x)
    relu1 = self.relu1(conv1) # Has a skip connection
    norm1 = self.norm1(relu1)
    pool1 = self.pool1(norm1)
    conv2 = self.conv2(pool1) # Has a skip connection
    relu2 = self.relu2(conv2)
    pool2 = self.pool2(relu2)
    conv3 = self.conv3(pool2)
    relu3 = self.relu3(conv3)
    conv4 = self.conv4(relu3)
    relu4 = self.relu4(conv4)
    conv5 = self.conv5(relu4)
    relu5 = self.relu5(conv5) # Has a skip connection
    pool5 = self.pool5(relu5)
    conv_fc6 = self.conv_fc6(pool5)
    relu6 = self.relu6(conv_fc6)
    drop6 = self.drop6(relu6)
    conv_fc7 = self.conv_fc7(drop6)
    relu7 = self.relu7(conv_fc7)
    drop7 = self.drop7(relu7)
    nin_fc7 = self.nin_fc7(drop7)
    relu_nin7 = self.relu_nin7(nin_fc7)
    up1 = self.up1(relu_nin7)
    relu_up1 = self.relu_up1(up1)
    crop_conv5 = self.crop_conv5(relu5)
    nin_crop_conv5 = self.nin_crop_conv5(crop_conv5)
    fuse1 = torch.add(nin_crop_conv5, relu_up1)
    up2 = self.up2(fuse1)
    relu_up2 = self.relu_up2(up2)
    nin_pool1 = self.nin_pool1(pool1)
    drop_nin_pool1 = self.drop_nin_pool1(nin_pool1)
    crop_nin_pool1 = self.crop_nin_pool1(drop_nin_pool1)
    fuse2 = torch.add(crop_nin_pool1, relu_up2)
    up3 = self.up3(fuse2)
    relu_up3 = self.relu_up3(up3)
    nin_conv1 = self.nin_conv1(conv1)
    crop_nin_conv1 = self.crop_nin_conv1(nin_conv1)
    fuse3 = torch.add(crop_nin_conv1, relu_up3)
    nin6= self.nin6(fuse3)
    conv6= self.conv6(nin6)
    conv7= self.conv7(conv6)
    return conv7

model_baseline = SegNet().to(device)
checkpoint = torch.load('/content/drive/MyDrive/DL Project/Final Results/Results/FCN/Epoch Wise/FCN-CMUYamaha-200-epochs-4bs.pth', map_location=torch.device('cpu'))
model_baseline.load_state_dict(checkpoint)

from torchsummary import summary

summary(model_baseline, (3, 300, 300))

model_attention = SegNetAttn().to(device)
checkpoint = torch.load('/content/drive/MyDrive/DL Project/Final Results/Results/Attention FCN/Epoch Wise/FCNAtt-CMUYamaha-200-epochs-4bs.pth', map_location=torch.device('cpu'))
model_attention.load_state_dict(checkpoint)

model_attention.eval()

from torchsummary import summary

summary(model_attention, (3, 300, 300))

from sklearn.metrics import confusion_matrix
import seaborn as sn

def createConfusionMatrix(groundtruth, prediction):

    y_pred, y_true = [],  []

    y_pred.extend(prediction.data.cpu().view(-1).tolist())
    y_true.extend(groundtruth.data.cpu().view(-1).tolist())

    # Build confusion matrix
    cf_matrix = confusion_matrix(y_true, y_pred)

    return cf_matrix

classes_dict = {0: [74, 144, 226],
           1: [139, 87, 42],
           2: [155, 155, 155],
           3: [59, 93, 4],
           4: [209, 225, 158],
           5: [184, 20, 124]}

def recreateImage(class_indices, classes):
    image = np.zeros((class_indices.shape[0], class_indices.shape[1], 3))

    for CLASS, RGB in classes.items():
        # print(CLASS, RGB)
        rows, columns = np.where(class_indices == CLASS)
        image[rows, columns, :] = RGB


    return image.astype(int)

from PIL import Image
model_attention.eval()
IOU = {0: [], 1:[], 2:[], 3:[], 4:[], 5:[]}


with torch.no_grad():
    correct = 0
    total = 0
    for i, (images, labels) in enumerate(test_loader):
        images = images.permute(0, 3, 1, 2)
        images = images.to(device)
        labels = labels.to(device)
        outputs = model_attention(images)
        _, predicted = torch.max(outputs.data, 1)

        classes = np.unique(predicted.data.cpu().numpy())

        # df_cm = createConfusionMatrix(labels, predicted)

        # intersection = np.diag(df_cm)
        # ground_truth_set = df_cm.sum(axis=1)
        # predicted_set = df_cm.sum(axis=0)
        # union = ground_truth_set + predicted_set - intersection
        # IoU = intersection / union.astype(np.float32)


        # for iter, class_val in enumerate(classes):
        #     IOU[class_val].append(100 * IoU[iter])


        image_path_pred = f"/content/drive/MyDrive/DL Project/Base Line (Best mIOU = 66%)/images_pred and true_train/{i}_pred.png"
        img_pred= recreateImage(predicted.cpu().numpy()[0] , classes_dict)
        pil_pred = Image.fromarray(img_pred.astype(np.uint8))
        pil_pred.save(image_path_pred)
        image_path_true = f"/content/drive/MyDrive/DL Project/Base Line (Best mIOU = 66%)/images_pred and true_train/{i}_true.png"
        pil_true = Image.fromarray(recreateImage(labels.cpu().numpy()[0], classes_dict).astype(np.uint8))
        pil_true.save(image_path_true)


        # fig, axes = plt.subplots(1, 2, figsize=(18, 4))
        # axes[0].imshow(recreateImage(predicted.cpu().numpy()[0])), axes[0].set_title('Predicted')
        # axes[1].imshow(recreateImage(labels.cpu().numpy()[0])), axes[1].set_title('Ground Truth')
        # plt.show()
        # print('Pixel Accuracy = {} %'.format(round(correct * 100/total, 2)))


        # print('IOU = ', np.mean(IoU), end = '\r')
        # IOU.append(np.mean(IoU))

        # plt.figure(figsize = (12,7))
        # sn.heatmap(df_cm, annot=True)
        # print('Loss = ',loss.item())
        print(i)

attention_testIOU = IOU

from google.colab import drive
drive.mount('/content/drive')

path= '/content/drive/MyDrive/DL Project/Base Line (Best mIOU = 66%)/images_pred and ground'

model_baseline.eval()
IOU = {0: [], 1:[], 2:[], 3:[], 4:[], 5:[]}
with torch.no_grad():
    correct = 0
    total = 0
    for i, (images, labels) in enumerate(test_loader):
        images = images.permute(0, 3, 1, 2)
        images = images.to(device)
        labels = labels.to(device)
        outputs = model_baseline(images)
        _, predicted = torch.max(outputs.data, 1)

        classes = np.unique(predicted.data.cpu().numpy())


        df_cm = createConfusionMatrix(labels, predicted)

        intersection = np.diag(df_cm)
        ground_truth_set = df_cm.sum(axis=1)
        predicted_set = df_cm.sum(axis=0)
        union = ground_truth_set + predicted_set - intersection
        IoU = intersection / union.astype(np.float32)

        for iter, class_val in enumerate(classes):
            IOU[class_val].append(100 * IoU[iter])




        # fig, axes = plt.subplots(1, 2, figsize=(18, 4))
        # axes[0].imshow(recreateImage(predicted.cpu().numpy()[0])), axes[0].set_title('Predicted')
        # axes[1].imshow(recreateImage(labels.cpu().numpy()[0])), axes[1].set_title('Ground Truth')
        # plt.show()
        # # print('Pixel Accuracy = {} %'.format(round(correct * 100/total, 2)))


        print('IOU = ', np.mean(IoU), end = '\r')
        # IOU.append(np.mean(IoU))

        # plt.figure(figsize = (12,7))
        # sn.heatmap(df_cm, annot=True)
        # print('Loss = ',loss.item())

baseline_testIOU = IOU

classes = ['Sky', 'Smooth Trail', 'Rough Trail', 'High Vegetation', 'Low Vegetation', 'Obstacle']

base_perf, attn_perf = [], []
for i, classes_val in enumerate(classes):
    print('Class = ', classes_val)

    base = baseline_testIOU[i]
    # non_zero_data_base = base[base != 0]

    print('Baseline Performance on Test Data: ', round(np.mean(base)), '%')

    attn = attention_testIOU[i]
    # non_zero_data_attn = attn[attn != 0]

    print('Attention Performance on Test Data: ', round(np.mean(attn)), '%')




    base_perf.append(round(np.mean(base)))
    attn_perf.append(round(np.mean(attn)))

species = classes[:4]
species[-1] = 'Vegetation'
penguin_means = {
    'Baseline FCN': base_perf[:4],
    'Attention FCN': attn_perf[:4]}

x = np.arange(len(species))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in penguin_means.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=10)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Mean IOU %')
ax.set_title('Performance on Test (Baseline FCN versus Attention FCN)')
ax.set_xticks(x + width, species)
ax.legend(loc='upper right')
ax.set_ylim(0, 80)

plt.show()

