with open(r"C:\Users\ruthw\AppData\Local\Programs\Python\Python313\Lib\site-packages\youtube_transcript_api\_api.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print("Total lines:", len(lines))
    print("First 100 lines:")
    print("".join(lines[:100]))
