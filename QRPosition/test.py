'''
Orientation and position of QR
Add into Pi RC_main
'''
import cv2
import qr_extractor as reader

cap = cv2.VideoCapture(0)
# change it to pi USB cam

while True:
    _, frame = cap.read()
    codes, frame, angle_a, angle_b, center = reader.extract(frame, True)
    cv2.imshow("frame", frame)
    print(angle_a, angle_b, center)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print ("I quit!")
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
