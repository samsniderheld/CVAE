#!/bin/bash
rm ../../Results/GeneratedVideos/reconstruction.mp4

python3 test_reconstructions.py

ffmpeg -r 30 -f image2 -s 1024x512 -i ../../Results/GeneratedReconstructionFrames/image%04d.png  -vcodec libx264 -crf 25  -pix_fmt yuv420p ../../Results/GeneratedVideos/reconstruction.mp4
