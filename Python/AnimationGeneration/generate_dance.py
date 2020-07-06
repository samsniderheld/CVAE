import argparse
from tqdm import tqdm
import numpy as np
import librosa
import os
import shutil
import glob
from tensorflow.keras.models import load_model
import cv2
import random
import sys
sys.path.append("..")
from config import ConfigOptions
from Utils.image_sampling import load_vector, generate_frame, interpolate, load_centroid, get_interim_centroid, get_closest_centroid_index

if os.path.exists("../../Results/GeneratedDanceFrames"):
  shutil.rmtree("../../Results/GeneratedDanceFrames")
  os.makedirs('../../Results/GeneratedDanceFrames')
else:
  os.makedirs('../../Results/GeneratedDanceFrames')


parser = argparse.ArgumentParser()
parser.add_argument('--tracked_onset_cutoff', type=float, default=.25)
parser.add_argument('--copied_frames_segment_modulus', type=int, default=2)
parser.add_argument('--minimum_copy_frames_thresh', type=int, default=20)
parser.add_argument('--copy_framerate_multiplier', type=int, default= 2)
parser.add_argument('--lerped_midpoint_search_modulus', type=int, default=60)
parser.add_argument('--framerate', type=int, default=100)
parser.add_argument('--model', type=int, default=55)
parser.add_argument('--number_subdivisions', type=int, default=0)

args = parser.parse_args()


#audio parameters
tracked_onset_cutoff = args.tracked_onset_cutoff

#copied sections parameters
copied_frames_segment_modulus = args.copied_frames_segment_modulus
minimum_copy_frames_thresh = args.minimum_copy_frames_thresh
copy_framerate_multiplier = args.copy_framerate_multiplier

#lerped section parameters
lerped_midpoint_search_modulus = args.lerped_midpoint_search_modulus

#global paramters
framerate = args.framerate

number_subdivisions = args.number_subdivisions

#load configs
config = ConfigOptions()

model_dir = config.out_model_dir

encoder = load_model("../"+ model_dir + "ConditionalVAEEncoderDance_epoch_{}.h5".format(args.model))
decoder = load_model("../"+ model_dir + "ConditionalVAEDecoderDance_epoch_{}.h5".format(args.model))

audio_path = config.track

data_dir = "../../Data/NumpyDataDepth/{}/*.npz".format(config.img_dim)
files = sorted(glob.glob(data_dir))

con_dir = "../../Data/NumpyDataDepth/Centroids/*.npz"
con_files = sorted(glob.glob(con_dir))



#analyze track and get list of times where beats occur
y, sr = librosa.load(audio_path)

o_env = librosa.onset.onset_strength(y, sr=sr)
times = librosa.times_like(o_env, sr=sr)
onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)

onset_times = times[onset_frames]
onset_vals = o_env[onset_frames]
kept_onset_idxs = np.argwhere(onset_vals > tracked_onset_cutoff)

final_times = onset_times[kept_onset_idxs]
final_onset_vals = onset_vals[kept_onset_idxs]

num_seconds = librosa.get_duration(y=y, sr=sr)

num_frames = num_seconds * framerate

final_times = np.insert(final_times,0,0, axis=0)

final_times = np.insert(final_times,len(final_times),num_seconds,axis=0)


# generate random indices array and calculate all number of frames to generate
num_frames_array = [int((final_times[i] - final_times[i-1]) * framerate) for i in range(1,len(final_times))]


#fix rounded frames issue, by adding remainder frames periodically
frames_behind = 0
for i in range(1,len(final_times)):
  rounded = num_frames_array[i-1]
  real =  (final_times[i] - final_times[i-1])*framerate
  lost_frames = real-rounded
  frames_behind = (frames_behind + lost_frames)
  if(frames_behind>1):
    num_frames_array[i-1]+=1
    frames_behind-=1

#making sure we don't get any index out of range errors for our toy dataset
indices = [random.randrange(0,500) for i in range(0,len(final_times))]

generated_frames = []

#generate all the frames
for i in tqdm(range(1,len(final_times))):

	v1 = load_vector(indices[i],files,con_files,encoder,config.img_dim)
	v2 = load_vector(indices[i-1],files,con_files,encoder,config.img_dim)

	num_frames_to_gen = num_frames_array[i-1]

	#if this is a section that we copy and it is above the min number of copy frames
	if(i % copied_frames_segment_modulus == 0 and num_frames_to_gen > minimum_copy_frames_thresh):

		#figure out the number of frames we want to lerp to smoothout transitions
		lerp_frames = int(num_frames_to_gen/4)

		for j in range(0, num_frames_to_gen-lerp_frames):

			next_index = indices[i-1]+(j*copy_framerate_multiplier)

			# todo fix index out of range bug here
			completion_vector = load_vector(next_index,files,con_files,encoder,config.img_dim)

			frame = generate_frame(completion_vector,decoder,config.latent_size)

			generated_frames.append(frame)
			

		v2 = load_vector(next_index,files,con_files,encoder,config.img_dim)

		#lerp out of copied set
		for x in list(np.linspace(0, 1,lerp_frames)):

			new_vector = interpolate(v1,v2,x)

			frame = generate_frame(new_vector,decoder,config.latent_size)

			generated_frames.append(frame)
			
	else:

		#else to generate frames from scratch with lerped interim vectors
		#if we want we can break up the interpolation insterting know vectors into the lerp
		centroid_1 = load_centroid(indices[i], con_files)
		centroid_2 = load_centroid(indices[i-1], con_files)

		all_subdivided_centroids = []

		all_subdivided_centroids.append(centroid_2)
		all_subdivided_centroids.append(centroid_1)
		

		for j in range(0,number_subdivisions):
			all_subdivided_centroids_length = len(all_subdivided_centroids)-1
			for k in range(0,all_subdivided_centroids_length):
				new_subdivided_centroid = get_interim_centroid(all_subdivided_centroids[k],all_subdivided_centroids[k+1])
				all_subdivided_centroids.insert(k+1,new_subdivided_centroid)

		all_vectors = []

		start_vector = load_vector(indices[i-1],files,con_files,encoder,config.img_dim)
		all_vectors.append(start_vector)

		for j in range(1, len(all_subdivided_centroids)-1):
			new_closest_index = get_closest_centroid_index(all_subdivided_centroids[j], con_files,lerped_midpoint_search_modulus)
			new_interim_vector = load_vector(new_closest_index,files,con_files,encoder,config.img_dim)
			all_vectors.append(new_interim_vector)

		end_vector = load_vector(indices[i],files,con_files,encoder,config.img_dim)
		all_vectors.append(end_vector)

		num_interim_frames = int(num_frames_to_gen/2**number_subdivisions)

		lost_frames = num_frames_to_gen - (num_interim_frames * 2**number_subdivisions)

		for j in range(1,len(all_vectors)):

			v1 = all_vectors[j]
			v2 = all_vectors[j-1]

			#add lost frame into last section
			if(j == len(all_vectors)-1):

				for x in list(np.linspace(0, 1,num_interim_frames+lost_frames)):

					new_vector = interpolate(v1,v2,x)

					frame = generate_frame(new_vector,decoder,config.latent_size)

					generated_frames.append(frame)
					


			else:

				for x in list(np.linspace(0, 1,num_interim_frames)):

					new_vector = interpolate(v1,v2,x)

					frame = generate_frame(new_vector,decoder,config.latent_size)

					generated_frames.append(frame)
					


for i in range(0,len(generated_frames)):

	cv2.imwrite('../../Results/GeneratedDanceFrames/image{}.png'.format('%04d'%i), generated_frames[i])


	