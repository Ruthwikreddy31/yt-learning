from youtube_transcript_api import YouTubeTranscriptApi

try:
    print("Calling get_transcript directly for video V3iEsLPAD68...")
    # Let's try calling it
    res = YouTubeTranscriptApi.get_transcript("V3iEsLPAD68")
    print("Success! Transcript segments fetched:", len(res))
    print("First segment:", res[0])
except Exception as e:
    print("Direct call failed with exception:", type(e), e)
