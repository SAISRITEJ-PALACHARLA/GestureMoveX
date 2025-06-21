import cv2
import mediapipe as mp
import time
import pyautogui

# Key mappings
LEFT_ARROW     = 'left'
RIGHT_ARROW    = 'right'
UP_ARROW       = 'up'
DOWN_ARROW     = 'down'
BREAK_KEY      = LEFT_ARROW
ACCEL_KEY      = RIGHT_ARROW

def PressKey(key):
    pyautogui.keyDown(key)

def ReleaseKey(key):
    pyautogui.keyUp(key)

# MediaPipe setup
mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
tipIds = [4, 8, 12, 16, 20]

video = cv2.VideoCapture(0)
prev_time = 0
current_keys = set()
frame_w, frame_h = None, None

with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=2) as hands:

    # Center thresholds for 4-way control (20% margin)
    tol_x_frac = 0.2
    tol_y_frac = 0.2

    while True:
        ret, image = video.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        if frame_w is None:
            frame_h, frame_w = image.shape[:2]
            tol_x = int(frame_w * tol_x_frac)
            tol_y = int(frame_h * tol_y_frac)
            x_center = frame_w // 2
            y_center = frame_h // 2

        # Flip & convert
        image = cv2.flip(image, 1)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        rgb.flags.writeable = True
        image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        # Release any arrow keys from right hand each frame
        for k in (UP_ARROW, DOWN_ARROW, LEFT_ARROW, RIGHT_ARROW):
            if k in current_keys:
                ReleaseKey(k)
                current_keys.discard(k)

        # Default status
        detected_text = "No hands detected"

        if results.multi_hand_landmarks:
            detected_text = f"{len(results.multi_hand_landmarks)} hand(s)"
            for hand_landmarks, handedness in zip(
                        results.multi_hand_landmarks,
                        results.multi_handedness):

                # Draw skeleton
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                label = handedness.classification[0].label  # "Left" or "Right"

                # build list of (id, x_px, y_px)
                lmList = []
                for idx, lm in enumerate(hand_landmarks.landmark):
                    px, py = int(lm.x * frame_w), int(lm.y * frame_h)
                    lmList.append((idx, px, py))

                if label == 'Left' and lmList:
                    # your existing finger count → BRAKE/GAS
                    fingers = []
                    # Thumb
                    fingers.append(1 if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1] else 0)
                    # Other fingers
                    for i in range(1, 5):
                        fingers.append(1 if lmList[tipIds[i]][2] < lmList[tipIds[i]-2][2] else 0)
                    total = sum(fingers)

                    if total == 0:
                        cv2.putText(image, "BRAKE", (45, 375),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
                        if BREAK_KEY not in current_keys:
                            PressKey(BREAK_KEY); current_keys.add(BREAK_KEY)
                        if ACCEL_KEY in current_keys:
                            ReleaseKey(ACCEL_KEY); current_keys.discard(ACCEL_KEY)

                    elif total == 5:
                        cv2.putText(image, "GAS", (45, 375),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
                        if ACCEL_KEY not in current_keys:
                            PressKey(ACCEL_KEY); current_keys.add(ACCEL_KEY)
                        if BREAK_KEY in current_keys:
                            ReleaseKey(BREAK_KEY); current_keys.discard(BREAK_KEY)

                elif label == 'Right' and lmList:
                    # 4-way movement
                    # get index-tip coords
                    _, ix, iy = lmList[8]

                    if ix < x_center - tol_x:
                        move = LEFT_ARROW
                    elif ix > x_center + tol_x:
                        move = RIGHT_ARROW
                    elif iy < y_center - tol_y:
                        move = UP_ARROW
                    elif iy > y_center + tol_y:
                        move = DOWN_ARROW
                    else:
                        move = None

                    if move:
                        PressKey(move)
                        current_keys.add(move)
                        cv2.putText(image, move.upper(), (45, 450),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 5)

        # Status & FPS
        cv2.putText(image, detected_text, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        now = time.time()
        fps = int(1/(now-prev_time)) if now!=prev_time else 0
        prev_time = now
        cv2.putText(image, f'FPS: {fps}', (480, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Show
        cv2.namedWindow("Automation Gestures", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Automation Gestures", 800, 600)
        cv2.imshow("Automation Gestures", image)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

# Cleanup
for k in list(current_keys):
    ReleaseKey(k)
video.release()
cv2.destroyAllWindows()
