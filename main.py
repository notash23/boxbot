import json
import time
from os import listdir
from os.path import isfile, join

import discord
import youtube_dl
from discord import FFmpegPCMAudio as Mpeg
from discord.ext import commands
from twilio.rest import Client

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn'
}

# Make the bot mute someone if they talks over me
# Plays music DONE
# Randomly insults someone DONE

GENERAL_ID = 1154127265496580258
ALL_MUSIC = []
music_index = 0
changing = False


def read_token():
    with open("token.json") as f:
        data = json.load(f)
        return data['token'], data['numbers']


token, numbers = read_token()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        channel = bot.get_channel(GENERAL_ID)

        # Checks if it is the first person that joined
        voice_channel = bot.get_channel(after.channel.id)
        if len(voice_channel.members) > 1:
            return
        text = f'{member} just joined {after.channel.name}. So GET ON!'
        await channel.send(f"@everyone {text}")
        send_whatsapp_message(text)
        return
    if before.channel is not None:
        channel = bot.get_channel(GENERAL_ID)
        text = f'{member} just left... Bummer'
        await channel.send(text)


def send_whatsapp_message(text):
    for number in numbers:
        account_sid = 'ACf79386f85d6bb06e7f157a9f723c47cc'
        auth_token = '621e91acbba0587d8ea1bf448b15248b'
        client = Client(account_sid, auth_token)

        client.messages.create(
            from_='whatsapp:+14155238886',
            body=text,
            to='whatsapp:' + number
        )


@bot.command(pass_context=True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = Mpeg('surprise.mp3')
        voice.play(source)
    else:
        await ctx.send("Join a channel first you idiot")


@bot.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        ctx.guild.voice_client.stop()
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("What is bro smoking? I'm not even in a channel")


def play_queue(voice, reset=False, change=False):
    global music_index, changing
    if changing:
        if change:
            changing = True
        else:
            return
    if music_index >= len(ALL_MUSIC) or music_index < 0 or reset:
        music_index = 0
    path = ALL_MUSIC[music_index]
    if path.startswith('https://www.youtube.com/watch?v='):
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            data = ydl.extract_info(ALL_MUSIC[music_index], download=False)
        if data['url'] is None:
            return
        path = data['url']
    source = Mpeg(path)
    music_index += 1
    voice.play(source, after=lambda x=None: play_queue(voice))


@bot.command(pass_context=True)
async def play(ctx, *, arg=None):
    global ALL_MUSIC
    voice = ctx.guild.voice_client
    if voice is None:
        await ctx.send("If only I could donate brain cells... MAKE ME JOIN A VOICE CALL FIRST! You know what I'll do it"
                       " myself. What song do you want me to play again?")
        await join(ctx)
        return
    # Plays all the music on the computer
    if arg is None:
        await ctx.send("Behold plebeians - my spectacular playlist.")
        ALL_MUSIC = [join('music', f) for f in listdir('music') if isfile(join('music', f)) and f.endswith('.mp3')]
        play_queue(voice, reset=True, change=True)
        return
    # Plays a specific music on the computer
    if (path := f'music/{arg}.mp3') in ALL_MUSIC:
        source = Mpeg(path)
        voice.play(source, after=lambda x=None: play_queue(voice))
    elif arg.startswith('https://www.youtube.com/watch?v=') or arg.startswith('https://youtu.be/'):
        if arg.startswith('https://youtu.be/'):
            arg = arg[17:].split('?')[0]
        # get YouTube if it is a link
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            data = ydl.extract_info(arg, download=False)
        if len(data['url']) == 0:
            await ctx.send("This song doesn't exist idiot")
            return
        path = data['url']
        await ctx.send("I found this song on youtube")
        source = Mpeg(path)
        voice.play(source, after=lambda x=None: play_queue(voice))
    else:
        # if not found, search YouTube
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            data = ydl.extract_info(arg, download=False)
        if len(data.get('entries', [])) == 0:
            await ctx.send("This song doesn't exist idiot")
            return
        path = data['entries'][0]['url']
        await ctx.send("I found this song on youtube")
        source = Mpeg(path)
        voice.play(source, after=lambda x=None: play_queue(voice))


@bot.command(pass_context=True)
async def pQueue(ctx, *, arg=None):
    global ALL_MUSIC
    voice = ctx.guild.voice_client
    if voice is None:
        await ctx.send("If only I could donate brain cells... MAKE ME JOIN A VOICE CALL FIRST! You know what I'll do it"
                       " myself. What song do you want me to play again?")
        await join(ctx)
        return
    playlist_format_options = {
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True
    }

    with youtube_dl.YoutubeDL(playlist_format_options) as ydl:
        result = ydl.extract_info(arg, download=False)
    if "entries" not in result:
        return
    ALL_MUSIC = [f"https://www.youtube.com/watch?v={item['url']}" for item in result['entries']]
    await ctx.send("Added to 25 songs from this playlist to queue")
    play_queue(voice, reset=True, change=True)


@bot.command(pass_context=True)
async def queue(ctx, *, arg=None):
    global ALL_MUSIC
    ALL_MUSIC += arg
    await ctx.send("Added to queue")


@bot.command(pass_context=True)
async def pause(ctx):
    voice = ctx.guild.voice_client
    if not voice:
        await ctx.send("What is bro smoking? I'm not even in a channel")
        return
    if voice.is_playing():
        voice.pause()
        await ctx.send("Pausing")


@bot.command(pass_context=True)
async def resume(ctx):
    voice = ctx.guild.voice_client
    if not voice:
        await ctx.send("What is bro smoking? I'm not even in a channel")
        return
    if voice.is_paused():
        voice.resume()
        await ctx.send("Resuming")


@bot.command(pass_context=True)
async def stop(ctx):
    global music_index, changing
    voice = ctx.guild.voice_client
    if not voice:
        await ctx.send("What is bro smoking? I'm not even in a channel")
        return
    changing = True
    voice.stop()
    await ctx.send("Stopping")


@bot.command(pass_context=True)
async def skip(ctx):
    global music_index, changing
    voice = ctx.guild.voice_client
    if not voice:
        await ctx.send("What is bro smoking? I'm not even in a channel")
        return
    changing = True
    voice.stop()
    play_queue(voice, change=True)
    await ctx.send("Putting the next song")


@bot.command(pass_context=True)
async def previous(ctx):
    global music_index, changing
    voice = ctx.guild.voice_client
    if not voice:
        await ctx.send("What is bro smoking? I'm not even in a channel")
        return
    changing = True
    voice.stop()
    music_index -= 2
    play_queue(voice, change=True)
    await ctx.send("Putting the next song")


@bot.command(pass_context=True)
async def harass(ctx, *, arg=None):
    if arg is None:
        await ctx.message.author.send("You didn't even write a name you retard")
        return
    for member in bot.get_all_members():
        if arg == member.global_name:
            # threading.Thread(target=asyncio.run, args=(spam_harass(member),)).start()
            return
    await ctx.message.author.send("You can't even type a name right you retard")


async def spam_harass(member):
    while True:
        await send_harass(member)
        time.sleep(5)


async def send_harass(member):
    await member.send("You suck")


bot.run(token)
