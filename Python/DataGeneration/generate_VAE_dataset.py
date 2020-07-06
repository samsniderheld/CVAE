from PIL import Image
import glob 
import numpy as np 
import os
import shutil
import sys
sys.path.append("..")
from config import ConfigOptions
from Utils.misc import *

config = ConfigOptions()

if os.path.exists("../../Data/NumpyDataDepth"):
  shutil.rmtree("../../Data/NumpyDataDepth")


os.makedirs('../../Data/NumpyDataDepth/{}/'.format(config.img_dim))
os.makedirs('../../Data/NumpyDataDepth/Centroids/')

imgs = sorted(glob.glob("../"+config.raw_data_dir+"*.png"),key=natural_keys)


data_length = len(imgs)
print(data_length)

all_centroids = np.zeros((data_length,2))

for i in range(0,data_length):

    img = Image.open(imgs[i])

    new_data = np.array(img.copy())

    img.close()

    new_data = resize(new_data)

    for_centroid = new_data.copy()

    centroid_data = convert(process(for_centroid))

    new_data = convert(new_data)

    new_data = new_data/255.

    np.savez_compressed("../../Data/NumpyDataDepth/{}/{}".format(config.img_dim,'%06d'%i),data=new_data)

    #get centroids and save
    x_val = 0;
    x_counter = 0;
    y_val = 0;
    y_counter = 0;
    for x in range(0,centroid_data.shape[0]):
        for y in range(0,centroid_data.shape[0]):
            if(centroid_data[x][y] == 0):
                x_val+=x
                x_counter+=1
                y_val+=y
                y_counter+=1


    centroid = [int(y_val/y_counter), int(x_val/x_counter)]
    numpy_centroid = np.array(centroid)
    all_centroids[i] = numpy_centroid
    np.savez_compressed("../../Data/NumpyDataDepth/Centroids/{}".format('%06d'%i),data=numpy_centroid )
    
    if(i%1000 == 0):
        print(i)


print("allDatedCreated")

