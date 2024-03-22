from operator import not_
from unicodedata import decimal
import cv2
from object_detector import *
import numpy as np
from math import dist
#from background_detector import HomogeneousBgDetector
from collections import namedtuple
# Reading an excel file using Python
import xlrd
#import easygui
import json

from http import client
#import paho.mqtt.client as mqtt

camera_id = 1
resolution_setting = 1  # 0 = 640x480    # 1 = 1920x1080 (2.1MPx)   # 3 = 12MPx
grid = False
real_aruco_perimeter = 192 #604  # 15.1 cm aruco marker #  192 #240  # aruco marker perimiter
resolution_x = 640
resolution_y = 480
scale_percent = 50  #50 for 1920x1080 # percent of original size
centre_square_side = 100


#ruler test data:
start_offset = 0
startx = 1850   #1843 + 3.5564934938948674*start_offset
starty = 1150 #960
ruler_test_length_mm = 151 - start_offset

ax = 2040
ay = 1820
bx = 3690
by = 1820
ab_length_mm= 372


cx = 3980
cy = 900
dx = cx
dy = 1820
cd_length_mm= 135

#static_img_path = "testimg/fr473-1-lowlight-2.1mp.jpg"
#static_img_path = "testimg/fr473-normallight-2.1mp.jpg"
#static_img_path = "testimg/fr473-12mp-2.jpg"
#static_img_path = "testimg/fr473-12mp-6.jpg"
static_img_path = "F:\\Vs Code\\images\\CMM_Machine_Psuedo.jpeg"
#static_img_path = "testimg/IMG_6097.png"

mouseX = 0
mouse = 0


known_focal_length_1080Q  = 490   #507 #490 # 490 at 640x480   #680   # 680 for 1080p red-dragon webcam # 480 for manual focus 1080p quantum webcam
KNOWN_WIDTH               = real_aruco_perimeter
KNOWN_DISTANCE  = 1165    #1000      # mm # to calculate focal length

dist_to_marker = 0

aruco_detected = False

box_colors = [(0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0), (120, 120, 120), (255, 255, 255), (120, 120, 120), (255, 255, 255),(0, 255, 0),(0, 255, 0),(0, 255, 0),(0, 255, 0)]

# values from measurements
measurement = {"dimid":"-1", "nom":0.000, "actual":0.000}
report_list = []

# # mqtt stuff
# client = mqtt.Client('mvcmm')

# # The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))

#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("ind40demo/ccmv/cmm/cmd")

# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic + " " + str(msg.payload))
#     #mqttSend(47.5, 104.2)

# def mqttSend(jsn):
#     #message = '{"id":"FR73"' + '"AB":' + str(dim1) + ',"CD":' + str(dim2) + '}'
#     client.publish("ind40demmo/ccmv/cmm/scandata", jsn)

# def mqttConnect():
#     client.connect("dev.coppercloud.in", 1883)
#     client.on_connect = on_connect
#     client.on_message = on_message
#     #client.loop_forever()

def mouse_click(event,x,y,flags,param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDOWN:  #DBLCLK:
        mouseX,mouseY = x,y


def setup_square(img):
  cv2.rectangle(img, (10, 10), (250, 100), (255, 255, 255), 2)
  cv2.putText(img, 'Marker Alignment: OK', (12, 30), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 1)
  cv2.putText(img, 'Distance: OK', (12, 60), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 1)
  cv2.putText(img, 'View Angle: OK', (12, 90), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 1)
  return img

def draw_centre_square(img, color=1, width=640, height=480, side=100):
  cent_x = int(resolution_x/2)
  cent_y = int(resolution_y/2)
  size =   int(centre_square_side/2)

  cv2.rectangle(img, (cent_x-size, cent_y-size), (cent_x+size, cent_y+size), box_colors[int(color)], 4)
  
  if camera_id != -1:   # show distance to camera only for live feed
    cv2.putText(img, "Distance: {} mm".format(round(dist_to_marker, 2)), (12, 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
  
  return img


def draw_grid(img, grid_shape=(16,16), color=(100, 100, 100), thickness=1):
    h, w, _ = img.shape
    rows, cols = grid_shape
    dy, dx = h / rows, w / cols

    # draw vertical lines
    for x in np.linspace(start=dx, stop=w-dx, num=cols-1):
        x = int(round(x))
        cv2.line(img, (x, 0), (x, h), color=color, thickness=thickness)
        cv2.putText(img, "{}".format(x), (x-10, 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    # draw horizontal lines
    for y in np.linspace(start=dy, stop=h-dy, num=rows-1):
        y = int(round(y))
        cv2.line(img, (0, y), (w, y), color=color, thickness=thickness)
        cv2.putText(img, "{}".format(y), (10, y+5), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)


    return img

# Give the location of the file
# press 'r' to reload config in the middle of a run
#loc = easygui.fileopenbox()
loc = "F:\\Vs Code\\CMM_Major_Project\\roi_config_main.xls"
print(loc)
#loc = ('C:\\prodconfig\\roiconfig.xls')

# To open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

region = namedtuple('region', ['x1', 'y1', 'x2', 'y2'])
#roi1 = region(400, 100, 600, 300)
#roi2 = region(100, 250, 300, 450)

def reloadConfig():
  global wb, sheet
  wb = xlrd.open_workbook(loc)
  sheet = wb.sheet_by_index(0)
  print('reloaded data from config excel')

# Load Aruco detector
parameters = cv2.aruco.DetectorParameters()
#aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_100)
aruco_dict =  cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)

# Load Object Detector
detector = cv2.bgsegm.createBackgroundSubtractorMOG() #HomogeneousBgDetector()
params = cv2.SimpleBlobDetector_Params()

# blob detection parameters -
# Change thresholds
params.minThreshold = 100
params.maxThreshold = 255

# Filter by Area.
params.filterByArea = True
params.minArea = 100

# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.4
# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.8
# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.5

#mqttConnect()

# Create a detector with the parameters
#cap = cv2.VideoCapture(0)                # slow cam loading

#if camera_id != -1:
cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)  # fast cam loading

# get the current resolution
#img = cap.read()  #read immage from camera
#print('shape: '+ img.shape)

if camera_id == -1:
  resolution_x = 1920 #4272   #1920
  resolution_y = 1080 #2848   #1080
  centre_square_side = 200  #600   #200 for 1920x1080

else:
  #*****************************************#
  # to change resolution
  if resolution_setting == 1:
    print("selected res: 1920x1280")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    known_focal_length_1080Q  = 1115    #1150  #1127    #1115 #1115 at 1920x1080 #490
    scale_percent = 50 # percent of original size
    centre_square_side = 200
    resolution_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    resolution_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

  # if resolution_setting == 2:
  #   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
  #   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
  #   known_focal_length_1080Q  = 1115 #1115 at 1920x1080 #490
  #   scale_percent = 50 # percent of original size
  #   centre_square_side = 200
  #   resolution_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
  #   resolution_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
  #*****************************************#


aruco_x1 = int(resolution_x/2 - centre_square_side/2)
aruco_y1 = int(resolution_y/2 - centre_square_side/2)
aruco_x2 = int(resolution_x/2 + centre_square_side/2)
aruco_y2 = int(resolution_y/2 + centre_square_side/2)

# print resolution
print(resolution_x)
print(resolution_y)


while True:
    if camera_id == -1:
      img = cv2.imread(static_img_path)
    else:
      _, img = cap.read()  #read immage from camera

    # cv2.imshow("img", img)
      # key = cv2.waitKey(0)
      
    aruco_roi = img[(aruco_y1):(aruco_y2), (aruco_x1):(aruco_x2)]
    #img = cv2.circle(img, (int(startx), int(starty)), 4, (0,0,200), 2)

    # cv2.rectangle(img, (aruco_x1, aruco_y1),(aruco_x2, aruco_y2), (255, 0, 0), 10)

    corners, _, _ = cv2.aruco.detectMarkers(aruco_roi, aruco_dict, parameters=parameters)
    #print(corners)

    if corners:
        report_list.clear() # report entry - clear report list
        # draw green centre square to indicate that marker alignment is proper
        img = draw_centre_square(img, 2)

        # Draw polygon around the marker
        int_corners = np.int0(corners)
        #cv2.polylines(img, int_corners, True, (0, 255, 0), 2, lineType=cv2.LINE_AA)

        # Aruco Perimeter
        px_aruco_perimeter = cv2.arcLength(corners[0], True)
        
        # print distance to marker
        # the focal length
        # focalLength = (px_aruco_perimeter * KNOWN_DISTANCE) / KNOWN_WIDTH
        # print("focal length:")
        # print(focalLength)
        # quit()

        dist_to_marker = (known_focal_length_1080Q * KNOWN_WIDTH) / px_aruco_perimeter

        # Pixel to cm ratio - this allows the code to calculate actual size of object
        # no matter how far it is from the camera lens
        pixel_mm_ratio = px_aruco_perimeter / real_aruco_perimeter   #get px per mm ratio  # because perimeter of aruco marker is 240 mm +/-
        #print("ppmm:" + str(pixel_mm_ratio))

        # ruler line:
        #img = cv2.circle(img, (int(startx), int(starty)), 3, (0,0,200), 2)
        ruler_length_px = ruler_test_length_mm * pixel_mm_ratio
        img = cv2.line(img, (int(startx),int(starty+20)), (int(startx),int(starty-20)), (0,0,200), 1, lineType=cv2.LINE_AA)
        img = cv2.line(img, (int(startx),int(starty)), (int(startx+ruler_length_px),int(starty)), (0,0,200), 1, lineType=cv2.LINE_AA)
        img = cv2.line(img, (int(startx+ruler_length_px),int(starty+20)), (int(startx+ruler_length_px),int(starty-20)), (0,0,200), 1, lineType=cv2.LINE_AA)

        ab_length_px = 1323   #px #ab_length_mm * pixel_mm_ratio
        img = cv2.line(img, (int(ax),int(ay+20)), (int(ax),int(ay-20)), (0,0,200), 1, lineType=cv2.LINE_AA)
        img = cv2.line(img, (int(ax),int(ay)), (int(ax+ab_length_px),int(ay-20)), (0,0,200), 1, lineType=cv2.LINE_AA)
        img = cv2.line(img, (int(ax+ab_length_px),int(ay+20)), (int(ax+ab_length_px),int(ay-20)), (0,0,200), 1, lineType=cv2.LINE_AA)

        cd_length_px = cd_length_mm * pixel_mm_ratio
        img = cv2.line(img, (int(cx+20),int(cy)), (int(cx-20),int(cy)), (0,0,200), 1, lineType=cv2.LINE_AA)
        img = cv2.line(img, (int(cx),int(cy)), (int(cx),int(cy+cd_length_px)), (0,0,200), 1, lineType=cv2.LINE_AA)
        img = cv2.line(img, (int(cx+20),int(cy+cd_length_px)), (int(cx-20),int(cy+cd_length_px)), (0,0,200), 1, lineType=cv2.LINE_AA)



        im = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # light background of blobs

        #****************************************************
        # following 3-4 lines for dark background of blobs:
        # gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # blur = cv2.GaussianBlur(gray,(5,5),0)
        # ret3, im = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #keypoints_1 = detector_1.detect(th3) # th3 = im
        #****************************************************
        
        detector_1 = cv2.SimpleBlobDetector_create(params)

        for i in range(1, sheet.nrows):
          # hardcoded roi coords
          active = sheet.cell_value(i, 11)
          if active == 'y':
            dimid = sheet.cell_value(i, 0)

            roi1 = region(sheet.cell_value(i, 1), sheet.cell_value(i, 2), sheet.cell_value(i, 3), sheet.cell_value(i, 4))
            roi2 = region(sheet.cell_value(i, 5), sheet.cell_value(i, 6), sheet.cell_value(i, 7), sheet.cell_value(i, 8))
            nom = sheet.cell_value(i, 9)

            roi_1 = im[int(roi1.y1):int(roi1.y2),int(roi1.x1):int(roi1.x2)]
            roi_2 = im[int(roi2.y1):int(roi2.y2),int(roi2.x1):int(roi2.x2)]

            img = cv2.rectangle(img, (int(roi1.x1), int(roi1.y1)), (int(roi1.x2), int(roi1.y2)), box_colors[int(dimid)], 2)
            img = cv2.rectangle(img, (int(roi2.x1), int(roi2.y1)), (int(roi2.x2), int(roi2.y2)), box_colors[int(dimid)], 2)
            cv2.putText(img, "{}".format(int(dimid)), (int(roi1.x1), int(roi1.y1-10)), cv2.FONT_HERSHEY_PLAIN, 1.5, box_colors[int(dimid)], 2)
            cv2.putText(img, "{}".format(int(dimid)), (int(roi2.x1), int(roi2.y1-10)), cv2.FONT_HERSHEY_PLAIN, 1.5, box_colors[int(dimid)], 2)
            #cv2.imshow("img", img)
          #### --- tabbing shifted to be under if - start
            # find blobs in roi1
            keypoints_1 = detector_1.detect(roi_1)
            number_of_blobs_1 = len(keypoints_1)

            # find blobs in roi2  
            detector_2 = cv2.SimpleBlobDetector_create(params)
            keypoints_2 = detector_2.detect(roi_2)
            number_of_blobs_2 = len(keypoints_2)

            if (number_of_blobs_1 > 0) and (number_of_blobs_2 > 0):
              x1= keypoints_1[0].pt[0]+roi1.x1
              y1= keypoints_1[0].pt[1]+roi1.y1
              x2= keypoints_2[0].pt[0]+roi2.x1
              y2= keypoints_2[0].pt[1]+roi2.y1

              distance= dist([x1,y1],[x2,y2])
              distance= distance/ pixel_mm_ratio
              img = cv2.circle(img, (int(x1), int(y1)), 3, (255,0,200), 2)
              img = cv2.circle(img, (int(x2), int(y2)), 3, (255,0,200), 2)
              img = cv2.line(img, (int(x1),int(y1)), (int(x2),int(y2)), (255,0,200), 2, lineType=cv2.LINE_AA)
              cv2.putText(img, "{} mm".format(round(distance, 2)), (int((x2+x1)/2-50), int((y2+y1)/2)), cv2.FONT_HERSHEY_PLAIN, 2, (0, 100, 255), 3)
              cv2.putText(img, "nom {} mm, act {} mm".format(nom, round(distance, 2)), (int(roi1.x1+20), int(roi1.y1-10)), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

              measurement['dimid'] = sheet.cell_value(i, 0) # report entry
              measurement['nom'] = sheet.cell_value(i, 9) # report entry
              measurement['actual'] = distance # report entry
              report_list.append(measurement.copy()) # report entry - add to report list
              #print('adding record:' + str(i))
          #### --- tabbing shifted to be under if - end

    else:
      dist_to_marker = 0
      img = draw_centre_square(img, 1)

    #draw the final image
    #img = setup_square(img)
    if grid:
      img = draw_grid(img)    # draw the grid

    # final step - resize image to fit screen
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img_resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    cv2.imshow("img", img_resized)
    cv2.setMouseCallback('img', mouse_click)

    # if camera_id == -1:   # static image - no need to read camera in a loop
    #    break
    
    key = cv2.waitKey(1)

    if key == ord('r'):   #key == 114:
      reloadConfig()

    if key == ord('g'):
      grid = not grid

    if key == ord('s'):
      print("report list =", report_list)
      json_report = json.dumps(report_list)
      print("json =", json_report)
      #mqttSend(json_report)

    if key == ord('m'):
      print(mouseX, mouseY)

    if key == ord('f'):
      cv2.imwrite("./results/result.png", img)

    if key == 27:
      break
    #break

# if camera_id == -1:
#   key = cv2.waitKey(0)

cap.release()
cv2.destroyAllWindows()

wb.release_resources()
del wb