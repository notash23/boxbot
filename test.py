import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True
}

with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
    result = ydl.extract_info('https://www.youtube.com/watch?v=-hB-WOW2BN0&list=RDlxZ7OTm72mY&index=2', download=False)

for item in result['entries']:
    print(item['url'])
