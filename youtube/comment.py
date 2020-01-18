import datetime
from dateutil.parser import parse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langdetect import detect
import pymysql
import re

from util import DEVELOPER_KEY_LIST, DEVELOPER_AUTH_LIST
from util.load import load_target_list
from database.connector import DataBase

YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_SERVICE_NAME = "youtube"

"""
DATABASE used:
yt_comment_steam
yt_videoidsearch
"""


class YouTubeComment:

    def __init__(self, developer_key_index):
        self.developer_key_index = developer_key_index % len(DEVELOPER_KEY_LIST)
        self.developer_key = DEVELOPER_KEY_LIST[self.developer_key_index]
        self.developer_auth = DEVELOPER_AUTH_LIST[self.developer_key_index]
        print(self.developer_key, self.developer_auth)

        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.developer_key)
        self.db = DataBase()

    def _rebuild(self, developer_key_index):
        self.developer_key_index = developer_key_index % len(DEVELOPER_KEY_LIST)
        self.developer_key = DEVELOPER_KEY_LIST[self.developer_key_index]
        self.developer_auth = DEVELOPER_AUTH_LIST[self.developer_key_index]
        print("Rebuilding...")
        print(developer_key_index, '|', self.developer_key, self.developer_auth)
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.developer_key)

    def fetch_video_ids(self, condition=" where date='2020-01-14 00:00:00';"):
        # condition 으로 수집할 비디오 목록만 추림
        SQL = "SELECT appid, gameName, videoId, channelId from yt_videoidsearch"
        SQL = SQL + condition

        self.db.cur.execute(SQL)
        video_ids = self.db.cur.fetchall()
        video_ids = [{'appid': id[0], 'gameName': id[1], 'videoId': id[2], 'channelId': id[3]} for id in video_ids]
        return video_ids

    def comment_list(self, skip=0, file_path='TARGETLIST.txt'):
        print(skip)
        games = load_target_list(file_path)
        for i, game in enumerate(games):
            print("[", i, "/", len(games), ']', game['name'])
            if i < skip:
                continue
            condition = " where appid=" + game['appid']
            video_ids = self.fetch_video_ids(condition=condition)
            print(len(video_ids))

            for j, video in enumerate(video_ids):
                print(j, '/', len(video_ids), video['gameName'], '|', video['appid'], '|', video['videoId'])
                self.get_comments(videoId=video['videoId'], appid=video['appid'], gameName=video['gameName'],
                                  channelId=video['channelId'], db_insert=True, verbose=False)

    def _get_comment_threads(self, videoid, next_page_token):
        try:
            results = self.youtube.commentThreads().list(
                part="snippet",
                maxResults=100,
                videoId=videoid,
                textFormat="plainText",
                pageToken=next_page_token
            ).execute()
            return results
        except HttpError:
            # API KEY 할당량 초과하면 다음 키로 다시 빌드
            self._rebuild(self.developer_key_index + 1)
            return "restart"
        except Exception as e:
            print(e)
            return None

    def get_comments(self, videoId, appid, gameName, channelId, db_insert=True, verbose=False):

        next_page_token = ''
        further = True
        comment_count = 0
        SQL = """
        INSERT INTO yt_comment_steam
        (
        `appid`,
        `gameName`,
        `channelId`,
        `videoId`,
        `author`,
        `authorId`,
        `likeCount`,
        `replyCount`,
        `publishedAt`,
        `text`,
        `language`,
        `char_length`,
        `date`)
        VALUES
        (
        {appid},
        '{gameName}',
        '{channelId}',
        '{videoId}',
        '{author}',
        '{authorId}',
        {likeCount},
        {replyCount},
        '{publishedAt}',
        '{text}',
        '{language}',
        {char_length},
        '{date}');
        """

        while further:
            print(comment_count, end=' ', flush=True)
            results = self._get_comment_threads(videoId, next_page_token)
            if results is None:
                return
            elif results is "restart":
                print("restart comment thread after rebuilding...")
                continue
            next_page_token = ''

            for item in results["items"]:
                try:
                    comment_count += 1
                    comment = item["snippet"]["topLevelComment"]
                    author = re.sub('[^가-힝0-9a-zA-Z\\s]', '', comment["snippet"]["authorDisplayName"])
                    authorId = comment["snippet"]["authorChannelId"]["value"]
                    likeCount = comment["snippet"]["likeCount"]
                    replyCount = item["snippet"]['totalReplyCount']
                    publishedAt = parse(comment["snippet"]["publishedAt"], ignoretz=True).strftime('%Y-%m-%d %H-%M-%S')
                    text = pymysql.escape_string(comment["snippet"]["textDisplay"].replace('\n', ' '))
                    text_length = len(text)
                    text_1000 = text[:1000]
                    language = 'none'
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

                    if text_length >= 2:
                        try:
                            language = detect(text_1000)
                        except:
                            pass

                    if db_insert:
                        self.db.cur.execute(
                            SQL.format(appid=appid, gameName=gameName, channelId=channelId, videoId=videoId,
                                       author=author,
                                       authorId=authorId,
                                       likeCount=likeCount, replyCount=replyCount, publishedAt=publishedAt,
                                       text=text_1000, language=language,
                                       char_length=text_length, date=now))

                    if verbose:
                        print(videoId, author, authorId, likeCount, publishedAt, text_1000, language, text_length)

                except Exception as e:
                    print("ERROR|", e, end='')
            else:  # for-else
                try:
                    next_page_token = results["nextPageToken"]
                except KeyError:
                    print(videoId, "| total comments =", comment_count)
                    further = False
