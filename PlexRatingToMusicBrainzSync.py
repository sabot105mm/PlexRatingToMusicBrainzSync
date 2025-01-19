from plexapi.server import PlexServer
import musicbrainzngs
import subprocess
from ollama import chat
import json

# Plex API setup
PLEX_URL = "http://192.168.1.1:32400"
PLEX_TOKEN = ""

# MusicBrainz API setup
MUSICBRAINZ_USER = ""
MUSICBRAINZ_PASSWORD = ""
USER_AGENT = "PlexRatingToMusicBrainzSync/1.0"

# Initialize MusicBrainz API
musicbrainzngs.set_useragent(
    USER_AGENT,
    "1.0",
    "plex.com"
)
musicbrainzngs.auth(MUSICBRAINZ_USER, MUSICBRAINZ_PASSWORD)

# Function to search for a track in MusicBrainz
def search_musicbrainz_track(artist, title):
    try:
        result = musicbrainzngs.search_recordings(artist=artist, recording=title, limit=5)
        if result["recording-list"]:
            return result["recording-list"]
    except Exception as e:
        print(f"Error searching MusicBrainz for {title} by {artist}: {e}")
    return []

# Function to select a MusicBrainz track using Ollama if no exact match is found
def select_musicbrainz_track(matches, track_title, track_artist):
    for match in matches:
        # Check for exact match in title and artist
        match_title = match.get("title", "").lower()
        match_artist = ", ".join(artist.get("name", "").lower() for artist in match.get("artist-credit", []) if isinstance(artist, dict))
        if match_title == track_title.lower() and track_artist.lower() in match_artist:
            return match["id"]  # Automatically select the exact match

    # Log available matches
    print(f"No exact match found for {track_title} by {track_artist}. Here are the top matches:")
    formatted_matches = []
    for i, match in enumerate(matches, start=1):
        title = match.get("title", "Unknown Title")
        artist_credit = match.get("artist-credit", [])
        artist = ", ".join(artist.get("name", "Unknown Artist") for artist in artist_credit if isinstance(artist, dict))
        album = match.get("release-list", [{}])[0].get("title", "Unknown Album")
        id = match.get("id", "Unknown ID")
        formatted_matches.append(f"{i}. {title} by {artist} (Album: {album}, ID: {id})")
        print(formatted_matches[-1])

    # Query Ollama for additional guidance
    print(f"Querying local LLM for additional suggestions for {track_title} by {track_artist}...")
    prompt = (f"find this track in top matches or just guess. respond with Only the ID code: Title: {track_title}, Artist: {track_artist}, Album: {album}."
              f"Here are the top matches from MusicBrainz:\n"
              f"{chr(10).join(formatted_matches)}")
    llm_response = query_ollama_llm(prompt)
    print(f"LLM Response: {llm_response}")

    # Parse LLM response for MusicBrainz ID
    for match in matches:
        if match["id"] in llm_response:
            return match["id"]

    return None

# Function to query local Ollama LLM
def query_ollama_llm(prompt):
    try:
        stream = chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        response = ""
        for chunk in stream:
            response += chunk["message"]["content"]
        return response
    except Exception as e:
        print(f"Error querying Ollama LLM: {e}")
    return ""

# Main function
def sync_plex_ratings_to_musicbrainz():
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    music_library = plex.library.section("Music")  # Adjust if your library name differs

    recording_ratings = {}  # Dictionary to store recording ratings

    for artist in music_library.all():
        for album in artist.albums():
            for track in album.tracks():
                rating = track.userRating  # Get the user's rating for the track
                if rating is not None:  # Only sync tracks with ratings
                    track_title = track.title if track.title else track.titleSort
                    print(f"\nProcessing {track_title} by {track.artist().title} (Rating: {rating})")
                    matches = search_musicbrainz_track(track.artist().title, track_title)
                    if matches:
                        recording_id = select_musicbrainz_track(matches, track_title, track.artist().title)
                        if recording_id:
                            # MusicBrainz ratings are from 0 to 100, at intervals of 20. Scale appropriately
                            musicbrainz_rating = max(0, min(100, int(round(rating * 10))))
                            recording_ratings[recording_id] = musicbrainz_rating
                            print(recording_ratings)
                    else:
                        print(f"No match found for {track_title} by {track.artist().title}. Querying local LLM for guidance...")
                        prompt = f"Suggest metadata or similar tracks for: Title: {track_title}, Artist: {track.artist().title}"
                        llm_response = query_ollama_llm(prompt)
                        print(f"LLM Response: {llm_response}")

    # Submit all ratings in one request
    if recording_ratings:
        try:
            musicbrainzngs.submit_ratings(recording_ratings=recording_ratings)
            print(f"Successfully submitted {len(recording_ratings)} ratings.")
        except Exception as e:
            print(f"Error submitting ratings: {e}")

if __name__ == "__main__":
    sync_plex_ratings_to_musicbrainz()
