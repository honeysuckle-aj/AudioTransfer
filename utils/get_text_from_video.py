import cv2
from PIL import Image
import numpy as np
import os
import re
import pandas as pd
from paddleocr import PaddleOCR,draw_ocr
from copy import deepcopy


def get_video_info(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)
    # if fps-int(fps)<0.5:
    #     fps = int(fps)
    # else:
    #     fps=int(fps)+1
    frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    return fps, frame, height, width


def cal_stderr(img, imgo=None):
    if imgo is None:
        return (img ** 2).sum() / img.size * 100
    else:
        return ((img - imgo) ** 2).sum() / img.size * 100


def cal_texterr(t1, t2):
    l1 = list(t1)
    l2 = list(t2)
    l_inter = deepcopy(l1)
    for c in l1:
        if c not in l2:
            l_inter.remove(c)
    return 2 * len(l_inter) / (len(l1) + len(l2))


def save_image(img_folder, img: Image, start_frame: int, end_frame: int):
    # 保存字幕图片到文件夹
    timeline = '-'.join([str(start_frame), str(end_frame)]) + ".png"
    try:
        imgname = os.path.join(img_folder, timeline)
        img.save(imgname)
        print('export subtitle at %s' % timeline)
    except Exception:
        print('export subtitle at %s error' % timeline)


def get_timeline(img_name: str):
    for i in range(len(img_name)):
        if img_name[i] == '-':
            start_frame = int(img_name[:i])
            end_frame = int(img_name[i + 1:-4])
            return start_frame, end_frame

def sort_timeline(img_name:str):
    for i in range(len(img_name)):
        if img_name[i] == '-':
            start_frame = int(img_name[:i])
            return start_frame

def save_text(dict, text, start_frame, end_frame, i):
    dict[str(i)] = {"text": text, "start": start_frame, "end": end_frame}

def find_text(video_filename,skip_frame = 10):
    img_folder = os.path.join("temp_files","test_imgs")
    if not os.path.exists(img_folder):
        os.mkdir(img_folder)
    cap = cv2.VideoCapture(video_filename)
    fps, total_frame, height, width = get_video_info(cap)
    count=0
    success = True
    for _ in range(skip_frame):
            cap.read()
    while success and count<20:
        # very 10 frame get a cut
        for _ in range(5):
            cap.read()
        success, frame = cap.read()
        #
        if not success:
            break
        img = cv2.cvtColor(frame[3*height//4:height], cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
        while cal_stderr(img)<1:
            success, frame = cap.read()
            if not success:
                break
            img = cv2.cvtColor(frame[3*height // 4:height], cv2.COLOR_BGR2GRAY)
            _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
        count+=1
        img = Image.fromarray(img)
        try:
            imgname = os.path.join(img_folder, str(count))+'.png'
            img.save(imgname)
            print('export subtitle at %s' % count)
        except Exception:
            print('export subtitle at %s error' % count)
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    for img in os.listdir(img_folder):
        filename = os.path.join(img_folder, img)
        # text = pytesseract.image_to_string(filename,lang='chi_sim',config='--psm 7 -c preserve_intertext_spaces=1')
        res = ocr.ocr(filename, cls=True)
        text_y_min = height//4
        text_y_max = 0
        if len(res)>0:
            y_list = [p[1] for p in res[0][0]]
            text_y_min = min(text_y_min,min(y_list))
            text_y_max = max(text_y_max,max(y_list))
        # print(text_y_min)
    return int(text_y_min+3*height//4),int(text_y_max+3*height//4)

def export_subtitle_img(video_filename, skip_frames=0):
    text_y = find_text(video_filename)
    img_folder = os.path.join("temp_files","text_imgs")
    if not os.path.exists(img_folder):
        os.mkdir(img_folder)
    cap = cv2.VideoCapture(video_filename)
    # 跳过
    for _ in range(skip_frames):
        cap.read()
    start_frame = skip_frames
    curr_frame = skip_frames
    fps, total_frame, height, width = get_video_info(cap)
    success = True
    subtitle_img = None
    last_img = None
    while success:
        # 每次跳过5帧
        # for _ in range(2):
        #     success,frame = cap.read()
        success, frame = cap.read()
        curr_frame += 1
        if frame is None:
            if subtitle_img != None:
                save_image(img_folder, subtitle_img, start_frame, curr_frame - 1)
            print('video: %s finish at %d frame.' % (video_filename, curr_frame))

            break

        # 图像中字幕所在的位置
        img = cv2.cvtColor(frame[text_y[0]:text_y[1]], cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
        # 若图像中没有字幕
        if cal_stderr(img) < 0.6:
            # 若前一帧也没有字幕
            if last_img is None:
                continue
            # 若前一帧图像有字幕，则保存字幕
            else:
                save_image(img_folder, subtitle_img, start_frame, curr_frame - 1)
                last_img = None
                subtitle_img = None
        # 若图像中有字幕
        else:
            # 若前一帧没有字幕
            if last_img is None:
                subtitle_img = Image.fromarray(img)
                last_img = img
                start_frame = curr_frame
            # 若前一帧图像的字幕相同
            elif cal_stderr(img, imgo=last_img) < 1.6:
                continue
            # 若与前一帧图像字幕不同
            else:
                save_image(img_folder, subtitle_img, start_frame, curr_frame - 1)
                subtitle_img = Image.fromarray(img)
                last_img = img
                start_frame = curr_frame

    print('video: %s export subtitle finish!' % video_filename)
    return  fps, total_frame, height, width


def img2text(img_folder='temp_files/text_imgs'):
    dict_folder = os.path.join("temp_files","text_dict")
    if not os.path.exists(dict_folder):
        os.mkdir(dict_folder)
    vocals_list = []
    last_text = ""
    count = 0
    # ocr = CnOcr()
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    img_list = os.listdir(img_folder)
    img_list.sort(key=sort_timeline)
    for img in img_list:
        start_frame, end_frame = get_timeline(img)

        filename = os.path.join(img_folder, img)
        # text = pytesseract.image_to_string(filename,lang='chi_sim',config='--psm 7 -c preserve_intertext_spaces=1')
        res = ocr.ocr(filename, det=False, cls=False)
        print(res)
        if res:
            text = res[0][0]
        else:
            text = ''

        if text != '' and text != ' ':
            sub_texts = text.split()
            str = '.'
            text = str.join(sub_texts)
            # 防止出现乱码，只保留中英文，数字及'.'
            text = re.sub(u"([^\u0041-\u005a\u0030-\u0039\u4e00-\u9fa5\u002e])", "", text)
        else:
            # os.remove(filename)
            continue
        start_frame, end_frame = get_timeline(img)
        if cal_texterr(text, last_text) > 0.7 or end_frame-start_frame<=3:
            if len(vocals_list)>0:
                vocals_list[-1][1] = end_frame
        else:
            vocals_list.append([start_frame, end_frame, text])
            last_text = text
            count += 1
    print("finish. text count=", count)
    name = ["start frame", "end frame", "text"]
    vocals_list.sort(key=lambda x: x[0])
    vocals = pd.DataFrame(columns=name, data=vocals_list)
    try:
        vocals.to_csv(os.path.join(dict_folder, "vocals.csv"), encoding='utf-8')
        print("succeed exporting dict")
    except:
        print("failed to export dict ...")


