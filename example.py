from client_terminal import *
import json

current_channel = None

def check_text_channel():
	if not current_channel:
		error('Unknown current channel. Use "setch" command to set a new current channel')
		return True

	if not isinstance(current_channel, discord.TextChannel) and not issubclass(current_channel, discord.abc.PrivateChannel):
		error('Current channel is not a text channel')
		return True

def check_voice_channel():
	if not current_channel:
		error('Unknown current channel. Use "setch" command to set a new current channel')
		return True

	if not isinstance(current_channel, discord.VoiceChannel):
		error('Current channel is not a voice channel')
		return True

### CONFIG ###

CFG_PATH = "config.json"
CFG_CID = "ChannelID"
CFG_TOK = "BotToken"

def check_config():
	from os.path import exists
	if not exists(CFG_PATH):
		open(CFG_PATH, "w").close()

def write_config(key: str, value):
	check_config()

	cfg = None
	with open(CFG_PATH, "r+") as file:
		buffer = file.read()
		if len(buffer):
			cfg = json.loads(buffer)
	
		file.seek(0)

		if type(cfg) is dict:
			cfg[key] = value
			file.write(json.dumps(cfg, sort_keys=True, indent=4))
		else:
			dummy = {key: value}
			file.write(json.dumps(dummy, sort_keys=True, indent=4))
		
		file.close()

def read_config():
	check_config()

	cfg = None
	with open(CFG_PATH, "r") as file:
		buffer = file.read()
		if not len(buffer):
			return
		cfg = json.loads(buffer)
		file.close()

	if type(cfg) is dict:
		return cfg

async def load_config():
	try:
		await set_channel(read_config()[CFG_CID])
	except TypeError or KeyError:
		pass

	notice("Config loaded")

### GARBAGE COLLECTOR ###

async def clear_cache():
	from os import remove
	try:
		remove("cache")
	except Exception as e:
		error(e)
		return

	notice("Cache successfully cleared")

### COMMANDS ###

async def cmdlist(*msgs: str):
	bold('List of registered commands')
	
	for key in client.terminal.cmd_reg.keys():
		echo(key)

async def set_channel(channel_user_id: int):
	channel = client.get_channel(channel_user_id)
	
	if not channel:
		channel = client.get_user(channel_user_id)
		
		if not channel:
			try:
				channel = await client.fetch_channel(channel_user_id)
			except:
				try:
					channel = await client.fetch_user(channel_user_id)
				except discord.NotFound:
					error('Invalid channel/user ID!')
					return

	global current_channel
	current_channel = channel
	
	notice(f'Current channel set to {type(channel).__name__} "{channel.name}"')

	write_config(CFG_CID, channel_user_id)

async def sendmsg(*msgs: str):
	if check_text_channel(): return

	await current_channel.send(' '.join(msgs))

async def join_channel():
	if check_voice_channel(): return

	try:
		await current_channel.connect()
	except discord.ClientException:
		error('Unable to connect! Voice client is already connected')

async def leave_all_voice_channels():
	left = 0

	for voice_client in client.voice_clients:
		if voice_client.is_connected():
			await voice_client.disconnect()
			left += 1
	
	notice(f'Left {left} voice channels')

async def leave_voice_channel(channel_guild_id: int):
	guild = None
	channel = client.get_channel(channel_guild_id)

	if not channel:
		guild = client.get_guild(channel_guild_id)

		if not guild:
			try:
				channel = await client.fetch_channel(channel_guild_id)
			except discord.NotFound:
				try:
					guild = await client.fetch_guild(channel_guild_id)
				except discord.NotFound:
					error('Invalid channel/guild ID!')
					return
	
	if not guild:
		guild = channel.guild

	if not guild.voice_client:
		error(f'Not connected in "{guild.name}"')
		return

	await guild.voice_client.disconnect()

async def play_audio(path: str):
	if check_voice_channel(): return

	vc = current_channel.guild.voice_client

	if not vc:
		error(f'Not connected in "{current_channel.guild.name}"')
		return
	
	try:
		vc.play(discord.FFmpegPCMAudio(source=path))
	except discord.ClientException:
		error("Already playing audio")
		return

async def play_audio_web(url: str):
	if check_voice_channel(): return

	from youtube_dl import YoutubeDL
	path = None
	with YoutubeDL({"outtmpl": "cache\%(title)s-%(id)s.%(ext)s", "format": "bestaudio", "nooverwrites": False, "quiet": True, "noplaylist": True}) as ytdl:
		try:
			result = ytdl.extract_info(url)
			path = ytdl.prepare_filename(result)
		except:
			error("Unable to download audio")
			return
		
	await play_audio(path)

async def stop_audio():
	if check_voice_channel(): return

	vc = current_channel.guild.voice_client

	if not vc:
		error(f'Not connected in "{current_channel.guild.name}"')
		return
	
	vc.stop()

async def pause_audio():
	if check_voice_channel(): return

	vc = current_channel.guild.voice_client

	if not vc:
		error(f'Not connected in "{current_channel.guild.name}"')
		return
	
	vc.pause()
	
async def resume_audio():
	if check_voice_channel(): return

	vc = current_channel.guild.voice_client

	if not vc:
		error(f'Not connected in "{current_channel.guild.name}"')
		return

	vc.resume()

async def username(user_id: int):
	user = client.get_user(user_id)
	
	if not user:
		try:
			user = await client.fetch_user(user_id)
		except discord.NotFound:
			error('Invalid user ID!')
			return
	
	return f'{user.name}#{user.discriminator}'

async def delete_num(count: int = 5):
	if check_text_channel(): return

	deleted = 0
	
	async for message in current_channel.history(limit=count):
		await message.delete()
		deleted += 1
	
	notice(f'Successfully deleted {deleted} message(s)')

async def delete_last():
	if check_text_channel(): return

	message = None
	
	try:
		message = await current_channel.history(limit=100).find(lambda m: m.author.id == client.user.id)
	except:
		error('Last message too far or not found!')
		return
	
	await message.delete()
	notice('Successfully deleted 1 message')

async def msg_history(count: int = 5):
	if check_text_channel(): return

	last = None
	msgs = await current_channel.history(limit = count).flatten()
	msgs.reverse()
	
	if not len(msgs):
		notice("No messages in record")
		return
	
	try:
		for m in msgs:
			user = await username(m.author.id)
			
			if last != user:
				notice(user, '\t', m.created_at)
			
			echo(m.content)
			
			last = user
	except Exception as e:
		error(e)

async def nop(*args):
	pass

async def eval_e(*args):
	try:
		eval(' '.join(args))
	except Exception as e:
		error(e)

def main():
	client = Client()
	echo('Registering commands...')
	
	client.terminal.register('help', cmdlist)
	
	client.terminal.register('echo', echo)
	client.terminal.register('ntc', notice)
	client.terminal.register('err', error)
	client.terminal.register('bold', bold)
	client.terminal.register('cls', clear)
	client.terminal.register('pos', cur_pos)
	
	client.terminal.register('input', ainput)
	client.terminal.register('nop', nop)
	client.terminal.register('eval', eval_e)
	
	client.terminal.register('break', client.close)

	client.terminal.register('unam', username)
	
	client.terminal.register('setch', set_channel)
	client.terminal.register('msg', sendmsg)
	client.terminal.register('unmsg', delete_last)
	client.terminal.register('rmsg', delete_num)
	client.terminal.register('his', msg_history)

	client.terminal.register('join', join_channel)
	client.terminal.register('leavall', leave_all_voice_channels)
	client.terminal.register('leavc', leave_voice_channel)
	client.terminal.register('play', play_audio)
	client.terminal.register('playw', play_audio_web)
	client.terminal.register('stop', stop_audio)
	client.terminal.register('paus', pause_audio)
	client.terminal.register('rsum', resume_audio)

	client.terminal.register('cfg', load_config)
	client.terminal.register('cachc', clear_cache)

	notice(f'Successfully registered {len(client.terminal.cmd_reg)} commands. Type "help" to see a full list of instructions')
	echo('Client connecting...')

	client.run

	try:
		client.loop.run_until_complete(client.start(read_config()[CFG_TOK]))
	except TypeError or KeyError:
		error(f"Missing bot token in {CFG_PATH}")
	except discord.LoginFailure:
		error(f"Invalid bot token in {CFG_PATH}")
	except KeyboardInterrupt:
		client.loop.run_until_complete(client.close())
	except:
		pass

if __name__ == '__main__':
	main()
