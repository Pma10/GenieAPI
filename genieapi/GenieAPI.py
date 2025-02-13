import os
import json
import requests
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from genieapi.Error import GenieScraperError


class GenieAPI:
    """지니뮤직 API"""

    def __init__(self):
        self.SEARCH_BASE_URL = "https://www.genie.co.kr/search/searchAuto"
        self.SONG_INFO_BASE_URL = "https://www.genie.co.kr/detail/songInfo?xgnm="
        self.LYRICS_BASE_URL = "https://dn.genie.co.kr/app/purchase/get_msl.asp?path=a&songid="

    def _get_request_headers(self) -> dict:
        """브라우저를 모방한 요청 헤더 생성."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def search_song(self, query: str, limit: int = 4) -> List[Dict[str, str]]:
        """
        지니뮤직에서 노래 검색.

        입력값:
            query (str): 검색할 노래 이름
            limit (int, optional): 검색 결과 제한. 기본값은 4.

        반환값:
            각 노래 정보를 담은 dictionary 리스트.
            각 dictionary는 다음 키를 포함합니다:
                - title: 노래 제목
                - id: 노래 ID
                - artist: 아티스트 이름
                - thumbnail: 썸네일 URL
        """
        try:
            response = requests.get(
                self.SEARCH_BASE_URL,
                params={"query": query},
                headers=self._get_request_headers()
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for song in data.get("song", [])[:limit]:
                song_id = song.get("id", "")
                artist, _ = self._parse_genie_extra_info(song.get("field1", ""))
                thumbnail = self._get_album_art_url(song_id)
                results.append({
                    "title": song.get("word", ""),
                    "id": song_id,
                    "artist": artist,
                    "thumbnail": thumbnail or "없음"
                })

            return results

        except requests.RequestException as e:
            raise GenieScraperError(f"검색 요청 실패: {e}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise GenieScraperError(f"예상치 못한 응답 형식: {e}")

    def _parse_genie_extra_info(self, extra_info: str) -> Tuple[str, str]:
        """추가 정보에서 아티스트와 앨범 분리"""
        parts = extra_info.split(' - ', 1)
        artist = parts[0].strip()
        album = parts[1].strip() if len(parts) > 1 else ""
        return artist, album

    def _get_album_art_url(self, song_id: str) -> Optional[str]:
        """지니뮤직에서 앨범 아트 URL 가져오기"""
        try:
            response = requests.get(
                f"{self.SONG_INFO_BASE_URL}{song_id}",
                headers=self._get_request_headers()
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            album_img = soup.select_one('div.photo-zone span.cover > img')
            if album_img and 'src' in album_img.attrs:
                img_url = album_img['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                return img_url.replace('/dims/resize/Q_80,0', '')
        except Exception as e:
            print(f"[DEBUG] 앨범 아트 URL 가져오기 실패: {e}")
        return None

    def get_lyrics(self, song_id: str) -> Optional[str]:
        """주어진 노래 ID의 가사 조회."""
        try:
            response = requests.get(
                f"{self.LYRICS_BASE_URL}{song_id}",
                headers=self._get_request_headers()
            )
            response.raise_for_status()
            lyrics_json_str = response.text[
                response.text.index("(") + 1:response.text.rindex(")")
            ]
            return self._make_lrc_file(song_id, lyrics_json_str)
        except requests.RequestException as e:
            raise GenieScraperError(f"가사 조회 실패: {e}")
        except (ValueError, json.JSONDecodeError) as e:
            raise GenieScraperError(f"잘못된 가사 형식: {e}")

    def _make_lrc_file(self, file_name: str, lyrics_json: str) -> str:
        """동기화된 가사를 가진 LRC 파일 생성."""
        os.makedirs("result", exist_ok=True)
        try:
            lyrics_data = json.loads(lyrics_json)
        except json.JSONDecodeError as e:
            raise GenieScraperError(f"가사 JSON 파싱 실패: {e}")

        output_path = os.path.join("result", f"{file_name}.lrc")
        lrc_lines = [
            f"[{int(time_ms) // 60000:02}:{(int(time_ms) % 60000) // 1000:02}.{(int(time_ms) % 1000) // 10:02}] {lyric}"
            for time_ms, lyric in sorted(lyrics_data.items(), key=lambda x: int(x[0]))
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lrc_lines))
        print(f"[GENIEAPI] LRC 파일 생성: {output_path}")
        return output_path
