class ConfigOptions():
	def __init__(self):
		#define hyperparameters 
		self.latent_size = 128
		self.beta = 1
		self.img_dim = 256
		self.kernal_size = 3
		self.batch_size = 16
		self.epochs = 10
		self.raw_data_dir = "../Data/UnityOutput/"
		self.data_dir= "../Data/NumpyDataDepth/"
		self.out_dir= "../Results/VAE/TrainingImages/"
		self.out_model_dir = "../SavedModels/"
		self.epoch_for_gen = 55
		self.normal_dims = 5
		self.save_model = True
		self.track = '../../Music/chopinNocturne.mp3'

