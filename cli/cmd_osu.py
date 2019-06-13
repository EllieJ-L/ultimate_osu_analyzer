import time

from osu.local.beatmap.beatmapIO import BeatmapIO
from osu.local.replay.replayIO import ReplayIO

from misc.callback import callback


class CmdOsu():

    @staticmethod
    def open_replay_file(replay_filepath):
        return ReplayIO.open_replay(replay_filepath)
        

    @staticmethod
    def save_web_beatmaps(web_beatmaps):
        '''
        In: [ WebBeatmap, ... ]
        '''
        for web_beatmap in web_beatmaps:
            web_beatmap.download_beatmap('tmp/beatmaps/')
            time.sleep(0.1)


    @staticmethod
    def save_web_replays(web_replays):
        '''
        In: [ WebReplay, ... ]
        '''
        for web_replay in web_replays:
            web_replay.download_replay('tmp/replays/')
            time.sleep(10)


    @staticmethod
    @callback
    def create_score_offset_graph(replay_data):
        CmdOsu.create_score_offset_graph.emit(replay_data)


    @staticmethod
    @callback
    def create_cursor_velocity_graph(replay_data):
        CmdOsu.create_cursor_velocity_graph.emit(replay_data)


    @staticmethod
    @callback
    def create_cursor_acceleration_graph(replay_data):
        CmdOsu.create_cursor_acceleration_graph.emit(replay_data)


    @staticmethod
    @callback
    def create_cursor_jerk_graph(replay_data):
        CmdOsu.create_cursor_jerk_graph.emit(replay_data)