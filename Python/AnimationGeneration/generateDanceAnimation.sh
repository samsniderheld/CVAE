#!/bin/bash
rm ../../Results/GeneratedVideos/dance.mp4

python3 generate_dance.py --framerate=30 --tracked_onset_cutoff=.15 --copied_frames_segment_modulus=2 --minimum_copy_frames_thresh=20 --copy_framerate_multiplier=1 --lerped_midpoint_search_modulus=1000 --model=55


ffmpeg -r 30 -f image2 -s 512x512 -i ../../Results/GeneratedDanceFrames/image%04d.png -i ../../Music/chopinNocturne.mp3 -vcodec libx264 -crf 25  -pix_fmt yuv420p ../../Results/GeneratedVideos/dance.mp4


