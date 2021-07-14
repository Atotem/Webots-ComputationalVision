# Author: Alberto Bella

# import modules
from controller import Robot, Display
from time import time
import numpy as np
import cv2
from skimage.transform import hough_line, hough_line_peaks # shapes
from skimage import measure # objects characteristics

#---Functions---
def Recognition(img, min, max):
    # all changes will be applied to a copy of the original image
    copy = img.copy()

    # identify color
    color_identified = False # default
    channels = [ch for ch in range(img.shape[2])] # range of third dim of image (channels)
    all_colors = ['red', 'green', 'blue'] # colors, in same order of the channels

    for channel in channels:
        colors = channels.copy()
        r_color = colors.pop(channel) # reference channel from reference color

        # for each RGB color/channel: (!) modify here for other colors
        if np.any((img[:, :, r_color] > min) & (img[:, :, r_color] < max) & (img[:, :, colors[0]] < 200) & (img[:, :, colors[1]] < 200)):
            # stay with the first recongized color
            color_identified = True
            color = all_colors[r_color]
            break

    if color_identified == False:
        return False

    # threshold: select range of color
    img_proc = np.where((copy[:, :, r_color] > min) & (copy[:, :, r_color] < max), copy[:, :, r_color], 0)
    ret, thresh = cv2.threshold(img_proc, 120, 255, cv2.THRESH_BINARY)

    # border of object
    B = cv2.Canny(img_proc, threshold1=min, threshold2=max)
    
    # exctract object characteristics for each
    all_labels = measure.label(thresh)
    region = measure.regionprops(label_image=all_labels)
    centroid = [round(region[0].centroid[0], 2), round(region[0].centroid[1], 2)]
    
    # calculate distance
    # (!) important: if bbox coord steps with screen borders
    # *(!) important: then re-calculate when area is greater,
    # ... then save the last distance (if it's behind an object)
    # **(!) fix: factor is missing, function is made based on specific size: 0.1
    # if vertical
    if np.any(np.array(region[0].bbox)[0] > 2 & np.array(region[0].bbox)[2] < (height - 2)):
        distance = int(np.array(region[0].bbox)[2] - np.array(region[0].bbox)[0])
        distance = round(distance_bbox(distance), 2)
    # if horizontal
    elif np.any(np.array(region[0].bbox)[1] > 2 & np.array(region[0].bbox)[3] < (width - 2)):
        distance = int(np.array(region[0].bbox)[3] - np.array(region[0].bbox)[1])
        distance = round(distance_bbox(distance), 2)
    
    # check shape
    # apply hough lines
    h, theta, d = hough_line(B, theta=angles)
    
    # extract max values from hough transform
    max_values = hough_line_peaks(h, theta, d)
    
    # if there is 'a lot' of max_values it's assumed is a circle
    if len(max_values[0]) > 16:
        shape = 'sphere'
    else:
        shape = 'cube'

    # update img: add red border
    copy[:, :, 0] = np.where(B == 255, 255, copy[:, :, 0])
    copy[:, :, 1] = np.where(B == 255, 0, copy[:, :, 1])
    copy[:, :, 2] = np.where(B == 255, 0, copy[:, :, 2])

    # print('shape: ', shape, ', distance: ', distance)
        
    return copy, centroid, shape, distance, color

def Foward(centroid):
    # move foward
    # align according to centroid inside margin (-5, +5)
    if (width/2) - 5 < centroid[0] < (width/2) + 5: # move foward
        r_Speed = 1.0
        l_Speed = 1.0
    elif (width/2) + 5 <= centroid[0] < (width - 10): # rotate to right, if it already made the turn, then continue rotating
        r_Speed = 1.0
        l_Speed = -1.0
    elif 10 < centroid[0] <= (width/2) - 5: # rotate to left, if it already made the turn, then continue rotating
        r_Speed = -1.0
        l_Speed = 1.0
    else:
        r_Speed, l_Speed = Rotate(1.0)

    return r_Speed, l_Speed

def Rotate(sense):
    r_Speed = 1.0 * (-1.0 * sense)
    l_Speed = 1.0 * ( 1.0 * sense)

    return r_Speed, l_Speed

# coordenates taken before to generate model based on regionprops bbox
# ... and actual distances from the object
coord = [[957.114, 880.314, 803.514], [36, 40, 42]]
coef = np.polyfit(coord[1], coord[0], 1)
distance_bbox = np.poly1d(coef) # (!) important

#---Setup---

TIME_STEP = 64
robot = Robot()

# initialize motors
# wheel1: top-right wheel
# wheel2: bottom-right wheel
# wheel3: top-left wheel
# wheel4: bottom-left wheel
wheels = []
wheelsNames = ['wheel1', 'wheel2', 'wheel3', 'wheel4']
for i in range(4):
    wheels.append(robot.getDevice(wheelsNames[i]))
    wheels[i].setPosition(float('inf'))
    wheels[i].setVelocity(0.0)
    
# initialize GPS
gps = robot.getDevice('gps')
gps.enable(TIME_STEP)

# initialize Compass
compass = robot.getDevice('compass')
compass.enable(TIME_STEP)

# initialize camara
camera = robot.getDevice('camera')
camera.enable(TIME_STEP)

# initialize display
display = robot.getDevice('display')

# initialize distance sensor
ds = robot.getDevice('distance sensor')
ds.enable(TIME_STEP)

# variables
r_Speed = 1.0
l_Speed = 1.0
t = time()
angles = np.linspace(-np.pi/2, np.pi/2, 360) # for hough lines

visited = [] # long list of all visited objects (shape and color)
previous = ['shape', 'color'] # the previous visited object
l = 0 # lenght of the list 'visited'

width = camera.getWidth()
height = camera.getHeight()

#---Loop---

while robot.step(TIME_STEP) != -1:
    # move robot
    # set speed to motors
    wheels[0].setVelocity(r_Speed)
    wheels[1].setVelocity(r_Speed)
    wheels[2].setVelocity(l_Speed)
    wheels[3].setVelocity(l_Speed)

    # recognition
    # get img data
    img = camera.getImageArray()
    img = np.array(img, np.uint8)

    # if there is no identified color, then gridsearch: rotate
    if Recognition(img, 205, 230) == False:
        r_Speed, l_Speed = Rotate(1.0) # -1.0: rotate to right; 1.0: rotate to left
    else: 
        img, centroid, shape, distance, color = Recognition(img, 205, 230)

        # if it hasn't been visited, the distance is less than 1500 and it's 'in front' of the robot, then mark the object
        # ... (when the robot makes a turn sometimes the shape changes too)
        if ([shape, color] != previous) and (distance < 1500) and ((width/2) - 5 < centroid[0] < (width/2) + 5):
            visited.append([shape, color])

        if distance > 1550:
            # take a look (if the object is distant, then the most probable shape is 'sphere')
            r_Speed, l_Speed = Foward(centroid)
        else:
            # if it has been visited, then make a turn
            if [shape, color] == previous:
                r_Speed, l_Speed = Rotate(1.0) # -1.0: rotate to right; 1.0: rotate to left
            # otherwise, continue and visit the object
            else:
                r_Speed, l_Speed = Foward(centroid)
        
    # out img in list format: necesary
    img = img.tolist()
        
    # display new image
    if img:
        ir = display.imageNew(img, Display.RGB, width, height)
        display.imagePaste(ir, 0, 0, False)
        display.imageDelete(ir)

    # print visited element
    if len(visited) > l:
        previous = visited[len(visited)-1]
        print('visited: ', previous)
        l = len(visited)
    
    # exit controller
    if (time() - t > 6*60.0): # after 6 minutes
    
        for wheel in wheels:
            wheel.setVelocity(0.0)
        
        print(round(time() - t, 2), '[s]')        
        break
    