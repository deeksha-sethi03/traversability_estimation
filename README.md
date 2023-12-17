# Improved Traversability Estimation using Attention with Fully Convolutional Networks

This project aims to prove that integrating attention with fully convolutional networks can improve the traversability estimation of the terrain. A red line to highlight the best possible path through the most traversable terrains in the field of view of the robot (as shown below).

![2](https://github.com/deeksha-sethi03/traversability_estimation/assets/63807125/eb6bbc7b-ed21-4d4d-b8c7-78325193db6b)



The below plot demonstrates the consistent improvement in the performance of the model across epochs in the training phase. The training was performed on 931 training images (from the Yamaha CMU Off-Road Dataset). The proposed attention integration in the FCN has marginally improved the performance with minimal data instances for a semantic segmentation task. If scaled with better computing and larger datasets, it can potentially improve the performance of the network. 


![Training mIOU](https://github.com/deeksha-sethi03/traversability_estimation/assets/63807125/352d9d9b-5e58-420d-8f8a-1658b03572c1)


The results of the test images are shown below. The improvement in the smooth terrain is evident in the mean IOU. We compare the results of our proposed Attention FCN with the Baseline FCN inspired by the model used in https://www.ri.cmu.edu/app/uploads/2017/11/semantic-mapping-offroad-nav-compressed.pdf.


![Test mIOU](https://github.com/deeksha-sethi03/traversability_estimation/assets/63807125/9096e7af-a248-44d2-9b16-83f7dfe8addc)


