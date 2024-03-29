import itertools
import json
import os
import platform
import subprocess
import time
import numpy as np


# Minhas classes
class Container:
    pass


class AutoDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class Config:
    def __init__(self, filename: str, factor: str):
        self.filename = filename
        self.scale = ''
        self.fps = 0
        self.gop = 0
        self.duration = 0
        self.qp_list = []  # Quality
        self.rate_list = []  # Quality
        self.crf_list = []  # Quality
        self.quality_list = []  # Quality
        self.scale_list = []  # Quality
        self.tile_list = []
        self.tile_list1 = []
        self.tile_list2 = []
        self.videos_list = {}
        self.single_videos_list = {}
        self.factor = factor  # Obrigatório na inicialização
        self.config_data = {}
        self.sl = check_system()['sl']
        if filename:
            self._load_config(filename)

    def _load_config(self, filename: str):
        with open(filename, 'r') as f:
            self.config_data = json.load(f)

        for key in self.config_data:
            setattr(self, key, self.config_data[key])

        self.quality_list = self.config_data[f'{self.factor}_list']

        # Seleciona o tile_list de acordo com o factor
        if self.factor not in 'scale':
            self.tile_list = self.tile_list1
        else:
            self.tile_list = self.tile_list2


class Video:
    class AutoDict(dict):
        def __missing__(self, key):
            value = self[key] = type(self)()
            return value

    def __init__(self, config: Config, dectime: dict = None):
        if dectime is None:
            self.dectime = self.AutoDict()
        else:
            self.dectime = self.AutoDict(dectime)

        self.sl = '/'
        self.config = config
        self.m = self.n = self.num_tiles = None
        self.bench_stamp = None

        self.scale = config.scale
        self.fps = config.fps
        self.gop = config.gop
        self.duration = config.duration

        # saída: dicionário com todos os dados de saída

        # pastas
        self._basename = None
        self.project = None
        self.dectime_base = None
        self.segment_base = None
        self._log_path = None
        self._segment_path = None

        self.decoder = None
        self.name = None
        self._fmt = None
        self.factor = None
        self.quality = None
        self.tile = None
        self.chunk = None
        self.multithread = None

    @property
    def basename(self):
        if self.factor is None or self.quality is None or self.name is None:
            exit('[basename] Esta faltando algum atributo (factor, quality or name).')

        self._basename = (f'{self.name}_'
                          f'{self.scale}_'
                          f'{self.fps}_'
                          f'{self.fmt}_'
                          f'{self.factor}{self.quality}')
        return self._basename

    @property
    def segment_path(self):
        if self.project is None or self.segment_base is None or self.tile is None or self.chunk is None:
            exit('[segment_path] Esta faltando algum atributo.')

        self._segment_path = (f'{self.project}{self.sl}'
                              f'{self.segment_base}{self.sl}'
                              f'{self.basename}{self.sl}'
                              f'tile{self.tile}_{self.chunk:03}')
        return self._segment_path

    @property
    def log_path(self):

        self._log_path = (f'{self.project}{self.sl}'
                          f'{self.dectime_base}{self.sl}'
                          f'{self.basename}{self.sl}'
                          f'tile{self.tile}_{self.chunk:03}_'
                          f'{self.multithread}')

        return self._log_path

    @property
    def size(self):  # name, fmt, quality, tile, chunk
        if self.name is None or \
                self.fmt is None or \
                self.quality is None or \
                self.tile is None or \
                self.chunk is None:
            exit('[size] Esta faltando algum atributo.')

        return self.dectime[self.name][self.fmt][self.quality][self.tile][self.chunk]['size']

    @size.setter
    def size(self, value):
        if self.name is None or \
                self.fmt is None or \
                self.quality is None or \
                self.tile is None or \
                self.chunk is None:
            exit('[size] Esta faltando algum atributo.')
        self.dectime[self.name][self.fmt][self.quality][self.tile][self.chunk]['size'] = value

    @property
    def times(self):
        if self.name is None or \
                self.fmt is None or \
                self.quality is None or \
                self.tile is None or \
                self.chunk is None:
            exit('[size] Esta faltando algum atributo.')
        return self.dectime[self.name][self.fmt][self.quality][self.tile][self.chunk]['times']

    @times.setter
    def times(self, value):
        if self.name is None or \
                self.fmt is None or \
                self.quality is None or \
                self.tile is None or \
                self.chunk is None:
            exit('[size] Esta faltando algum atributo.')
        self.dectime[self.name][self.fmt][self.quality][self.tile][self.chunk]['times'] = value

    @property
    def fmt(self):
        return self._fmt

    @fmt.setter
    def fmt(self, value):
        self._fmt = value
        self.m, self.n = list(map(int, value.split('x')))
        self.num_tiles = self.m * self.n


class Atribs:
    def __init__(self):
        # System params
        self._encoder = ''
        self._decoder = ''
        self.sl = ''  # OK
        self.config = None
        self.program = ''
        self.threads = ''

        # Streaming params
        self.factor = ''
        self.quality_list = []
        self.quality = 0

        # video properties
        self._scale = ''  # OK
        self._tile_format = ''
        self.fps = 0
        self.gop = 0
        self.duration = 0
        self.width = 0
        self.height = 0
        self.tile_w = 0
        self.tile_h = 0
        self.number_tiles = 0
        self.tile = 0
        self.chunk = 0

        # file properties
        self.project = ''  # OK
        self.name = ''  # OK
        self._basename = ''

        self.yuv = ''  # OK
        self.hevc_base = ''  # OK
        self.mp4_base = ''  # OK
        self.segment_base = ''  # OK
        self.dectime_base = ''  # OK

        self._yuv_video = ''
        self.hevc_video = ''
        self.mp4_video = ''
        self.tiled_video = ''
        self._segment_video = ''
        self._dectime_log = ''

        self._hevc_folder = ''
        self._mp4_folder = ''
        self._segment_folder = ''
        self._dectime_folder = ''

    # --- Diretórios base ---
    @property
    def basename(self):
        if self.factor in '':
            exit('[basename] É preciso definir o atributo factor antes.')
        if self.quality == 0:
            exit('[basename] É preciso definir o atributo quality antes.')

        self._basename = (f'{self.name}_'
                          f'{self.scale}_'
                          f'{self.fps}_'
                          f'{self.tile_format}_'
                          f'{self.factor}{self.quality}')
        return self._basename

    @property
    def hevc_folder(self):
        if self.project in '':
            exit('[hevc] É preciso definir o atributo "project" antes.')
        self._hevc_folder = f'{self.project}{self.sl}{self.hevc_base}{self.sl}{self.basename}'
        makedir(self._hevc_folder)
        return self._hevc_folder

    @property
    def mp4_folder(self):
        if self.project in '':
            exit('[mp4] É preciso definir o atributo "project" antes.')
        self._mp4_folder = f'{self.project}{self.sl}{self.mp4_base}{self.sl}{self.basename}'
        makedir(self._mp4_folder)
        return self._mp4_folder

    @property
    def dectime_folder(self):
        if self.project in '':
            exit('[dectime] É preciso definir o atributo "project" antes.')
        self._dectime_folder = f'{self.project}{self.sl}{self.dectime_base}{self.sl}{self.basename}'
        makedir(self._dectime_folder)
        return self._dectime_folder

    @property
    def segment_folder(self):
        if self.project in '':
            exit('[dectime] É preciso definir o atributo "project" antes.')
        self._segment_folder = f'{self.project}{self.sl}{self.segment_base}{self.sl}{self.basename}'
        makedir(self._segment_folder)
        return self._segment_folder

    @property
    def segment_video(self):
        if self.tile == 0 or self.chunk == 0:
            exit('[dectime] É preciso definir o atributo "tile" ou "chunk" antes.')
        self._segment_video = f'{self.segment_folder}{self.sl}tile{self.tile}_{self.chunk:03}'
        return self._segment_video

    @property
    def dectime_log(self):
        if self.tile == 0 or self.chunk == 0:
            exit('[dectime] É preciso definir o atributo "tile" ou "chunk" antes.')
        self._dectime_log = f'{self.dectime_folder}{self.sl}tile{self.tile}_{self.chunk:03}_{self.threads}'
        return self._dectime_log

    @property
    def yuv_video(self):
        if self.name in '':
            exit('[yuv_video] É preciso definir o atributo "name" antes.')
        self._yuv_video = f'{self.yuv}{self.sl}{self.config.videos_list[self.name]["filename"]}'
        return self._yuv_video

    # -----------------------------

    # --- Propriedades do vídeo ---
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.width, self.height = list(map(int, value.split('x')))

    @property
    def tile_format(self):
        return self._tile_format

    @tile_format.setter
    def tile_format(self, value):
        self._tile_format = value
        m, n = list(map(int, value.split('x')))
        self.tile_w = int(self.width / m)
        self.tile_h = int(self.height / n)
        self.number_tiles = m * n

    # -----------------------------

    # --- Codecs ---
    @property
    def encoder(self):
        return self._encoder

    @encoder.setter
    def encoder(self, value):
        self._encoder = value
        self.program = check_system()[value]

    @property
    def decoder(self):
        return self._decoder

    @decoder.setter
    def decoder(self, value):
        self._decoder = value
        self.program = check_system()[value]


class VideoParams(Atribs):
    def __init__(self, config, yuv='../yuv-full', hevc_base='hevc', mp4_base='mp4', segment_base='segment',
                 dectime_base='dectime'):
        super().__init__()
        # Initial actions
        self.sl = check_system()['sl']
        self.config = config
        self.rodada = 0
        self.scale = config.scale
        self.fps = config.fps
        self.gop = config.gop
        self.duration = config.duration
        self.yuv = yuv
        self.hevc_base = hevc_base
        self.mp4_base = mp4_base
        self.segment_base = segment_base
        self.dectime_base = dectime_base
        self.factor = config.factor


# Funções para codificação
def encode(video: VideoParams):
    if video.encoder in 'kvazaar':
        _encode_kvazaar(video=video)

    elif video.encoder in 'ffmpeg':
        _encode_ffmpeg(video=video)

    else:
        print('[encode] Encoder só pode ser "ffmpeg" ou "kvazaar"')


def _encode_ffmpeg(video):
    global_params = '-hide_banner -y -psnr'
    param_in = (f'-s {video.scale} '
                f'-framerate {video.fps} '
                f'-i {video.yuv_video}')
    param_out = (f'-t {video.duration} '
                 f'-codec libx265 '
                 f'-x265-params '
                 f'"keyint={video.gop}'
                 f':min-keyint={video.gop}'
                 f':open-gop=0'
                 f':info=0'
                 f':psnr=1'
                 f':temporal-layers=0'
                 f':temporal-mvp=0'
                 f':log-level=3')

    if video.factor in 'qp':
        param_out += (f':qp={video.quality}'
                      f':qpmin={video.quality}'
                      f':qpmax={video.quality}"')
    elif video.factor in 'rate':
        rate = int(video.quality / video.number_tiles)
        param_out = f'-b:v {rate} {param_out}"'
    elif video.factor in 'crf':
        param_out = f'-crf {video.quality} -tune psnr {param_out}"'
    elif video.factor in 'scale':
        param_out = f'-s {video.quality} {param_out}"'
    else:
        exit('Fator de qualidade só pode ser "qp" ou "rate" ou crf.')

    tile_count = 0
    for x in range(0, video.width, video.tile_w):
        for y in range(0, video.height, video.tile_h):
            tile_count += 1
            video.mp4_video = f'{video.mp4_folder}{video.sl}tile{tile_count}'

            filter_params = f'-vf "crop=w={video.tile_w}:h={video.tile_h}:x={x}:y={y}"'

            if video.factor in 'rate':
                # 1-pass
                command = f'{video.program} {global_params} {param_in} {param_out}:pass=1" {filter_params} -f mp4 nul'
                run(command, f'{video.mp4_video}', 'mp4', log_mode='none')

                # 2-pass
                command = (f'{video.program} {global_params} {param_in} {param_out}:pass=2" {filter_params} -f mp4 '
                           f'{video.mp4_video}.mp4')
                run(command, f'{video.mp4_video}', 'mp4', overwrite=True)

            elif video.factor in 'qp':
                command = f'{video.program} {global_params} {param_in} {param_out} {filter_params} {video.mp4_video}.mp4'
                run(command, f'{video.mp4_video}', 'mp4', overwrite=True)

            elif video.factor in 'crf':
                command = f'{video.program} {global_params} {param_in} {param_out} {filter_params} {video.mp4_video}.mp4'
                run(command, f'{video.mp4_video}', 'mp4', overwrite=True)

            elif video.factor in 'scale':
                command = f'{video.program} {global_params} {param_in} {param_out} {filter_params} {video.mp4_video}.mp4'
                run(command, f'{video.mp4_video}', 'mp4', overwrite=True)


def _encode_kvazaar(video: VideoParams):
    params_common = (f'--input {video.yuv_video} '
                     f'-n {video.duration * video.fps} '
                     f'--input-res {video.scale} '
                     f'--input-fps {video.fps} '
                     f'-p {video.gop} '
                     '--no-tmvp '
                     '--no-open-gop ')

    if video.factor in 'qp':
        params_common += f'--qp {video.quality}'
    elif video.factor in 'rate':
        params_common += f'--bitrate {video.quality}'
    else:
        exit('Fator de qualidade só pode ser "qp" ou "rate"')

    if video.tile_format not in '1x1':
        tile_params = f' --tiles {video.tile_format} --slices tiles --mv-constraint frametilemargin'
        params_common += tile_params

    video.hevc_video = f'{video.hevc_folder}{video.sl}{video.basename}'

    command = f'{video.program} {params_common} --output {video.hevc_video}.hevc'
    run(command, video.hevc_video, 'hevc')


def run(command, video_name, ext, overwrite=False, log_mode='w'):
    if os.path.isfile(f'{video_name}.{ext}') and not overwrite:
        print(f'arquivo {video_name}.{ext} existe. Pulando.')

    else:
        print(command)
        if log_mode in 'none':
            subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
        else:
            with open(video_name + '.log', log_mode, encoding='utf-8') as f:
                subprocess.run(command, shell=True, stdout=f, stderr=subprocess.STDOUT)


def encapsule(video: VideoParams):
    """
    Encapsula o vídeo usando o MP4Box quando codificado com kvazaar
    :return:
    """
    if video.encoder in 'ffmpeg':
        pass
    elif video.encoder in 'kvazaar':

        mp4box = check_system()['mp4box']
        video.mp4_video = f'{video.mp4_folder}{video.sl}{video.basename}'
        command = f'{mp4box} -add {video.hevc_video}.hevc:split_tiles -new {video.mp4_video}.mp4'
        run(command, video.mp4_video, 'mp4')
    else:
        print('[encapsule] Opção de encoder inválida.')


def extract_tile(video):
    """
    Extrai os tiles do vídeo quando codificado com o kvazaar com a opção -tile
    :return:
    """
    if video.encoder in 'ffmpeg':
        pass
    elif video.encoder in 'kvazaar':
        mp4box = check_system()['mp4box']

        for tile_count in range(1, video.number_tiles + 1):
            video.tiled_video = f'{video.mp4_folder}{video.sl}tile{tile_count}'

            # Extract desired track
            track = tile_count + 1
            if video.tile_format in '1x1':
                track = 1

            command = f'{mp4box} -raw {track} {video.mp4_video}.mp4 -out {video.tiled_video}.hevc'
            run(command, video.tiled_video, 'hevc')

            # Add resulting track in new mp4
            command = f'{mp4box} -add {video.tiled_video}.hevc -new {video.tiled_video}.mp4'
            run(command, video.tiled_video, 'mp4', log_mode='a')


def make_segments(video):
    """
    Codifica o vídeo usando o codificador especificado em encoder
    :type video: VideoParams
    :param video:
    :return:
    """
    mp4box = check_system()['mp4box']

    for tile_count in range(1, video.number_tiles + 1):
        segment_log = f'{video.segment_folder}{video.sl}{video.basename}_tile{tile_count}'
        video.tiled_video = f'{video.mp4_folder}{video.sl}tile{tile_count}'

        # Segment tiles in chunks
        command = f'{mp4box} -split 1 {video.tiled_video}.mp4 -out {video.segment_folder}{video.sl}'
        run(command, segment_log, 'log')


# Funções para decodificação
def decode(video: VideoParams):
    """
    :param video:
    :return:
    """
    for video.tile in range(1, video.number_tiles + 1):
        for video.chunk in range(1, video.duration + 1):
            if video.decoder in 'ffmpeg':
                if video.threads in 'multi':
                    command = (f'{video.program} '
                               f'-hide_banner -benchmark -codec hevc -threads 0 -i {video.segment_video}.mp4 '
                               f'-f null -')
                else:
                    command = (f'{video.program} '
                               f'-hide_banner -benchmark -codec hevc -threads 1 -i {video.segment_video}.mp4 '
                               f'-f null -')

            elif video.decoder in 'mp4client':
                if video.threads in 'multi':
                    command = (f'start /b /wait '
                               f'{video.program} -bench {video.segment_video}.mp4')
                else:
                    command = (f'start /b /wait /affinity 0x800 '
                               f'{video.program} -bench {video.segment_video}.mp4')
            else:
                command = ''
                exit('Decoders disponíveis são mp4client e ffmpeg.')
            print(f'Rodada {video.rodada} - {video.basename}_tile{video.tile}_chunk{video.chunk}')
            _run(command, video.dectime_log, 'txt', log_mode='a')


def _run(command, log_path, ext, overwrite=False, log_mode='w', bench_stamp='bench: utime'):
    import shlex
    if os.path.isfile(f'{log_path}.{ext}') and not overwrite and not log_mode in 'a':
        print(f'arquivo {log_path}.{ext} existe. Pulando.')
    else:
        with subprocess.Popen(shlex.split(command),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              encoding='utf-8') as proc, \
                open('temp.txt', 'w', encoding='utf-8') as f:

            for line in proc.stdout:
                if line.find(bench_stamp) >= 0:
                    f.write(line)

        with open('temp.txt', 'r', encoding='utf-8') as f1, \
                open(f'{log_path}.{ext}', log_mode, encoding='utf-8') as f2:
            f2.write(f1.read())

        # attempts = 1
        # while True:
        #     print(command)
        #
        #     try:
        #         # p = subprocess.run(f'{command} 1>2 temp.txt', shell=True, encoding='utf-8')
        #         # print(f'Returncode = {p.returncode}')
        #         with open('temp.txt', 'w', encoding='utf-8') as f:
        #             p = subprocess.run(' '.join(command))
        #             print(f'Returncode = {p.returncode}')
        #             if p.returncode != 0:
        #                 print(f'Tentativa {attempts}. Erro. Exitcode == {p.returncode}. Tentando novamente.')
        #                 attempts += 1
        #                 continue
        #
        #         with open('temp.txt', 'r', encoding='utf-8') as f1, \
        #                 open(f'{log_path}.{ext}', log_mode, encoding='utf-8') as f2:
        #             f2.write(f1.read())
        #             break
        #
        #     except FileNotFoundError:
        #         print(f'Tentativa {attempts}. Erro ao abrir o arquivo {"temp.txt" + ".log"}')
        #         print('Tentando novamente em 5s.')
        #         attempts += 1
        #         time.sleep(5)


# Funções para estatística
def collect_data(video_seg: Video):
    if video_seg.decoder in 'ffmpeg':
        video_seg.bench_stamp = 'bench: utime'
    elif video_seg.decoder in 'mp4client':
        video_seg.bench_stamp = 'frames FPS'

    print(f'Processing {video_seg.basename}.txt')

    for video_seg.tile in range(1, video_seg.num_tiles + 1):
        for video_seg.chunk in range(1, video_seg.duration * video_seg.fps + 1):
            if os.path.isfile(f'{video_seg.segment_path}.mp4'):
                video_seg.size = os.path.getsize(f'{video_seg.segment_path}.mp4')

            if os.path.isfile(f'{video_seg.log_path}.txt'):
                video_seg.times = _get_times(video_seg)

    return dict(video_seg.dectime)


def _get_times(dectime: Video) -> list:
    # with open(f'{dectime.log_path}.txt', 'r') as f:
    try:
        f = open(f'{dectime.log_path}.txt', 'r')
    except FileNotFoundError:
        print(f'O arquivo {dectime.log_path}.txt não existe')
        return [0] * 5

    times = []
    for line in f:
        idx = line.find(dectime.bench_stamp)
        if idx >= 0:
            if dectime.decoder in 'ffmpeg':
                line1 = line.replace('bench: ', ' ')
                line2 = line1.replace('s ', ' ')
                line3 = line2.strip()[:-1]
                line4 = line3.split(' ')
                for i in range(0, 15, 3):
                    try:
                        times.append(float(line4[i][6:]))
                    except IndexError:
                        print(f'O video {dectime.basename} deu faltou o índice {i}.')
    f.close()
    return np.average(times)


# Utilitários e funções gerais
def check_system() -> dict:
    if platform.system() == 'Windows':
        sl = '\\'
        sys = 'windows'
        ffmpeg = 'ffmpeg.exe'
        mp4box = 'C:\\"Program Files"\\GPAC\\MP4Box.exe'
        mp4client = 'C:\\"Program Files"\\GPAC\\MP4Client.exe'
        kvazaar = 'bin\\kvazaar.exe'
        siti = 'bin\\SITI.exe'
    else:
        sl = '/'
        sys = 'unix'
        ffmpeg = 'ffmpeg'
        mp4box = 'MP4Box'
        kvazaar = 'kvazaar'
        siti = 'bin/siti'
        mp4client = 'MP4Client'

    programs = dict(sl=sl,
                    sys=sys,
                    ffmpeg=ffmpeg,
                    mp4box=mp4box,
                    kvazaar=kvazaar,
                    siti=siti,
                    mp4client=mp4client)
    return programs


def save_json(obj: dict, filename: str):
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=2)


def load_json(filename: str = 'times.json') -> dict:
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def show_json(obj: dict, show=True, ret=False):
    output = json.dumps(obj, indent=2)
    if show:
        print(output)
    if ret:
        return output


def makedir(dirname: str):
    os.makedirs(dirname, exist_ok=True)
