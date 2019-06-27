# -*- coding: cp1252 -*-

import time
import argparse
import math
import almath
import motion
from naoqi import ALProxy

#Robot configuration
try:
    IP = input("Enter robot IP between simple quote: ")
except: #If nothing than connect to local robot
    IP = 'localhost'
try:
    PORT = input("Enter robot PORT:")
except: #If nothing than connect to default PORT
    PORT = 9559

FRAME_TORSO = 0
FRAME_ROBOT = 2
currentCamera = "CameraBottom"

motionProxy = ALProxy("ALMotion", IP, PORT)
tracker = ALProxy("ALTracker", IP, PORT)
posture = ALProxy("ALRobotPosture", IP, PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)
landmarkProxy = ALProxy("ALLandMarkDetection", IP, PORT)
video = ALProxy("ALVideoDevice", IP, PORT)
setcam = video.setActiveCamera(1) #Set bottom camera


#----------------Aux Programs


def head(motionProxy): # set Head position that best sees the environment
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([1.0])
    keys.append([math.radians(-14)])

    motionProxy.angleInterpolation(names, keys, times, True)


#landmark
def getMarkId():
    landmarkTheoreticalSize = 0.09  # LandMark size in meters
    # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
    landmarkProxy.subscribe("landmarkTest")
    markId = None
    # Wait for a mark to be detected.
    markData = memoryProxy.getData("LandmarkDetected")
    if (markData is None or len(markData) == 0):
        markId = None
    else:
        markInfoArray = markData[1]
        for markInfo in markInfoArray:
            markShapeInfo = markInfo[0]
            markExtraInfo = markInfo[1]
            alpha = markShapeInfo[1]
            beta = markShapeInfo[2]
            print "mark  ID: %d" % (markExtraInfo[0])
            markId = markExtraInfo[0]

    return markId

def searchLandmark(motionProxy):
    motionProxy.setMoveArmsEnabled(False, False)
    while True:
       markId = getMarkId() #Check if any mark is seen
       if markId == None:
           print("searching.........")
           motionProxy.moveTo(0.0, 0.0, math.pi / 8) #If not, rotate robot 180/8 degrees
           time.sleep(1)
       else:
           break
    return markId

def find(x): #find specific mark X
    posture.goToPosture("StandInit", 1.0)
    head(motionProxy)
    time.sleep(1)
    argu = x
    markId = None
    while True:
        markId = searchLandmark(motionProxy) #Find any mark
        if markId != argu: #If found mark is not X
            pass
        else:
            break
    print markId,"was found"
    return markId

def goto(x): #Find and go to specific mark
    mark = x
    find(mark)
    landmarkTheoreticalSize = 0.09
    if mark % 2 == 1: #If mark is odd
        targetdistance = 0.38
    if mark % 2 == 0: #If mark is even
        targetdistance = 0.19
    targetName = "LandMark"
    tracker.registerTarget(targetName, [landmarkTheoreticalSize, [mark]])
    mode = "Move" #set move mode in mark tracking
    tracker.setMode(mode)
    tracker.track(targetName)
    too_far = True
    tracker.toggleSearch(False)
    while too_far:
        position = tracker.getTargetPosition(FRAME_ROBOT) #Get target distance to robot
        if position != []:
            #Trig to get distance
            distance = math.sqrt(math.pow(position[0],2) + math.pow(position[1],2))
            if distance < targetdistance:
                too_far = False
                theta = math.atan2(distancey, distancex)
                tracker.stopTracker()
                tracker.unregisterAllTargets()
                print distance
                print "Tracker: Target reached"
    too_far=True
    time.sleep(1.0)

def checkvision(x): #Check if any mark is seen and return true or false
    mark = x
    test = getMarkId()
    if test != mark:
        return False
    if test == mark:
        return True
    
def handempty(): #Check if NAO robot is grasping on something with left hand
    handempty_threshold = 0.20 #Adjust hand tolerance
    motionProxy.setAngles("RHand", 0.0, 0.35)
    time.sleep(2.0)
    hand_angle = motionProxy.getAngles("LHand", True)
    if hand_angle[0] < handempty_threshold:
        result = True
        print("Nothing in my hand.")
    else:
        print("I detect something in my hand.")
        result = False
    return result

def batterylevel(): #Check robot battery
    batLevel = memoryProxy.getData('Device/SubDeviceList/Battery/Charge/Sensor/Value')
    return batLevel

def getwithlefthand(): #Pick up block with left hand
    posture.goToPosture("Crouch", 1.0)
    
    names = list()
    times = list()
    keys = list()

    names.append("LShoulderPitch")
    times.append([1.0, 2.0, 3.0, 5.0])
    keys.append([math.radians(-10), math.radians(-6.5), math.radians(7.6), math.radians(-40)])

    names.append("LShoulderRoll")
    times.append([1.0, 2.0, 3.0, 5.0])
    keys.append([math.radians(72.1), math.radians(-17.9), math.radians(-2.8), math.radians(40)])
   
    names.append("LElbowRoll")
    times.append([1.0, 2.0, 3.0])
    keys.append([math.radians(-87.3), math.radians(-20.8), math.radians(-56.7)])

    names.append("LHand")
    times.append([2.0, 4.0])
    keys.append([1, 0.0])
        
    names.append("LWristYaw")
    times.append([2.0, 3.0])
    keys.append([math.radians(22.9), math.radians(21.5)])

    names.append("LElbowYaw")
    times.append([2.0, 3.0])
    keys.append([math.radians(-40.1), math.radians(-24.5)])
    
    motionProxy.angleInterpolation(names, keys, times, True)

def get(): #Pick up block with both hands
    motion = ALProxy("ALMotion", IP, PORT)
    tracker = ALProxy("ALTracker", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)
    posture.goToPosture("Stand", 1.0)
    
    names = list()
    times = list()
    keys = list()

    names.append("LShoulderRoll")
    times.append([1.0, 2.0])
    keys.append([0.06, -0.20])

    names.append("LShoulderPitch")
    times.append([1.0,3.0])
    keys.append([0.75, 0.0])
    
    names.append("LElbowRoll")
    times.append([1.0])
    keys.append([-0.29])

    names.append("LElbowYaw")
    times.append([1.0])
    keys.append([-0.95])
    
    names.append("LWristYaw")
    times.append([1.0])
    keys.append([-0.04])

    names.append("LHand")
    times.append([1.0, 3.0])
    keys.append([1, 0.67])
    
    names.append("RShoulderRoll")
    times.append([1.0, 2.0])
    keys.append([-0.06, 0.20])

    names.append("RShoulderPitch")
    times.append([1.0, 3.0])
    keys.append([0.75, 0.0])
    
    names.append("RElbowRoll")
    times.append([1.0])
    keys.append([0.29])

    names.append("RElbowYaw")
    times.append([1.0])
    keys.append([0.95])
    
    names.append("RWristYaw")
    times.append([1.0])
    keys.append([0.04])

    names.append("RHand")
    times.append([1.0,3.0])
    keys.append([1,0.67])

    motion.angleInterpolation(names, keys, times, True)
    
def release(): #Release block with left hand
    names = list()
    times = list()
    keys = list()

    names.append("LShoulderPitch")
    times.append([2.0])
    keys.append([math.radians(28.8)])

    names.append("LShoulderRoll")
    times.append([2.0])
    keys.append([math.radians(32.3)])
   
    names.append("LHand")
    times.append([2.0])
    keys.append([1.0])

    motionProxy.angleInterpolation(names, keys, times, True)
    print "Block was released"

#---------------- Actions

def pickup(x):
    block = x
    while True: #While True check process while action is running
        visible = checkvision(block) #If block is visible
        if visible == True:
            checkbat = battery()
            if checkbat > 30: #If battery is higher than 30%
                goto(block)
                getwithlefthand()
                return 'endactivity(PICKUP)'
            else:
                return 'lowbattery()'
        else:
            return 'notvisible(%d)' % block
        break #Stop While loop
        

def put(x,y):
    while True:
        place = y
        block = x
        visible = checkvision(place)
        if visible == True: #If place is visible
            checkbat = battery()
            if checkbat > 30:
                checkhand = handempty()
                if checkhand == False: #If hand is not empty
                    goto(block)
                    release()
                    return 'endactivity(PUT)'
                else:
                    return 'lost(%d)' % block
            else:
                return 'lowbattery()'
        else:
            return 'notvisible(%d)' % place
        break
    
    
def putdown(x):
    block = x
    while True:
        checkbat = battery()
        if checkbat > 30:
            checkhand = handempty() #If hand is not empty
            if checkhand == False:
                release()
                return 'endactivity(PUTDOWN)'
            else:
                return 'lost(%d)' % block
        else:
            return 'lowbattery()'
        break
    
def rest():
    while True:
        checkhand = handempty()
        if checkhand == False: #Check if hand is not empty before resting
            release()
        tracker.stopTracker()
        tracker.unregisterAllTargets()
        posture.goToPosture("Crouch", 1.0)
        motionProxy.rest()
        return 'endactivity(REST)'
        break

def search(x):
    targ = x
    while True:
        checkbat = battery()
        if checkbat > 30:
            find(targ)
            return 'endactivity(SEARCH)'
        else:
            return 'lowbattery()'
        break
            

def remove(x,y):
    block = x
    place = y
    while True:
        visible = checkvision(place)
        if visible == True: #If place is visible
            visible = checkvision(block)
            if visible == True: #If block is visible
                checkbat = battery()
                if checkbat > 30:
                    goto(block)
                    getwithlefthand()
                    return 'endactivity(REMOVE)'
                else:
                    return 'lowbattery()'
            else:
                return 'notvisible(%d)' % block
        else:
            return 'notvisible(%d)' % place
        break
