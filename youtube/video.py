import datetime
from dateutil.parser import parse
from googleapiclient.discovery import build
import pymysql

from util import DEVELOPER_KEY_LIST, DEVELOPER_AUTH_LIST
from database.connector import DataBase

YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_SERVICE_NAME = "youtube"

"""
DATABASE used:
yt_videoidsearch
yt_video_info
"""


class YouTubeVideo:

    def __init__(self, developer_key_index):
        self.developer_key = DEVELOPER_KEY_LIST[developer_key_index]
        self.developer_auth = DEVELOPER_AUTH_LIST[developer_key_index]
        print(self.developer_key, self.developer_auth)

        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.developer_key)
        self.db = DataBase()

    def fetch_all_games(self):
        SQL = "SELECT appid, gameName from yt_videoidsearch group by appid;"
        self.db.cur.execute(SQL)

        games = self.db.cur.fetchall()
        games = [{'appid': game[0], 'name': game[1]} for game in games]
        return games

    def fetch_video_ids(self, appid='', name='', qtype='appid'):
        """
        :param qtype: 쿼리 타입 appid 이면 appid 로 검색, name 이면 gameName 으로 검색
        :return: [appid, gameName, videoId] 리스트
        """
        if qtype == 'appid':
            SQL = "SELECT appid, gameName, videoId from yt_videoidsearch where appid={appid};"
            self.db.cur.execute(SQL.format(appid=appid))
        elif qtype == 'name':
            SQL = "SELECT appid, gameName, videoId from yt_videoidsearch where gameName={name};"
            self.db.cur.execute(SQL.format(name=name))

        video_ids = self.db.cur.fetchall()
        video_ids = [{'appid': id[0], 'name': id[1], 'videoId': id[2]} for id in video_ids]
        return video_ids

    def get_video_info_list(self, skip=0):
        games = self.fetch_all_games()
        for i, game in enumerate(games):
            if i < skip:
                continue
            print(game['appid'], game['name'])
            video_ids = self.fetch_video_ids(game['appid'])
            for video_id in video_ids:
                self.get_video_info(game['appid'], game['name'], video_id['videoId'])
                print("|", end="", flush=True)
            print("")

    def get_video_info(self, appid, name, video_id):
        video_info = self.youtube.videos().list(
            part="snippet, statistics, contentDetails",
            id=video_id
        ).execute()

        snippet = video_info['items'][0]['snippet']

        pub_date = parse(snippet['publishedAt']).strftime('%Y-%m-%d %H-%M-%S')
        channel_id = snippet['channelId']
        title = pymysql.escape_string(snippet.get('title', ""))
        description = pymysql.escape_string(snippet.get('description', ""))

        statistics = video_info['items'][0]['statistics']

        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        dislike_count = int(statistics.get('dislikeCount', 0))
        favorite_count = int(statistics.get('favoriteCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        now = datetime.datetime.now().strftime('%Y-%m-%d')

        SQL = """
        INSERT INTO `yt`.`yt_video_info`
        (`id`,
        `appid`,
        `gameName`,
        `videoId`,
        `videoTitle`,
        `channelId`,
        `description`,
        `viewCount`,
        `likeCount`,
        `dislikeCount`,
        `favoriteCount`,
        `commentCount`,
        `pub_date`,
        `date`)
        VALUES
        (NULL,
        {appid},
        '{name}',
        '{video_id}',
        '{title}',
        '{channel_id}',
        '{description}',
        {view_count},
        {like_count},
        {dislike_count},
        {favorite_count},
        {comment_count},
        '{pub_date}',
        '{date}');
        """
        self.db.cur.execute(SQL.format(appid=appid, name=name, video_id=video_id, title=title, channel_id=channel_id,
                                       description=description, view_count=view_count, like_count=like_count,
                                       dislike_count=dislike_count,
                                       favorite_count=favorite_count,
                                       comment_count=comment_count, pub_date=pub_date, date=now))
