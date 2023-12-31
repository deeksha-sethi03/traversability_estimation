# -*- coding: utf-8 -*-
"""FCN-YamahaCMU-HSV-Baseline.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1n91Z_BT4WiX4fwVaU2F5XyJzQDKF3IZ2
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
from torch.utils.data import DataLoader, TensorDataset
import math
from matplotlib.colors import ListedColormap
from tqdm import tqdm
from itertools import chain


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(device)

path = '.'
train = path + '/yamaha_v0/train/'
test = path + '/yamaha_v0/valid/'

def get_folder_names(directory_path):
    folder_names = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]
    prefix = directory_path

    images = [prefix + element + '/rgb.jpg' for element in folder_names]
    labels = [prefix + element + '/labels.png' for element in folder_names]

    return np.array(images), np.array(labels)

train_images, train_labels = get_folder_names(train)
test_images, test_labels = get_folder_names(test)
train_images_folders, train_labels_folders = np.sort(train_images), np.sort(train_labels)
test_images_folders, test_labels_folders = np.sort(test_images), np.sort(test_labels)

def load_images(filename_list):
    images = []
    c = 0
    for filename in filename_list:
        img = cv.imread(filename)
        # img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        if img is not None:
            img= cv.resize(img, (300, 300))

            images.append(img)



    return np.array(images)

train_images = load_images(train_images_folders)
train_labels = load_images(train_labels_folders)


test_images = load_images(test_images_folders)
test_labels = load_images(test_labels_folders)

img = cv.cvtColor(train_labels[354], cv.COLOR_BGR2RGB)
plt.imshow(img), plt.show()

"""![image.png](attachment:image.png)"""

classes = {0: [74, 144, 226],
           1: [139, 87, 42],
           2: [155, 155, 155],
           3: [59, 93, 4],
           4: [209, 225, 158],
           5: [184, 20, 124]}

def recreateImage(class_indices):
    image = np.zeros((class_indices.shape[0], class_indices.shape[1], 3))

    for CLASS, RGB in classes.items():
        # print(CLASS, RGB)
        rows, columns = np.where(class_indices == CLASS)
        image[rows, columns, :] = RGB


    return image.astype(int)

old_labels = train_labels
train_labels_indexed = np.zeros((old_labels.shape[0], old_labels.shape[1], old_labels.shape[2]))

print(old_labels.shape[0])

for index in tqdm(range(old_labels.shape[0]), desc="Processing", unit="iteration"):

    # print(index)

    label = old_labels[index]

    img_hsv = cv.cvtColor(label, cv.COLOR_BGR2HSV)

    mask_1 = cv.inRange(img_hsv,(85, 100, 20), (130, 255, 255)) # SKY
    mask_2 = cv.inRange(img_hsv,(0, 50, 20),(30, 255, 255)) # ROUGH TRAIL
    mask_3 = cv.inRange(img_hsv,(0, 10, 0),(60, 100, 255)) # SMOOTH TRAIL
    mask_4 = cv.inRange(img_hsv,(45, 100, 20),(80, 255, 150)) # HIGH VEGETATION
    mask_5 = cv.inRange(img_hsv,(40, 100, 150),(80, 255, 255)) # LOW VEGETATION
    mask_6 = cv.inRange(img_hsv,(130, 50, 150),(180, 255, 255)) # OBSTACLE


    labeledimg = np.dstack((mask_1, mask_2, mask_3, mask_4, mask_5, mask_6))
    # print(labeledimg[9, 6, :])
    # print(labeledimg[0, 0, :])
    # print(labeledimg[26, 57, :])
    # print(labeledimg[7, 0, :])
    # print(labeledimg[299, 299, :])
    # print(labeledimg[64, 62, :])
    # print(labeledimg[47, 8, :])
    # print(labeledimg[0, 78, :])

    labelindices = np.argmax(labeledimg, axis = 2)
    train_labels_indexed[index] = labelindices

    # plt.figure(figsize=(24, 8))




    # plt.subplot(191), plt.imshow(cv.cvtColor(label, cv.COLOR_BGR2RGB), cmap='gray'), plt.title('Original Image')
    # plt.subplot(192), plt.imshow(img_hsv, cmap='gray'), plt.title('HSV Image')
    # plt.subplot(193), plt.imshow(mask_1, cmap='gray'), plt.title('Sky')
    # plt.subplot(194), plt.imshow(mask_2, cmap='gray'), plt.title('Rough Trail')
    # plt.subplot(195), plt.imshow(mask_3, cmap='gray'), plt.title('Smooth Trail')
    # plt.subplot(196), plt.imshow(mask_4, cmap='gray'), plt.title('High Vegetation')
    # plt.subplot(197), plt.imshow(mask_5, cmap='gray'), plt.title('Low Vegetation')
    # plt.subplot(198), plt.imshow(mask_6, cmap='gray'), plt.title('Obstacle')
    # plt.subplot(199), plt.imshow(recreateImage(labelindices), cmap='gray'), plt.title('Recontructed Image')

old_labels = test_labels
test_labels_indexed = np.zeros((old_labels.shape[0], old_labels.shape[1], old_labels.shape[2]))

print(old_labels.shape[0])

for index in tqdm(range(old_labels.shape[0]), desc="Processing", unit="iteration"):


    label = old_labels[index]

    img_hsv = cv.cvtColor(label, cv.COLOR_BGR2HSV)

    mask_1 = cv.inRange(img_hsv,(85, 100, 20), (130, 255, 255)) # SKY
    mask_2 = cv.inRange(img_hsv,(0, 50, 20),(30, 255, 255)) # ROUGH TRAIL
    mask_3 = cv.inRange(img_hsv,(0, 10, 0),(60, 100, 255)) # SMOOTH TRAIL
    mask_4 = cv.inRange(img_hsv,(45, 100, 20),(80, 255, 255)) # HIGH VEGETATION
    mask_5 = cv.inRange(img_hsv,(40, 100, 150),(85, 255, 255)) # LOW VEGETATION
    mask_6 = cv.inRange(img_hsv,(140, 100, 20),(180, 255, 255)) # OBSTACLE

    labeledimg = np.dstack((mask_1, mask_2, mask_3, mask_4, mask_5, mask_6))
    labelindices = np.argmax(labeledimg, axis = 2)
    test_labels_indexed[index] = labelindices


    # plt.figure(figsize=(24, 8))




    # plt.subplot(191), plt.imshow(cv.cvtColor(label, cv.COLOR_BGR2RGB), cmap='gray'), plt.title('Original Image')
    # plt.subplot(192), plt.imshow(img_hsv, cmap='gray'), plt.title('HSV Image')
    # plt.subplot(193), plt.imshow(mask_1, cmap='gray'), plt.title('Sky')
    # plt.subplot(194), plt.imshow(mask_2, cmap='gray'), plt.title('Rough Trail')
    # plt.subplot(195), plt.imshow(mask_3, cmap='gray'), plt.title('Smooth Trail')
    # plt.subplot(196), plt.imshow(mask_4, cmap='gray'), plt.title('High Vegetation')
    # plt.subplot(197), plt.imshow(mask_5, cmap='gray'), plt.title('Low Vegetation')
    # plt.subplot(198), plt.imshow(mask_6, cmap='gray'), plt.title('Obstacle')
    # plt.subplot(199), plt.imshow(recreateImage(labelindices), cmap='gray'), plt.title('Recontructed Image')

xTrain = torch.from_numpy(train_images).type(torch.float32)
yTrain = torch.from_numpy(train_labels_indexed).type(torch.LongTensor)
xTest = torch.from_numpy(test_images).type(torch.float32)
yTest = torch.from_numpy(test_labels_indexed).type(torch.LongTensor)

print(xTrain.size(), xTest.size())
print(yTrain.size(), yTest.size())

train = TensorDataset(xTrain, yTrain)
test = TensorDataset(xTest, yTest)

train_loader = DataLoader(train, shuffle = True, batch_size = 4)
test_loader = DataLoader(test, shuffle = True, batch_size = 1)

torch.save(train_loader, 'train_loader_CMUYamaha.pth')
torch.save(test_loader, 'test_loader_CMUYamaha.pth')

train_loader = torch.load('./train_loader_CMUYamaha.pth')
test_loader = torch.load('./test_loader_CMUYamaha.pth')

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

from sklearn.metrics import confusion_matrix
import seaborn as sn

def createConfusionMatrix(groundtruth, prediction):

    y_pred, y_true = [],  []

    y_pred.extend(prediction.data.cpu().view(-1).tolist())
    y_true.extend(groundtruth.data.cpu().view(-1).tolist())

    # Build confusion matrix
    cf_matrix = confusion_matrix(y_true, y_pred)

    return cf_matrix

def recreateImage(class_indices):
    image = np.zeros((class_indices.shape[0], class_indices.shape[1], 3))

    for CLASS, RGB in classes.items():
        # print(CLASS, RGB)
        rows, columns = np.where(class_indices == CLASS)
        image[rows, columns, :] = RGB


    return image.astype(int)

save_fig_folder = './Results/FCN/Epoch Wise/'

# The training loop

def train(net, optimizer, criterion, train_loader, epochs, model_name):

    model = net.to(device)
    train_loss_values = []
    train_mIOU = []
    output_imgs = []
    output_preds = []
    output_labels = []

    for epoch in range(epochs):
        correct = 0
        total = 0
        flag = 0
        running_loss = 0.0
        IOU = 0
        output_imgs = []
        output_preds = []
        output_labels = []

        for i, (images, labels) in enumerate(tqdm(train_loader, desc="Processing", unit=" Iterations")):

            images = images.permute(0, 3, 1, 2)

            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)


            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)


            df_cm = createConfusionMatrix(labels, predicted)

            intersection = np.diag(df_cm)
            ground_truth_set = df_cm.sum(axis=1)
            predicted_set = df_cm.sum(axis=0)
            union = ground_truth_set + predicted_set - intersection
            IOU = IOU + np.mean(intersection / union.astype(np.float32))

            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            optimizer.step()

            if i == 31 or i == 45 or i == 5:

                output_imgs.append(np.transpose(images.cpu().numpy()[0], (1, 2, 0)))
                output_labels.append(labels.cpu().numpy()[0])
                output_preds.append(predicted.cpu().numpy()[0])


        plt.figure(figsize=(24, 4))

        plt.subplot(191), plt.imshow(cv.cvtColor(output_imgs[0].astype(np.uint8), cv.COLOR_BGR2RGB), cmap='gray'), plt.title('Original'), plt.xticks([]), plt.yticks([])
        plt.subplot(192), plt.imshow(recreateImage(output_labels[0]), cmap='gray'), plt.title('Ground Truth'), plt.xticks([]), plt.yticks([])
        plt.subplot(193), plt.imshow(recreateImage(output_preds[0]), cmap='gray'), plt.title('Predicted'), plt.xticks([]), plt.yticks([])
        plt.subplot(194), plt.imshow(cv.cvtColor(output_imgs[1].astype(np.uint8), cv.COLOR_BGR2RGB), cmap='gray'), plt.title('Original'), plt.xticks([]), plt.yticks([])
        plt.subplot(195), plt.imshow(recreateImage(output_labels[1]), cmap='gray'), plt.title('Ground Truth'), plt.xticks([]), plt.yticks([])
        plt.subplot(196), plt.imshow(recreateImage(output_preds[1]), cmap='gray'), plt.title('Predicted'), plt.xticks([]), plt.yticks([])
        plt.subplot(197), plt.imshow(cv.cvtColor(output_imgs[2].astype(np.uint8), cv.COLOR_BGR2RGB), cmap='gray'), plt.title('Original'), plt.xticks([]), plt.yticks([])
        plt.subplot(198), plt.imshow(recreateImage(output_labels[2]), cmap='gray'), plt.title('Ground Truth'), plt.xticks([]), plt.yticks([])
        plt.subplot(199), plt.imshow(recreateImage(output_preds[2]), cmap='gray'), plt.title('Predicted'), plt.xticks([]), plt.yticks([])
        title = f'Epoch: {epoch + 1}'
        plt.tight_layout()
        plt.suptitle(title)
        save_name = f'{save_fig_folder}epoch_{epoch+1}.jpg'
        plt.savefig(save_name)

        # fig, axes = plt.subplots(1, 9, figsize=(18, 18))

        # axes[0].imshow(recreateImage(predicted.cpu().numpy()[31])), axes
        # axes[1].imshow(recreateImage(labels.cpu().numpy()[31]))
        # axes[2].imshow(recreateImage(predicted.cpu().numpy()[45]))
        # axes[3].imshow(recreateImage(labels.cpu().numpy()[45]))
        # axes[4].imshow(recreateImage(predicted.cpu().numpy()[46]))
        # axes[5].imshow(recreateImage(labels.cpu().numpy()[46]))
        # plt.show()



        print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch+1, epochs, running_loss/len(train_loader)))
        print('Epoch [{}/{}], Mean IOU: {:.4f}'.format(epoch+1, epochs, IOU/len(train_loader)))

        train_loss_values.append(running_loss)
        train_mIOU.append(100*IOU/len(train_loader))

    return train_mIOU, train_loss_values

model = SegNet().to(device)
epochs = 200
class_weights = torch.Tensor([1.0, 1.1, 1.1, 1.0, 1.0, 1.0]).to(device)

criterion = nn.CrossEntropyLoss(weight= class_weights)
# criterion = nn.CrossEntropyLoss()



optimizer = optim.Adam(model.parameters(), lr=0.001)
train_mIOU, train_loss_values= train(model, optimizer, criterion, train_loader, epochs, 'cnn_curve')

torch.save(model.state_dict(), './Results/FCN/Epoch Wise/FCN-CMUYamaha-200-epochs-4bs.pth')
np.save('./Results/FCN/Epoch Wise/train_mIOU', np.array(train_mIOU))
np.save('./Results/FCN/Epoch Wise/train_loss', np.array(train_loss_values))



plt.figure(figsize=(24, 6))
denominator = len(train_loader)

plt.subplot(121), plt.plot(train_mIOU), plt.title('Mean IOU')
plt.subplot(122), plt.plot(np.array(train_loss_values)/denominator), plt.title('Loss')
plt.tight_layout()
plt.show()

print(max(train_loss_values)/len(train_loader), min(train_loss_values)/len(train_loader))

model = SegNet().to(device)
checkpoint = torch.load('./Results/FCN/Epoch Wise/FCN-CMUYamaha-200-epochs-4bs.pth')
model.load_state_dict(checkpoint)

def draw_contours(image):
  # cv2_imshow(np.array(image)) # OpenCV uses BGR, matplotlib uses RGB
  img = image.astype(np.uint8)
  imghsv = cv.cvtColor(img, cv.COLOR_RGB2HSV)

  mask_2 = cv.inRange(imghsv,(0, 0, 0),(255, 10, 255)) # ROUGH TRAIL
  mask_3 = cv.inRange(imghsv,(10, 40, 20),(30, 255, 200)) # SMOOTH TRAIL
  # # mask_1 = cv.inRange(img_hsv,(85, 100, 20), (130, 255, 255)) # SKY

  # lower_gray = np.array([0, 0, 0])
  # upper_gray = np.array([255, 10, 255])
  combined_mask = cv.bitwise_or(mask_2, mask_3)
  # mask_gray = cv.inRange(imghsv, lower_gray, upper_gray)
  contours, _ = cv.findContours(combined_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  im = np.copy(img)
  cv.drawContours(im, contours, -1, (255, 0, 0), 1)
  # cv.imshow('image', im)
  return contours, im

# print(contours)
from sklearn.linear_model import RANSACRegressor
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit


def find_vector(contours):
  min_y= 1000
  max_y= 0
  color = (255, 0, 0)


  contours = np.concatenate(contours)

  contours_flatten = np.squeeze(contours, axis = 1)

  contours_sorted_i = np.argsort(contours_flatten[:, -1])
  contours_sorted= contours_flatten[contours_sorted_i]
  # print('contours_sorted', contours_sorted)

  unique_val, counts = np.unique(contours_sorted[:, -1], return_counts= True)
  val_multi= unique_val[counts >= 2]
  selected_contours = contours_sorted[np.isin(contours_sorted[:, -1], val_multi)]

  mean_rows = []

  # Iterate through unique values and calculate the mean for each group
  for value in np.unique(selected_contours[:, -1]):
      group_rows = selected_contours[selected_contours[:, -1] == value]
      mean_row = np.mean(group_rows, axis=0)
      mean_rows.append(mean_row)

  # Convert the list of mean rows into a NumPy array
  result = np.array(mean_rows)


  # contour_pairs= selected_contours.reshape(-1, 2, selected_contours.shape[1])

  # sum_of_pairs = np.add(contour_pairs[:, 0, :], contour_pairs[:, 1, :])//2

  # print(sum_of_pairs)
  x= result[:, 0]
  y= result[:, -1]



  ransac = RANSACRegressor(base_estimator = LinearRegression(), residual_threshold = 100.0)
  ransac.fit(x.reshape(-1, 1), y)
  inliers_mask = ransac.inlier_mask_

  x = x[inliers_mask]
  y = y[inliers_mask]


  # Define the polynomial function for fitting
  def polynomial_fit(x, a, b, c):
      return a * x**2 + b * x + c

  # Fit the polynomial function to the zigzag data
  params, covariance = curve_fit(polynomial_fit, y, x)

  # Generate a smooth curve using the fitted parameters
  smooth_y = np.linspace(min(y), max(y), 1000)
  smooth_x = polynomial_fit(smooth_y, *params)



  return smooth_x, smooth_y

predicted = []

model.eval()
with torch.no_grad():
    correct = 0
    total = 0
    for i, (images, labels) in enumerate(train_loader):
        images = images.permute(0, 3, 1, 2)
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)

        # loss = criterion(outputs, labels)

        df_cm = createConfusionMatrix(labels, predicted)

        intersection = np.diag(df_cm)
        ground_truth_set = df_cm.sum(axis=1)
        predicted_set = df_cm.sum(axis=0)
        union = ground_truth_set + predicted_set - intersection
        IoU = intersection / union.astype(np.float32)

        target = predicted[0]
        # print(target.shape)

        if torch.any(torch.eq(target, 1)) or torch.any(torch.eq(target, 2)):

            print('Terrain is traversable!')
            # print(target.shape)
            equality_tensors_rough = [torch.eq(target, 1)]
            equality_tensors_smooth = [torch.eq(target, 2)]
            # print(equality_tensors_smooth.shape)
            # print(equality_tensors_rough, equality_tensors_smooth)

            counts_rough = [torch.sum(tensor).item() for tensor in equality_tensors_rough]
            counts_smooth = [torch.sum(tensor).item() for tensor in equality_tensors_smooth]

            # print(counts_rough, counts_smooth)
            traversable_rough = round(100 * counts_rough[0]/90000, 1)
            traversable_smooth = round(100 * counts_smooth[0]/90000, 1)

            print('In the field of view, {} percentange is smooth terrain, while {} percentange is rough terrain'.format(traversable_smooth, traversable_rough))

            pred_recreated = recreateImage(predicted.cpu().numpy()[0])
            gt_recreated = recreateImage(labels.cpu().numpy()[0])


            compare= []
            compare.append(pred_recreated)
            compare.append(gt_recreated)

            contours1, im1 = draw_contours(compare[0])
            contours2, im2 = draw_contours(compare[1])


            # print(contours1)
            pred_line_x, pred_line_y = find_vector(contours1)
            gt_line_x, gt_line_y = find_vector(contours2)

            fig, axes = plt.subplots(1, 2, figsize=(18, 4))
            axes[0].imshow(recreateImage(predicted.cpu().numpy()[0])), axes[0].set_title('Predicted')
            axes[0].plot(pred_line_x, pred_line_y, '-', color = 'red')
            axes[1].imshow(recreateImage(labels.cpu().numpy()[0])), axes[1].set_title('Ground Truth')
            # axes[1].plot(gt_line_x, gt_line_y, '-', color = 'red')
            plt.show()


        else:
            print('No traversable terrain found!')

            fig, axes = plt.subplots(1, 2, figsize=(18, 4))
            axes[0].imshow(recreateImage(predicted.cpu().numpy()[0])), axes[0].set_title('Predicted')
            axes[1].imshow(recreateImage(labels.cpu().numpy()[0])), axes[1].set_title('Ground Truth')
            plt.show()

        # print('Pixel Accuracy = {} %'.format(round(correct * 100/total, 2)))


        print('IOU = ', np.mean(IoU))

        # plt.figure(figsize = (12,7))
        # sn.heatmap(df_cm, annot=True)
        # print('Loss = ',loss.item())
        break

"""MISCELLANEOUS"""

# a = np.array([[1, 2, 1], [2, 5, 4]])
# row, col = np.where(a == 1)
# print(row, col)


# a[row, col] = 2929292
# print(a)


# for CLASS, RGB in classes.items():
#     print(CLASS, RGB)

# idx = np.random.permutation(image)
# final_labels = flat_labels
# train_x, train_y = flat_images[ :int(len(idx)*0.8)], final_labels[ :int(len(idx)*0.8)]
# test_x, test_y = flat_images[int(len(idx)*0.8): ], final_labels[int(len(idx)*0.8): ]

# xTrain = torch.from_numpy(train_x).type(torch.float32)
# yTrain = torch.from_numpy(train_y).type(torch.LongTensor)
# xTest = torch.from_numpy(test_x).type(torch.float32)
# yTest = torch.from_numpy(test_y).type(torch.LongTensor)

# print(xTrain.size(), xTest.size())
# print(yTrain.size(), yTest.size())

# train = TensorDataset(xTrain, yTrain)
# test = TensorDataset(xTest, yTest)

# train_loader = DataLoader(train, shuffle = True, batch_size = 4)
# test_loader = DataLoader(test, shuffle = True, batch_size = 1)

# plt.imshow(labels[0][0][:][:])
# plt.show()

# plt.imshow(labels[0][0][:, :, 0])
# plt.show() # R

# plt.imshow(labels[0][0][:, :, 1])
# plt.show() # G

# plt.imshow(labels[0][0][:, :, 2])
# plt.show() # B

# print(labels[0][0].shape)

# label = labels[0][0]

# # Apply Sobel filter
# sobel_x = cv.Sobel(label, cv.CV_64F, 1, 0, ksize=3)
# sobel_y = cv.Sobel(label, cv.CV_64F, 0, 1, ksize=3)

# # Combine the results
# sobel_combined = np.sqrt(sobel_x**2 + sobel_y**2)


# # Specify the weight for blending (0.0 for image1, 1.0 for image2)
# alpha = 0.5

# # Blend the images
# blended_image = cv.addWeighted(label, 1 - alpha, np.abs(sobel_x).astype(np.uint8), alpha, 0)
# hsv_values = cv.cvtColor(label, cv.COLOR_RGB2HSV)
# print(hsv_values.shape)


# # Display the results
# plt.figure(figsize=(24, 8))

# plt.subplot(151), plt.imshow(labels[0][0], cmap='gray'), plt.title('Original Image')
# plt.subplot(152), plt.imshow(np.abs(sobel_x).astype(np.uint8), cmap='gray'), plt.title('Sobel X')
# plt.subplot(153), plt.imshow(np.abs(sobel_y).astype(np.uint8), cmap='gray'), plt.title('Sobel Y')
# plt.subplot(154), plt.imshow(np.abs(blended_image), cmap='gray'), plt.title('Superimposed Image')
# plt.subplot(155), plt.imshow(hsv_values, cmap='gray'), plt.title('HSV Image')

# A = np.unique(hsv_values.reshape((-1, 3)), axis = 0)
# print(A)

# plt.show()

# # im2 = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# print(im2)


# img_hsv = cv.cvtColor(label, cv.COLOR_BGR2HSV)

# mask_forest = cv.inRange(img_hsv,(60, 100, 20), (70, 255, 255) )
# mask_smallveg = cv.inRange(img_hsv,(40, 100, 20),(60, 255, 255))
# mask_obstacle = cv.inRange(img_hsv,(40, 100, 20),(60, 255, 255))
# mask_smoothtr = cv.inRange(img_hsv,(40, 100, 20),(60, 255, 255))
# mask_roughtr = cv.inRange(img_hsv,(40, 100, 20),(60, 255, 255))
# mask_sky = cv.inRange(img_hsv,(40, 100, 20),(60, 255, 255))




# plt.figure(figsize=(24, 8))

# plt.subplot(171), plt.imshow(img_hsv, cmap='gray'), plt.title('Original Image')
# plt.subplot(172), plt.imshow(imgray, cmap='gray'), plt.title('Gray Scale')
# plt.subplot(173), plt.imshow(im2, cmap='gray'), plt.title('Contoured')
# plt.subplot(174), plt.imshow(label, cmap='gray'), plt.title('Original Image')
# plt.subplot(175), plt.imshow(imgray, cmap='gray'), plt.title('Gray Scale')
# plt.subplot(176), plt.imshow(im2, cmap='gray'), plt.title('Contoured')



# import os
# import numpy as np

# import cv2
# img = label
# from matplotlib import pyplot as plt
# # print(img.dtype)

# print((np.unique(img.reshape(-1,3),axis=0)).shape)

# plt.imshow(mask)
# print(mask)

# def rgb2gray(rgb):

#     r, g, b = rgb[0], rgb[1], rgb[2]
#     gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
#     return np.round(gray)

# Forest = [59, 93, 4]
# SmallVegetation = [209, 225, 158]
# Obstacle = [184, 20, 124]
# SmoothTrail = [155, 155, 155]
# RoughTrail = [139, 87, 42]
# Sky = [74, 144, 226]


# COLOR_DICT = np.array([Forest, SmallVegetation, Obstacle, SmoothTrail, RoughTrail, Sky])
# print(COLOR_DICT)


# a = np.argmax(COLOR_DICT, axis = 1)
# print(a)
# COLOR_DICT[range(len(a)), a] = 255
# print(COLOR_DICT)

