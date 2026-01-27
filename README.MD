# GenieAPI

지니뮤직(genie.co.kr)의 비공식 Python API 래퍼입니다. 이 라이브러리를 사용하면 노래 검색, 실시간 차트 조회, 가사 추출, 그리고 노래 및 앨범의 상세 정보를 쉽게 가져올 수 있습니다.

## 주요 기능

-   **노래 검색:** 검색어를 통해 노래 목록과 메타데이터를 조회합니다.
-   **실시간 차트:** Top 200 실시간 차트 순위를 가져옵니다.
-   **노래 상세 정보:** 곡의 장르, 재생 시간, 작사/작곡/편곡자 등 상세 정보를 조회합니다.
-   **앨범 상세 정보:** 앨범의 아티스트, 발매일, 수록곡 목록(Tracklist) 등을 조회합니다.
-   **가사 추출:** 타임스탬프가 포함된 가사 데이터를 가져옵니다.
-   **플레이리스트:** 공개된 플레이리스트의 수록곡을 가져옵니다.

## 설치 방법

이 프로젝트는 Python 3.8 이상을 필요로 하며, 다음 라이브러리에 의존합니다:

```bash
pip install requests beautifulsoup4
```

## 사용 방법

```python
from genieapi import GenieAPI

genie = GenieAPI()

# 1. 노래 검색
songs = genie.search_song("Ditto")
if songs:
    print(f"검색 결과: {songs[0].title} - {songs[0].artist}")

# 2. 실시간 Top 200 차트 조회
chart = genie.get_chart_top200()
for entry in chart[:5]:
    print(f"{entry.rank}위: {entry.song.title} - {entry.song.artist}")

# 3. 노래 상세 정보 조회
detail = genie.get_song_detail("99570005") # Ditto 의 ID
if detail:
    print(f"제목: {detail.title}, 재생시간: {detail.duration}")
    print(f"작사가: {detail.lyricist}")

# 4. 앨범 상세 정보 조회
album = genie.get_album_detail("83325577") # NewJeans 'OMG' 앨범 ID
if album:
    print(f"앨범명: {album.title}, 아티스트: {album.artist}, 발매일: {album.release_date}")
    print("수록곡 목록:")
    for track in album.tracklist:
        print(f" - {track.title}")
```

## 프로젝트 구조

-   `genieapi/`: 메인 패키지 디렉토리
    -   `GenieAPI.py`: 네트워크 요청 및 API의 메인 엔트리 포인트
    -   `parsers.py`: HTML 파싱 로직을 담당하는 순수 함수 모듈
    -   `models.py`: 데이터 모델 (Song, Album, Lyric, ChartEntry)
    -   `Error.py`: 사용자 정의 예외 클래스

## 주의사항

이 API는 공식적인 방법이 아닌 웹 스크래핑을 통해 동작하므로, 지니뮤직 사이트의 구조 변경에 따라 동작하지 않을 수 있습니다. 교육 및 연구 목적으로만 사용하시기 바라며, 과도한 요청은 자제해 주세요.
