import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple, Dict
import json
from .models import Song, Lyric, ChartEntry, Playlist, Album
from .Error import GenieScraperError
from . import parsers

class GenieAPI:
    """지니뮤직 API 레퍼 (권장하지 않는 비공식 API)"""

    BASE_URL = "https://www.genie.co.kr"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        })

    def _get_soup(self, url: str, params: Optional[dict] = None) -> BeautifulSoup:
        """URL을 요청하고 BeautifulSoup 객체를 반환합니다."""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            raise GenieScraperError(f"네트워크 요청 실패: {e}")

    def search_song(self, query: str, limit: int = 20) -> List[Song]:
        """
        노래 검색 (더 풍부한 결과를 위해 메인 검색 페이지 파싱)
        """
        url = f"{self.BASE_URL}/search/searchMain"
        soup = self._get_soup(url, params={"query": query})
        
        songs = []
        # selector relaxed for robustness
        rows = soup.select("div.search_song tr.list")
        
        for row in rows[:limit]:
            try:
                song = parsers.parse_song_row(row)
                if song:
                    songs.append(song)
            except Exception as e:
                print(f"[DEBUG] 검색 결과 파싱 오류: {e}")
                continue
                
        return songs

    def get_chart_top200(self, page: int = 1) -> List[ChartEntry]:
        """
        실시간 Top 200 차트 조회
        page 1: 1~50위, page 2: 51~100위 ...
        """
        url = f"{self.BASE_URL}/chart/top200"
        soup = self._get_soup(url, params={"ditc": "D", "ymd": "20230101", "hh": "12", "rtm": "Y", "pg": page}) # 파라미터는 지니 기본값 참조
        return parsers.parse_chart_entries(soup)

    def get_playlist_songs(self, playlist_id: str) -> List[Song]:
        """플레이리스트 수록곡 조회"""
        url = f"{self.BASE_URL}/playlist/detailView"
        soup = self._get_soup(url, params={"plms": playlist_id})
        
        songs = []
        rows = soup.select("#songlist-box > div.music-list-wrap > table > tbody > tr.list")
        
        for row in rows:
            song = parsers.parse_song_row(row)
            if song:
                songs.append(song)
        
        return songs

    def get_lyrics(self, song_id: str) -> Lyric:
        """가사 조회"""
        url = "https://dn.genie.co.kr/app/purchase/get_msl.asp"
        try:
            response = self.session.get(url, params={"path": "a", "songid": song_id})
            response.raise_for_status()
            
            # JSONP response handling: extract json from parentheses
            content = response.text
            if "(" in content and ")" in content:
                json_str = content[content.index("(") + 1 : content.rindex(")")]
                data = json.loads(json_str)
                return Lyric(song_id=song_id, raw_lyrics=data)
            else:
                 raise GenieScraperError("가사 데이터 형식이 올바르지 않습니다.")
                 
        except Exception as e:
            raise GenieScraperError(f"가사 조회 실패: {e}")

    def get_song_detail(self, song_id: str) -> Optional[Song]:
        """
        노래 상세 정보를 조회하여 (장르, 재생시간 등) Song 객체를 반환합니다.
        """
        url = f"{self.BASE_URL}/detail/songInfo"
        try:
            soup = self._get_soup(url, params={"xgnm": song_id})
            return parsers.parse_song_detail(soup, song_id)
        except Exception as e:
            print(f"상세 정보 조회 실패: {e}")
            return None

    def get_album_detail(self, album_id: str) -> Optional[Album]:
        """앨범 상세 정보 조회"""
        url = f"{self.BASE_URL}/detail/albumInfo"
        try:
            soup = self._get_soup(url, params={"axnm": album_id})
            return parsers.parse_album_detail(soup, album_id)
        except Exception as e:
            print(f"앨범 정보 조회 실패: {e}")
            return None
