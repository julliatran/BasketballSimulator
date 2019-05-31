from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import pygame
import sys
import math
import numpy
import os
import getopt
from socket import *
from pygame.locals import *

if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread
intro = True
splashScreen = True
endGame = False

'''
pygamegame.py
created by Lukas Peraza
 for 15-112 F15 Pygame Optional Lecture, 11/11/15
use this code in your term project if you want
- CITE IT
- you can modify it to your liking
  - BUT STILL CITE IT
- you should remove the print calls from any function you aren't using
- you might want to move the pygame.display.flip() to your redrawAll function,
    in case you don't need to update the entire display every frame (then you
    should use pygame.display.update(Rect) instead)
'''

#for loading the image
def load_png(name):
    fullname = os.path.join("C:\\Users\\vikra\Desktop\\Hack112",name)
    image = pygame.image.load(fullname)
    if image.get_alpha is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image, image.get_rect()
    
# colors for drawing different bodies 
SKELETON_COLORS = [pygame.color.THECOLORS["red"], 
                  pygame.color.THECOLORS["blue"], 
                  pygame.color.THECOLORS["green"], 
                  pygame.color.THECOLORS["orange"], 
                  pygame.color.THECOLORS["purple"], 
                  pygame.color.THECOLORS["yellow"], 
                  pygame.color.THECOLORS["violet"]]

def getJointPoint(jointPoints, joint):
        return (jointPoints[joint].x,jointPoints[joint].y)
splashScreen = True

joint_points = None

def handState():
    handR = getJointPoint(jointPoints, PyKinectV2.JointType_HandRight)
    handTip = getJointPoint(jointPoints, PyKinectV2.JointType_HandTipRight)
    thumb = getJointPoint(jointPoints, PyKinectV2.JointType_ThumbRight)

    distH = math.sqrt((handR[0]-handTip[0])**2 + (handR[1]-handTip[1])**2 )
    distT = math.sqrt((handR[0]-thumb[0])**2 + (handR[1]-thumb[1])**2 )
    #joints[]
    # print(PyKinectV2.HandRightState())

        
    if distH <= 30 and distT <= 25:
        handClosed = True
        pygame.draw.rect(self._frame_surface, color, (int(handR[0]), int(handR[1]), 100, 100))
    else:
        handClosed = False
    
def button(msg,x,y,w,h,ic,ac,surface, action):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
         pygame.draw.rect(surface, ac, (x,y,w,h))

         if click[0] == 1:
             action()
    else:
         pygame.draw.rect(surface, ic, (x,y,w,h))

    buttonFont = pygame.font.SysFont('Helvetica', 10)

    buttonSurface = buttonFont.render(msg, True, (255,255,255))
    buttonRect = buttonSurface.get_rect()
    buttonRect.center = ( (x + (w/2)), (y + (h/2)) )
    surface.blit(buttonSurface, buttonRect)

def quitGame():
    pygame.quit()


def startGame():
    global intro
    intro = False

def game_intro():

    global endGame
    endGame = True

    pygame.font.init()

    mouse = pygame.mouse.get_pos()
    myfont = pygame.font.SysFont('Helvetica', 40)

    clock = pygame.time.Clock()
    #pygame.mixer.music.load('music.mp3')
    #pygame.mixer.music.play()
    global intro
    while intro:

        keys = pygame.key.get_pressed()
        screen = pygame.display.set_mode((960, 540))
        pygame.display.set_caption("Test")
        
        
        textSurface = myfont.render('Kinect Ball Game', False, (0,0,0))
        background = pygame.Surface(screen.get_size())
        background.fill((255,255,255))

        
        textRect = textSurface.get_rect()
        textRect.center = (480,100)

        screen.blit(background, (0,0))
        screen.blit(textSurface,textRect)

        red = (200,0,0)
        blue = (0,0,200)
        brightBlue = (0,0,255)
        brightRed = (255,0,0)

        button("Play with Balls!", 150, 270, 270, 50, red, brightRed, screen, startGame, 10)
        button("Don't play with Balls :(", 550, 270, 270, 50, blue, brightBlue, screen, quitGame, 10)

        pygame.display.update()
        pygame.display.flip()
    splashScreen = False


class BodyGameRuntime(object):

    def init(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('ball4.png')
        self.ballcX = self.width//2
        self.ballcY = 0
        self.ballR = 75
        self.speedY = 0
        self.speedX = 0 
        self.bounces = 1

        self.basket, self.rect2 = load_png('basket.png')
        self.baskety1 = 150
        self.baskety2 = 350
        self.basketx1 = self.width - 200
        self.basketx2 = self.width
        self.scoredBasket = False
        self.score = 0
        self.countDown = 60
        self.maxTime = 60

        #cX = posX wrist +radius
        self.playercX = 250
        #CY = posY wrist + radius
        self.playercY = 250
        self.playerPrevcX = 250
        self.playerPrevcY = 250
        
        #radius = ((abs(posX tip of hand - posX wrist)**2+ abs(posY tip of Hand - posY wrist)**2)**1/2)//2
        self.playerR = 50
        
        self.playerVx = 0
        self.playerVy = 0
        self.ballInHand = False
        self.wasJustInHand = False
        
        #takes in bool value for self.closedHand
        self.closedHand = False
        
        self.time = 0
        self.startTime = self.time
        #change from self.height to feet position
        
        self.bottomOfScreen = self.height
        
    
    def isBallInHand(self):
        if(((self.ballcX-self.playercX)**2+(self.ballcY-self.playercY)**2)**0.5)<=(self.playerR + self.ballR):
            self.ballInHand =True
 

    def mouseMotion(self, x, y):
        self.playercX=x
        self.playercY=y
        pass

    def keyPressed(self, keyCode, modifier):
        #if pygame.K_SPACE:
        #    self.closedHand = not(self.closedHand)
        pass

    def keyReleased(self, keyCode, modifier):
        pass
    
    def bounceOfSides(self):
        if (self.ballcX+self.ballR)>=self.width or (self.ballcX-self.ballR)<=0:
            self.speedX = -int(0.1*self.speedX)
                
            
    def handVelocity(self):
        Vx = self.playercX-self.playerPrevcX
        Vy = self.playercY-self.playerPrevcY
        if Vx>0 or Vy>0:
            self.playerVx=Vx
            self.playerVy=Vy
        
        self.playerPrevcX = self.playercX
        self.playerPrevcY = self.playercY 

    def getBasket(self):
        if (self.basketx1-self.ballR<self.ballcX<=self.basketx2+self.ballR) and self.baskety1>=self.ballcY and self.scoredBasket==False:
            self.score+=1
            self.scoredBasket=True
        elif self.baskety1-20<=self.ballcY<=self.baskety1+20 and self.ballcX == self.basketx1:
            self.speedX = -self.speedX
        elif self.ballcY>=self.baskety2:
            self.scoredBasket = False


    def timerFired(self, dt):
        global endGame
        if self.countDown<=0:
            endGame = True
        
        #countDown timer
        self.countDown = self.maxTime - (self.time//1000)
        #finding the new velocity of the hand every millisec
        self.handVelocity()
        
        #cause it to bounce of sides of the screen
        self.bounceOfSides()

        #check if basket is being made
        self.getBasket()
        
        #time in millisecs
        self.time = pygame.time.get_ticks()
        
        #check if ball is in hand
        self.isBallInHand()
       
        #stops it from going too far out on the sides
        if self.ballcX>=self.width-self.ballR:
            self.ballcX = self.width-self.ballR
        elif self.ballcX<=self.ballR:
            self.ballcX = self.ballR
        
          
        totV = (self.playerVx**2 + self.playerVy**2 ) ** 0.5
        if totV < 35:
            self.closedHand = True
        else:
            self.closedHand = False
       
        
        if self.ballInHand and self.closedHand:
            self.ballcX = self.playercX
            self.ballcY = self.playercY
            
            #when the ball has been picked up it resets speed and bounce values
            self.bounces = 1
            self.speedY = 0
            self.speedX = 0
            
            self.startTime = self.time
            
            self.wasJustInHand = True
            
        elif self.wasJustInHand == True:
            self.speedX= self.playerVx 
            self.speedY= self.playerVy
            self.wasJustInHand = False
            
        elif self.ballcY>=self.bottomOfScreen-self.ballR:
            #stop ball at the bottom of the screen
            self.ballcY=self.bottomOfScreen-self.ballR
            
            #reset time for next free fall
            self.startTime = self.time
            
            self.ballInHand = False
            self.isBallInHand()

            #counts the number of bounces for halving the speed each bounce
            self.bounces+=1
            
            self.speedY //= ((2)*(self.bounces))
            self.speedX //= ((2)*(self.bounces))
            
            if self.speedY<1:
                self.speedY = 0
                
            if self.speedX<1:
                self.speedX = 0
            
            self.speedY = -(self.speedY)

        else:
            #free falling, 10 is used for gravity
            dTimeForAcceleration = (self.time-self.startTime)/1000
            if dTimeForAcceleration>0:
                self.speedY += int((dTimeForAcceleration)*10)
            self.ballInHand = False
            self.isBallInHand()
            
        
        #changes X and Y location based on speed in X and Y direction
        self.ballcY+=self.speedY
        self.ballcX+=self.speedX
       

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)
   
    def __init__(self, width=1920, height=1080, fps=60, title="112 Pygame Game"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (255, 255, 255)
        pygame.init()
    
        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect for Windows v2 Body Game")

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        
        # here we will store skeleton data 
        self._bodies = None

        self.bgColor = (255, 255, 255)


  
                      
                      
    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):

        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked): 
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good 
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        
        try:
            pygame.draw.circle(self._frame_surface, color , (int(jointPoints[joint1].x), int(jointPoints[joint1].y)), 5 )
            pygame.draw.line(self._frame_surface, color, start, end, 8)
        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);
    
        # Right Arm    
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight);

        handR = getJointPoint(jointPoints, PyKinectV2.JointType_HandRight)
        handTip = getJointPoint(jointPoints, PyKinectV2.JointType_HandTipRight)
        thumb = getJointPoint(jointPoints, PyKinectV2.JointType_ThumbRight)

        distH = math.sqrt((handR[0]-handTip[0])**2 + (handR[1]-handTip[1])**2 )
        distT = math.sqrt((handR[0]-thumb[0])**2 + (handR[1]-thumb[1])**2 )
        
       
        

        hX = int(getJointPoint(jointPoints, PyKinectV2.JointType_HandTipRight)[0])
        hY = int(getJointPoint(jointPoints, PyKinectV2.JointType_HandTipRight)[1])
        wX = int(getJointPoint(jointPoints, PyKinectV2.JointType_WristRight)[0])
        wY = int(getJointPoint(jointPoints, PyKinectV2.JointType_WristRight)[1])

        self.playerR = int(((abs(hX - wX)**2+ abs(hY - wY)**2)**(1/2))//2)
 
        #cX = posX wrist +radius
        self.playercX = wX + self.playerR
        #CY = posY wrist + radius
        self.playercY = wY  + self.playerR



        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft);

        # Right Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight);

        # Left Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft);
    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def run(self):
        clock = pygame.time.Clock()
        screen = self._screen
        pygame.display.set_caption(self.title)
        self._keys = dict()
        self.init()
        # -------- Main Program Loop -----------
        while not self._done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                    
            # --- Game logic should go here
            if splashScreen:
                 game_intro()


            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
             
                if (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
        
                elif event.type == pygame.QUIT:
                    playing = False

            # --- Getting frames and drawing  
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data 
            if endGame:
                pygame.quit()
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            # --- draw skeletons to _frame_surface

            if self._bodies is not None: 
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 
                    global joint_points
                    joints = body.joints 
                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.draw_body(joints, joint_points, SKELETON_COLORS[i])
           # pygame.draw.circle(self._frame_surface, (255,0,0), [self.playercX,self.playercY],self.playerR) 
            pygame.draw.circle(self._frame_surface, (0,0,255), [self.ballcX, self.ballcY], self.ballR)
            self._frame_surface.blit(self.image, (self.ballcX-self.ballR, self.ballcY-self.ballR))
            self._frame_surface.blit(self.basket, (self.basketx1, self.baskety1))
            pygame.font.init()
            myfont = pygame.font.SysFont('Arial',50)
            textsurface = myfont.render(("Score:"+str(self.score)),False, (0,0,0))
            textsurfaceTimer = myfont.render(("Time Left:"+str(self.countDown)),False,(0,0,0))
            self._frame_surface.blit(textsurface,(0,0))
            self._frame_surface.blit(textsurfaceTimer,(0,100))

            

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()
        
        
            
            

__main__ = "Kinect v2 Body Game"
game = BodyGameRuntime();
game.run();