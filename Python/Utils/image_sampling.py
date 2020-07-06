import numpy as np
import cv2
from scipy.spatial import distance
import random

def create_conditional_sample_pic(dims, epoch, encoder, decoder,in_dir,out_dir):
  data = np.load('{}{}/000000.npz'.format(in_dir,dims))
  img = data['data']

  centroid = np.load('{}Centroids/000000.npz'.format(in_dir))
  conditional = centroid['data']

  img = cv2.resize(img, dsize=(dims, dims), interpolation=cv2.INTER_NEAREST)
  encoded = encoder.predict([np.reshape(img,(1,dims,dims,1)),np.reshape(conditional,(1,2))])
  decoded = decoder.predict(encoded[2]) 
  img_out = decoded[0]
  img_out *= 255
  save_img = cv2.resize(img_out, dsize=(512, 512), interpolation=cv2.INTER_NEAREST)
  cv2.imwrite('{}/image_res_{}_epoch_{}.png'.format(out_dir,'%04d'%dims,'%04d'%epoch), save_img)

def print_test_pic(in_dir,out_dir,dims):
  data = np.load('{}{}/000000.npz'.format(in_dir,dims))
  img = data['data']
  img = img*255.
  save_img = cv2.resize(img, dsize=(512, 512), interpolation=cv2.INTER_NEAREST)
  cv2.imwrite('{}/0_{}.png'.format(out_dir,dims), save_img)

def load_centroid(index,conditional_files):
  centroid_data = np.load(conditional_files[index])
  centroid = centroid_data['data']
  return centroid

def get_interim_centroid(centroid_1, centroid_2):
  x = (centroid_1[0] + centroid_2[0])/2
  y = (centroid_1[1] + centroid_2[1])/2
  return np.array([x,y])

def get_closest_centroid_index(centroid,conditional_files,modulus):
  highest_dist = 10000
  winning_index = 0

  for i in range(0,len(conditional_files),modulus):
    test_centroid = load_centroid(i,conditional_files)
    distval = distance.euclidean(centroid,test_centroid)

    if(distval<highest_dist):
      highest_dist = distval
      winning_index = i

    if(highest_dist<=.25):
      return winning_index

  return winning_index

def load_vector(index,files,conditional_files,encoder,img_dim):
  img_data = np.load(files[index])
  img = img_data['data']

  centroid_data = np.load(conditional_files[index])
  centroid = centroid_data['data']

  encoded = encoder.predict([np.reshape(img,(1,img_dim,img_dim,1)),np.reshape(centroid,(1,2))])
  return encoded[2]


def generate_frame(vector,decoder,latent_size):
  y = decoder.predict(np.reshape(vector,(1,latent_size+2)))
  y *= 255
  return y[0]

def interpolate(v1,v2,x):
  v = x * v1 + (1-x) * v2
  return v

def load_ground_truth(index,files):
  img_data = np.load(files[index])
  img = img_data['data']
  return np.expand_dims(img, axis=2)*255


