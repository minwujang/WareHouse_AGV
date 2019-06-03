'''
Need
'''
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
from imutils.video import VideoStream
from imutils.video import FPS
import time
import imutils
import pytesseract
import argparse
import math
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
map = ['Start', 'Start-1', 'Start-2', 'Start-3', 'Start-4', 'Yongsan', 'Yangcheon', 'Songpa', 'Seongbuk', 'Dongjak', 'Seocho', 'Seodaemun', 'Mapo', 'Jonno', 'Guro', 'Gwangjin', 'Nowon', 'Gwanak', 'Gangnam', 'Gangbuk']

def decode_predictions(scores, geometry):
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range (0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):
            if scoresData[x] < args["min_confidence"]:
                continue

            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY + (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
    return (rects, confidences)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, help="path to input image")
ap.add_argument("-east", "--east", type=str, help="path to input EAST text detector")
ap.add_argument("-c", "--min-confidence", type=float, default=0.5, help="minimum probability required to inspect a region")
ap.add_argument("-w", "--width", type=int, default=320, help="nearest multiple of 32 for resized width")
ap.add_argument("-e", "--height", type=int, default=320, help="nearest multiple of 32 for resized height")
ap.add_argument("-p", "--padding", type=float, default=0.0, help="amount of padding to add to each border of ROI")
args = vars(ap.parse_args())

def main(args):
    (W, H) = (None, None)
    (newW, newH) = (args["width"], args["height"])
    (rW, rH) = (None, None)

    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    print("[INFO] loading EAST text detector...")
    # net = cv2.dnn.readNet(args["east"])
    net = cv2.dnn.readNet("frozen_east_text_detection.pb")

    cap = VideoStream(src=0).start()
    # cap = cv2.Videocapture(0)
    time.sleep(1.0)
    fps = FPS().start()
    while(True):
        image = cap.read()
        #image = cv2.resize(image, (640, 480))
        #아래거 없애봐야할덧 비디오파일일시 사용
        #image = image[1]


        if image is None:
            break

        image = imutils.resize(image, width=1000)
        orig = image.copy()

        (origH, origW) = image.shape[:2]
        # (newW, newH) = (args["width"], args["height"])
        if W is None or H is None:
            (H, W) = image.shape[:2]
            rW = W / float(newW)
            rH = H / float(newH)

        image = cv2.resize(image, (newW, newH))

        blob = cv2.dnn.blobFromImage(image, 1.0, (newW, newH), (123.68, 116.78, 103.94), swapRB=True, crop=False)
        net.setInput(blob)
        (scores, geometry) = net.forward(layerNames)

        (rects, confidences) = decode_predictions(scores, geometry)
        boxes = non_max_suppression(np.array(rects), probs=confidences)

        # tesseractOutputImage = np.zeros_like(orig)
        # origTesseract = orig.copy()
        results = []
        text = ''
        for (startX, startY, endX, endY) in boxes:
            # scale the bounding box coordinates based on the respective
            # ratios
            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)

            # in order to obtain a better OCR of the text we can potentially
            # apply a bit of padding surrounding the bounding box -- here we
            # are computing the deltas in both the x and y directions
            dX = int((endX - startX) * args["padding"])
            dY = int((endY - startY) * args["padding"])

            # apply padding to each side of the bounding box, respectively
            startX = max(0, startX - dX)
            startY = max(0, startY - dY)
            endX = min(origW, endX + (dX * 2))
            endY = min(origH, endY + (dY * 2))

            # extract the actual padded ROI
            roi = orig[startY:endY, startX:endX]

            config = ("-l eng --oem 1 --psm 7")
            text = pytesseract.image_to_string(roi, config=config)

            # add the bounding box coordinates and OCR'd text to the list
            # of results
            results.append(((startX, startY, endX, endY), text))

        results = sorted(results, key=lambda r: r[0][1])

        output = orig.copy()

        # loop over the results
        for ((startX, startY, endX, endY), text) in results:
            # display the text OCR'd by Tesseract
            #print("OCR TEXT")
            #print("========")
            #print("{}\n".format(text))
            print(text)

            #return string type

            # strip out non-ASCII text so we can draw the text on the image
            # using OpenCV, then draw the text and a bounding box surrounding
            # the text region of the input image
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
            #output = orig.copy()
            StartX = 'startX'
            cv2.rectangle(output, (startX, startY), (endX, endY), (0, 0, 255), 2)
            cv2.putText(output, text, (startX, startY - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            #cv2.putText(output, StartX, (startX, -startY), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            # print(startX, startY)

        fps.update()
        # show the output image
        #cv2.imshow("Text Detection", origTesseract)
        cv2.imshow("Text Detection", output)
        #print(startX, startY)
        for loc in map:
            if text == loc:
                fps.stop()
                cap.stop()
                cv2.destroyAllWindows()
                return text

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # if we are using a webcam, release the pointer
    cap.stop()
    # cap.release() when videocapture
    # close all windows
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(args)

'''
'''