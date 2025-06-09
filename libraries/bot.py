import discord
from discord import app_commands
from discord.ext import commands
import libraries.constants as Constants

class SmithedBot(commands.Bot):
	def __init__(self, command_prefix: str = "!", settings: dict = None, environment: dict = None):
		super().__init__(command_prefix=command_prefix, case_insensitive=True, intents=discord.Intents.all())
		self.settings = settings
		self.environment = environment

def is_catter():
	"""Is catter1"""
	
	def catter(interaction: discord.Interaction):
		if interaction.user.id == Constants.User.CATTER:
			return True
		else:
			return app_commands.MissingPermissions("Only catter is allowed to use this command!")
	return app_commands.check(catter)