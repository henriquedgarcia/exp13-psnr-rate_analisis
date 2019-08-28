#!/bin/env python3
# import sys
# sys.modules[__name__].__dict__.clear()

# import importlib
# importlib.reload(modulename)

# Início
import itertools
from utils import util

sl = util.check_system()['sl']

rodada = None


def main():
    decode()


def decode():
    # Abre configurações
    config = util.Config('config.json')

    # Cria objeto "video" com suas principais pastas
    video = util.VideoParams(config=config,
                             yuv=f'..{sl}yuv-10s')

    # Configura objeto VideoParams
    video.project = f'results{sl}ffmpeg_scale_12videos_60s'
    video.decoder = 'ffmpeg'
    video.factor = 'scale'
    video.threads = 'single'
    video.quality_list = getattr(config, f'{video.factor}_list')
    video.dectime_base = f'dectime_{video.decoder}'

    # para vada video, para cada fmt, para cada qualidadae... decodificar 3 vezes
    for video.name in config.videos_list:
        for video.tile_format in config.tile_list:
            for video.rodada in range(3):
                for video.quality in video.quality_list:
                    util.decode(video=video)


if __name__ == '__main__':
    main()
