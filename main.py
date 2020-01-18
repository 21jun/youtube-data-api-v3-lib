from youtube.search import YouTubeSearch
from youtube.video import YouTubeVideo
from youtube.comment import YouTubeComment

"""
https://developers.google.com/youtube/v3/determine_quota_cost?hl=ko
https://developers.google.com/youtube/v3/docs/videos?hl=ko#resource
https://developers.google.com/youtube/v3/docs/search/list?hl=ko&apix_params=%7B%22part%22%3A%22id%22%7D
"""

# 비디오 검색
# yt_search = YouTubeSearch(api_call_limit=2, developer_key_index=4)
# yt_search.search_list(skip=0)


# 비디오 정보 저장
'''
SELECT * FROM yt.yt_video_info;
SELECT * FROM yt.yt_video_info group by appid;	
ALTER TABLE yt_video_info AUTO_INCREMENT = 1762;
'''
# yt_video = YouTubeVideo(developer_key_index=6)
# yt_video.get_video_info_list(skip=18)


# 비디오 댓글 저장
yt_comment = YouTubeComment(developer_key_index=0)
# yt_comment.get_comments(videoId='QUYXlMFlhlk', verbose=True, db_insert=False, gameName='d', appid=0000, channelId='1')
yt_comment.comment_list(skip=3)
