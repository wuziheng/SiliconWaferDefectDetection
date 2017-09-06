# SiliconWafer DefectDetection

Python implemetation of siliconwafer defectdetecion algorithm prototype, wrapper of some designed cv2 method. Now includes pixel level border locate and crack detection. Further more detection will be added such as droplets/dirty

Contributions Welcome

### Functions 
#
* ***Border locate***:  according to characteristic of siliconwafer samples and cv2.findContours method, perform a fast pixel border locate of sample. result can be used by other operation. 

* ***Slice***:  along the border(below), slice the sample(4kx4k) into suitable size for further detection, it can also be regard as calibration. the slices are classified in to three type according to their different characteristic: border,inner,corner 

* ***Crack detection***: using adaptive threshold and  closed operation and grow method to detect the crack defection. 


### Notes
#
* This is a prototype of siliconwafer defectdetcion algorithm, now only includes location and crack detecion, futher will add droplet/dirty/
In order to debug, lots of logging and datetime are used.(using at first time)
Welcome suggesion and contribution!
