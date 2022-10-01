import random, discord
from urllib import response
import utils.database as db
from discord.ext import commands, menus
from discord import app_commands, Interaction, ui

class ChoiceTransformerError(app_commands.AppCommandError):
    pass

class ChoiceTransformer(app_commands.Transformer):

	async def transform(self, interaction: Interaction, value: str, /) -> str:
		options = db.raffles.find({"guild": interaction.guild_id})
		async for option in options:
			if value == option["RaffleName"]:
				return value
		raise ChoiceTransformerError(f'"{value}" is not a valid option.')

	async def autocomplete(self, interaction: Interaction, value: str, /) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name = option["RaffleName"], value = option["RaffleName"]) async for option in db.raffles.find({"guild": interaction.guild_id})]



def random_chooser(userlist: list, tixlist: list):
	return random.choices(userlist, weights = tixlist,k=1)[0]


class MenuPages(ui.View, menus.MenuPages):
	def __init__(self, source):
		super().__init__(timeout = 60)
		self._source = source
		self.current_page = 0
		self.ctx: commands.Context = None
		self.message: discord.Message = None

	async def send_initial_message(self, ctx: commands.Context):
		page = await self._source.get_page(0)
		kwargs = await self._get_kwargs_from_page(page)
		return await ctx.interaction.followup.send_message(**kwargs)

	async def start(self, ctx: commands.Context, *, channel = None, wait = False):
		await self._source._prepare_once()
		self.ctx = ctx
		self.message = await self.send_initial_message(ctx)

	async def _get_kwargs_from_page(self, page):
		value = await super()._get_kwargs_from_page(page)
		if "view" not in value:
			value.update({"view": self})
		return value

	async def interaction_check(self, interaction):
		return interaction.user == self.ctx.author

	@ui.button(label = "≪", style = discord.ButtonStyle.gray)
	async def first_page(self, interaction: Interaction, button):
		await self.show_page(0)

	@ui.button(label = "Previous Page", style = discord.ButtonStyle.blurple)
	async def before_page(self, interaction: Interaction, button):
		if self.current_page == 0:
			await interaction.followup.send_message("You can't go to previous page because it doesn't exists", ephemeral = True)
		else:
			await self.show_checked_page(self.current_page - 1)

	@ui.button(emoji = "\U000023f9", style = discord.ButtonStyle.red)
	async def stop_page(self, interaction: Interaction, button):
		self.stop()

	@ui.button(label = "Next Page", style = discord.ButtonStyle.blurple)
	async def next_page(self, interaction: Interaction, button):
		if self.current_page == self._source.get_max_pages() - 1:
			await interaction.followup.send_message("You can't go to previous page because it doesn't exists", ephemeral = True)
		else:
			await self.show_checked_page(self.current_page + 1)

	@ui.button(label = "≫", style = discord.ButtonStyle.gray)
	async def last_page(self, interaction: Interaction, button):
		await self.show_page(self._source.get_max_pages() - 1)

class Source(menus.ListPageSource):
	def __init__(self, entries, name,*, per_page):
		self.name = name
		super().__init__(entries, per_page=per_page)
		

	async def format_page(self, menu, data):
		embed = discord.Embed(
			title = self.name,
			description = "Ticket List",
			color = 0xf08080
		)
		for i in data:
			embed.add_field(name = i["Member"], value = i["tickets"], inline = False)

		return embed


class EditChoice(ui.View):

	def __init__(self, *, timeout = 180):
		super().__init__(timeout=timeout)
		self.choice = None

	@ui.button(emoji = "\U0001f1f3", style = discord.ButtonStyle.blurple)
	async def name_choice(self, interaction: Interaction, button):
		await interaction.response.defer(thinking = True)
		self.choice = "name"
		self.stop()

	@ui.button(emoji = "\U0001f1ee", style = discord.ButtonStyle.blurple)
	async def info_choice(self, interaction: Interaction, button):
		await interaction.response.defer(thinking = True)
		self.choice = "info"
		self.stop()

	@ui.button(emoji = "\U0001f1f9", style = discord.ButtonStyle.blurple)
	async def ticket_choice(self, interaction: Interaction, button):
		await interaction.response.defer(thinking = True)
		self.choice = "ticket"
		self.stop()

	@ui.button(emoji = "\U0001f1e7", style = discord.ButtonStyle.blurple)
	async def bank_choice(self, interaction: Interaction, button):
		await interaction.response.defer(thinking = True)
		self.choice = "bank"
		self.stop()

	@ui.button(emoji = "\U0001f1f5", style = discord.ButtonStyle.blurple)
	async def channel_choice(self, interaction: Interaction, button):
		await interaction.response.defer(thinking = True)
		self.choice = "channel"
		self.stop()

	@ui.button(emoji = "\U000023f9", style = discord.ButtonStyle.blurple)
	async def stop_choice(self, interaction: Interaction, button):
		await interaction.response.defer()
		self.stop()
