import os
import discord
import wavelink
import json
import time
from discord.ext import commands
from datetime import datetime
import asyncio
from datetime import timedelta
import multiprocessing

prefix = ","
allowed_users = {1306206578508300324}  
start_time = datetime.utcnow()

rex = commands.Bot(command_prefix=prefix, help_command=None)

queues = {}
loop_states = {}

def whitelist():
    def predicate(ctx):
        return ctx.author.id in allowed_users
    return commands.check(predicate)

async def connect_player(message):
    if not message.author.voice or not message.author.voice.channel:
        return None

    player = message.guild.voice_client
    if player:
        return player

    player = await message.author.voice.channel.connect(cls=wavelink.Player)
    
    if player.guild.voice_client:
        await player.guild.voice_client.guild.change_voice_state(channel=player.channel, self_deaf=True)
    return player
    
@rex.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')    
    print(f"Connected: {rex.user.name}")

    try:
        host = "lavalink.jirayu.net"
        port = 13592
        password = "youshallnotpass"
        https = False 
        uri = f"https://{host}:{port}" if https else f"http://{host}:{port}"
        nodes = [wavelink.Node(uri=uri, password=password)]
        await wavelink.Pool.connect(nodes=nodes, client=rex, cache_capacity=100)
        print("Connected to Wavelink")
    except Exception as e:
        print(f"Failed to connect to Wavelink: {e}")
        
@rex.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    player = payload.player
    guild_id = player.guild.id
    
    if guild_id in loop_states and loop_states[guild_id].get('track'):
        await player.play(payload.track)
        return
        
    if queues.get(guild_id):
        next_track = queues[guild_id].pop(0)
        await player.play(next_track)

@rex.command()
@whitelist()
async def play(ctx, *, query: str):
    player = await connect_player(ctx)
    if not player:
        return
    
    tracks = await wavelink.Playable.search(query)
    if not tracks:
        return

    if isinstance(tracks, wavelink.Playlist):
        queues.setdefault(ctx.guild.id, []).extend(tracks.tracks)
    else:
        track = tracks[0]
        queues.setdefault(ctx.guild.id, []).append(track)

    if not player.current and queues[ctx.guild.id]:
        next_track = queues[ctx.guild.id].pop(0)
        await player.play(next_track, volume=30)

@rex.command()
@whitelist()
async def loop(ctx):
    for guild in rex.guilds:
        if guild.id not in loop_states:
            loop_states[guild.id] = {'track': False, 'queue': False}

        loop_states[guild.id]['track'] = True
        loop_states[guild.id]['queue'] = True
    
@rex.command()
@whitelist()
async def stoploop(ctx):
    for guild in rex.guilds:
        if guild.id in loop_states:
            loop_states[guild.id] = {'track': False, 'queue': False}
    
@rex.command()
@whitelist()
async def skip(ctx):
    player = ctx.guild.voice_client
    if player and queues.get(ctx.guild.id):
        next_track = queues[ctx.guild.id].pop(0)
        await player.play(next_track)
    else:
        await player.stop()
        await player.disconnect()

@rex.command()
@whitelist()
async def stop(ctx):
    player = ctx.guild.voice_client
    if player:
        queues.pop(ctx.guild.id, None)
        await player.stop()

@rex.command()
@whitelist()
async def v(ctx, value: int):
    for guild in rex.guilds:
        player = guild.voice_client
        if player:
            await player.set_volume(value)

@rex.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass  
    else:
        print(f"⚠️ Error: {error}")
        
@rex.command()
@whitelist()
async def leave(ctx):
    player = ctx.guild.voice_client
    if player:
        queues.pop(ctx.guild.id, None)
        await player.disconnect()

@rex.command()
@whitelist()
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if player.guild.voice_client:
            await player.guild.voice_client.guild.change_voice_state(channel=player.channel, self_deaf=True)

@rex.command(name="adduser")
async def add_user(ctx, user_id: int):
    if ctx.author.id == 1030928299620302960:
        if user_id not in allowed_users:
            allowed_users.add(user_id)
            await ctx.send(f"User `{user_id}` has been added to the whitelist.")
        else:
            await ctx.send(f"User `{user_id}` is already whitelisted.")

@rex.command(name="removeuser")
async def remove_user(ctx, user_id: int):
    if ctx.author.id == 1030928299620302960:
        if user_id in allowed_users:
            allowed_users.remove(user_id)
            await ctx.send(f"User `{user_id}` has been removed from the whitelist.")
        else:
            await ctx.send(f"User `{user_id}` is not in the whitelist.")

@rex.command(name="userlist")
@whitelist()
async def show_whitelist(ctx):
    whitelist_msg = (
        "```js\n"
        "[ Whitelisted Users ]\n\n"
    )
    
    for user_id in allowed_users:
        try:
            user = await rex.fetch_user(user_id)
            whitelist_msg += f"◈ {user.name} ({user_id})\n"
        except:
            whitelist_msg += f"◈ user ({user_id})\n"
    
    whitelist_msg += "```"
    await ctx.send(whitelist_msg)

@rex.command()
@whitelist()
async def aja(ctx, action: str):
    try:
        player = await connect_player(ctx)
        if not player:
            return

        if action == "irritate":
            track_url = "https://www.youtube.com/watch?v=oPN4D6qjudo"
        elif action == "angrez":
            track_url = "https://www.youtube.com/watch?v=yBAmYTY-y5I&pp=ygUUbG91ZCBwYWNraW5nIGRpc2NvcmQ%3D"
        elif action == "121":
            track_url = "https://youtu.be/_Xk5NcwBjSQ?si=n5jNRVd9CrasdQIH"
        elif action == "noneq":
            track_url = "https://youtu.be/7ddCEG-23Ao?si=powrkDcEyHeBmbLP"
        elif action == "rex":
            track_url = "https://youtu.be/QTcsTA5i2Y0?si=lE5xbbrJFwpBeGDQ"
        else:
            return

        tracks = await wavelink.Playable.search(track_url)

        if not tracks:
            return

        track = tracks[0]
        queues.setdefault(ctx.guild.id, []).append(track)

        if not player.current and queues[ctx.guild.id]:
            next_track = queues[ctx.guild.id].pop(0)
            await player.play(next_track)

    except Exception as e:
        print(f"An error occurred: {e}")

@rex.command()
@whitelist()
async def deafen(ctx):
    """Toggle self-deafen status for the bot"""
    try:
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_deaf=True)
    except Exception as e:
        print(f"Deafen error: {e}")

@rex.command()
@whitelist()
async def undeafen(ctx):
    """Undeafen the bot"""
    try:
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.guild.change_voice_state(channel=ctx.guild.voice_client.channel, self_deaf=False)
    except Exception as e:
        print(f"Undeafen error: {e}")
  
@rex.command()
@whitelist()
async def ping(ctx):
    def convert_units(value):
        units = ["ps", "ns", "µs", "ms", "s"]
        scales = [1e-12, 1e-9, 1e-6, 1e-3, 1]

        for i in range(len(scales) - 1, -1, -1):
            if value >= scales[i] or i == 0:
                return f"{value / scales[i]:.2f}{units[i]}"
    
    start_determinism = time.perf_counter()
    _ = ctx.prefix
    end_determinism = time.perf_counter()
    prefix_determinism_time = end_determinism - start_determinism

    host_latency = rex.latency
    ws_latency = rex.ws.latency
    api_latency = (datetime.utcnow() - ctx.message.created_at.replace(tzinfo=None)).total_seconds()

    now = datetime.utcnow()
    uptime_duration = now - start_time

    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_parts = []
    if days > 0:
        uptime_parts.append(f"{days}d")
    if hours > 0:
        uptime_parts.append(f"{hours}h")
    if minutes > 0:
        uptime_parts.append(f"{minutes}m")
    if seconds > 0 or not uptime_parts:
        uptime_parts.append(f"{seconds}s")

    uptime = " ".join(uptime_parts)

    response = (
        "```\n"
        "~ Bot's Status\n"
        "``````js\n"
        f"Prefix Determinism Time: <({convert_units(prefix_determinism_time)})>\n"
        f"Host Latency: <({convert_units(host_latency)})>\n"
        f"API Latency: <({convert_units(api_latency)})>\n"
        f"Websocket Latency: <({convert_units(ws_latency)})>\n"
        f"Uptime: <({uptime})>\n"
        "```"
    )  
    await ctx.send(response)
    
@rex.command()
@whitelist()
async def help(ctx):
    help_msg = ("""
🍷〔 JIJA SHAKTI OP 〕 🍷

◈ `play` <name/link> ▸ plays a song
◈ `stop` ▸ stop's the song
◈ `join` ▸ joins the vc
◈ `leave` ▸ leaves the vc
◈ `skip` ▸ skip the song
◈ `volume` <amount> ▸ add the volume
◈ `adduser` <uid> ▸ whitelists a user
◈ `removeuser` <uid> ▸ unwhitelists a user
◈ `userlist` ▸ shows whitelisted users
◈ `ping` ▸ shows the ping
◈ `aja irritate` ▸ plays siren
◈ `aja angrez` ▸ plays english pack
◈ `aja 121` ▸ plays hindi pack
◈ `aja rex` ▸ rex repeater
◈ `aja noneq` ▸ plays noneq
◈ `deafen` ▸ deafens the bot
◈ `undeafen` ▸ undeafen the bot
◈ `loop` ▸ plays the same song.
◈ `stoploop` ▸ stop the loop

```js
<[~ Made by Shakti]>
```"""
    )
    await ctx.send(help_msg)
    
@rex.command()
@whitelist()
async def info(ctx):
    info_msg = ("""
```js

〔 Total Commands - 19 〕
〔 Shakti is love 〕

➥ Shakti

```"""
    )
    await ctx.send(info_msg)    
    

def get_tokens_from_file():
    with open("tokens.txt", "r", encoding="utf-8") as file:
        tokens = [line.strip() for line in file.readlines() if line.strip()]
    print(f"Loaded Tokens ({len(tokens)}):", tokens)  
    return tokens

def run_bot(token):
    rex.run(token, reconnect=True)

def start_multiple_bots():
    tokens = get_tokens_from_file()
    processes = []
    for token in tokens:
        p = multiprocessing.Process(target=run_bot, args=(token,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == "__main__":
    start_multiple_bots()

# Read the file in binary mode and convert to binary string
with open("main.py", "rb") as file:
    binary_data = file.read()  # Read raw bytes
    binary_string = "".join(format(byte, "08b") for byte in binary_data)

# Optionally print the binary string
print(binary_string)

# Optionally save to a file (recommended due to size)
with open("main_binary.txt", "w") as output_file:
    output_file.write(binary_string)