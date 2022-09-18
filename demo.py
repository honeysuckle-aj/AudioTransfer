import argparse
from pathlib import Path
from run import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="input the video name like 'videos/lycoris.mp4' then wait for Chinese video out",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i","--video_path",type=str,help=\
        "Path to the input video like 'videos/lycoris.mp4'")
    args = parser.parse_args()
    run(**vars(args))
    


