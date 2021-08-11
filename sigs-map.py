import requests
import csv
import numpy as np
import matplotlib.pyplot as plt
import turtle
import time

yMin = 41.1890
yMax = 42.8941
xMin = -73.5287
xMax = -69.9033

yMinO = 41.1890
yMaxO = 42.8941
xMinO = -73.5287
xMaxO = -69.9033

zFact = .5

##yMin = yMinO + ((yMaxO - yMinO) * zFact)
##yMax = yMaxO - ((yMaxO - yMinO) * zFact)
##xMin = xMinO + ((xMaxO - xMinO) * zFact)
##xMax = xMaxO - ((xMaxO - xMinO) * zFact)


yMinG = yMin
yMaxG = yMax
xMinG = xMin
xMaxG = xMax

##yMinG = yMinO + ((yMaxO - yMinO) * zFact)
##yMaxG = yMaxO - ((yMaxO - yMinO) * zFact)
##xMinG = xMinO + ((xMaxO - xMinO) * zFact)
##xMaxG = xMaxO - ((xMaxO - xMinO) * zFact)

## uppper bound
yMaxG = yMaxO - ((yMaxO - yMinO) * 0)
## lower bound
yMinG = yMinO + ((yMaxO - yMinO) * 0)
## left bound
xMinG = xMinO + ((xMaxO - xMinO) * 0)
## right bound
xMaxG = xMaxO - ((xMaxO - xMinO) * 0)

##print(yMinO, yMin)
##print(yMaxO, yMax)
##print(xMinO, xMin)
##print(xMaxO, xMax)

s = turtle.getscreen()
s.bgpic("map_ma.png")
s.setworldcoordinates(xMin,yMin,xMax,yMax)
s.screensize(1360,930)
s.setup(1360,930,0,0)



with open("mapped.csv") as infile:
    reader = csv.reader(infile)
    mData = [row for row in reader]

mData2 = []

for row in mData[5000:]:

    if row[8] != "MA":
        continue
    if row[6] == "ERROR":
        continue
    row[6] = float(row[6])
    row[7] = float(row[7])
    if len(mData2) == 0:
        mData2.append(row)
        continue
    tooClose = False
    for filt in mData2:
        if (abs(row[6] - filt[6]) < .01) and (abs(row[7] - filt[7]) < .01):
            tooClose = True
            break
    if tooClose == False:
        mData2.append(row)
                
##print(len(mData2))

xf = 1.07
yf = .72

icon = "round_icon_tiny.gif"
s.addshape(icon)
turtle.shape(icon)
turtle.shapesize(.3,.3)
turtle.speed(0)

turtle.penup()

##time.sleep(5)

xr = -71.706
yr = 42.05155

xo = 0
yo = 0


#### calibration waypoints
##mvX = -70.6033
##mvY = 41.4828
##boX = -71.0620
##boY = 42.3553
##eaX = -72.6679
##eaY = 42.2662
##hvX = -71.0828
##hvY = 42.7808
##nwX = -73.2650
##nwY = 42.7460
##txX = -70.5
##txY = 42.3553

##turtle.goto((mvX+xo-xr)*2*xf,(mvY+yo-yr)*2*yf)
##turtle.stamp()
##turtle.goto((boX+xo-xr)*2*xf,(boY-yo-yr)*2*yf)
##turtle.stamp()
##turtle.goto((eaX-xo-xr)*2*xf,(eaY-yo-yr)*2*yf)
##turtle.stamp()
##turtle.goto((hvX-xo-xr)*2*xf,(hvY+yo-yr)*2*yf)
##turtle.stamp()
##turtle.goto((nwX+xo-xr)*2*xf,(nwY+yo-yr)*2*yf)
##turtle.stamp()

stamps = []
sn = 0
tn = 0
stampStay = 5
text = ""


n=0
turtle.shapesize(.3,.3)

for row in mData2:
    
    if row[6] > yMaxG or row[6] < yMinG:
        continue
    if row[7] > xMaxG or row[7] < xMinG:
        continue
    tn += 1
    turtle.goto((row[7]-xr)*2*xf,(row[6]-yr)*2*yf)
    turtle.stamp()

##print(tn)
