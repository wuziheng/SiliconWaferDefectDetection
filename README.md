# CUDA version ISP

CUDA implemenation of paralleled Image signal process on Nvidia TegraX1.(Only include the image process part) , 59 fps for 4k(3840x1920) image input.

Olympus license. Contributions welcome

### Functions 
#
* ***Automatic exporsure***:  automatic modify gain coefficient of the input channel or modify the capture devices' exposure time 

* ***Automatic white balance***: automatic modify there channels gain to fit the image in to a white balance situation

* ***Gamma correct***: to correct the capture devices sensor's gamma effect

* ***Edge enhancement***: edge enhancement to sharp the curve detail,  strengthen the detail of image

* ***Format transform***: transform the input RAW(bayes_rggb) format into RGB format for screen show, transform RGB format into YUYV format for video encode

### Notes
#
* This code is only image process part for the whole project which aims to develop  a software integrated capture/image process/realtime display/video encode and transform/ on Nvidia TegraX1

* The repository also includes the serial version ISP which help to understand the code details. and some input test data.
