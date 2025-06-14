import discord
import logging
from discord import app_commands
from discord.ext import commands
from libraries import bot
import libraries.constants as Constants

class Template(commands.Cog):
	def __init__(self, client: bot.Smithed):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')

async def setup(client):
	await client.add_cog(Template(client))