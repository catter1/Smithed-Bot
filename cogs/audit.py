import discord
import logging
import datetime
from discord.ext import commands
from libraries import bot
import libraries.constants as Constants

class Audit(commands.Cog):
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

	### EVENTS ###
		
	@commands.Cog.listener()
	async def on_message_edit(self, before: discord.Message, after: discord.Message):
		moderator = await after.guild.fetch_role(Constants.Role.MODERATOR)
		
		if after.author.bot:
			return
		
		if not after.channel.permissions_for(moderator).view_channel:
			return
		
		if before.content == after.content:
			return
		
		embed = discord.Embed(
			color=discord.Color.yellow(),
			timestamp=datetime.datetime.now(),
			description=after.jump_url
		)

		embed.add_field(name="Before:", value=before.content, inline=False)
		embed.add_field(name="After:", value=after.content, inline=False)
		embed.set_footer(text="Edited message")
		embed.set_author(name=after.author.display_name, icon_url=after.author.display_avatar)

		await self.audit_channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_message_delete(self, message: discord.Message):
		moderator = await message.guild.fetch_role(Constants.Role.MODERATOR)
        
		if message.author.bot:
			return
		
		if not message.channel.permissions_for(moderator).view_channel:
			return
		
		embed = discord.Embed(
			color=discord.Color.red(),
			timestamp=datetime.datetime.now(),
			description=f"<#{message.channel.id}>"
		)

		embed.add_field(name="Message:", value=message.content, inline=False)
		embed.set_footer(text="Deleted message")
		embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)

		await self.audit_channel.send(embed=embed)
		
	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		embed = discord.Embed(
			color=discord.Color.orange(),
			timestamp=datetime.datetime.now()
		)

		embed.set_footer(text="User left")
		embed.set_author(name=member.display_name, icon_url=member.display_avatar)

		await self.audit_channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_ban(self, guild: discord.Guild, user: discord.User):
		embed = discord.Embed(
			color=discord.Color.red(),
			timestamp=datetime.datetime.now()
		)

		ban: discord.BanEntry = await guild.fetch_ban(user)

		embed.add_field(name="Reason:", value=ban.reason or "N/A", inline=False)
		embed.set_footer(text="User banned")
		embed.set_author(name=user.display_name, icon_url=user.display_avatar)

		await self.audit_channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_member_update(self, member_before: discord.Member, member_after: discord.Member):
		if member_before.timed_out_until == member_after.timed_out_until:
			return
		
		timed_out_until = member_after.timed_out_until.replace(tzinfo=datetime.timezone.utc)
		
		embed = discord.Embed(
			color=discord.Color.yellow(),
			timestamp=datetime.datetime.now(),
			description=f"Timeout ends <t:{int(timed_out_until.timestamp())}:f>"
		)

		embed.set_footer(text="User timed out")
		embed.set_author(name=member_after.display_name, icon_url=member_after.display_avatar)

		await self.audit_channel.send(embed=embed)

async def setup(client):
	await client.add_cog(Audit(client))