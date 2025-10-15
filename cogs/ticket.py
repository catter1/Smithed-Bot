import discord
import logging
from discord import app_commands
from discord.ext import commands
from libraries import bot
import libraries.constants as Constants

class Ticket(commands.Cog):
	def __init__(self, client: bot.SmithedBot):
		self.client: bot.SmithedBot = client

	async def cog_load(self):
		self.client.add_view(TicketCreateView())
		self.client.add_view(TicketCloseView())
		logging.info(f'> {self.__cog_name__} cog loaded')

	async def cog_unload(self):
		logging.info(f'> {self.__cog_name__} cog unloaded')
		
	### COMMAND ###
	
	@app_commands.command(name="setup_ticket", description="Send the embed/button for private ticket creation")
	@app_commands.default_permissions(administrator=True)
	@app_commands.checks.has_permissions(administrator=True)
	@app_commands.describe(
		msg_id="[Optional] a message id to edit instead of creating a new message"
	)
	async def settings(self, interaction: discord.Interaction, msg_id: str = None) -> None:
		""" /setup_ticket [msg_id] """

		if msg_id:
			if not msg_id.isdigit():
				await interaction.response.send_message("The message ID provided is not numeric! Please submit a real id.", ephemeral=True)
				return
			try:
				msg = await interaction.channel.fetch_message(msg_id)
			except discord.NotFound:
				await interaction.response.send_message("Message not found! If you are creating a new message, you should leave the `msg_id` field empty.", ephemeral=True)
				return
		else:
			msg = None

		await interaction.response.send_modal(TicketSetupMenu(msg=msg))
			
	### MODALS ###

class TicketSetupMenu(discord.ui.Modal):
	def __init__(self, msg: discord.Message = None):
		super().__init__(title="Create Ticket Message", timeout=None, custom_id="smithed:ticketcreationmodal")
		self.msg = msg

	embed_title = discord.ui.TextInput(
		label='Embed Title',
		style=discord.TextStyle.short,
		placeholder='ex: Contact the Mods',
		required=True,
		max_length=64
	)

	embed_message = discord.ui.TextInput(
		label='Embed Message',
		style=discord.TextStyle.long,
		placeholder='A longer description, such as "Need to contact us? Click the button below to open a new thread"',
		required=True,
		max_length=1024
	)

	async def on_submit(self, interaction: discord.Interaction):
		embed_title = self.embed_title.value
		embed_message = self.embed_message.value
		
		embed = discord.Embed(
			colour=discord.Colour.blue(),
			title=embed_title,
			description=embed_message
		)

		if self.msg:
			await self.msg.edit(embed=embed, view=TicketCreateView())
			await interaction.response.defer()
			return
		
		await interaction.channel.send(embed=embed, view=TicketCreateView())
		await interaction.response.defer()

class TicketCreateButton(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.blurple, label="Create Ticket", disabled=False, custom_id="smithed:create_ticket_button", emoji=Constants.Emoji.TICKET)

	async def callback(self, interaction):
		for thread in interaction.channel.threads:
			if thread.name == interaction.user.name and not thread.archived:
				await interaction.response.send_message(f"Please refrain from opening more than one ticket. You already have an open one here: <#{thread.id}>", ephemeral=True)
				return
			
		new_thread = await interaction.channel.create_thread(
			name=interaction.user.name,
			message=None,
			type=discord.ChannelType.private_thread,
			reason="New support ticket",
			invitable=False,
			slowmode_delay=None
		)

		first_msg = await new_thread.send(f"Hey <@{interaction.user.id}>, this ticket has been created for you to talk with the <@{Constants.Role.MODERATOR}> team. Please explain your request, and they will be with you soon.", view=TicketCloseView())
		await first_msg.pin()
		await interaction.response.send_message(f"Your ticket has been created! Go visit it here: <#{new_thread.id}>", ephemeral=True)

class TicketCloseButton(discord.ui.Button):
	def __init__(self):
		super().__init__(style=discord.ButtonStyle.red, label="Close Ticket", disabled=False, custom_id="smithed:close_ticket_button", emoji=Constants.Emoji.RESOLVE)

	async def callback(self, interaction):
		await interaction.response.defer()
		await interaction.channel.send("This ticket is now being closed.")
		await interaction.channel.edit(locked=True, archived=True, reason="Closing support ticket")

class TicketCreateView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(TicketCreateButton())

class TicketCloseView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(TicketCloseButton())


async def setup(client):
	await client.add_cog(Ticket(client))