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
# Every circuit component returns a tripple:
#
#  (track, cavity, cuts)
#
# track is the conducting material needed to make the circuit.
# cavity is the hole in the insulating material into which track will be printed.
# cuts is things that need to be subtracted from all the tracks when they are complete.
#
# So to build a complete circuit inside an insulator called block take the three unions of all these:
#
#  finalTrack = nullSet
#  finalCavity = nullSet
#  finalCuts = nullSet
#
#  bitOfCircuit = CircuitElement(args1)
#  finalTrack = finalTrack.fuse(bitOfCircuit[0])
#  finalCavity = finalCavity.fuse(bitOfCircuit[1])
#  finalCuts = finalCuts.fuse(bitOfCircuit[2])
#
#  anotherBitOfCircuit = AnotherCircuitElement(args2)
#  finalTrack = finalTrack.fuse(anotherBitOfCircuit[0])
#  finalCavity = finalCavity.fuse(anotherBitOfCircuit[1])
#  finalCuts = finalCuts.fuse(anotherBitOfCircuit[2])
#
#  finalTrack = finalTrack.cut(finalCuts)
#  block = block.cut(finalCavity)
#
# Now block will be the thing to print in insulating material, and finalTrack will be the thing to print in the conducting material.
# 
# Note DIL chips are mounted upside-down.
#

import Part, FreeCAD
from FreeCAD import Base
import math as maths

# Some dimensions in mm...

pinPitch = 2.54   # Chip pin pitch
trackWidth = 1.5  # Printed track width
trackDepth = 4    # Printed track depth
chipDepth = 7.3   # Cavity depth to push a DIL chip into
trackChamfer = 1  # To allow tracks to be printed without support
wire = 0.8         # The diameter of, say, a resistor lead
cavityD = 1        # How much below the surface the tracks stop. Prevents the head smearing them together when printing the final layer.
viaDia = 2         # The outer diameter of a via/pin hole for a component lead.
runOut = 2*pinPitch - 1 # Chip lead length

# FreeCAD needs a better way to make the null set...

nullSet = Part.makeBox(1, 1, 1)
nullSet.translate(Base.Vector(10, 10, 10))
nullSet = nullSet.common(Part.makeBox(1, 1, 1))

# Where a resistor or capacitor lead connects to a track.

def ComponentPin(p, depth):
 r = viaDia/2
 cavity = Part.makeCylinder(r, depth + cavityD)
 cavity.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 cut = Part.makeCone(wire/2, wire/1.7, depth)
 cut.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 track = Part.makeCylinder(r, depth)
 track.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 return (track, cavity, cut)

# Internal function to join rectangular track sections

def Corner(p, depth):
 track = Part.makeCylinder(trackWidth/2, depth)
 track.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 cavity = Part.makeCylinder(trackWidth/2, depth + cavityD)
 cavity.translate(Base.Vector(p[0], p[1], -(depth + cavityD)))
 return (track, cavity, nullSet)

# Internal function to make a single element of a track

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

# Internal function to make all single-step elements of a track
def TrackStep(p0, p1, chamfer, depth):

 track = TrackStepI(p0, p1, chamfer, depth)
 cavity = TrackStepI(p0, p1, chamfer, depth + cavityD)
 track.translate(Base.Vector(0, 0, -cavityD))
 return (track, cavity, nullSet)


# Make a whole complete track; points is a collection of ((x, y), join) where the first element is the coordinates of a change
# of direction and join decides what to put there.
#
#  join:
#
#  0 - no join, 
#  1 - join with cylinder, 
#  2 - join with component lead hole, 
#  3 - long via, TBC
#  4 - long lead hole, TBC
#  5 - chamfer flat end (for chip pins)
#

def Track(points, depth):
 index = 0
 track = nullSet
 cavity = nullSet
 cuts = nullSet
 p0 = points[index][0]
 while index < len(points) - 1:
  p1 = points[index+1][0]
  join = points[index][1]
  if join == 1:
   tsc = Corner(p0, depth)
   track = track.fuse(tsc[0])
   cavity = cavity.fuse(tsc[1])
  if join == 2:
   tsc = ComponentPin(p0, depth)
   track = track.fuse(tsc[0])
   cavity = cavity.fuse(tsc[1])
   cuts = cuts.fuse(tsc[2])
  if join == 5:
   tsc = TrackStep(p0, p1, True, depth)
  else:
   tsc = TrackStep(p0, p1, False, depth)
  track = track.fuse(tsc[0])
  cavity = cavity.fuse(tsc[1])
  p0 = p1
  index += 1
 join = points[len(points) - 1][1]
 if join == 1:
  corner = Corner(p1, depth)
  track = track.fuse(corner[0])
  cavity = cavity.fuse(corner[1])
 if join == 2:
  tsc = ComponentPin(p0, depth)
  track = track.fuse(tsc[0])
  cavity = cavity.fuse(tsc[1])
  cuts = cuts.fuse(tsc[2]) 
 return (track, cavity, cuts)

# Internal function to make the cavity in which a DIL chip will fit

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

# Make a DIL chip with pins pins; width will generally be a multiple (3x, say) of pinPitch (above);
# depth will generally be trackDepth (above).

def DILChip(pins, width, depth):
 w = width + 0.5
 if pins%2 != 0:
  print("Chip does not have an even number of pins!")
 track = nullSet
 cavity = nullSet
 pins2 = round(pins/2)
 for pin in range(pins2):
  y = pin*pinPitch
  p0=((0, y), 5)
  p1=((-runOut, y), 1)
  t = Track((p0, p1), depth)
  track = track.fuse(t[0])
  cavity = cavity.fuse(t[1])
  p0=((w, y), 5)
  p1=((w + runOut, y), 1)
  t = Track((p0, p1), depth)
  track = track.fuse(t[0])
  cavity = cavity.fuse(t[1]) 
 track.translate(Base.Vector(-0.5*w, -0.5*(pins2 - 1)*pinPitch, 0))
 cavity.translate(Base.Vector(-0.5*w, -0.5*(pins2 - 1)*pinPitch, 0))
 cavity = cavity.fuse(ChipBlock(pins, width))
 return (track, cavity, nullSet) 

def AddPin(n):
 x = 1




tracks = []
track = []
track.append(((-3.69,10.11),2))
track.append(((-9.69,10.11),1))
track.append(((-13.73,6.07),1))
track.append(((-13.73,1.27),1))
track.append(((-8.25,1.27),0))
tracks.append(track)
track = []
track.append(((-3.91,-13.29),2))
track.append(((-13.49,-13.29),1))
track.append(((-13.73,-12.69),1))
track.append(((-13.73,1.27),1))
tracks.append(track)
track = []
track.append(((0.91,-8.39),2))
track.append(((-6.85,-8.39),1))
track.append(((-8.17,-7.07),1))
track.append(((-8.17,-3.81),0))
tracks.append(track)
track = []
track.append(((3.71,-13.29),2))
track.append(((8.81,-13.29),1))
track.append(((11.41,-10.69),2))
tracks.append(track)
track = []
track.append(((11.41,-10.69),0))
track.append(((14.71,-10.69),1))
track.append(((14.71,-4.69),1))
track.append(((13.83,-3.81),1))
track.append(((8.09,-3.81),0))
tracks.append(track)
track = []
track.append(((8.13,-1.27),0))
track.append(((11.59,-1.27),1))
track.append(((11.93,-1.27),1))
track.append(((13.91,0.709999999999997),2))
tracks.append(track)
track = []
track.append(((8.17,1.27),0))
track.append(((10.17,1.27),1))
track.append(((15.21,6.31),1))
track.append(((15.21,10.31),1))
track.append(((11.11,10.41),0))
tracks.append(track)
track = []
track.append(((3.93,10.11),2))
track.append(((11.11,10.41),2))
tracks.append(track)
track = []
track.append(((5.91,-8.39),2))
track.append(((11.41,-8.15),2))
tracks.append(track)
track = []
track.append(((8.21,3.81),0))
track.append(((11.11,6.71),1))
track.append(((11.11,7.91),2))
tracks.append(track)

finalTrack = nullSet
finalCavity = nullSet
finalCuts = nullSet
for t in tracks:
 tr = Track(t, trackDepth)
 finalTrack = finalTrack.fuse(tr[0])
 finalCavity = finalCavity.fuse(tr[1])
 finalCuts = finalCuts.fuse(tr[2])
finalTrack = finalTrack.cut(finalCuts)
Part.show(finalTrack) 




'''

t = DILChip(8, 3*pinPitch, trackDepth)
tr = t[0]

Part.show(tr) 
Part.show(t[1])
'''