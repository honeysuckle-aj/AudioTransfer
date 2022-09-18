from genericpath import exists
import os,shutil
from utils.audio_video_partition import audio_video_partition,vocal_accompaniment_partition,vocals_segmentation
from utils.get_text_from_video import export_subtitle_img,img2text
from utils.gen_voice import generate_wav
from utils.combine import combine_vocals_accompniment,combine_audio_video
from pathlib import Path

def get_video_name(video_path):
    base_name = os.path.split(video_path)[1]
    base_name = base_name.split('.')[0]
    print("转化的视频为: %s"%base_name)
    return base_name

def run(video_path:str):
    if not os.path.exists("temp_files"):
        os.mkdir("temp_files")
    video_name = get_video_name(video_path)
    video_mute = os.path.join("temp_files",video_name+"_mute.mp4")
    if not os.path.exists(os.path.join("temp_files","audios")):
        os.mkdir(os.path.join("temp_files","audios"))
    streched_audio = os.path.join("temp_files","audios",video_name)+'.aac'
    vocal_path = os.path.join("temp_files","spleeter_output",video_name,"vocals.wav")

    audio_video_partition(video_path,video_mute,streched_audio)
    vocal_accompaniment_partition(streched_audio)
    print("finish separating audio...")
    fps, total_frame, height, width = export_subtitle_img(video_mute)
    img2text()
    vocals_segmentation(vocal_path,fps)
    print("finish cut vocals...")
    enc = Path("utils/encoder/saved_models/pretrained_m.pt")
    syn = Path("utils/synthesizer/saved_models/ceshi.pt")
    voc = Path("utils/vocoder/saved_models/pretrained_m.pt")

    generate_wav(enc,syn,voc)
    combine_vocals_accompniment(video_name,fps)
    combine_audio_video(video_name)
    print("finish output Chinese video...")
    print("Please wait for cleaning...")
    shutil.rmtree("temp_files")
    print("finish!")
