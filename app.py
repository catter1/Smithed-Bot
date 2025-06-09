import discord
import logging
import logging.handlers
import os
import json
import asyncio
from libraries import bot
from discord import app_commands
from discord.ext import commands
from discord.ext.tasks import loop

# Get settings
with open('settings.json', 'r') as f:
	settings = json.load(f)

# Define Bot Client and Console
client = bot.SmithedBot()
client.remove_command('help')

# Logging settings
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
	filename='bot.log',
	encoding='utf-8',
	maxBytes=32 * 1024 * 1024,  # 32 MiB
	backupCount=5,
)
dt_fmt = '%d-%m-%Y %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Discord big doo doo butt >:(
discord.utils.setup_logging(handler=handler, formatter=formatter, level=logging.INFO, root=True)

# Define COG LIST for later
cog_list = sorted([
	f"{file[:-3]}"
	for file in os.listdir('./cogs')
	if file.endswith('.py')
])

# Start everything up!
async def run():
	def get_env() -> dict:
		environment = {}
		token = os.environ.get("SMITHED_BOT_TOKEN")
		dummy = os.environ.get("SMITHED_BOT_DUMMY")
		if not token:
			print("Please set a bot token in the SMITHED_BOT_TOKEN environment.")
			exit()
			
		environment["SMITHED_BOT_TOKEN"] = str(token)
		environment["SMITHED_BOT_DUMMY"] = bool(dummy)

		return environment
	
	try:
		client.settings = settings
		client.environment = get_env()

		logging.info("Logging in")
		await client.start(client.environment["SMITHED_BOT_TOKEN"])
	except KeyboardInterrupt:
		await client.logout()

@client.event
async def setup_hook():
	# Load cogs
	for filename in os.listdir('./cogs'):
		if filename.endswith('.py'):
			await client.load_extension(f'cogs.{filename[:-3]}')
		
	# All set!
	print('Smithed Bot is now online.')

@client.command(name="sync")
@bot.is_catter()
async def sync(ctx: commands.context.Context):
	synced = await client.tree.sync()
	await ctx.send(f"Synced {len(synced)} commands")

cog_group = app_commands.Group(name='cog', description='[ADMIN] Uses the cog management menu', default_permissions=discord.permissions.Permissions.all())

@cog_group.command(name="load", description="[ADMIN] Loads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def load(interaction: discord.Interaction, cog: str):
	await interaction.response.defer(thinking=True, ephemeral=True)
	try:
		await client.load_extension(cog)
	except Exception as error:
		await interaction.followup.send("Issue loading cog!", ephemeral=True)
		raise error
	else:
		await interaction.followup.send("Cog loaded successfully", ephemeral=True)

@cog_group.command(name="unload", description="[ADMIN] Unloads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def unload(interaction: discord.Interaction, cog: str):
	await interaction.response.defer(thinking=True, ephemeral=True)
	try:
		await client.unload_extension(cog)
	except Exception as error:
		await interaction.followup.send("Issue unloading cog!", ephemeral=True)
		raise error
	else:
		await interaction.followup.send("Cog unloaded successfully", ephemeral=True)

@cog_group.command(name="reload", description="[ADMIN] Reloads a cog")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def _reload(interaction: discord.Interaction, cog: str):
	await interaction.response.defer(thinking=True, ephemeral=True)
	try:
		await client.unload_extension(cog)
		await client.load_extension(cog)
	except Exception as error:
		await interaction.followup.send("Issue reloading cog!", ephemeral=True)
		raise error
	else:
		await interaction.followup.send("Cog reloaded successfully", ephemeral=True)


@load.autocomplete('cog')
@unload.autocomplete('cog')
@_reload.autocomplete('cog')
async def autocomplete_callback(_: discord.Interaction, current: str):
	coglist = [
		app_commands.Choice(name=cog, value=f"cogs.{cog}")
		for cog in cog_list
		if current.lower() in cog.lower()
	]

	return coglist

client.tree.add_command(cog_group)

@client.event
async def on_command_error(ctx, error):
	raise error

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
	if isinstance(error, (app_commands.CheckFailure, app_commands.MissingPermissions)):
		await interaction.response.send_message(str(error), ephemeral=True)
	else:
		try:
			await interaction.response.send_message("An unregistered error has occurred!", ephemeral=True)
		except discord.errors.NotFound:
			await interaction.followup.send("An unregistered error has occurred!", ephemeral=True)
		raise error

try:
	loop = asyncio.new_event_loop()
	loop.run_until_complete(run())
except KeyboardInterrupt:
	logging.info("Smithed Bot is now offline.")