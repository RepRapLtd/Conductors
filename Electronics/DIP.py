# FreeCAD program to create 3D printable circuitry
# 
# Adrian Bowyer
# RepRap Ltd
# https://reprapltd.com
#
# 16 July 2022
#
# Licence: GPL 3

import Part, FreeCAD
from FreeCAD import Base
import math as maths

pins = 8
pinPitch = 2.54
trackWidth = 1.5
trackDepth = 2
projection = 4
chipDepth = 7.3

def NullSet():
 result = Part.makeBox(1, 1, 1)
 result.translate(Base.Vector(10, 10, 10))
 return result.common(Part.makeBox(1, 1, 1))

def Corner(p):
 result = Part.makeCylinder(trackWidth/2, trackDepth)
 result.translate(Base.Vector(p[0], p[1], 0))
 return result


def TrackStep(p0, p1):
 d = (p1[0] - p0[0], p1[1] - p0[1])
 length = maths.sqrt(d[0]*d[0] + d[1]*d[1])
 result = Part.makeBox(length, trackWidth, trackDepth)
 result.translate(Base.Vector(0, -0.5*trackWidth, 0))
 angle = maths.atan2(d[1], d[0])
 result.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), angle*180/maths.pi)
 result.translate(Base.Vector(p0[0], p0[1], 0))
 return result

# 0 - no join, 1 - join with cylinder, 2 - join with via/socket, 3 - long via, 4 - long socket

def Track(track):
 index = 0
 result = NullSet()
 p0 = track[index][0]
 while index < len(track) - 1:
  p1 = track[index+1][0]
  c = track[index][1]
  if c == 1:
   result = result.fuse(Corner(p0))
  result = result.fuse(TrackStep(p0, p1))
  p0 = p1
  index += 1
 c = track[len(track) - 1][1]
 if c == 1:
  result = result.fuse(Corner(p1))
 return result

def ChipBlock():
 holeWidth = width + 2
 holeDepth = (pins/2)*pinPitch
 result = Part.makeBox(holeWidth, holeDepth, chipDepth + 1)
 result.translate(Base.Vector(-0.5*holeWidth, -0.5*holeDepth, -chipDepth))
 c = Part.makeCylinder(trackWidth, chipDepth*2 + 4)
 c.translate(Base.Vector(0, 0, -chipDepth*2 -2))
 result = result.fuse(c)
 return b

def ChipTracks(pins, width):
 if pins%2 != 0:
  print("Chip does not have an even number of pins!")
 result = NullSet()
 for pin in range(round(pins/2)):
  y = pin*pinPitch
  p0=((0, y), False)
  p1=((-2*pinPitch, y), True)
  result = result.fuse(Track((p0, p1)))
  p0=((width, y), False)
  p1=((width + 2*pinPitch, y), True)
  result = result.fuse(Track((p0, p1))) 
 return result 

def AddPin(n):
 x = 1


track = []
track.append(((0,0),0))
track.append(((0,10),1))
track.append(((10,20),1))
track.append(((20,-30),1))
track.append(((-10,-10),1))
track.append(((-5,-5),1))

b = Track(track)
#c = ChipTracks(8, 3*pinPitch)
Part.show(b) 