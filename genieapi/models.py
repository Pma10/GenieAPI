from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json
import os

@dataclass
class Song:
    """노래 정보를 담는 데이터 클래스"""
    id: str
    title: str
    artist: str
    album: str
    album_id: str
    thumbnail_url: str
    duration: Optional[str] = None  # 상세 정보에서 확인 가능
    genre: Optional[str] = None     # 상세 정보에서 확인 가능
    release_date: Optional[str] = None # 상세 정보에서 확인 가능
    lyricist: Optional[str] = None
    composer: Optional[str] = None
    arranger: Optional[str] = None

    @property
    def url(self) -> str:
        return f"https://www.genie.co.kr/detail/songInfo?xgnm={self.id}"

@dataclass
class Lyric:
    """가사 정보를 담는 데이터 클래스"""
    song_id: str
    raw_lyrics: Dict[str, str]

    def to_lrc(self, output_path: Optional[str] = None) -> str:
        """LRC 형식의 문자열로 변환하거나 파일로 저장합니다."""
        lrc_lines = [
            f"[{int(time_ms) // 60000:02}:{(int(time_ms) % 60000) // 1000:02}.{(int(time_ms) % 1000) // 10:02}] {lyric}"
            for time_ms, lyric in sorted(self.raw_lyrics.items(), key=lambda x: int(x[0]))
        ]
        content = "\n".join(lrc_lines)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return output_path
        return content

@dataclass
class ChartEntry:
    """차트 순위 정보를 담는 데이터 클래스"""
    rank: int
    song: Song
    rank_change: str  # "new", "keep", "up", "down" 등
    rank_change_value: int = 0

@dataclass
class Playlist:
    """플레이리스트 정보를 담는 데이터 클래스"""
    id: str
    title: str
    songs: List[Song] = field(default_factory=list)

@dataclass
class Album:
    """앨범 정보를 담는 데이터 클래스"""
    id: str
    title: str
    artist: str
    image_url: str
    genre: Optional[str] = None
    publisher: Optional[str] = None
    agency: Optional[str] = None
    release_date: Optional[str] = None
    description: Optional[str] = None
    tracklist: List[Song] = field(default_factory=list)
