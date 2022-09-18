import ffmpy
import subprocess
import os
import soundfile as sf
import librosa
import matplotlib.pyplot as plt
import json
import numpy as np
from tqdm import tqdm

def audio_video_partition(input_video,output_video,output_audio):
    ff = ffmpy.FFmpeg(
    inputs={input_video: None},
    outputs={
        output_video: [
        '-an','-y'
        ],
        output_audio:
        ['-acodec', 'copy', '-y']
    }
    )
    print(ff.cmd)
    try:
        ff.run()
    except:
        print("Sorry... can't transfer")

def vocal_accompaniment_partition(input_audio):
    output_path = os.path.join("temp_files","spleeter_output")
    cmd = "spleeter separate -p spleeter:2stems -o %s %s"%(output_path,input_audio)
    subprocess.call (cmd,shell=True)

def show_vocals(input_audio):
    sig, sample_rate = sf.read(input_audio)
    print("采样率：%d" % sample_rate)
    print("时长：", sig.shape[0]/sample_rate, '秒')

    # 声音有两个通道
    serviceData = sig.T[0]
    clientData = sig.T[1]

    plt.rcParams['figure.figsize'] = (15, 5) # 设置figure_size尺寸
    plt.figure()
    l=sig.shape[0]

    x = [i/8000 for i in range(l)]
    plt.plot(x, serviceData, c='b')
    print(l,serviceData)
    plt.show()

def save_audio(start_frame,end_frame,audio_data,sample_rate,audio_folder):
    timeline = '-'.join([str(start_frame),str(end_frame)]) + '.wav'
    try:
        audio_name = os.path.join(audio_folder,timeline)
        sf.write(file=audio_name,data=audio_data,samplerate=sample_rate)
        print("exporting audio: %s"%timeline)
    except:
        print("exporting audio error at %s"%timeline)
        
    
    

def audio_segmentation(input_audio,dict_file="text_dict/vocals.json"):
    sig, sample_rate = sf.read(input_audio)
    
    print('正在读取文件:%s' % input_audio)
    print("采样率：", sample_rate)
    print("时长：%s" % (sig.shape[0] / sample_rate), '秒')
    # 参数设置
    min_voice = 0.08 #最低声音数值，超过这个数值才认为是说话声
    min_interval = int(0.4*sample_rate) #最短对话间隔，超过这个时间才进行切割
    # 通道1
    if len(sig.T)>2:
        audio_data = sig.T
    else:
        audio_data = sig.T[0]
    vocals = []
    vocal = (0,0)
    flag_vocal = False
    flag_temp_interval = False
    for i, value in tqdm(enumerate(audio_data)):
        if i==len(audio_data)-1:
            if flag_vocal:
                vocal = (vocal[0],i)
                vocals.append(vocal)
        # 若大于阈值
        if value >= min_voice:
            # 初始状态特殊处理
            if i==0:
                flag_vocal=True
                continue

            # 若之前处于对话阶段，则不做处理
            if flag_vocal:
                flag_temp_interval=False
                continue
            # 若之前不处于对话阶段，则转化为对话
            if not flag_vocal:
                flag_vocal=True
                vocal = (i,i)
                continue
        # 若小于阈值
        else:
            if i==0:
                continue
            # 若之前处于对话阶段，则暂时记录下时间
            if flag_vocal and not flag_temp_interval:
                flag_temp_interval = True
                vocal = (vocal[0],i)
                continue
            # 若之前处于可能的停顿时间
            if flag_vocal and flag_temp_interval:
                # 超过阈值，判定为一个停顿
                if i-vocal[1]>=min_interval:
                    flag_vocal=False
                    flag_temp_interval=True
                    vocal = (vocal[0],i)
                    vocals.append(vocal)
                else:
                    continue
    # print(vocals)
    # 具体切割时间
    times = [(vocal[0]/sample_rate,vocal[1]/sample_rate) for vocal in vocals]
    # print(times)
    vocals_dict = {}
    if not os.path.exists("seg_audios"):
        os.makedirs("seg_audios")
    for i in range(len(vocals)):
        print("正在保存段落 "+str(i))
        vocal = vocals[i]
        audio_name = "seg_audios/"+str(i)+".wav"
        sf.write(file=audio_name,data=sig[vocal[0]:vocal[1]],samplerate=sample_rate)
        vocals_dict[str(i)]={"frame":vocal}
    translate_json = json.dumps(vocals_dict,sort_keys=False,indent=4,separators=(',', ': '),ensure_ascii=False)
    with open(dict_file, 'w',encoding='utf8') as f:
        f.write(translate_json)
    print("音频分割完成")
        # # 图像化
    # print("正在绘制分割图像")
    # plt.rcParams['figure.figsize'] = (15, 5) # 设置figure_size尺寸
    # # plt.figure()

    # x = [i for i in range(sig.shape[0])]
    # plt.plot(x, audio_data, linewidth=0.5,c='b')
    # for vocal in vocals:
    #     plt.vlines(vocal[0],ymin=-1,ymax=1,colors='r',linestyles='dashed')
    #     plt.vlines(vocal[1],ymin=-1,ymax=1,colors='g',linestyles='dashed')
    # # plt.show()
    # plt.savefig("images/seg.png",dpi=600,format='png')
    # print("图像绘制完成")
 
def vocals_segmentation(input_audio,video_fps,dict_file="temp_files/text_dict/vocals.csv",vocals_folder="temp_files/seg_audios"):
    # 读取分割数据
    vocals_dict = np.loadtxt(open(dict_file,"rb"),dtype=np.int64,delimiter=",",skiprows=1,usecols=[1,2])
    sig, sr = sf.read(input_audio)
    
    print('正在读取音频:%s' % input_audio)
    print("采样率：", sr)
    print("时长：%s" % (sig.shape[0] / sr), '秒')
    # 通道1
    if len(sig.T)>2:
        audio_data = sig.T
    else:
        audio_data = sig.T[0]
    sample_rate = 16000
    audio_data = librosa.resample(audio_data,sr,sample_rate)
    if not os.path.exists(vocals_folder):
        os.makedirs(vocals_folder)
    for (s_f,e_f) in vocals_dict:
        # start_frame = s_f*sample_rate//video_fps+200
        # end_frame = e_f*sample_rate//video_fps-200
        start_frame = int(s_f*sample_rate/video_fps)
        end_frame = int(e_f*sample_rate/video_fps)
        # o_vocal_data = audio_data[start_frame:end_frame]
        # 删除静音帧，减少干扰
        # vocal_data = o_vocal_data[np.where(o_vocal_data>0)]
        vocal_data = audio_data[start_frame:end_frame]
        save_audio(s_f,e_f,vocal_data,sample_rate,vocals_folder)
    print("finish exporting vocals")
        
        
        







