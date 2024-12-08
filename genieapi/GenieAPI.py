import os
import json
import requests
from typing import List, Tuple, Optional
from genieapi.Error import GenieScraperError



class GenieAPI:
    """지니뮤직 가사 불러오기 클래스"""

    def __init__(self):
        """지니뮤직 검색 및 가사 조회를 위한 기본 URL 초기화."""
        self.LYRICS_BASE_URL = "https://dn.genie.co.kr/app/purchase/get_msl.asp?path=a&songid="
        self.SEARCH_BASE_URL = "https://www.genie.co.kr/search/searchAuto"

    def _get_request_headers(self) -> dict:
        """브라우저를 모방한 요청 헤더 생성."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search_song(self, song_name: str, limit: int = 1) -> List[Tuple[str, str, str]]:
        """
        지니뮤직에서 노래 검색.

        입력값:
            song_name (str): 검색할 노래 이름
            limit (int, optional): 검색 결과 제한. 기본값은 1.

        반환값:
            (노래 이름, 노래 ID, 추가 필드)의 튜플 리스트
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
            for i in range(min(limit, len(data.get('song', [])))):
                song = data['song'][i]
                songs.append((song['word'], song['id'], song.get('field1', '')))

            return songs

        except requests.RequestException as e:
            raise GenieScraperError(f"검색 요청 실패: {e}")
        except (KeyError, IndexError) as e:
            raise GenieScraperError(f"예상치 못한 응답 형식: {e}")

    def get_lyrics(self, song_id: str) -> Optional[str]:
        """
        주어진 노래 ID의 가사 조회.

        입력값:
            song_id (str): 노래 고유 식별자

        반환값:
            생성된 LRC 파일 경로 또는 None
        """
        try:
            response = requests.get(
                self.LYRICS_BASE_URL + song_id,
                headers=self._get_request_headers()
            )
            response.raise_for_status()

            lyrics_json_str = response.text[response.text.index("(") + 1:response.text.rindex(")")]
            return self._make_lrc_file(song_id, lyrics_json_str)

        except requests.RequestException as e:
            raise GenieScraperError(f"가사 조회 실패: {e}")
        except (ValueError, json.JSONDecodeError) as e:
            raise GenieScraperError(f"잘못된 가사 형식: {e}")

    def _make_lrc_file(self, file_name: str, lyrics_json: str) -> str:
        """
        동기화된 가사를 가진 LRC 파일 생성.

        입력값:
            file_name (str): 출력 파일 기본 이름
            lyrics_json (str): 가사와 타임스탬프를 포함한 JSON 문자열

        반환값:
            생성된 LRC 파일 경로
        """
        os.makedirs("result", exist_ok=True)

        lyrics_data = json.loads(lyrics_json)
        output_path = os.path.join("result", f"{file_name}.lrc")

        with open(output_path, "w", encoding="utf-8") as f:
            # 타임스탬프 정렬 및 LRC 형식화
            lrc_lines = [
                f"[{int(time_ms) // 60000:02}:{(int(time_ms) % 60000) // 1000:02}.{(int(time_ms) % 1000) // 10:02}] {lyric}"
                for time_ms, lyric in sorted(lyrics_data.items(), key=lambda x: int(x[0]))
            ]
            f.write("\n".join(lrc_lines))
        print(f"[GENIEAPI] LRC 파일 생성: {output_path}")
        return output_path
