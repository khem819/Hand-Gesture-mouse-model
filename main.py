import cv2
import mediapipe as mp
import pyautogui
import time
import math


#initalize mediapipe hands
print("Starting Hand Tracking...")
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.5,min_tracking_confidence=0.5)

#start web cam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


# Gesture control variables
click_time = []
freeze_cursor = False
click_cooldown = 0.5
scroll_mode = False
freeze_cursor = False
screenshot_cooldown = 2
last_screenshot_time = 0

screen_w, screen_h = pyautogui.size()
print("\n Smart Hand Mouse Control System.")

# Previous cursor position
prev_screen_x = 0
prev_screen_y = 0

if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Camera opened successfully")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # Draw landmarks
            mp_drawing.draw_landmarks(frame,hand_landmarks,mp_hands.HAND_CONNECTIONS)

            # Finger tips
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]


             # Finger detection
            fingers = [
                1 if hand_landmarks.landmark[tip].y <
                     hand_landmarks.landmark[tip - 2].y else 0
                for tip in [8, 12, 16, 20]
            ]


            # Distance between thumb and index
            dist = math.hypot(
                thumb_tip.x - index_tip.x,
                thumb_tip.y - index_tip.y
            )

            # CLICK GESTURE
            if dist < 0.06:
                if not freeze_cursor:
                    freeze_cursor = True
                    click_time.append(time.time())

                    # Double click
                    if len(click_time) >= 2 and \
                       click_time[-1] - click_time[-2] < 0.4:
                        pyautogui.doubleClick()
                        cv2.putText(
                            frame,
                            "Double Click",
                            (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 255),
                            2
                        )
                        click_time = []

                    else:
                        pyautogui.click()
                        cv2.putText(
                            frame,
                            "Single Click",
                            (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 0),
                            2
                        )

            else:
                if freeze_cursor:
                    time.sleep(0.1)
                freeze_cursor = False

            # MOVE CURSOR
            if not freeze_cursor:
                screen_x = int(index_tip.x * screen_w)
                screen_y = int(index_tip.y * screen_h)

                # Smooth cursor movement
                curr_x = prev_screen_x + (screen_x - prev_screen_x) / 5
                curr_y = prev_screen_y + (screen_y - prev_screen_y) / 5
                pyautogui.moveTo(curr_x, curr_y)

                prev_screen_x = curr_x
                prev_screen_y = curr_y

        #scroll mode
        if sum(fingers) == 3:
            scroll_mode = True
        else:
            scroll_mode=False  

        #scroll actions    
        if scroll_mode:
            if index_tip.y < 0.4:
                pyautogui.scroll(60)
                cv2.putText(frame,"scroll up",(10,20),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

            elif index_tip.y > 0.6:
                pyautogui.scroll(-60)
                cv2.putText(frame,"scroll down",(10,10),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,25),2) 

        #screenshot
        if sum(fingers) == 0:
            current_time = time.time()
            if current_time - last_screenshot_time > screenshot_cooldown:
             pyautogui.screenshot(f"screenshot_{int(current_time)}.png")
             cv2.putText(frame,"screenshot Taken!",(10,130),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)
             last_screenshot_time = current_time


    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()