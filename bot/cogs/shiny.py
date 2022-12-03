from typing import Literal, Optional
import discord, datetime
from discord import HTTPException, app_commands
from discord.ext import commands
import utils.database as db, utils.definitions as d

async def setup(client: commands.Bot):
    await client.add_cog(Shiny(client))

class Shiny(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    # @app_commands.guilds(965285949447753769)
    # @app_commands.command(name = "save", description = "For saving shinies and other useful pokemons. Warning: This command is only for 1 person per channel")
    # @app_commands.guild_only()
    # @app_commands.describe(
    #     pokemon_type = "Type of the pokemon you want to save",
    #     channel = "The channel where you will route",
    #     pokemon = "The name of the pokemon (only if ``Normal`` option is selected in ``pokemon_type``)"
    # )

    # async def save(self, interaction: discord.Interaction, pokemon_type: Literal["Shiny","Normal"], channel: discord.TextChannel, pokemon: Optional[str] = None):
        
    #     guild = db.savior_dbase[str(interaction.guild_id)]
    #     channelDoc = await guild.find_one({"_id": interaction.channel_id})
    #     memberDoc = await guild.find_one({"member": interaction.user.id})

    #     if channelDoc:
    #         userId = channelDoc["member"]

    #         channelEmbed = discord.Embed(
    #             title = "Hold UP",
    #             description = f"This channel is already in use by <@{userId}>",
    #             color = 0xf08080
    #         )

    #         await interaction.response.send_message(embed = channelEmbed)

    #     elif memberDoc:
    #         channelId = memberDoc["_id"]

    #         memberEmbed = discord.Embed(
    #             title = "Hold UP",
    #             description = f"You are already using <#{channelId}> so go there and route",
    #             color = 0xf08080
    #         )

    #         await interaction.response.send_message(embed = memberEmbed)

    #     else:
            
    #         doc = {
    #             "_id": interaction.channel_id,
    #             "member": interaction.user.id,
    #             "poke": pokemon,
    #             "type": pokemon_type,
    #             "status": "Catching"
    #         }

    #         await guild.insert_one(doc)

    #         savingEmbed = discord.Embed(
    #             description = "We will look out for your selected pokemon or shiny\nHappy Routing!!",
    #             color = 0xf08080
    #         )

    #         await interaction.response.send_message(embed = savingEmbed)
    
    @commands.command()
    @commands.is_owner()
    async def interaction_check(self, ctx: commands.Context):
        try:
            referMsg = ctx.message.to_reference()
        except HTTPException:
            await ctx.reply("No reference found")
            return
        interact = referMsg.cached_message.interaction
        if interact:
            await ctx.send(interact.user.mention)
        else:
            await ctx.send("No interaction")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            pass
            # await user.timeout(datetime.timedelta(seconds = 10))