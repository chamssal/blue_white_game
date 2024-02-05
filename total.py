import RPi.GPIO as GPIO  # 라즈베리 파이 GPIO 제어를 위한 RPi.GPIO 라이브러리를 가져옵니다.
import os
import random
import pygame  # 오디오 재생을 위한 Pygame 라이브러리를 가져옵니다.
import cv2  # 컴퓨터 비전을 위한 OpenCV 라이브러리를 가져옵니다.
import mediapipe as mp  # 포즈 추정을 위한 MediaPipe 라이브러리를 가져옵니다.
import numpy as np
import math
import I2C_LCD_driver  # I2C LCD 디스플레이 드라이버를 가져옵니다.
from time import *

f_right = 0  # 오른쪽 팔 각도를 저장하기 위한 전역 변수 초기화
f_left = 0   # 왼쪽 팔 각도를 저장하기 위한 전역 변수 초기화

# MediaPipe 설정
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# GPIO 핀 설정
button_pin = 17  # 버튼을 위한 GPIO 핀 번호 설정

mp3_folder = "/home/ubuntu/문서/blue_white(1.5)"  # MP3 파일이 저장된 폴더 경로 지정

# 지정된 폴더에서 MP3 파일 목록 가져오기
mp3_files = [file for file in os.listdir(mp3_folder) if file.endswith(".mp3")]

# Pygame 오디오 믹서 초기화
pygame.mixer.init()

# I2C LCD 디스플레이 초기화
mylcd = I2C_LCD_driver.lcd()

# 오른쪽 어깨, 팔꿈치, 손목, 왼쪽 어깨, 팔꿈치, 손목 지점 정의
R_point_shoulder = 12
R_point_elbow = 14
R_point_wrist = 16
L_point_shoulder = 11
L_point_elbow = 13
L_point_wrist = 15

# 세 지점 사이의 각도 계산하는 함수
def calculate_angle(a, b, c):
    ang_radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = math.degrees(ang_radians)
    if angle < 0:
        angle += 360
    if angle > 180:
        angle = 360 - angle
    return angle

# 랜덤 MP3 파일을 여러 번 재생하는 함수
def play_random_mp3_multiple_times():
    global random_mp3
    random_mp3 = random.choice(mp3_files)
    mp3_path = os.path.join(mp3_folder, random_mp3)
    pygame.mixer.music.load(mp3_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# 지정된 시간만큼 딜레이를 주는 함수
def counter():
    i = 0
    while i < 1:
        sleep(1)
        i += 1
    return i

# Mediapipe 포즈 추정을 수행하는 함수
def mediapipe_code():
    cap = cv2.VideoCapture(0)  # 카메라 열기
    width = 480  # 비디오 피드의 가로 해상도 지정
    height = 360  # 비디오 피드의 세로 해상도 지정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # MediaPipe 포즈 추정 초기화
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 비디오 프레임을 RGB로 변환

            # MediaPipe를 사용하여 팔 관절 찾기
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                # 오른쪽 어깨, 팔꿈치, 손목 지점 추출
                landmarks = results.pose_landmarks.landmark
                right_shoulder = (landmarks[R_point_shoulder].x, landmarks[R_point_shoulder].y)
                right_elbow = (landmarks[R_point_elbow].x, landmarks[R_point_elbow].y)
                right_wrist = (landmarks[R_point_wrist].x, landmarks[R_point_wrist].y)
                # 왼쪽 어깨, 팔꿈치, 손목 지점 추출
                left_shoulder = (landmarks[L_point_shoulder].x, landmarks[L_point_shoulder].y)
                left_elbow = (landmarks[L_point_elbow].x, landmarks[L_point_elbow].y)
                left_wrist = (landmarks[L_point_wrist].x, landmarks[L_point_wrist].y)

                # 오른쪽 각도 계산
                R_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                # 왼쪽 각도 계산
                L_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

                # 오른쪽 결과 표시
                cv2.putText(frame, f'R_Angle: {R_angle:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # 왼쪽 결과 표시
                cv2.putText(frame, f'L_Angle: {L_angle:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # 지점과 연결선 그리기
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Pose Estimation', frame)

            if cv2.waitKey(1) & (counter() == 1):
                break

    return R_angle, L_angle

# expected answer: 정답을 처리하는 함수
def answer():
    global f_right, f_left
    
    if random_mp3 == 'raise_blue.mp3' :
        if f_right == 0:
            f_right += 1
    
    if random_mp3 == 'raise_white.mp3' :
        if f_left == 0:
            f_left += 1
    
    if random_mp3 == 'down_blue.mp3' :
        if f_right == 1:
            f_right -= 1
    
    if random_mp3 == 'down_white.mp3' :
        if f_left == 1:
            f_left -= 1
  
    return f_right, f_left

# real result: 실제 결과를 처리하는 함수
def player_result():
    global r_right, r_left
    
    r_angle, l_angle = mediapipe_code()
    print(f'{r_angle},{l_angle}')
       # time.sleep(2)
    
    if r_angle <= 15:
        r_right = 1    # 플레이어의 오른쪽 각도 결과    
    elif r_angle >= 135:
        r_right = 0    # 플레이어의 오른쪽 각도 결과
    else :
        r_right = -1  # 15~135도 범위 내의 각도

    
    if l_angle <= 15:
        r_left = 1    # 플레이어의 왼쪽 각도 결과
    elif l_angle >= 135:
        r_left = 0    # 플레이어의 왼쪽 각도 결과
    else :
        r_left = -1  # 15~135도 범위 내의 각도
    
    return r_right,r_left
       
       
# player's result vs answer result (1=correct, 0=wrong)
def compare():
    
    if(f_right == r_right and f_left == r_left) :
        print("correct")
        return 1
    else :
        print("wrong")
        return 0
    
# 정답 횟수 및 오답 횟수를 초기화
correct_count = 0
wrong_count = 0

# LCD에 결과 출력
def output_LCD():
    global correct_count, wrong_count
    
    if correct_count + wrong_count == 5:
        correct_count = 0
        wrong_count = 0
        
    if(compare()==1):
        mylcd.lcd_display_string("    CORRECT!    ",2)
        correct_count += 1
        
    elif(compare()==0):
        mylcd.lcd_display_string("    Cheer Up    ",2)
        wrong_count += 1
    sleep(1)
    mylcd.lcd_display_string(f"                ",2)

# 버튼 이벤트 핸들러
def button_callback(channel):
    
    global f_right,f_left,r_right,r_left
    
    mylcd.lcd_display_string(f"                ",1)
    mylcd.lcd_display_string(f"                ",2)
    
    for i in range(1,6) :
        f_right=0
        f_left=0
        r_right=0
        r_left=0
        mylcd.lcd_display_string(f"     QUIZ {i}     ",1)
        
        for _ in range(random.randint(1,3)) :
            play_random_mp3_multiple_times()
            answer()
        
        player_result()
        output_LCD()
    
    mylcd.lcd_display_string(f"Correct Count:{correct_count}",1)
    mylcd.lcd_display_string(f"Wrong Count:{wrong_count}",2)
    sleep(2)

    mylcd.lcd_display_string("  PRESS BUTTON  ",1)
    mylcd.lcd_display_string("    TO START!   ",2)

# 메인 함수
def main():
    cap = cv2.VideoCapture(0)
    while True:
        ret,frame=cap.read()
        if not ret:
            break
        cv2.imshow('Webcam',frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
    cap.release()
    cv2.destroyAllWindows()
    # GPIO 핀 번호 모드 설정
    GPIO.setmode(GPIO.BCM)

    # 버튼 핀을 입력 모드로 설정하고 Pull-up 저항 활성화
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # 버튼 눌림을 감지하는 이벤트 핸들러 등록
    GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

    try:
        mylcd.lcd_display_string("  PRESS BUTTON  ",1)
        mylcd.lcd_display_string("    TO START!   ",2)
        while True:
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()  # 프로그램 종료 시 GPIO 설정 초기화

if __name__ == "__main__":
    main()