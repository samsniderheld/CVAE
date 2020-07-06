from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Conv2DTranspose, Reshape, Flatten, BatchNormalization, Lambda, concatenate
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow.keras.losses import mse

#via https://keras.io/examples/variational_autoencoder/
def sampling(args):
    """Reparameterization trick by sampling fr an isotropic unit Gaussian.
    # Arguments
        args (tensor): mean and log of variance of Q(z|X)
    # Returns
        z (tensor): sampled latent vector
    """

    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean=0 and std=1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon


def conditional_vae(latent = 50, dims = 128, kernal_size = 3, beta = 1):

	#define model
	latent_size = latent

	original_dims = dims * dims

	input_shape = (dims,dims,1)

	#encoder input
	X = Input(shape=input_shape)
	cond = Input(shape = (2,))

	cond_layer = Dense(original_dims)(cond)
	# reshape to additional channel
	cond_img = Reshape((dims, dims, 1))(cond_layer)

	merge = concatenate([X,cond_img])


	#downsampling/encoder
	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(merge)
	x = BatchNormalization()(x)
	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = MaxPooling2D((2, 2), padding='same')(x)

	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = MaxPooling2D((2, 2), padding='same')(x)

	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = MaxPooling2D((2, 2), padding='same')(x)

	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = MaxPooling2D((2, 2), padding='same')(x)

	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x)
	x = BatchNormalization()(x)
	x = MaxPooling2D((2, 2), padding='same')(x)

	# get shape info for later
	shape = K.int_shape(x)


	#latent space vector
	x = Flatten()(x)
	z_mean = Dense(latent_size)(x)
	z_log_var = Dense(latent_size)(x)

	#z layer layer
	z = Lambda(sampling, output_shape=(latent_size,), name='z')([z_mean,z_log_var])
	z = concatenate([z,cond],axis=1)

	#instantiate encoder model
	encoder = Model([X,cond], [z_mean, z_log_var, z], name='encoder')
	encoder.summary()

	#decoder input
	latent_inputs = Input(shape=(latent_size+2,), name='z_sampling')

	# #upsampling/decoder
	x2 = Dense(shape[1] * shape[2] * shape[3])(latent_inputs)

	x2 = Reshape((shape[1], shape[2], shape[3]))(x2)

	#decoder layers
	x2 = Conv2D(1024, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2D(1024, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2DTranspose(8,(kernal_size, kernal_size), strides=(2, 2), padding='same')(x2)

	x2 = Conv2D(512, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2D(512, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2DTranspose(8,(kernal_size, kernal_size), strides=(2, 2), padding='same')(x2)

	x2 = Conv2D(256, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2D(256, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2DTranspose(8, (kernal_size, kernal_size), strides=(2, 2), padding='same')(x2)

	#extra for 256 dims
	x2 = Conv2D(128, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2D(128, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2DTranspose(8, (kernal_size, kernal_size), strides=(2, 2), padding='same')(x2)

	x2 = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2D(64, (kernal_size, kernal_size), activation='relu', padding='same')(x2)
	x2 = BatchNormalization()(x2)
	x2 = Conv2DTranspose(64, (kernal_size, kernal_size), strides=(2, 2), padding='same')(x2)


	decoder_outputs = Conv2D(1, (kernal_size, kernal_size), activation='sigmoid', padding='same')(x2)
	             
	# instantiate decoder model
	decoder = Model(latent_inputs, decoder_outputs, name='decoder')
	decoder.summary()
	             
	# instantiate VAE model
	outputs = decoder(encoder([X,cond])[2])

	vae = Model([X,cond], outputs, name='vae')

	#define losses
	reconstruction_loss = mse(K.flatten(X), K.flatten(outputs))
	reconstruction_loss *= dims * dims
	kl_loss = (1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)) * beta
	kl_loss = K.sum(kl_loss, axis=-1)
	kl_loss *= -0.5
	vae_loss = K.mean(reconstruction_loss + kl_loss)
	vae.add_loss(vae_loss)
	vae.compile(optimizer='adam')


	return  encoder, decoder, vae
