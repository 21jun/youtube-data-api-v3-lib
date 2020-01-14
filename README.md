## Installation

Windows10, python 3.6+

```sh
pip install -r requirements.txt
```

> 또는 가상환경 설정후 설치

```sh
python -m venv venv
venv\Script\Acivate
```

```sh
pip install -r requirements.txt
```

### Database 설치
```
database\connector.py 에서 mysql 접속 설정
```
```
video_info.sql
videoidsearch.sql 
두 파일으로 테이블 생성
```

### API KEY 설정
`APIKEYLIST.txt` 파일을 생성하고,

```
AIz------your api key------2UWVv4UNv3Hs 이 뒤로는 메모 (쉽게 관리하기 위해 해당 계정의 ID/PW를 적어둠)
AIz------your api key------2UWVv4UNv3Hs ID PW
... 
```

위와 같이 APIKEY를 한줄에 하나씩 적어둠


## Usage

### youtube 키워드 검색

`SEARCHLIST.txt` 에 검색할 게임 목록 붙여넣기

(appid) (gameName) 순서


`main.py`에서 

```py
from youtube.search import YouTubeSearch
# 비디오 검색
yt_search = YouTubeSearch(api_call_limit=2, developer_key_index=4)
# API KEY의 할당량을 초과하여 다시 수집할때는
# 이미 수집된 결과만큼 skip에 할당 (SEARCHLIST.txt)
yt_search.search_list(skip=0) 
```

`videoidsearch` 테이블에 저장


### youtube video 정보 수집

`main.py`에서 

```py
from youtube.video import YouTubeVideo

yt_video = YouTubeVideo(developer_key_index=6)

# 한 videoId 에 대해서 수집
yt_video.get_video_info(appid, name, video_id)

# videoidsearch 에 존재하는 모든 video에 대해서 수집
# 수집중 API KEY의 할당량이 끝나는 경우.
# 다른 API KEY를 사용하여 진행
# 이때, 이미 수집한 video_info 수를 Skip으로 넣어줌  
yt_video.get_video_info_list(skip=18)
```

`video_info` 테이블에 저장