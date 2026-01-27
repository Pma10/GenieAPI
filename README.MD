# GenieAPI

A robust, unofficial Python wrapper for the Genie Music (genie.co.kr) API. This library allows you to search for songs, fetch charts, retrieve lyrics, and get detailed information about songs and albums.

## Features

-   **Search Songs:** Search by query and retrieve song metadata.
-   **Charts:** Fetch the real-time Top 200 chart.
-   **Song Details:** Get comprehensive song info (Genre, Duration, Lyricist, Composer, etc.).
-   **Album Details:** Get album metadata (Artist, Release Date, Tracklist, etc.).
-   **Lyrics:** Retrieve synchronized lyrics.
-   **Playlists:** Fetch songs from public playlists.

## Installation

This project requires Python 3.8+ and the following dependencies:

```bash
pip install requests beautifulsoup4
```

## Usage

```python
from genieapi import GenieAPI

genie = GenieAPI()

# 1. Search for a song
songs = genie.search_song("Ditto")
if songs:
    print(f"Found: {songs[0].title} by {songs[0].artist}")

# 2. Get Top 200 Chart
chart = genie.get_chart_top200()
for entry in chart[:5]:
    print(f"{entry.rank}위: {entry.song.title} - {entry.song.artist}")

# 3. Get Song Details
detail = genie.get_song_detail("99570005") # ID for Ditto
if detail:
    print(f"Title: {detail.title}, Duration: {detail.duration}")

# 4. Get Album Details
album = genie.get_album_detail("83325577") # ID for NewJeans 'OMG'
if album:
    print(f"Album: {album.title}, Artist: {album.artist}, Date: {album.release_date}")
    print("Tracks:")
    for track in album.tracklist:
        print(f" - {track.title}")
```

## Project Structure

-   `genieapi/`: Main package directory.
    -   `GenieAPI.py`: Main client class handling network requests.
    -   `parsers.py`: Pure functions for parsing HTML responses.
    -   `models.py`: Data classes (Song, Album, Lyric, ChartEntry).
    -   `Error.py`: Custom exception classes.

## Disclaimer

This is an unofficial API wrapper and is for educational purposes only. Use it responsibly and respect Genie Music's terms of service.
