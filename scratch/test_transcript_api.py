import youtube_transcript_api
print("Module attributes:", dir(youtube_transcript_api))

# Let's inspect what is available
for attr in dir(youtube_transcript_api):
    print(f"Attr: {attr}, Type: {type(getattr(youtube_transcript_api, attr))}")
