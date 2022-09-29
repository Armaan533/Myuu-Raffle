import discord
from discord.app_commands import Transform
from discord import app_commands
from discord.ext import commands
import utils.definitions as d, utils.database as db
# from utils import definitions as d, database as db

class Tickets(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.hybrid_group(name = "tickets")
    async def tickets():
        pass

    @tickets.command(name = "add", help = "For adding tickets to a member")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @discord.app_commands.describe(
        raffle_name = "name of raffle in which tickets are going to be added",
        member = "person to whom tickets will be given",
        tickets = "no of tickets which are supposed to be given"
    )
    # @app_commands.rename(raffle_name = "raffle name")
    @commands.guild_only()
    async def add(self, ctx: commands.Context, raffle_name: Transform[str, d.ChoiceTransformer], member: discord.Member, tickets: int):
        raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name})
        if raffleDoc:
            guild = db.dbase[str(ctx.guild.id)]
            raffleid = raffleDoc["_id"]
            currentTotalTix = raffleDoc["Total Tickets"]

            buyerDoc = await guild.find_one({"_id": member.id, "Raffle": raffleid})
            
            if tickets > 0:
                if buyerDoc:
                    prevtix: int = buyerDoc["tickets"]
                    currentTix = prevtix + tickets
                    await guild.find_one_and_update({"_id": member.id, "Raffle": raffleid},{"$set":{"tickets": currentTix}})

                else:
                    prevtix = 0
                    currentTix = tickets
                    ticketDoc = {"_id": member.id, "tickets": tickets}
                    await guild.insert_one(ticketDoc)
                
                await db.raffles.find_one_and_update({"_id": raffleid}, {"$set": {"Total Tickets": currentTotalTix + tickets}})
                ticketsAddedEmbed = discord.Embed(
                    title = "Tickets Added",
                    description = f"{tickets} tickets added by {ctx.author.mention} in wallet of {member.mention}\nCurrent Tickets: ``{currentTix}``",
                    color = 0xf08080
                )
                await ctx.reply(embed = ticketsAddedEmbed)
            else:
                await ctx.reply(f"Hold UP dude {ctx.author.mention}!! \nThe minimum number of tickets you can give is 1")
        else:
            noRaffleMatchEmbed = discord.Embed(
                title = "Invalid Name",
                description = f"No raffle named ``{raffle_name}`` exists in this server",
                color = 0xf08080
            )
            noRaffleMatchEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

            await ctx.reply(embed = noRaffleMatchEmbed)

    @add.error
    async def add_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))

    
    @tickets.command(name = "remove", help = "For manually removing/deleting tickets from wallet of a user")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @app_commands.describe(
        raffle_name = "name of raffle from which tickets are going to be removed",
        member = "person from whom tickets will be removed",
        tickets = "no of tickets which are supposed to be removed"
    )
    # @app_commands.rename(raffle_name = "raffle name")
    async def remove(self, ctx: commands.Context, raffle_name: Transform[str, d.ChoiceTransformer], member: discord.Member, tickets: int):
        raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name})
        
        if raffleDoc:
            guild = db.dbase[str(ctx.guild.id)]
            raffleid = raffleDoc["_id"]
            currentTotalTix = raffleDoc["Total Tickets"]

            buyerDoc = await guild.find_one({"_id": member.id, "Raffle": raffleid})

            if tickets > 0:
                if buyerDoc["tickets"] >= tickets:
                    
                    prevTix = buyerDoc["tickets"]
                    currentTix = prevTix - tickets
                    await guild.find_one_and_update({"_id": member.id, "Raffle": raffleid},{"$set":{"tickets": currentTix}})

                    await db.raffles.find_one_and_update({"_id": raffleid}, {"$set": {"Total Tickets": currentTotalTix - tickets}})

                    ticketsRemovedEmbed = discord.Embed(
                        title = "Tickets Removed",
                        description = f"{tickets} tickets removed by {ctx.author.mention} from the wallet of {member.mention}\nCurrent Tickets: ``{currentTix}``",
                        color = 0xf08080
                    )
                    await ctx.reply(embed = ticketsRemovedEmbed)
                
                else:
                    lessTicketsEmbed = discord.Embed(
                        title = "Invalid Number of Tickets",
                        description = f"You can't remove {tickets} tickets because {member.mention} doesn't even have that many tickets",
                        color = 0xf08080
                    )
                    await ctx.reply(embed = lessTicketsEmbed)
            else:
                await ctx.reply(f"Hold UP dude {ctx.author.mention}!! \nThe minimum number of tickets you can remove is 1")
        
        else:
            noRaffleMatchEmbed = discord.Embed(
                title = "Invalid Name",
                description = f"No raffle named ``{raffle_name}`` exists in this server",
                color = 0xf08080
            )
            noRaffleMatchEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

            await ctx.reply(embed = noRaffleMatchEmbed)



async def setup(client: commands.Bot):
    client.add_cog(Tickets(client))