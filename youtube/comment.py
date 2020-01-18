import datetime
from dateutil.parser import parse
from googleapiclient.discovery import build
from langdetect import detect
import pymysql
import re

from util import DEVELOPER_KEY_LIST, DEVELOPER_AUTH_LIST
from database.connector import DataBase

YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_SERVICE_NAME = "youtube"

"""
DATABASE used:
yt_comment_steam
"""


class YouTubeComment:
    
    def __init__(self, developer_key_index):
        self.developer_key = DEVELOPER_KEY_LIST[developer_key_index]
        self.developer_auth = DEVELOPER_AUTH_LIST[developer_key_index]
        print(self.developer_key, self.developer_auth)

        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.developer_key)
        self.db = DataBase()

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
        except:
            print("error")
            return None

    def get_comments(self, videoId, db_insert=True, verbose=False):

        next_page_token = ''
        further = True
        comment_count = 0
        SQL="""
        INSERT INTO yt_comment_steam
        (`channelId`,
        `videoId`,
        `author`,
        `authorId`,
        `likecount`,
        `publishDate`,
        `text`,
        `language`,
        `char_length`,
        `date`)
        VALUES
        ('{channelId}',
        '{videoId}',
        '{author}',
        '{authorId}',
        {likecount},
        '{publishDate}',
        '{text}',
        '{language}',
        {char_length},
        '{date}';
        """

        while further:
            print(comment_count, end=' ', flush=True)
            results = self._get_comment_threads(videoId, next_page_token)
            if results is None:
                return
            next_page_token = ''

            for item in results["items"]:
                try:
                    comment_count += 1
                    comment = item["snippet"]["topLevelComment"]
                    author = re.sub('[^가-힝0-9a-zA-Z\\s]', '', comment["snippet"]["authorDisplayName"])
                    authorId = comment["snippet"]["authorChannelId"]["value"]
                    likeCount = comment["snippet"]["likeCount"]
                    publishedAt = parse(comment["snippet"]["publishedAt"], ignoretz=True)
                    text = pymysql.escape_string(comment["snippet"]["textDisplay"].replace('\n', ' '))
                    text_length = len(text)
                    text_1000 = text[:1000]
                    language = 'none'
                    if text_length >= 2:
                        try:
                            language = detect(text_1000)
                        except:
                            pass
                    
                    if db_insert:
                        self.db.cur.execute(SQL.format(channelId='-----', videoId=videoId, author=author, authorId=authorId))
                        
                    if verbose:
                        print(videoId, author, authorId, likeCount, publishedAt, text_1000, language, text_length)

                except:
                    print("ERROR|", end='')
            else:  # for-else
                try:
                    next_page_token = results["nextPageToken"]
                except KeyError as e:
                    print(e,"is None", "|", videoId, "is Done, total comments =", comment_count)
                    further = False