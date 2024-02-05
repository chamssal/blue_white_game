import os
import random
import pygame

mp3_folder = "C:\\Users\\chams\\Documents\\blue_white"
#mp3 파일 목록 가져오기
mp3_files = [file for file in os.listdir(mp3_folder) if file.endswith(".mp3")]
#pygame 초기화
pygame.mixer.init()
#무작위 mp3 파일 재생 함수

def play_random_mp3s(num_files):
    random_mp3s = random.sample(mp3_files, num_files)
    for mp3_file in random_mp3s:
        mp3_path = os.path.join(mp3_folder, mp3_file)
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

random_num_files = random.randint(1, len(mp3_files))  # 랜덤 개수 생성
play_random_mp3s(random_num_files)

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
