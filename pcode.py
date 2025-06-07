import tkinter as tk
from threading import Thread
import cv2
import mediapipe as mp
import pyautogui
import math

class VirtualMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Mouse App")
        self.is_running = False

        self.label = tk.Label(root, text="Virtual Mouse using Hand Gestures", font=("Helvetica", 14))
        self.label.pack(pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.stop_button.pack(pady=5)

    def run_mouse(self):
        cap = cv2.VideoCapture(0)
        hand_detector = mp.solutions.hands.Hands(max_num_hands=1)
        screen_w, screen_h = pyautogui.size()

        dragging = False

        def distance(a, b):
            return math.hypot(a.x - b.x, a.y - b.y)

        while self.is_running:
            success, frame = cap.read()
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = hand_detector.process(rgb)
            hands = output.multi_hand_landmarks
            h, w, _ = frame.shape

            if hands:
                for hand in hands:
                    lm = hand.landmark

                    # Move cursor
                    x = int(lm[8].x * w)
                    y = int(lm[8].y * h)
                    screen_x = screen_w / w * x
                    screen_y = screen_h / h * y
                    pyautogui.moveTo(screen_x, screen_y)

                    # Click
                    if distance(lm[8], lm[4]) < 0.03:
                        pyautogui.click()
                        pyautogui.sleep(0.5)

                    # Right click
                    if distance(lm[12], lm[4]) < 0.03:
                        pyautogui.rightClick()
                        pyautogui.sleep(0.5)

                    # Scroll
                    fingers = [lm[4], lm[8], lm[12], lm[16], lm[20]]
                    finger_status = [lm[i].y < lm[i-2].y for i in [4, 8, 12, 16, 20]]

                    if finger_status[1] and finger_status[2]:
                        pyautogui.scroll(30)
                    elif finger_status[1] and finger_status[3]:
                        pyautogui.scroll(-30)

            cv2.imshow("Virtual Mouse", frame)
            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def start(self):
        self.is_running = True
        self.thread = Thread(target=self.run_mouse)
        self.thread.start()

    def stop(self):
        self.is_running = False

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMouseApp(root)
    root.mainloop()
