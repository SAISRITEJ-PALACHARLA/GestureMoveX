import cv2

print("⏳ Trying to access the camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not accessible. macOS likely blocked it.")
else:
    print("✅ Camera is working! You should now see a permission popup.")
    ret, frame = cap.read()
    if ret:
        cv2.imshow("CAMERA TEST — ESC to Exit", frame)
        cv2.waitKey(0)

cap.release()
cv2.destroyAllWindows()
