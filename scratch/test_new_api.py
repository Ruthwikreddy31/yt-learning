from youtube_transcript_api import YouTubeTranscriptApi

try:
    print("Instantiating YouTubeTranscriptApi and fetching V3iEsLPAD68...")
    api = YouTubeTranscriptApi()
    res = api.fetch("V3iEsLPAD68")
    print("Success! Result type:", type(res))
    raw_data = res.to_raw_data()
    print("Raw data type:", type(raw_data))
    print("First item in raw data:", raw_data[0] if raw_data else "None")
except Exception as e:
    print("Failed with exception:", type(e), e)
