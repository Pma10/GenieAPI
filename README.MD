# GenieAPI 🎵

**GenieAPI**는 [Genie Music](https://www.genie.co.kr/) 데이터를 쉽게 가져올 수 있는 Python API 라이브러리입니다.

## 주요 기능 ✨
- 곡 정보 가져오기
- 싱크 가사 다운로드 하기

## 설치 방법 🛠️

    ```bash
    pip install GenieAPI
    ```

## 사용 방법 💡

    ```python
    from genieapi import GenieAPI

    genie = GenieAPI()
    song = genie.search_song("APT ROSE", limit=1)

    genie.get_lyrics(song[0][1])
    ```

- **APT ROSE**: 검색할 곡 제목  
- **limit=1**: 가져올 곡의 개수 (기본값: 1)
