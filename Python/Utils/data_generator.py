import tensorflow as tf
import numpy as np
import glob
import random
from config import ConfigOptions


class ConditionalDataGenerator(tf.keras.utils.Sequence):
#     'Generates data for tf.keras'
    def __init__(self, dir='../Data/numpyData/', batch_size=16, shuffle=True, dims = 4):
        'Initialization'
        self.dir = dir + '{}/*.npz'.format(dims)
        self.condDir = dir + 'Centroids/*.npz'.format(dims)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.dims = dims
        self.config = ConfigOptions()
        self.files  = sorted(glob.glob(self.dir))
        self.condFiles  = sorted(glob.glob(self.condDir))
        self.on_epoch_end()
        self.count = self.__len__()
        print("mnumber of all samples = ", len(self.files))


    def __len__(self):
        'Denotes the number of batches per epoch'
        self.num_batches = int(np.floor(len(self.files) / self.batch_size))
        return self.num_batches

    def __getitem__(self, index):
      
        X = self.__data_generation(index)

        return X

    def on_epoch_end(self):
        if self.shuffle == True:
            np.random.shuffle(self.files)

    def __data_generation(self, idx):
        'Generates data containing batch_size samples' 
        
        files = self.files[idx*self.batch_size:idx*self.batch_size+self.batch_size]
        condFiles = self.condFiles[idx*self.batch_size:idx*self.batch_size+self.batch_size]
        
        X = np.empty((self.batch_size, self.dims, self.dims))
        XCentroid  = np.empty((self.batch_size, 2))
        
        for i, file in enumerate(files):
          
          data = np.load(file)
          img = data['data']
          
          centroidData = np.load(self.condFiles[i])
          centroid = centroidData['data']
      
          X[i,] = img
          XCentroid[i,] = centroid

        X = np.expand_dims(X,axis=3)
        
        return ([X,XCentroid],)
