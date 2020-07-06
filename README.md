
# Remixing Motion Capture Data With Conditional Variational Autoencoders

![A Reconstructed Animation](/Imgs/reconstruction.gif)

This repo is a bare bones demonstration of the code that was used to make our machine learning based animation videos.

It includes a basic unity project that can be used to generated depth data samples and render neural network output, a tensorflow.keras implementation of our CVAE, and basic neural network generation code.

The licensing on the motioncapture data we used in this project does not allow for redistribution, and is not included here.

Included is some toy data intended to show how the neural network works, but can not be used to train a successful neural network though. It can be used to generate animation samples though.

A write up of the project can be found here: 

# Unity Project

The Unity project is setup into two separate scenes, one for data generation and one for rendering the generated animations.

The data generation sample code is very basic. It generates depth images for a rotating cube. This is because none of the motion capture data we used was licensed for redistribution.

The rendering scene shows a basic point cloud approach to rendering the neural network output, and features a basic follow cam functionality.

# Python Code

The python code demonstrates the data processing functionalities, the CVAE model, and basic animation generation. 

# Python Installation

    $ git clone https://github.com/samsniderheld/CVAE
    $ cd CVAE/Python
    $ sudo pip3 install -r requirements.txt




