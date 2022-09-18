import soundfile as sf
import librosa
import numpy as np
import os
import ffmpy

def combine_vocals_accompniment(audio_name,fps,vocals_folder="temp_files/trans_audios",dict_file = "temp_files/text_dict/vocals.csv"):
    # 读入背景音
    accompaniment_file = os.path.join("temp_files","spleeter_output",audio_name,"accompaniment.wav")
    sig_accom,origin_sr = sf.read(accompaniment_file)
    
    if len(sig_accom.T)>2:
        accom_data = sig_accom.T
    else:
        accom_data = sig_accom.T[0]
    sample_rate=16000
    if origin_sr != sample_rate:
        accom_data = librosa.resample(accom_data,origin_sr,sample_rate)
    audio_length = len(accom_data)

    # 创建语音数据
    vocals_dict = np.loadtxt(open(dict_file,"rb"),dtype=np.int64,delimiter=",",skiprows=1,usecols=[1,2])
    vocals_data = np.zeros(audio_length,dtype=np.float)
    i=0
    for s_f,e_f in vocals_dict:
        filename = os.path.join(vocals_folder,'-'.join([str(s_f),str(e_f)])+'.wav')
        sig_voc,sample_rate_voc = sf.read(filename)
        print("loading seg vocals %s"%filename)
        voc_data = sig_voc.T
        voc_lenth = len(voc_data)
        start_frame = int(s_f*sample_rate/fps)
        end_frame = start_frame+voc_lenth
        if end_frame>audio_length:
            end_frame=audio_length
            voc_data=voc_data[:audio_length-start_frame]
        vocals_data[start_frame:end_frame] += voc_data
        i += 1
    audio_data = vocals_data+accom_data
    audio_file = os.path.join("temp_files","audios",audio_name)+"_trans.flac"
    sf.write(file=audio_file,format='flac',data=audio_data,samplerate=sample_rate)

def combine_audio_video(video_name):
    input_video = os.path.join("temp_files",video_name+"_mute.mp4")
    input_audio = os.path.join("temp_files","audios",video_name+"_trans.flac")
    if not os.path.exists("output"):
        os.mkdir("output")
    output_video = os.path.join("output",video_name+"_trans.mp4")
    ff = ffmpy.FFmpeg(
    inputs={input_video:None, input_audio:None},
    outputs={
        output_video: [
        '-vcodec','copy', 
        '-acodec','copy',
        '-strict','-2',
        '-y'
        ],
    }
    )
    print(ff.cmd)
    try:
        ff.run()
    except:
        print("Sorry... can't transfer")



