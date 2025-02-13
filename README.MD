```markdown
# GenieAPI 🎵

**GenieAPI**는 [Genie Music](https://www.genie.co.kr/) 데이터를 쉽게 가져올 수 있는 Python API 라이브러리입니다.

## 주요 기능 ✨
- **곡 정보 가져오기:**  
  - 검색어를 입력하면 해당 곡의 정보를 가져옵니다.
  - 반환되는 정보는 **곡 제목 (title)**, **곡 ID (id)**, **아티스트/앨범 정보 (추가 정보)**, **앨범 아트(썸네일) URL** 등을 포함합니다.
- **싱크 가사 다운로드:**  
  - 특정 곡의 ID를 사용하여 싱크 가사가 포함된 `.lrc` 파일을 생성합니다.
  - 생성된 파일은 `result` 폴더에 저장됩니다.

## 설치 방법 🛠️

```bash
pip install GenieAPI
```

## 사용 방법 💡

```python
from genieapi import GenieAPI

# GenieAPI 인스턴스 생성
genie = GenieAPI()

# 1. 곡 정보 검색
# "APT ROSE"라는 곡을 검색하여 1개의 결과를 가져옵니다.
song = genie.search_song("APT ROSE", limit=1)
# 반환 예시: [{'title': 'APT ROSE', 'id': '12345678', 'artist': 'APT - Debut Album', 'thumbnail': 'https://thumbnail.link/...'}]
print(song)

# 2. 싱크 가사 다운로드
# 검색 결과에서 첫 번째 곡의 ID(song[0]['id'])를 사용하여 가사를 다운로드합니다.
genie.get_lyrics(song[0]['id'])
```

- **APT ROSE:** 검색할 곡 제목  
- **limit=1:** 가져올 곡의 개수 (기본값: 1)
```
