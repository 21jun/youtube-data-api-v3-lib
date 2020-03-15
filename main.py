from youtube.search import YouTubeSearch
from youtube.video import YouTubeVideo
from youtube.comment import YouTubeComment

"""
https://developers.google.com/youtube/v3/determine_quota_cost?hl=ko
https://developers.google.com/youtube/v3/docs/videos?hl=ko#resource
https://developers.google.com/youtube/v3/docs/search/list?hl=ko&apix_params=%7B%22part%22%3A%22id%22%7D
"""

# 비디오 검색
# yt_search = YouTubeSearch(api_call_limit=4, developer_key_index=3)
# yt_search.search_list(skip=72)


# 비디오 정보 저장
'''
SELECT * FROM yt.yt_video_info;
SELECT * FROM yt.yt_video_info group by appid;	
ALTER TABLE yt_video_info AUTO_INCREMENT = 1762;
'''

# TODO: oasis.yt_videoidsearch 에서 date 3/15 만 골라내고(OK), 이 중에서 기존 비디오와 겹치는거 제거해서 video_info video.py 다시 뽑자

custom_SQL = """
SELECT B.appid, B.gameName, B.videoId FROM
(SELECT * FROM yt_videoidsearch where date !="2020-03-15 00:00:00") A RIGHT JOIN
(SELECT appid, gameName, videoId from yt_videoidsearch where date ="2020-03-15 00:00:00")B ON A.videoId = B.videoId WHERE A.videoId is NULL and B.appid={appid};
"""

yt_video = YouTubeVideo(developer_key_index=3)
yt_video.get_video_info_list(skip=23, file_path="TARGETLIST.txt", qtype="file", db_insert=True, condition=' AND date = "2020-03-15"', custom_SQL=custom_SQL)



# 비디오 댓글 저장
# yt_comment = YouTubeComment(developer_key_index=0)
# # yt_comment.get_comments(videoId='QUYXlMFlhlk', verbose=True, db_insert=False, gameName='d', appid=0000, channelId='1')
# yt_comment.get_comment_list(db_insert=False,file_path="TEST.txt")
