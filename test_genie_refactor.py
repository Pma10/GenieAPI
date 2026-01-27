import sys
import os

# Add the current directory to sys.path to ensure we can import the package
sys.path.append(os.getcwd())

from genieapi.GenieAPI import GenieAPI

def test_genie_api():
    api = GenieAPI()
    
    # print("=== 1. Testing Search ===")
    # ... skipped ...
    first_song_id = "99570005" # Ditto

    with open("test_output.txt", "w", encoding="utf-8") as f:
        print("=== 3. Testing Top 200 Chart ===", file=f)
        try:
            chart = api.get_chart_top200(page=1)
            print(f"Chart entries fetched: {len(chart)}", file=f)
            for i, entry in enumerate(chart[:5]):
                print(f"{entry.rank}위: {entry.song.title} - {entry.song.artist}", file=f)
                
        except Exception as e:
            print(f"Chart Test Failed: {e}", file=f)

        print("\n=== 4. Testing Song Detail ===", file=f)
        try:
            detail = api.get_song_detail(first_song_id)
            if detail:
                print(f"Detail fetched: {detail.title}", file=f)
                print(f"Duration: {detail.duration}", file=f)
                print(f"Genre: {detail.genre}", file=f)
                print(f"Lyricist: {detail.lyricist}", file=f)
                print(f"Composer: {detail.composer}", file=f)
                print(f"Arranger: {detail.arranger}", file=f)
            else:
                print("Failed to fetch details.", file=f)
        except Exception as e:
            print(f"Detail Test Failed: {e}", file=f)

        print("\n=== 5. Testing Album Detail ===", file=f)
        album_id = "83325577" # NewJeans 'OMG'
        try:
            album = api.get_album_detail(album_id)
            if album:
                print(f"Album: {album.title} - {album.artist}", file=f)
                print(f"Release Date: {album.release_date}", file=f)
                print(f"Tracks: {len(album.tracklist)} songs", file=f)
                if album.tracklist:
                    print(f"Track 1: {album.tracklist[0].title}", file=f)
            else:
                print("Failed to fetch album.", file=f)
        except Exception as e:
            print(f"Album Test Failed: {e}", file=f)

if __name__ == "__main__":
    test_genie_api()
