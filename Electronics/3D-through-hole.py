# FreeCAD program to create 3D printable circuitry
# 
# Adrian Bowyer
# RepRap Ltd
# https://reprapltd.com
#
# 16 July 2022
#
# Licence: GPL 3
#

import Part, FreeCAD
from FreeCAD import Base
import math as maths

pinPitch = 2.54
trackWidth = 1.5
trackDepth = 4
projection = 4
chipDepth = 7.3
trackChamfer = 1
wire = 0.8
cavityD = 1
viaDia = 2

def NullSet():
 result = Part.makeBox(1, 1, 1)
 result.translate(Base.Vector(10, 10, 10))
 return result.common(Part.makeBox(1, 1, 1))

def ViaPin(p, depth):
 r = viaDia/2
 cavity = Part.makeCylinder(r, depth + cavityD)
 cavity.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 cut = Part.makeCone(wire/2, wire/1.7, depth)
 cut.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 track = Part.makeCylinder(r, depth)
 track.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 return (track, cavity, cut)


def Corner(p, depth):
 track = Part.makeCylinder(trackWidth/2, depth)
 track.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 cavity = Part.makeCylinder(trackWidth/2, depth + cavityD)
 cavity.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 return (track, cavity)


def TrackStepI(p0, p1, chamfer, depth):
 d = (p1[0] - p0[0], p1[1] - p0[1])
 length = maths.sqrt(d[0]*d[0] + d[1]*d[1])
 result = Part.makeBox(length, trackWidth, depth)
 if chamfer:
  c = Part.makeBox(length, trackWidth*2, depth)
  c.translate(Base.Vector(0, -1, -depth))
  c.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), 45)
  c.translate(Base.Vector(0, 0, trackChamfer/maths.sqrt(2.0)))
  result = result.cut(c)
 result.translate(Base.Vector(0, -0.5*trackWidth, -depth))
 angle = maths.atan2(d[1], d[0])
 result.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), angle*180/maths.pi)
 result.translate(Base.Vector(p0[0], p0[1], 0))
 return result

def TrackStep(p0, p1, chamfer, depth):
 track = TrackStepI(p0, p1, chamfer, depth)
 cavity = TrackStepI(p0, p1, chamfer, depth + cavityD)
 track.translate(Base.Vector(0, 0, -cavityD))
 return (track, cavity)

# 0 - no join, 1 - join with cylinder, 2 - join with via/socket, 3 - long via, 4 - long socket, 5 - chamfer no join

def Track(points, depth):
 index = 0
 track = NullSet()
 cavity = NullSet()
 cuts = NullSet()
 p0 = points[index][0]
 while index < len(points) - 1:
  p1 = points[index+1][0]
  c = points[index][1]
  if c == 1:
   tsc = Corner(p0, depth)
   track = track.fuse(tsc[0])
   cavity = cavity.fuse(tsc[1])
  if c == 2:
   tsc = ViaPin(p0, depth)
   track = track.fuse(tsc[0])
   cavity = cavity.fuse(tsc[1])
   cuts = cuts.fuse(tsc[2])
  if c == 5:
   tsc = TrackStep(p0, p1, True, depth)
  else:
   tsc = TrackStep(p0, p1, False, depth)
  track = track.fuse(tsc[0])
  cavity = cavity.fuse(tsc[1])
  p0 = p1
  index += 1
 c = points[len(points) - 1][1]
 if c == 1:
  corner = Corner(p1, depth)
  track = track.fuse(corner[0])
  cavity = cavity.fuse(corner[1])
 return (track.cut(cuts), cavity)

def ChipBlock(pins, width):
 holeWidth = width + 2
 holeDepth = 1.5 + (pins/2)*pinPitch
 z = (chipDepth + 1)*2
 result = Part.makeBox(holeWidth, holeDepth, z)
 result.translate(Base.Vector(-0.5*holeWidth, -0.5*holeDepth, -chipDepth))
 c = Part.makeCylinder(2.2, chipDepth*2 + 4)
 c.translate(Base.Vector(0, 0, -chipDepth*2 -2))
 result = result.fuse(c)
 c = Part.makeCylinder(trackWidth, z)
 c.translate(Base.Vector(0, holeDepth/2, -chipDepth))
 result = result.fuse(c)
 return result

def DILChip(pins, width, depth):
 w = width + 0.5
 if pins%2 != 0:
  print("Chip does not have an even number of pins!")
 track = NullSet()
 cavity = NullSet()
 pins2 = round(pins/2)
 for pin in range(pins2):
  y = pin*pinPitch
  p0=((0, y), 5)
  p1=((-2*pinPitch, y), 1)
  t = Track((p0, p1), depth)
  track = track.fuse(t[0])
  cavity = cavity.fuse(t[1])
  p0=((w, y), 5)
  p1=((w + 2*pinPitch, y), 1)
  t = Track((p0, p1), depth)
  track = track.fuse(t[0])
  cavity = cavity.fuse(t[1]) 
 track.translate(Base.Vector(-0.5*w, -0.5*(pins2 - 1)*pinPitch, 0))
 cavity.translate(Base.Vector(-0.5*w, -0.5*(pins2 - 1)*pinPitch, 0))
 cavity = cavity.fuse(ChipBlock(pins, width))
 return (track, cavity) 

def AddPin(n):
 x = 1


track = []
track.append(((0,0),0))
track.append(((0,10),1))
track.append(((10,20),2))
track.append(((20,-30),1))
track.append(((-10,-10),2))
track.append(((-5,-5),1))
t = Track(track, trackDepth)

#t = DILChip(14, 3*pinPitch, trackDepth)

Part.show(t[0]) 
Part.show(t[1])
