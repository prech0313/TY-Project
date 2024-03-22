import diplib as dip
import math

# Load image and set pixel size
img = dip.ImageRead('')
img.SetPixelSize(0.042, "mm")

# Extract object
obj = ~dip.Threshold(dip.Gauss(img))[0]
obj = dip.EdgeObjectsRemove(obj)

# Remove noise
obj = dip.Opening(dip.Closing(obj,9),9)

# Measure object area
lab = dip.Label(obj)
msr = dip.MeasurementTool.Measure(lab,img,['Size'])
objectArea = msr[1]['Size'][0]

# Measure holes
obj = dip.EdgeObjectsRemove(~obj)
lab = dip.Label(obj)
msr = dip.MeasurementTool.Measure(lab,img,['Size'])
sz = msr['Size']
holeAreas = []
for ii in sz.Objects():
   holeAreas.append(sz[ii][0])

# Add hole areas to main object area
objectArea += sum(holeAreas)

print('Object diameter = %f mm' % (2 * math.sqrt(objectArea / math.pi)))
for a in holeAreas:
   print('Hole diameter = %f mm' % (2 * math.sqrt(a / math.pi)))