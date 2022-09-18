# AudioTransfer

## Program Introduction

This program can transfer a Japanese-dubbed video which has subtitles into a Chinese-dubeed video with the similar vocal style.

## Installation

### ffmpeg

If you are using Ubuntu OS, use below command:

`sudo apt-get install ffmpeg`

If you are using MacOS, use homebrew:

`brew install ffmpeg`

If you are using Windows, you need to download the package from [this](https://github.com/BtbN/FFmpeg-Builds/releases). Then unzip it and add its PATH to you environment variables.

### Python environtemt

We command using anaconda to manage your environment.

#### pytorch && paddlepaddle

If you did't install CUDA in you computer, just type this:

```
pip install torch torchvision torchaudio #pytorch
pip install paddlepaddle==2.3.2 # paddlepaddle
```

Or, follow the website [pytorch](https://pytorch.org/get-started/locally/) and [paddlepaddle](https://www.paddlepaddle.org.cn/install/quick?docurl=documentation/docs/zh/install/pip/windows-pip.html)

#### rest packages

Install rest packages by entering the package directory and type:

`pip install -r requirements.txt`

### models: spleeter & audio transfer

For audio transfer, you need to download the released models of encoder, synthesizer and vocoder. Then move them to `utils/<coder>/saved_models/`  `<coder>` can be encoder/synthesizer/vocoder.

For spleeter, you need to download [2stems.tar.gz](https://github.com/deezer/spleeter/releases/download/v1.4.0/2stems.tar.gz). After unzipping it, you should move it into pretrained_models in root directory.

## Run

Copy your video to videos/. It's commanded that your video is less than 3 minuts because this program runs a bit slow. You can use ffmpeg to easily cut your video by:

`ffmpeg -ss <start, format is H:M:S.ms> -t <lasting time> -accurate_seek -i <video path> -codec copy <output path>`

Then type:

`python demo.py -i <video path>`

After that, you can get your Chinese-dubbed video in output/.
