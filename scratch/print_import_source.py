from youtube_transcript_api import YouTubeTranscriptApi
import inspect

try:
    source_file = inspect.getfile(YouTubeTranscriptApi)
    print("Import source file:", source_file)
except Exception as e:
    print("Could not get file path:", e)
    # Check module
    import youtube_transcript_api
    print("Module file:", youtube_transcript_api.__file__)
