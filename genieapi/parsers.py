from bs4 import BeautifulSoup
from typing import List, Optional, Dict
import re
import json
from .models import Song, Lyric, ChartEntry, Playlist, Album

def parse_song_row(row: BeautifulSoup) -> Optional[Song]:
    """테이블 행(tr.list)에서 노래 정보 추출"""
    try:
        song_id = row["songid"]
        
        info_td = row.select_one("td.info")
        title_elem = info_td.select_one("a.title")
        artist_elem = info_td.select_one("a.artist")
        album_elem = info_td.select_one("a.albumtitle")
        
        title = ""
        if title_elem:
            # 1. title 속성 우선
            title = title_elem.get("title", "").strip()
            # 2. text 사용하되 '재생' 등 불용어 제외
            if not title or title == "재생":
                text = title_elem.text.strip()
                if text != "재생":
                    title = text
            # 3. 여전히 재생이면 a.title 태그 구조를 더 명확히 파악해야 함. 보통 a.title.ellipsis를 씀.
        
        artist = ""
        if artist_elem:
            artist = artist_elem.get("title", "").strip() or artist_elem.text.strip()
            
        album = ""
        album_id = ""
        if album_elem:
            album = album_elem.get("title", "").strip() or album_elem.text.strip()
            # onclick="fnViewAlbumLayer('83325577');return false;"
            # or href with axnm
            onclick = album_elem.get("onclick", "")
            if "fnViewAlbumLayer" in onclick:
                match = re.search(r"fnViewAlbumLayer\('(\d+)'\)", onclick)
                if match:
                    album_id = match.group(1)
            elif "fnGoMore" in onclick:
                    match = re.search(r"fnGoMore\('albumInfo','(\d+)'\)", onclick)
                    if match:
                        album_id = match.group(1)

        cover_img = row.select_one("a.cover img")
        thumbnail = f"https:{cover_img['src']}" if cover_img else ""
        if thumbnail:
            thumbnail = thumbnail.replace("//", "https://").split("/dims/")[0]

        return Song(
            id=song_id,
            title=title,
            artist=artist,
            album=album,
            album_id=album_id,
            thumbnail_url=thumbnail
        )
    except Exception:
        return None

def parse_song_detail(soup: BeautifulSoup, song_id: str) -> Optional[Song]:
    """노래 상세 정보 페이지 파싱"""
    info_zone = soup.select_one("div.info-zone")
    
    if not info_zone:
        return None
        
    # 기본 메타데이터
    title_tag = soup.select_one("#body-content > div.song-main-infos > div.info-zone > h2")
    title = ""
    if title_tag:
        title = "".join([t for t in title_tag.contents if isinstance(t, str)]).strip()
        if not title:
                title = title_tag.text.strip()
    
    # 아티스트 & 앨범 추출
    artist = ""
    artist_tag = soup.select_one("div.info-zone > h3.artist") or soup.select_one("div.info-zone > div.artist")
    if artist_tag:
            artist = artist_tag.text.strip()

    # 2. 리스트 파싱 (ul.info-data 또는 ul.list-style)
    li_tags = info_zone.select("ul.info-data li")
    if not li_tags:
        li_tags = info_zone.select("ul.list-style li")

    duration = ""
    genre = ""
    lyricist = ""
    composer = ""
    arranger = ""

    for li in li_tags:
        # Key 찾기: span.attr > img [alt]  OR  span.type
        key = ""
        attr_span = li.select_one("span.attr")
        if attr_span:
            img = attr_span.select_one("img")
            if img and "alt" in img.attrs:
                key = img["alt"]
            else:
                key = attr_span.text.strip()
        
        if not key:
            type_span = li.select_one("span.type")
            if type_span:
                key = type_span.text.strip()

        # Value 찾기
        val = ""
        value_span = li.select_one("span.value")
        if value_span:
            val = value_span.text.strip()
        
        if not key or not val:
            continue

        if "장르" in key:
            genre = val
        elif "재생시간" in key:
            duration = val
        elif "작사가" in key:
            lyricist = val
        elif "작곡가" in key:
            composer = val
        elif "편곡자" in key:
            arranger = val
    
    # 썸네일
    img_tag = soup.select_one("div.photo-zone a img")
    if not img_tag:
            img_tag = soup.select_one("div.photo-zone img") # Fallback
    
    thumbnail = f"https:{img_tag['src']}" if img_tag else ""
    if thumbnail:
        thumbnail = thumbnail.replace("https:https:", "https:") # 가끔 발생하는 중복 프로토콜 방지

    return Song(
        id=song_id,
        title=title,
        artist=artist, 
        album="",
        album_id="",
        thumbnail_url=thumbnail,
        duration=duration,
        genre=genre,
        lyricist=lyricist,
        composer=composer,
        arranger=arranger
    )

def parse_album_detail(soup: BeautifulSoup, album_id: str) -> Optional[Album]:
    """앨범 상세 정보 페이지 파싱"""
    # 1. 앨범 기본 메타데이터
    # 유저 가이드와 달리 실제로는 album-detail-infos 일 수 있음
    info_zone = soup.select_one("div.album-detail-infos div.info-zone")
    if not info_zone:
            info_zone = soup.select_one("div.album-main-infos div.info-zone")
    
    if not info_zone:
        return None

    title = ""
    title_tag = info_zone.select_one("h2.title") or info_zone.select_one("h2.name") or info_zone.select_one("h2")
    if title_tag:
            title = "".join([t for t in title_tag.contents if isinstance(t, str)]).strip()
            if not title:
                title = title_tag.text.strip()
    
    artist = ""
    artist_tag = info_zone.select_one("h3.artist") or info_zone.select_one("div.artist") # sometimes it's div
    if artist_tag:
        artist = artist_tag.text.strip()
    
    genre = ""
    publisher = ""
    agency = ""
    release_date = ""

    # 2. 리스트 파싱
    li_tags = info_zone.select("ul.info-data > li")
    for li in li_tags:
        # The label is often an image with alt text
        img_tag = li.select_one("span.attr img")
        key = ""
        if img_tag:
            key = img_tag.get("alt", "").strip()
        
        # Taking value
        val_span = li.select_one("span.value")
        if not val_span:
            continue
        val_text = val_span.text.strip()

        if "장르" in key:
            genre = val_text
        elif "발매사" in key:
            publisher = val_text
        elif "기획사" in key:
            agency = val_text
        elif "발매일" in key:
            release_date = val_text
        elif "아티스트" in key:
            artist = val_text

    # 3. 앨범 아트
    img_tag = soup.select_one("div.photo-zone a span.cover-img img")
    if not img_tag: 
            img_tag = soup.select_one("div.photo-zone a img")
    
    image_url = f"https:{img_tag['src']}" if img_tag else ""
    if image_url:
        image_url = image_url.replace("https:https:", "https:").split("/dims/")[0]

    # 4. Description
    description = ""
    intro_box = soup.select_one("div.db-description-box")  # classic selector
    if not intro_box:
        # sometimes it's under regular description class
        intro_box = soup.select_one("div.description")
    
    if intro_box:
        description = intro_box.text.strip()

    # 5. 수록곡 목록
    tracklist = []
    # The table often has class 'list-wrap' or is inside 'music-list-wrap'
    track_table = soup.select_one("div.music-list-wrap table.list-wrap")
    if not track_table:
        track_table = soup.select_one("table.list-wrap")

    if track_table:
        # Standard song rows often have class 'list'
        rows = track_table.select("tr.list")
        for row in rows:
            song_obj = parse_song_row(row)
            if song_obj:
                tracklist.append(song_obj)

    return Album(
        id=album_id,
        title=title,
        artist=artist,
        image_url=image_url,
        genre=genre,
        publisher=publisher,
        agency=agency,
        release_date=release_date,
        description=description,
        tracklist=tracklist
    )

def parse_chart_entries(soup: BeautifulSoup) -> List[ChartEntry]:
    """차트 페이지에서 엔트리 목록 파싱"""
    entries = []
    rows = soup.select("table.list-wrap > tbody > tr.list")

    for row in rows:
        try:
            song = parse_song_row(row)
            if not song:
                continue

            # 순위 파싱
            rank_text = row.select_one("td.number").text.split()[0]
            rank = int(rank_text)

            # 순위 변동 파싱
            rank_span = row.select_one("td.number > span")
            rank_change = "keep"
            rank_change_value = 0
            
            if rank_span:
                class_list = rank_span.get("class", [])
                if "rank-up" in class_list:
                    rank_change = "up"
                    rank_change_value = int(rank_span.select_one("span.hide").text)
                elif "rank-down" in class_list:
                    rank_change = "down"
                    rank_change_value = int(rank_span.select_one("span.hide").text)
                elif "rank-new" in class_list:
                    rank_change = "new"

            entries.append(ChartEntry(
                rank=rank,
                song=song,
                rank_change=rank_change,
                rank_change_value=rank_change_value
            ))
        except Exception:
            continue
    
    return entries
