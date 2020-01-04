import datetime
from dateutil.parser import parse
from googleapiclient.discovery import build
import pymysql

from util import DEVELOPER_KEY_LIST, DEVELOPER_AUTH_LIST
from util.load import load_search_list
from database.connector import DataBase

YOUTUBE_API_VERSION = "v3"
YOUTUBE_API_SERVICE_NAME = "youtube"


class YouTubeSearch:

    def __init__(self, api_call_limit, developer_key_index):
        self.api_call_limit = api_call_limit  # limit number of search items
        developer_key = DEVELOPER_KEY_LIST[developer_key_index]
        developer_auth = DEVELOPER_AUTH_LIST[developer_key_index]
        print(developer_key, developer_auth)
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=developer_key)
        self.db = DataBase()

    def search_list(self, skip=0, file_path='SEARCHLIST.txt'):
        games = load_search_list(file_path)
        for i, game in enumerate(games):
            if i < skip:
                continue
            self.search(name=game['name'], add='game', appid=game['appid'])

    def search(self, name='None', add='game', appid=0, db_insert=True, verbose=False):
        items = []
        keyword = name + ' ' + add
        print("search query | ", keyword)
        next_page_token = None
        api_call_cnt = 0  # api 호출 횟수 (1번 호출당 검색결과 50개씩 반환)
        while api_call_cnt < self.api_call_limit:
            # API request
            api_call_cnt += 1
            response = self.youtube.search().list(
                part="snippet",
                maxResults=50,
                q=keyword,
                pageToken=next_page_token
            ).execute()

            # response parsing
            next_page_token = response.get('nextPageToken', None)
            for item in response['items']:
                video_id = item['id'].get('videoId', None)
                video_title = pymysql.escape_string(item['snippet'].get('title', ''))
                channel_id = item['snippet'].get('channelId', '')
                channel_title = pymysql.escape_string(item['snippet'].get('channelTitle', ''))
                publish_date = parse(item['snippet'].get('publishedAt', None)).strftime('%Y-%m-%d %H-%M-%S')
                description = pymysql.escape_string(item['snippet'].get('description', ''))
                now = datetime.datetime.now().strftime('%Y-%m-%d')

                if video_id is None:
                    continue

                items.append(
                    {'appid': int(appid),
                     'gameName': name,
                     'query': keyword,
                     'videoId': video_id,
                     'videoTitle': video_title,
                     'channelId': channel_id,
                     'channelTitle': channel_title,
                     'description': description,
                     'pub_date': publish_date,
                     'date': now}
                )
                if verbose:
                    print(keyword, '|', video_id, video_title, channel_id, channel_title, description,
                          publish_date, now)

                # 종료조건 2 : 더이상 검색 결과가 없으면 종료 (next page token 없으면)
                if next_page_token is None:
                    break

        print("API call is completed")

        SQL = """
        INSERT INTO yt_videoidsearch
        (`id`,
        `appid`,
        `gameName`,
        `query`,
        `videoId`,
        `videoTitle`,
        `channelId`,
        `channelTitle`,
        `description`,
        `pub_date`,
        `date`)
        VALUES
        (NULL, {appid}, '{gameName}', '{query}', '{videoId}', '{videoTitle}', '{channelId}', '{channelTitle}',
         '{description}', '{pub_date}', '{date}'
        )
        """
        if db_insert:
            for i in items:
                self.db.cur.execute(
                    SQL.format(appid=i['appid'], gameName=i['gameName'], query=i['query'], videoId=i['videoId'],
                               videoTitle=i['videoTitle'], channelId=i['channelId'], channelTitle=i['channelTitle'],
                               description=i['description'], pub_date=i['pub_date'], date=i['date']))

        print('db insert in completed')
