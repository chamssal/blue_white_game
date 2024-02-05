import RPi.GPIO as GPIO
import os
import random
import pygame
import cv2
import mediapipe as mp
import numpy as np

# mediapipe 설정
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# 사용할 GPIO 핀 번호 설정
button_pin = 17

mp3_folder = "/home/ubuntu/Desktop/sing"
# mp3 파일 목록 가져오기
mp3_files = [file for file in os.listdir(mp3_folder) if file.endswith(".mp3")]
# pygame 초기화
pygame.mixer.init()


def play_random_mp3_multiple_times(num_repeats):
    for _ in range(num_repeats):
        random_mp3 = random.choice(mp3_files)
        mp3_path = os.path.join(mp3_folder, random_mp3)
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


def mediapipe_code():
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("카메라를 찾을 수 없습니다.")
                # 동영상을 불러올 경우는 'continue' 대신 'break'를 사용합니다.
                continue

            # 필요에 따라 성능 향상을 위해 이미지 작성을 불가능함으로 기본 설정합니다.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            # 포즈 주석을 이미지 위에 그립니다.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            '''mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())'''
            # 보기 편하게 이미지를 좌우 반전합니다.
            cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()


def button_callback(channel):
    print("Hello")
    play_random_mp3_multiple_times(num_repeats=1)
    mediapipe_code()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def main():
    # GPIO 핀 번호 모드 설정
    GPIO.setmode(GPIO.BCM)

    # 버튼 핀을 입력 모드로 설정하고 Pull-up 저항 활성화
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # 버튼 눌림을 감지하는 이벤트 핸들러 등록
    GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

    try:
        print("Waiting for button press...")
        while True:
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()  # 프로그램 종료 시 GPIO 설정 초기화


if __name__ == "__main__":
    main()