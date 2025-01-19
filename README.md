### GitHub Repository Description:

**Plex to MusicBrainz Sync**  
This project synchronizes user ratings from a Plex music library to MusicBrainz, helping you enrich metadata and keep track ratings consistent across platforms.

### Features:
- **Plex API Integration**: Fetch user ratings and metadata from your Plex music library.
- **MusicBrainz API Integration**: Search for tracks and submit ratings using MusicBrainz's vast music database.
- **Local LLM Assistance**: Uses the Ollama LLM to intelligently match tracks when no exact match is found.
- **Flexible Matching**: Automatically matches tracks by title and artist or provides intelligent suggestions for ambiguous cases.
- **Batch Rating Submission**: Submits ratings in bulk for efficiency.

### How It Works:
1. Fetches rated tracks from your Plex music library.
2. Searches for matches in the MusicBrainz database.
3. Uses an LLM (Ollama) to resolve ambiguous matches or suggest metadata.
4. Submits scaled ratings (0–100) to MusicBrainz for the matched recordings.

### Requirements:
- Python 3.7+
- Plex server credentials
- MusicBrainz account credentials
- Ollama installed locally for LLM querying

### Use Cases:
- Maintain consistent track ratings between Plex and MusicBrainz.
- Contribute to the MusicBrainz database by submitting ratings.
- Enhance your personal music metadata collection with precise, curated data.

### Getting Started:
Clone the repository, install the required dependencies, and configure your Plex and MusicBrainz credentials to start synchronizing. Detailed setup instructions are included in the README.

--- 

Feel free to tweak this description to better match your vision or to add specific technical details. Let me know if you'd like help drafting any other sections!
