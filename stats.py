#!/bin/python3
# coding=utf-8
import os
from itertools import product as it

import fitter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors

from utils import util

sl = util.check_system()['sl']

project = 'times_12videos_scale'
config = util.Config('Config.json')
dectime = util.load_json('times_12videos_scale.json')
color_list = ['blue', 'orange', 'green', 'red']


def main():
    # psnr()  # Processar psnr também.
    # stats()
    # graph1()
    # graph2()
    # graph3()
    # graph2a()
    # graph3()
    # hist1()
    # hist1samefig()
    # hist1sameplt()
    # hist2samefig()
    # hist2sameplt()
    # hist3samefig()
    # hist3sameplt()
    pass


def stats():
    # Configura os objetos
    config = util.Config('config.json')

    # Base object
    video_seg = util.Video(config=config)
    video_seg.project = f'results{sl}ffmpeg_scale_12videos_60s'
    video_seg.factor = 'scale'
    video_seg.segment_base = 'segment'
    video_seg.dectime_base = f'dectime_ffmpeg'
    video_seg.bench_stamp = 'bench: utime'
    video_seg.multithread = 'single'

    video_seg.quality_list = config.quality_list

    for video_seg.name in config.videos_list:
        for video_seg.fmt in config.tile_list:
            for video_seg.quality in config.quality_list:
                print(f'Processing {video_seg.basename}.txt')

                for video_seg.tile in range(1, video_seg.num_tiles + 1):
                    chunks = video_seg.duration * video_seg.fps

                    for video_seg.chunk in range(1, chunks + 1):
                        # Processing segment size (bytes)
                        file = video_seg.segment_path + '.mp4'
                        if os.path.isfile(file):
                            video_seg.size = os.path.getsize(file)

                        # Processing decoding time
                        file = video_seg.log_path + '.txt'
                        if os.path.isfile(file):
                            times = []
                            f = open(file, 'r', encoding='utf-8')

                            for line in f:
                                if line.find(video_seg.bench_stamp) >= 0:
                                    # Pharse da antiga decodificação
                                    if video_seg.factor in 'crf':
                                        line = line.replace('bench: ', ' ')
                                        line = line.replace('s ', ' ')
                                        line = line.strip()[:-1]
                                        line = line.split(' ')
                                        for i in range(0, len(line), 3):
                                            times.append(float(line[i][6:]))

                                    elif video_seg.factor in 'scale':
                                        line = line.split(' ')[1]
                                        line = line.split('=')[1]
                                        times.append(float(line[:-1]))
                            f.close()

                            video_seg.times = np.average(times)

    util.save_json(dict(video_seg.dectime), 'times_12videos_scale.json')


def graph1(graph_folder='1_graph1-tiles-chunks_x_dec_time'):
    """
    tiles-chunksXdec_time (seconds) and chunks X file_size (Bytes)
    :return:
    """
    dirname = f'{sl}results{sl}{project}{sl}{graph_folder}'
    os.makedirs(dirname, exist_ok=True)

    for name in config.videos_list:
        group = config.videos_list[name]['group']

        for fmt in config.tile_list:
            m, n = list(map(int, fmt.split('x')))

            for quality in config.quality_list:
                title = f'{group}-{name}-{fmt}-{quality}'

                plt.close()
                fig, ax = plt.subplots(1, 2, figsize=(19, 6))

                # plota os chunks de todos os tiles de um video-fmt-quality
                for tile in range(1, m * n + 1):
                    print(f'Processing {title}-tile{tile}')
                    time, size, corr = get_data_chunks(name=name,
                                                       fmt=fmt,
                                                       quality=quality,
                                                       tile=tile)

                    ax[0].plot(time, label=(f'tile={tile}, '
                                            f'corr={corr: .3f}'))
                    ax[1].plot(size, label=(f'tile={tile}, '
                                            f'corr={corr: .3f}'))

                # Configura o plot
                for i, axes in enumerate(ax):
                    if i == 0:
                        axes.set_ylabel('Times (s)')
                        axes.set_title(f'{title}-{config.factor}{quality} '
                                       f'- Times by chunks')
                    elif i == 1:
                        axes.set_ylabel('Rates (bps)')
                        axes.set_title(f'{title}-{config.factor}{quality} '
                                       f'- Rates by chunks')
                    axes.set_xlabel('Chunks')
                    axes.set_ylim(bottom=0)
                    axes.legend(loc='upper left', ncol=2,
                                bbox_to_anchor=(1.01, 1.0))

                plt.tight_layout()

                savename = (f'{dirname}{sl}'
                            f'{group}-'
                            f'{name}_{fmt}_{config.factor}{quality}')

                print(f'Salvando {savename}.png')
                fig.savefig(f'{savename}')
                # fig.show()
                print('')


def graph2(graph_folder='2_graph2-quality-chunks_x_dec_time'):
    """
    quality-chunksXdec_time (seconds) and chunks X file_size (Bytes)
    :return:
    """
    dirname = f'{sl}results{sl}{project}{sl}{graph_folder}'
    os.makedirs(dirname, exist_ok=True)

    for name in config.videos_list:
        group = config.videos_list[name]['group']

        for fmt in config.tile_list:
            m, n = list(map(int, fmt.split('x')))

            for tile in range(1, m * n + 1):
                title = f'{group}-{name}-{fmt}-{tile}'

                plt.close()
                fig, ax = plt.subplots(1, 2, figsize=(19, 6))

                # plota os chunks de todos as qualidades de um video-fmt-tile
                for quality in config.quality_list:
                    print(f'Processing {title}-{config.factor}{quality}')
                    time, size, corr = get_data_chunks(name=name,
                                                       fmt=fmt,
                                                       quality=quality,
                                                       tile=tile)

                    ax[0].plot(time, label=(f'{config.factor}={quality}, '
                                            f'corr={corr: .3f}'))
                    ax[1].plot(size, label=(f'{config.factor}={quality}, '
                                            f'corr={corr: .3f}'))

                # Configura o plot
                for i, axes in enumerate(ax):
                    if i == 0:
                        axes.set_ylabel('Time/Tile (s)')
                        axes.set_title(f'{title}-tile{tile} '
                                       f'- Times by chunks')
                    elif i == 1:
                        axes.set_ylabel('Rate/Tile (bps)')
                        axes.set_title(f'{title}-tile{tile} '
                                       f'- Rates by chunks')
                    axes.set_xlabel('Chunks')
                    axes.set_ylim(bottom=0)
                    axes.legend(loc='upper left', ncol=2,
                                bbox_to_anchor=(1.01, 1.0))

                plt.tight_layout()

                savename = (f'{dirname}{sl}'
                            f'{group}-'
                            f'{name}_{fmt}_{config.factor}_tile{tile}')

                print(f'Salvando {savename}.png')
                fig.savefig(f'{savename}')
                # fig.show()
                print('')


def graph3(graph_folder='3_graph3_heatmap'):
    """
    bar
    tile X average_dec_time (seconds) and tile X average_rate (Bytes)
    :return: None
    """
    dirname = f'{sl}results{sl}{project}{sl}{graph_folder}'
    os.makedirs(dirname, exist_ok=True)

    for name in config.videos_list:
        group = config.videos_list[name]['group']

        for fmt in config.tile_list:
            m, n = list(map(int, fmt.split('x')))

            # Figure
            plt.close()
            fig = plt.figure(figsize=(10, 8), dpi=150)

            # Axes
            axes = [fig.add_subplot(4, 1, 1),
                    fig.add_subplot(4, 1, 2)]

            ax_hmt, ax_hms = [], []
            for x in range(9, 13): ax_hmt.append(fig.add_subplot(4, 4, x))
            for x in range(13, 17): ax_hms.append(fig.add_subplot(4, 4, x))

            # Bar config
            offset = 0
            width = 0.8 / len(config.crf_list)
            start_position = (0.8 - width) / 2

            average_time, average_size = {}, {}
            std_time, std_size = {}, {}
            c1, c2 = [], []  # colections of heatmap

            # Para cada qualidade
            for count, quality in enumerate(config.crf_list):
                heatmap = make_heatmap(name, fmt, quality)

                average_time[quality] = heatmap.average_time
                average_size[quality] = heatmap.average_size
                std_time[quality] = heatmap.std_time
                std_size[quality] = heatmap.std_size
                frame_time = heatmap.frame_time
                frame_size = heatmap.frame_size

                # Calcula a média dos chunks para cada tile
                # for tile, m_, n_ in it(range(1, m * n + 1),
                #                        range(1, m + 1),
                #                        range(1, n + 1)):
                #     # Coleta dados de todos os chunks
                #     time, size, _ = get_data_chunks(name, fmt, quality, tile)
                #
                #     # Anexa as médias e desvios padrões
                #     average_time[quality].append(np.average(time))
                #     average_size[quality].append(np.average(size))
                #     std_time[quality].append(np.std(time))
                #     std_size[quality].append(np.std(size))
                #
                #     # Preenche a matriz do heatmap
                #     frame1[n_ - 1, m_ - 1] = average_time[quality][-1]
                #     frame2[n_ - 1, m_ - 1] = average_size[quality][-1]

                # Plota dois bar

                x = np.arange(1, m * n + 1)
                # O eixo X, o numero de chunks
                x = x - start_position + offset
                corr = np.corrcoef(x=(average_time[quality],
                                      average_size[quality]))[1][0]
                axes[0].bar(x, average_time[quality],
                            yerr=std_time[quality],
                            width=width,
                            label=f'crf={quality}_corr={corr: .3f}')
                axes[1].bar(x, average_size[quality],
                            yerr=std_size[quality],
                            width=width,
                            label=f'crf={quality}')
                offset += width

                # Configura Bar
                for ax in axes:
                    ax.set_xlabel('Tile')
                    ax.set_ylim(bottom=0)
                    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))
                axes[0].set_title(f'{name} - Times by tiles, tile={fmt}')
                axes[1].set_title(f'{name} - Rates by tiles, tile={fmt}')
                axes[0].set_ylabel('Average Time (s)')
                axes[1].set_ylabel('Average Rate (bps)')
                axes[1].ticklabel_format(style='sci', axis='Y',
                                         scilimits=(6, 6))

                # Plota um Pcolor (Heatmap) e pega sua collection
                c1.append(ax_hmt[count].pcolor(frame_time, cmap='jet'))
                c2.append(ax_hms[count].pcolor(frame_size, cmap='jet'))

                # Configura os eixos do heatmap da qualidade atual
                ax_hms[count].set_title('Rate Heatmap')
                ax_hms[count].set_xticklabels([])
                ax_hms[count].set_yticklabels([])

                ax_hmt[count].set_title('time Heatmap')
                ax_hmt[count].set_xlabel(f'crf={quality}')
                ax_hmt[count].set_xticklabels([])
                ax_hmt[count].set_yticklabels([])

            # Normaliza heatmap
            vmin1 = min(collection.get_array().min() for collection in c1)
            vmax1 = max(collection.get_array().max() for collection in c1)
            vmin2 = min(collection.get_array().min() for collection in c2)
            vmax2 = max(collection.get_array().max() for collection in c2)

            norm1 = colors.Normalize(vmin=vmin1, vmax=vmax1)
            norm2 = colors.Normalize(vmin=vmin2, vmax=vmax2)
            for collection1, collection2 in zip(c1, c2):
                collection1.set_norm(norm1)
                collection2.set_norm(norm2)

            # Colorbar
            fig.colorbar(c1[-1], ax=ax_hmt,
                         orientation='vertical', fraction=.04)
            fig.colorbar(c2[-1], ax=ax_hms,
                         orientation='vertical', fraction=.04)
            plt.tight_layout()

            # Finaliza
            print(f'Salvando {dirname}{sl}{name}_{fmt}.')
            fig.savefig(f'{dirname}{sl}{group}-{name}_{fmt}')
            # plt.show()
            print('')


def hist1samefig(graph_folder="hist1samefig"):
    """ Compara os histogramas. Para cada video-fmt plota todas as qualidades
    (agrega tiles e chunks)
    :return:
    """
    dirname = f'{project}{sl}results{sl}{graph_folder}'
    best_dist_df = util.AutoDict()
    times = util.AutoDict()
    sizes = util.AutoDict()

    os.makedirs(f'{dirname}', exist_ok=True)

    # Coleta dados
    iterator = it(config.videos_list, config.tile_list, config.quality_list)
    for name, fmt, quality in list(iterator):
        m, n = list(map(int, fmt.split('x')))
        times[name][fmt][quality] = []
        sizes[name][fmt][quality] = []

        for tile, chunk in list(it(range(1, m * n + 1),
                                   range(1, config.duration + 1))):
            if name in 'ninja_turtles' and chunk > 58: continue
            t = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['times']
            s = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['size']
            times[name][fmt][quality].append(t)
            sizes[name][fmt][quality].append(s)

    # Calcular melhores fit e plota
    for name, fmt in list(it(config.videos_list, config.tile_list)):
        # Faz um fit por name-fmt-qualidade
        dists = ['alpha', 'beta', 'cauchy', 'chi', 'chi2', 'expon', 'gamma',
                 'gilbrat', 'laplace', 'levy', 'norm', 'pareto', 'rice', 't',
                 'uniform']

        fitter_dict = {}
        for quality in config.quality_list:
            data = times[name][fmt][quality]
            col_label = f'{fmt}-{quality}'

            # Faz o fit
            f = fitter.fitter.Fitter(data, bins=100, distributions=dists,
                                     verbose=False)
            fitter_dict[quality] = f
            fitter_dict[quality].fit()

            # Procura os menores SSE
            short_sse = fitter_dict[quality]
            short_sse = short_sse.df_errors
            short_sse = short_sse.sort_values(by="sumsquare_error")
            short_sse = short_sse.index[0]

            # Melhor fit
            sse = fitter_dict[quality].df_errors["sumsquare_error"][short_sse]
            best_dist_df[name][col_label] = f'{short_sse}, SSE={sse: .1f}'

        # Para cada video e fmt cria uma figura. cuidado. se mudar o formato do
        # gráfico vai ter que mudar tudo dentro da função.
        plt.close()
        fig = plt.figure(figsize=(13, 9), dpi=150)

        color_it = iter(color_list)
        m, n = list(map(int, fmt.split('x')))
        ax_rate = fig.add_subplot(3, 2, 5)
        ax_cdf = fig.add_subplot(3, 2, 6)

        for idx, quality in enumerate(config.quality_list, 1):
            color = next(color_it)

            ###############################################################
            # plota o histograma desta qualidade
            t_avg = np.average(times[name][fmt][quality])
            t_std = np.std(times[name][fmt][quality])
            t_ct = np.average(times[name][fmt][quality]) * (m * n)

            label = (f'dectime_avg={t_avg:.03f} s\n'
                     f'dectime_std={t_std:.03f} s\n'
                     f'time/chunk/tile={t_ct:.03f} s')

            ax = fig.add_subplot(3, 2, idx, sharex=ax_cdf)
            ax.hist(times[name][fmt][quality], color=color, bins=100,
                    histtype='bar',
                    density=True, label=label)
            ax.set_title(f'{name}, {fmt}, crf {quality}')
            ax.set_ylabel("PDF")
            ax.set_xlabel('Decoder Times')

            ###############################################################
            # plota os 3 best fit para esta qualidade
            best_dists = fitter_dict[quality].df_errors
            best_dists = best_dists.sort_values(by="sumsquare_error")
            best_dists = best_dists.index[0:3]

            for dist_name in best_dists:
                sse = fitter_dict[quality]
                sse = sse.df_errors["sumsquare_error"][dist_name]
                label = f'{dist_name},\nSSE = {sse: .3f}'
                ax.plot(fitter_dict[quality].x,
                        fitter_dict[quality].fitted_pdf[dist_name],
                        label=label)
            ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

            ###############################################################
            # plota o bar da taxa para esta qualidade
            s_avg = np.average(sizes[name][fmt][quality]) * 8
            s_std = np.std(sizes[name][fmt][quality]) * 8
            s_ct = np.average(sizes[name][fmt][quality]) * 8
            label = (f'rate_avg={s_avg / 1000:,.0f} Kbps\n'
                     f'rate_std={s_std / 1000:,.0f} Kbps\n'
                     f'rate/tile={s_ct / (1000 * m * n):.03f} kbps')
            ax_rate.bar(idx - 1, s_avg, color=color, yerr=s_std, label=label)
            ax_rate.set_title('Rate')
            ax_rate.set_ylabel("Rate (10³ bps)")
            ax_rate.set_xlabel("Decoder Time (s)")
            ax_rate.ticklabel_format(axis='y', style='scientific',
                                     scilimits=(3, 3))
            ax_rate.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

            ###############################################################
            # plota a CDF para esta qualidade
            label = f'{name}_{fmt}_crf{quality}'
            ax_cdf.hist(times[name][fmt][quality], color=color, bins=100,
                        density=True, cumulative=True, histtype='step',
                        label=label)
            ax_cdf.set_title('CDF')
            ax_cdf.set_ylabel("CDF")
            ax_cdf.set_xlabel("Decoder Time (s)")
            ax_cdf.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

        ax_rate.set_xticklabels(['0'] + config.quality_list)
        plt.tight_layout()
        grupo = config.videos_list[name]["grupo"]
        fig.savefig(f'{dirname}{sl}{grupo}-hist_{name}_{fmt}')
        # plt.show()
        print(f'hist_{name}_{fmt}')

    # Salva melhores fits em um csv
    best_dist_df = pd.DataFrame(best_dist_df)
    best_dist_df.to_csv(f'{dirname}{config.sl}best_dist.csv')


def hist1sameplt(graph_folder="hist1sameplt"):
    """ Compara os histogramas. Para cada video-fmt plota todas as qualidades
    (agrega tiles e chunks)
    :return:
    """
    dirname = f'{project}{sl}results{sl}{graph_folder}'
    times = util.AutoDict()
    sizes = util.AutoDict()

    os.makedirs(f'{dirname}', exist_ok=True)

    # Coleta dados
    for name, fmt, quality in it(config.videos_list, config.tile_list,
                                 config.quality_list):
        m, n = list(map(int, fmt.split('x')))
        times[name][fmt][quality] = []
        sizes[name][fmt][quality] = []

        for tile, chunk in it(range(1, m * n + 1),
                              range(1, config.duration + 1)):
            if name in 'ninja_turtles' and chunk > 58: continue
            t = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['times']
            s = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['size']
            times[name][fmt][quality].append(t)
            sizes[name][fmt][quality].append(s)

    # Calcular melhores fit e plota
    for name, fmt in it(config.videos_list, config.tile_list):
        # Para cada video e fmt cria uma figura. cuidado. se mudar o formato do
        # gráfico vai ter que mudar tudo dentro da função.
        plt.close()
        fig = plt.figure(figsize=(13, 9), dpi=150)

        color_it = iter(color_list)
        m, n = list(map(int, fmt.split('x')))
        ax_cdf = fig.add_subplot(2, 1, 2)
        ax = fig.add_subplot(2, 1, 1, sharex=ax_cdf)

        for idx, quality in enumerate(config.quality_list, 1):
            color = next(color_it)

            ###############################################################
            # plota o histograma desta qualidade
            t_avg = np.average(times[name][fmt][quality])
            t_std = np.std(times[name][fmt][quality])
            t_ct = np.average(times[name][fmt][quality]) * (m * n)

            label = (f'dectime_avg={t_avg:.03f} s\n'
                     f'dectime_std={t_std:.03f} s\n'
                     f'time/chunk/tile={t_ct:.03f} s')

            ax.hist(times[name][fmt][quality], color=color, bins=100,
                    histtype='bar', density=True, label=label)
            ax.set_title(f'{name}, {fmt}, crf {quality}')
            ax.set_ylabel("PDF")
            ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

            ###############################################################
            # plota a CDF para esta qualidade
            label = f'{name}_{fmt}_crf{quality}'
            ax_cdf.hist(times[name][fmt][quality], color=color, bins=100,
                        density=True, cumulative=True, histtype='step',
                        label=label)
            ax_cdf.set_title('CDF')
            ax_cdf.set_ylabel("CDF")
            ax_cdf.set_xlabel("Decoder Time (s)")
            ax_cdf.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

        plt.tight_layout()
        grupo = config.videos_list[name]["grupo"]
        fig.savefig(f'{dirname}{sl}{grupo}-hist_{name}_{fmt}')
        # plt.show()
        print(f'hist_{name}_{fmt}')


def hist2samefig(graph_folder="hist2samefig"):
    """ Compara os histogramas. Para cada video-fmt plota todas as qualidades
    (agrega tiles e chunks)
    :return:
    """
    dirname = f'{project}{sl}{graph_folder}'
    best_dist_df = util.AutoDict()
    times = util.AutoDict()
    sizes = util.AutoDict()

    os.makedirs(f'{dirname}', exist_ok=True)

    # Coleta dados
    for name, fmt, quality in it(config.videos_list, config.tile_list,
                                 config.quality_list):
        m, n = list(map(int, fmt.split('x')))
        times[name][fmt][quality] = []
        sizes[name][fmt][quality] = []

        for tile, chunk in it(range(1, m * n + 1),
                              range(1, config.duration + 1)):
            if name in 'ninja_turtles' and chunk > 58: continue
            t = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['times']
            s = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['size']
            times[name][fmt][quality].append(t)
            sizes[name][fmt][quality].append(s)

    # Calcular melhores fit e plota
    for name, quality in it(config.videos_list, config.quality_list):
        # Faz um fit por name-fmt-qualidade
        dists = ['alpha', 'beta', 'cauchy', 'chi', 'chi2', 'expon', 'gamma',
                 'gilbrat', 'laplace', 'levy', 'norm', 'pareto', 'rice', 't',
                 'uniform']

        fitter_dict = {}
        for fmt in config.tile_list:
            data = times[name][fmt][quality]
            col_label = f'{fmt}-{quality}'

            # Faz o fit
            f = fitter.fitter.Fitter(data, bins=100, distributions=dists,
                                     verbose=False)
            fitter_dict[fmt] = f
            fitter_dict[fmt].fit()

            # Procura os menores SSE
            short_sse = fitter_dict[fmt]
            short_sse = short_sse.df_errors
            short_sse = short_sse.sort_values(by="sumsquare_error")
            short_sse = short_sse.index[0]

            # Melhor fit
            sse = fitter_dict[fmt].df_errors["sumsquare_error"][short_sse]
            best_dist_df[name][col_label] = f'{short_sse}, SSE={sse: .1f}'

        # Para cada video e fmt cria uma figura. cuidado. se mudar o formato do
        # gráfico vai ter que mudar tudo dentro da função.
        plt.close()
        fig = plt.figure(figsize=(13, 9), dpi=150)

        color_it = iter(color_list)
        ax_rate = fig.add_subplot(3, 2, 5)
        ax_cdf = fig.add_subplot(3, 2, 6)

        for idx, fmt in enumerate(config.tile_list, 1):
            color = next(color_it)
            m, n = list(map(int, fmt.split('x')))

            ###############################################################
            # plota o histograma desta qualidade
            t_avg = np.average(times[name][fmt][quality])
            t_std = np.std(times[name][fmt][quality])
            t_ct = np.average(times[name][fmt][quality]) * (m * n)

            label = (f'dectime_avg={t_avg:.03f} s\n'
                     f'dectime_std={t_std:.03f} s\n'
                     f'time/chunk/tile={t_ct:.03f} s')

            ax = fig.add_subplot(3, 2, idx, sharex=ax_cdf)
            ax.hist(times[name][fmt][quality], color=color, bins=100,
                    histtype='bar',
                    density=True, label=label)
            ax.set_title(f'{name}, crf {quality}, {fmt}')
            ax.set_ylabel("PDF")
            ax.set_xlabel('Decoder Times')

            ###############################################################
            # plota os 3 best fit para esta qualidade
            best_dists = fitter_dict[fmt].df_errors
            best_dists = best_dists.sort_values(by="sumsquare_error")
            best_dists = best_dists.index[0:3]

            for dist_name in best_dists:
                sse = fitter_dict[fmt]
                sse = sse.df_errors["sumsquare_error"][dist_name]
                label = f'{dist_name},\nSSE = {sse: .3f}'
                ax.plot(fitter_dict[fmt].x,
                        fitter_dict[fmt].fitted_pdf[dist_name],
                        label=label)
            ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

            ###############################################################
            # plota o bar da taxa para esta qualidade
            s_avg = np.average(sizes[name][fmt][quality]) * 8
            s_std = np.std(sizes[name][fmt][quality]) * 8
            s_ct = np.average(sizes[name][fmt][quality]) * 8
            label = (f'rate_avg={s_avg / 1000:,.0f} Kbps\n'
                     f'rate_std={s_std / 1000:,.0f} Kbps\n'
                     f'rate/tile={s_ct / (1000 * m * n):.03f} kbps')
            ax_rate.bar(idx, s_avg, color=color, yerr=s_std, label=label)
            ax_rate.set_title('Rate')
            ax_rate.set_ylabel("Rate (10³ bps)")
            ax_rate.set_xlabel("Decoder Time (s)")
            ax_rate.ticklabel_format(axis='y', style='scientific',
                                     scilimits=(3, 3))
            ax_rate.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

            ###############################################################
            # plota a CDF para esta qualidade
            label = f'{name}_crf{quality}_{fmt}'
            ax_cdf.hist(times[name][fmt][quality], color=color, bins=100,
                        density=True, cumulative=True, histtype='step',
                        label=label)
            ax_cdf.set_title('CDF')
            ax_cdf.set_ylabel("CDF")
            ax_cdf.set_xlabel("Decoder Time (s)")
            ax_cdf.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

        ax_rate.set_xticklabels(['0'] + config.tile_list)
        plt.tight_layout()
        grupo = config.videos_list[name]["grupo"]
        fig.savefig(f'{dirname}{sl}{grupo}-hist_{name}_{quality}')
        # plt.show()
        print(f'hist_{name}_{quality}')

    # Salva melhores fits em um csv
    # best_dist_df = pd.DataFrame(best_dist_df)
    # best_dist_df.to_csv(f'{dirname}{config.sl}best_dist.csv')


def hist2sameplt(graph_folder="hist2sameplt"):
    """ Compara os histogramas. Para cada video-fmt plota todas as qualidades
    (agrega tiles e chunks)
    :return:
    """
    dirname = f'results{sl}{graph_folder}'
    times = util.AutoDict()
    sizes = util.AutoDict()

    os.makedirs(f'{dirname}', exist_ok=True)

    # Coleta dados
    for name, fmt, quality in it(config.videos_list, config.tile_list,
                                 config.quality_list):
        m, n = list(map(int, fmt.split('x')))
        times[name][fmt][quality] = []
        sizes[name][fmt][quality] = []

        for tile, chunk in it(range(1, m * n + 1),
                              range(1, config.duration + 1)):
            if name in 'ninja_turtles' and chunk > 58: continue
            t = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['times']
            s = dectime[name][fmt][str(quality)][str(tile)][str(chunk)]['size']
            times[name][fmt][quality].append(t)
            sizes[name][fmt][quality].append(s)

    # Calcular melhores fit e plota
    for name, quality in it(config.videos_list, config.quality_list):
        # Para cada video e fmt cria uma figura. cuidado. se mudar o formato do
        # gráfico vai ter que mudar tudo dentro da função.
        plt.close()
        fig = plt.figure(figsize=(13, 9), dpi=150)

        color_it = iter(color_list)
        ax_cdf = fig.add_subplot(2, 1, 2)
        ax = fig.add_subplot(2, 1, 1, sharex=ax_cdf)

        for idx, fmt in enumerate(config.tile_list, 1):
            color = next(color_it)
            m, n = list(map(int, fmt.split('x')))

            ###############################################################
            # plota o histograma desta qualidade
            t_avg = np.average(times[name][fmt][quality])
            t_std = np.std(times[name][fmt][quality])
            t_ct = np.average(times[name][fmt][quality]) * (m * n)

            label = (f'dectime_avg={t_avg:.03f} s\n'
                     f'dectime_std={t_std:.03f} s\n'
                     f'time/chunk/tile={t_ct:.03f} s')

            ax.hist(times[name][fmt][quality], color=color, bins=100,
                    histtype='bar', density=True, label=label)
            ax.set_title(f'{name}, crf {quality}, {fmt}')
            ax.set_ylabel("PDF")
            ax.set_xlabel('Decoder Times')
            ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

            ###############################################################
            # plota a CDF para esta qualidade
            label = f'{name}_crf{quality}_{fmt}'
            ax_cdf.hist(times[name][fmt][quality], color=color, bins=100,
                        density=True, cumulative=True, histtype='step',
                        label=label)
            ax_cdf.set_title('CDF')
            ax_cdf.set_ylabel("CDF")
            ax_cdf.set_xlabel("Decoder Time (s)")
            ax_cdf.legend(loc='upper left', bbox_to_anchor=(1.01, 1.0))

        plt.tight_layout()
        grupo = config.videos_list[name]["grupo"]
        fig.savefig(f'{dirname}{sl}{grupo}-hist_{name}_{quality}')
        # plt.show()
        print(f'hist_{name}_{quality}')

    # Salva melhores fits em um csv
    # best_dist_df = pd.DataFrame(best_dist_df)
    # best_dist_df.to_csv(f'{dirname}{config.sl}best_dist.csv')


def get_data_fmt(name):
    size = []
    time = []

    for fmt in config.tile_list:
        t, s, corr = get_data_quality(name, fmt)
        time.extend(t)
        size.extend(s)

    corr = np.corrcoef((time, size))[1][0]
    return time, size, corr


def get_data_quality(name, fmt):
    size = []
    time = []

    for quality in config.quality_list:
        t, s, corr = get_data_tiles(name, fmt, quality)
        time.extend(t)
        size.extend(s)

    corr = np.corrcoef((time, size))[1][0]
    return time, size, corr


def get_data_tiles(name, fmt, quality):
    size = []
    time = []
    m_, n_ = list(map(int, fmt.split('x')))

    for tile in range(1, m_ * n_ + 1):
        t, s, corr = get_data_chunks(name, fmt, quality, tile)
        time.extend(t)
        size.extend(s)

    corr = np.corrcoef((time, size))[1][0]
    return time, size, corr


def get_data_chunks(name, fmt, quality, tile):
    size = []
    time = []

    # Lista todos os chunks
    for chunk in range(1, config.duration + 1):
        if name in 'ninja_turtles' and chunk > 58: continue
        dec = dectime[name]
        dec = dec[fmt]
        dec = dec[str(quality)]
        dec = dec[str(tile)]
        dec = dec[str(chunk)]
        s = dec['size']
        t = dec['times']
        size.append(float(s) * 8)
        time.append(float(t))

    # Plota os dados
    corr = np.corrcoef((time, size))[1][0]
    return time, size, corr


class Heatmap:
    def __init__(self, m, n):
        self.average_time = []
        self.average_size = []
        self.std_time = []
        self.std_size = []
        self.frame_time = np.zeros((n, m))
        self.frame_size = np.zeros((n, m))


def make_heatmap(name, fmt, quality):
    m, n = list(map(int, fmt.split('x')))
    heatmap = Heatmap(m, n)

    for tile, x, y in it(range(1, m * n + 1),
                         range(1, m + 1),
                         range(1, n + 1)):
        # Coleta dados de todos os chunks
        time, size, _ = get_data_chunks(name, fmt, quality, tile)

        time = np.average(time)
        size = np.average(size)

        heatmap.average_time.append(time)
        heatmap.average_size.append(size)
        heatmap.std_time.append(np.std(time))
        heatmap.std_size.append(np.std(size))

        # Preenche a matriz do heatmap
        heatmap.frame_time[y - 1, x - 1] = time
        heatmap.frame_size[y - 1, x - 1] = size

    return heatmap


if __name__ == "__main__":
    main()
