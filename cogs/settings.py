import discord
import logging
import datetime
import json
from discord import app_commands
from discord.ext import commands
from libraries import bot
import libraries.constants as Constants

class Settings(commands.Cog):
	def __init__(self, client: bot.SmithedBot):
		self.client = client

	async def cog_load(self):
		logging.info(f'> {self.__cog_name__} cog loaded')

	@commands.Cog.listener()
	async def on_ready(self):
		self.audit_channel = await self.client.fetch_channel(self.client.settings["audit-channel-id"])
		if self.client.environment["SMITHED_BOT_DUMMY"]:
			self.audit_channel = self.client.get_channel(Constants.Channel.TESTING)

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')
		
	### COMMAND ###
	
	@app_commands.command(name="settings", description="View and modify bot settings")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(
		setting="The setting to view or modify",
		value="[Optional] if included, will modify the setting"
	)
	async def settings(self, interaction: discord.Interaction, setting: str, value: str = None) -> None:
		""" /settings <setting> [value] """

		# Check setting validity
		if setting not in self.client.settings.keys():
			await interaction.response.send_message("Invalid setting!", ephemeral=True)
			return
		
		# Return setting data
		if not value:
			await interaction.response.send_message(f"`{setting}` is currently set to `{self.client.settings[setting]}`.", ephemeral=True)
			return
		
		# Change setting data
		old_setting = self.client.settings[setting]
		self.client.settings[setting] = value
		with open('settings.json', 'w') as f:
			json.dump(self.client.settings, f, indent=4)

		await interaction.response.send_message(f"`{setting}` is now changed to `{self.client.settings[setting]}`.", ephemeral=True)

		embed = discord.Embed(
			color=discord.Color.pink(),
			timestamp=datetime.datetime.now(),
			description=f"**{setting}**"
		)

		embed.add_field(name="Before:", value=old_setting, inline=False)
		embed.add_field(name="After:", value=value, inline=False)
		embed.set_footer(text="Bot setting changed")
		embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)

		await self.audit_channel.send(embed=embed)

	@settings.autocomplete('setting')
	async def autocomplete_callback(self, _: discord.Interaction, current: str):
		actions = sorted(self.client.settings.keys())
		
		return [
            app_commands.Choice(name=action, value=action)
            for action in actions
            if current.lower() in action.lower()
        ]

async def setup(client):
	await client.add_cog(Settings(client))