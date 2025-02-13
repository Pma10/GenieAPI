import os
import json
import requests
from typing import List, Dict, Optional
from genieapi.Error import GenieScraperError
from bs4 import BeautifulSoup


class GenieAPI:
    """지니뮤직 API"""

    def __init__(self):
        self.LYRICS_BASE_URL = "https://dn.genie.co.kr/app/purchase/get_msl.asp?path=a&songid="
        self.SEARCH_BASE_URL = "https://www.genie.co.kr/search/searchAuto"
        # 앨범정보 관련 URL (썸네일과 발매일 정보를 추출)
        self.ALBUM_INFO_URL = "https://www.genie.co.kr/detail/albumInfo"

    def _get_request_headers(self) -> dict:
        """브라우저를 모방한 요청 헤더 생성."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def _get_thumbnail_url(self, song_id: str) -> Optional[str]:
        """
        노래의 썸네일 URL을 가져옵니다.
        URL 예: {앨범정보 URL}?xgnm={song_id}
        """
        try:
            url = f"{self.ALBUM_INFO_URL}?xgnm={song_id}"
            response = requests.get(url, headers=self._get_request_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            album_img = soup.select_one("div.photo-zone span.cover > img")
            if album_img and "src" in album_img.attrs:
                img_url = album_img["src"]
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                return img_url.replace("/dims/resize/Q_80,0", "")
        except Exception as e:
            print(f"[DEBUG] 썸네일 URL 가져오기 실패: {e}")
        return None

    def _get_release_date(self, song_id: str) -> Optional[str]:
        """
        노래의 발매일 정보를 가져옵니다.
        URL 예: https://www.genie.co.kr/detail/albumInfo?axnm={song_id}
        CSS Selector: #body-content > div.album-detail-infos > div.info-zone > ul > li:nth-child(5) > span.value
        """
        try:
            url = f"{self.ALBUM_INFO_URL}?axnm={song_id}"
            response = requests.get(url, headers=self._get_request_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            release_elem = soup.select_one(
                "#body-content > div.album-detail-infos > div.info-zone > ul > li:nth-child(5) > span.value"
            )
            if release_elem:
                return release_elem.text.strip()
        except Exception as e:
            print(f"[DEBUG] 발매일 정보 가져오기 실패: {e}")
        return None

    def search_song(self, song_name: str, limit: int = 1) -> List[Dict[str, str]]:
        """
        지니뮤직에서 노래 검색.
        
        입력:
            song_name (str): 검색할 노래 이름
            limit (int, optional): 검색 결과 제한 (1~4). 기본값은 1.
        
        반환:
            각 노래 정보를 담은 dictionary 리스트.
            각 dictionary는 다음 키를 포함:
                - title: 노래 제목
                - id: 노래 ID
                - extra: 추가 정보 (예: 아티스트/앨범)
                - thumbnail: 썸네일 URL
                - release_date: 발매일 정보
        """
        if not 1 <= limit <= 4:
            raise ValueError("limit 값은 1에서 4 사이여야 합니다.")

        try:
            response = requests.get(
                self.SEARCH_BASE_URL,
                params={"query": song_name},
                headers=self._get_request_headers()
            )
            response.raise_for_status()
            data = response.json()

            songs = []
            for song in data.get("song", [])[:limit]:
                song_id = song.get("id")
                thumbnail = self._get_thumbnail_url(song_id)
                release_date = self._get_release_date(song_id)
                songs.append({
                    "title": song.get("word", ""),
                    "id": song_id,
                    "extra": song.get("field1", ""),
                    "thumbnail": thumbnail or "",
                    "release_date": release_date or ""
                })

            return songs

        except requests.RequestException as e:
            raise GenieScraperError(f"검색 요청 실패: {e}")
        except (KeyError, IndexError) as e:
            raise GenieScraperError(f"예상치 못한 응답 형식: {e}")

    def get_lyrics(self, song_id: str) -> Optional[str]:
        """
        주어진 노래 ID의 가사를 조회하여 LRC 파일을 생성합니다.
        
        입력:
            song_id (str): 노래 고유 식별자
        
        반환:
            생성된 LRC 파일 경로 (str) 또는 None
        """
        try:
            url = self.LYRICS_BASE_URL + song_id
            response = requests.get(url, headers=self._get_request_headers())
            response.raise_for_status()

            # JSONP 형식의 응답에서 괄호 안의 JSON 문자열 추출
            text = response.text
            json_str = text[text.index("(") + 1 : text.rindex(")")]
            return self._make_lrc_file(song_id, json_str)

        except requests.RequestException as e:
            raise GenieScraperError(f"가사 조회 실패: {e}")
        except (ValueError, json.JSONDecodeError) as e:
            raise GenieScraperError(f"잘못된 가사 형식: {e}")

    def _make_lrc_file(self, file_name: str, lyrics_json: str) -> str:
        """
        동기화된 가사를 가진 LRC 파일을 생성합니다.
        
        입력:
            file_name (str): 출력 파일의 기본 이름
            lyrics_json (str): 가사와 타임스탬프를 포함한 JSON 문자열
        
        반환:
            생성된 LRC 파일의 경로 (str)
        """
        os.makedirs("result", exist_ok=True)
        try:
            lyrics_data = json.loads(lyrics_json)
        except json.JSONDecodeError as e:
            raise GenieScraperError(f"가사 JSON 파싱 실패: {e}")

        output_path = os.path.join("result", f"{file_name}.lrc")
        lrc_lines = []
        for time_ms, lyric in sorted(lyrics_data.items(), key=lambda x: int(x[0])):
            minutes = int(time_ms) // 60000
            seconds = (int(time_ms) % 60000) // 1000
            centiseconds = (int(time_ms) % 1000) // 10
            lrc_lines.append(f"[{minutes:02}:{seconds:02}.{centiseconds:02}] {lyric}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lrc_lines))
        print(f"[GENIEAPI] LRC 파일 생성: {output_path}")
        return output_path
