from Model.vae import conditional_vae
from Utils.data_generator import ConditionalDataGenerator
from Utils.image_sampling import create_conditional_sample_pic, print_test_pic
from config import ConfigOptions


#define hyperparameters
config = ConfigOptions()
latent_size = config.latent_size
beta = config.beta
img_dim = config.img_dim
batch_size = config.batch_size
epochs = config.epochs
data_dir = config.data_dir
out_dir = config.out_dir
normal_dims = config.normal_dims
kernal_size = config.kernal_size
model_dir = config.out_model_dir

print_test_pic(data_dir,out_dir,img_dim)

encoder, decoder, vae_model = conditional_vae(latent_size,img_dim,kernal_size,beta)

generator = ConditionalDataGenerator(dir=data_dir,dims=img_dim,batch_size=batch_size,shuffle=True)

for j in range(0,epochs):
	print("training epoch {}".format(j))
	vae_model.fit_generator(generator, epochs=1, shuffle=True)
	create_conditional_sample_pic(img_dim,j,encoder,decoder,data_dir,out_dir)
	if(config.save_model):
		encoder.save(model_dir + "ConditionalVAEEncoderDance_epoch_{}.h5".format(j))
		decoder.save(model_dir + "ConditionalVAEDecoderDance_epoch_{}.h5".format(j))
	generator.on_epoch_end()


