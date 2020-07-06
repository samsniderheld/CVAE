import numpy as np
import os
import shutil
import glob
from tensorflow.keras.models import load_model
import cv2
import random
import sys
sys.path.append("..")
from config import ConfigOptions
from Utils.image_sampling import load_vector, generate_frame, load_ground_truth



if os.path.exists("../../Results/GeneratedReconstructionFrames"):
  shutil.rmtree("../../Results/GeneratedReconstructionFrames")
  os.makedirs('../../Results/GeneratedReconstructionFrames')
else:
  os.makedirs('../../Results/GeneratedReconstructionFrames')



num_frames = 500


#load configs
config = ConfigOptions()

model_dir = config.out_model_dir

encoder = load_model("../"+ model_dir + "ConditionalVAEEncoderDance_epoch_{}.h5".format(config.epoch_for_gen))
decoder = load_model("../"+ model_dir + "ConditionalVAEDecoderDance_epoch_{}.h5".format(config.epoch_for_gen))

dat_dir = "../../Data/NumpyDataDepth/{}/*.npz".format(config.img_dim)
files = sorted(glob.glob(dat_dir))

con_dir = "../../Data/NumpyDataDepth/Centroids/*.npz"
con_files = sorted(glob.glob(con_dir))

generated_frames = []
ground_truth_frames = []

index = random.randrange(0,len(files)-num_frames)

for i in range(index,index+num_frames):

	vector = load_vector(i,files,con_files,encoder,config.img_dim)
	frame = generate_frame(vector,decoder,config.latent_size)
	generated_frames.append(frame)

	actual = load_ground_truth(i,files)
	ground_truth_frames.append(actual)

for i in range(0,len(generated_frames)):

	new_image = np.concatenate((generated_frames[i], ground_truth_frames[i]),axis=1)

	cv2.imwrite('../../Results/GeneratedReconstructionFrames/image{}.png'.format('%04d'%i), new_image)

