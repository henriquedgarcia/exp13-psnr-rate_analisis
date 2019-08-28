#!/bin/env python3
from utils import util
import itertools

sl = util.check_system()['sl']
config = util.Config('config.json', factor='qp')

i_folder = f'..{sl}yuv-full'
o_folder = f'results{sl}{ffmpeg_4videos_1x1_compare-quality}'
videos_list = dict(
    om_nom={
        "filename": "om_nom_4320x2160_30.yuv",
        "time": "0:10",
        "group": "0"
    },
    elephants={
        "filename": "elephants_4320x2160_30.yuv",
        "time": "1:00",
        "group": "1"
    },
    ski={
        "filename": "ski_4320x2160_30.yuv",
        "time": "0:40",
        "group": "2"
    },
    rollercoaster={
        "filename": "rollercoaster_4320x2160_30.yuv",
        "time": "1:30",
        "group": "3"
    }
)


def main():
    encode()


def encode():
    # Configure objetcts

    # iterate over 3 factors: video (complexity), tiles format, quality
    for name in config.videos_list:
        for scale in config.scale_list:
            video_input = (f'{i_folder}{sl}'
                          f'{config.videos_list[name]["filename"]}')
            video_output = (f'{o_folder}{sl}' 
                            f'{config.videos_list[name]["filename"][0:-4]}')

            global_params = '-hide_banner -y -psnr'
            param_in = (f'-s {config.scale} '
                        f'-framerate {config.fps} '
                        f'-i {video_input}')
            param_out = (f'-t {config.duration} '
                         f'-codec libx265 '
                         f'-x265-params '
                         f'"keyint={config.gop}'
                         f':min-keyint={config.gop}'
                         f':open-gop=0'
                         f':info=0'
                         f':psnr=1'
                         f':temporal-layers=0'
                         f':temporal-mvp=0'
                         f':log-level=3')

            for qp in config.qp_list:
                param_out += (f':qp={qp}'
                              f':qpmin={qp}'
                              f':qpmax={qp}"')
                command = (f'ffmpeg {global_params} {param_in} '
                           f'{param_out} {video_output}.mp4')

                with open(video_name + '.log', log_mode, encoding='utf-8') as f:
                    subprocess.run(command, shell=True, stdout=f,
                                   stderr=subprocess.STDOUT)

            for crf in config.crf_list:
                param_out = f'-crf {crf} -tune psnr {param_out}"'


if __name__ == '__main__':
    main()
