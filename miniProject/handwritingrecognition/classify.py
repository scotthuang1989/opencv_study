from __future__ import print_function
from sklearn.externals import joblib
from pyimagesearch.hog import HOG
from pyimagesearch import dataset
from pyimagesearch import imutils
import argparse
import mahotas
import cv2

ap=argparse.ArgumentParser()
ap.add_argument('-m', '--model', required=True,
        help='path to where the model will be stored')
ap.add_argument('-i', '--image', required=True,
        help='path to the image file')

args=vars(ap.parse_args())

model=joblib.load(args['model'])

hog=HOG(orientation=18, pixelsPerCell=(10,10),
        cellsPerBlock=(1,1), transform=True)

image=cv2.imread(args['image'])
# image=imutils.resize(image,width=28,height=28)
gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

blurred=cv2.GaussianBlur(gray,(5,5),0)
edged=cv2.Canny(blurred,30,150)
(_, cnts,_)=cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
cnts=sorted([(c, cv2.boundingRect(c)[0]) for c in cnts],
        key=lambda x:x[1])
for (c, _) in cnts:
    (x,y,w,h)=cv2.boundingRect(c)
    if w>=7 and h>=20:
        roi=gray[y:y+h, x:x+w]
        thresh=roi.copy()
        T=mahotas.thresholding.otsu(roi)
        thresh[thresh>T]=255
        thresh=cv2.bitwise_not(thresh)
        thresh=dataset.deskew(thresh,20)
        # import pdb; pdb.set_trace()
        thresh=dataset.center_extent(thresh,(20,20))
        hist=hog.describe(thresh)
        digit=model.predict([hist])[0]
        print("I think that number is : {}".format(digit))

        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),1)
        cv2.putText(image,str(digit),(x-10,y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0),2)
        cv2.imshow('image',image)
        cv2.waitKey(0)
