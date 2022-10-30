import discord, itertools, os, asyncio, logging
from discord.ext import commands
from typing import Optional, Literal
import utils.definitions as d, utils.database as db, utils.help_definitions as hd
from discord import app_commands

intents = discord.Intents.all()

logging.basicConfig(level = logging.INFO)

defaultPrefix = "!"

async def get_prefix(client: commands.Bot, message: discord.Message):
    Gprefix = await db.guildPref.find_one( {"_id": str(message.guild.id)} , {"_id": 0, "Prefix": 1})
    return commands.when_mentioned_or(Gprefix["Prefix"])(client, message)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = get_prefix,
            intents = intents,
            activity = discord.Game(name = "with raffles", type = 3),
            status = discord.Status.dnd,
            case_insensitive = True
        )

    async def setup_hook(self) -> None:
        await self.load_extension("cogs.raffle")
        await self.load_extension("cogs.tickets")

client = Bot()









class PaginatedHelpCommand(commands.HelpCommand):
    context: commands.Context

    def __init__(self):
        super().__init__(
            command_attrs={
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category',
            }
        )

    async def on_help_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            # Ignore missing permission errors
            if isinstance(error.original, discord.HTTPException) and error.original.code == 50013:
                return

            await ctx.send(str(error.original))

    def get_command_signature(self, command: commands.Command) -> str:
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        def key(command) -> str:
            cog = command.cog
            return cog.qualified_name if cog else '\U0010ffff'

        entries: list[commands.Command] = await self.filter_commands(bot.commands, sort=True, key=key)

        all_commands: dict[commands.Cog, list[commands.Command]] = {}
        for name, children in itertools.groupby(entries, key=key):
            if name == '\U0010ffff':
                continue

            cog = bot.get_cog(name)
            assert cog is not None
            all_commands[cog] = sorted(children, key=lambda c: c.qualified_name)

        menu = hd.HelpMenu(hd.FrontPageSource(), ctx=self.context)
        menu.add_categories(all_commands)
        # await self.context.release()
        await menu.start()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        menu = hd.HelpMenu(hd.GroupHelpPageSource(cog, entries, prefix=self.context.clean_prefix), ctx=self.context)
        # await self.context.release()
        await menu.start()

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.help or 'No help found...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour(0xf08080))
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = hd.GroupHelpPageSource(group, entries, prefix=self.context.clean_prefix)
        self.common_command_formatting(source, group)
        menu = hd.HelpMenu(source, ctx=self.context)
        # await self.context.release()
        await menu.start()


client.help_command = PaginatedHelpCommand()







"""---------------------------------------- Event Listeners Here ------------------------------------------"""








@client.event
async def on_ready():
    print("Raffle Manager Online!!")



@client.event
async def on_guild_join(guild: discord.Guild):
	if guild.me.guild_permissions.manage_roles:

		await guild.create_role(
			name = "Raffle Permissions",
			color = 0xf08080,
			reason = "Created a role to give permissions to handle raffle(s)"
		)

		guildDetails = {"_id": str(guild.id), "Prefix": "!", "Role Created": True}
	else:
		guildDetails = {"_id": str(guild.id), "Prefix": "!", "Role Created": False}
	await db.guildPref.insert_one(guildDetails)


@client.event
async def on_guild_remove(guild):
	await db.guildPref.delete_one({"_id": str(guild.id)})



@client.listen("on_message")
async def on_message(message: discord.Message):
    if message.guild:

        guildID = message.guild.id
        guildCursor = db.raffles.find({"guild": guildID})

        # guildDocs = []

        async for i in guildCursor:
            if i["_id"] == message.channel.id:
                guildDoc = i
                break
        else:
            guildDoc = None
        
        if (message.content == f"<@!{client.user.id}>" or message.content==f"<@{client.user.id}>") and message.author != message.guild.me:

            gPrefix = await db.guildPref.find_one({"_id": str(guildID)}, {"_id": 0, "Prefix": 1})
            prefix = gPrefix["Prefix"]

            mentionEmbed = discord.Embed(
                title = "Hello There!! :wave: ",
                description = f"My prefix is ``{prefix}``",
                color = 0xf08080
            )
            await message.reply(embed = mentionEmbed)

        
        elif guildDoc:
            
            guild = db.dbase[str(guildID)]

            if message.author.id == 438057969251254293 and message.embeds != None:

                bankID = guildDoc["bank"]
                tixcost = guildDoc["Ticket Cost"]
                currentTotalTix = guildDoc["Total Tickets"]

                for embed in message.embeds:
                    if embed.description.startswith(f"<@{bankID}>, you have just been gifted"):
                        splitList = embed.description.split()

                        pkc = int(splitList[6])

                        tickets = pkc // tixcost

                        buyerid = int(splitList[9][2:-2])

                        if tickets > 0:
                            buyerdoc = await guild.find_one({"id": buyerid, "Raffle": message.channel.id})
                            if buyerdoc:
                                prevtix: int = buyerdoc["tickets"]
                                currentTix = prevtix + tickets
                                await guild.find_one_and_update({"id":buyerid},{"$set":{"tickets": currentTix}})
                            
                            else:
                                prevtix = 0
                                currentTix = tickets
                                ticketDoc = {"id": buyerid, "tickets": tickets, "Raffle": message.channel.id}
                                await guild.insert_one(ticketDoc)
                            
                            await db.raffles.find_one_and_update({"_id": message.channel.id}, {"$set": {"Total Tickets": currentTotalTix + tickets}})

                            ticketEmbed = discord.Embed(
                                title = "Tickets Bought!!!",
                                description = f"<@{buyerid}> bought {tickets} tickets!!",
                                color = 0xf08080
                                # **Raffle Name**: ``{guildDoc["RaffleName"]}``
                                # **Previous Tickets**: {prevtix}
                            )
                            ticketEmbed.add_field(name = "Raffle Name", value = guildDoc["RaffleName"])
                            ticketEmbed.add_field(name = "Previous Tickets", value = prevtix, inline = True)
                            ticketEmbed.add_field(name = "Total Tickets", value = currentTix, inline = True)
                            ticketEmbed.add_field(name = "PKC sent", value = f"{pkc}<:PKC:1019594363183038554>")

                            await message.reply(embed = ticketEmbed)
                        else:
                            await message.channel.send(f"Hold UP dude <@{buyerid}>!! Ticket Cost is {tixcost}<:PKC:1019594363183038554>")









"""------------------------------------------- Commands Here ---------------------------------------------"""











@client.hybrid_command(name = "ping", help = "For checking the latency of the bot")
async def ping(ctx: commands.Context):
    pingEmbed = discord.Embed(
        description = f"Pong! Bot Latensy: ``{round(client.latency * 1000)}ms``",
        color = 0xf08080
    )
    await ctx.reply(embed = pingEmbed)







@client.hybrid_command(name = "prefix", help = "Changes the prefix of the bot for the guild")
@commands.has_permissions(administrator = True)
@commands.guild_only()
# @app_commands.rename(newPrefix = "new prefix")
async def prefix(ctx: commands.Context, newprefix: str):
    if len(newprefix) >= 5:
        longPrefix = discord.Embed(
            title = "Prefix too long",
            description = "Please choose a shorter prefix!\nMaximum length of prefix is 4 characters.",
            color = 0xf08080
        )
        await ctx.send(embed = longPrefix, ephemeral = True)
    
    else:
        filterPrefGuild = {"_id": str(ctx.guild.id)}
        prefixSet = {"$set":{"Prefix": newprefix}}
        await db.guildPref.update_one(filterPrefGuild, prefixSet)
        prefixSuccess = discord.Embed(title = "Prefix changed!",
									  description = f"Prefix changed successfully to ``{newprefix}``",
									  color = 0xf08080)
        await ctx.send(embed = prefixSuccess)

@prefix.error
async def prefix_error(ctx: commands.Context, error: commands.errors):
    if isinstance(error, commands.MissingPermissions):
        missingPrefixPermsEmbed = discord.Embed(
            title = "Hold Up!",
            description = "You need ``Administrator`` Permission to use this command!",
            color = 0xf08080
        )
        await ctx.reply(embed = missingPrefixPermsEmbed, delete_after = 20)

    elif isinstance(error, commands.MissingRequiredArgument):
        missingArgEmbed = discord.Embed(
            title = "Prefix Needed",
            description = f"You need to give prefix with command\nFor example:- ``{ctx.prefix}prefix <New Prefix>``\nPut the new prefix in place of <New Prefix>",
            color = 0xf08080
        )
        await ctx.reply(embed = missingArgEmbed)

@client.hybrid_command(name = "invite", help = "For inviting me!!")
@commands.guild_only()
async def invite(ctx: commands.Context):
    invlink = "https://discord.com/api/oauth2/authorize?client_id=945301514946244629&permissions=2416307264&scope=bot%20applications.commands"

    inviteEmbed = discord.Embed(
        title = "Invite ME!!",
        description = f"Click [here]({invlink}) to invite me!!",
        color = 0xf08080
    )
    await ctx.reply(embed = inviteEmbed)

@client.command()
@commands.is_owner()
async def enable(ctx, *, cogname = None):
	if cogname == None:
		return
	
	try:
		await client.load_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not load cog {cogname}: {str(e)}')

	else:
		await ctx.send('Enabled Commands Successfully')



@client.command()
@commands.is_owner()
async def disable(ctx,*, cogname = None):
	if cogname == None:
		return
    
	try:
		await client.unload_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not unload cog {cogname}: {str(e)}')

	else:
		await ctx.send('Disabled Commands Successfully')

@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

@client.command()
@commands.is_owner()
async def read(ctx: commands.Context):
    msg = await discord.PartialMessage(channel = ctx.channel, id = ctx.message.reference.message_id).fetch()
    if "★" in msg.embeds[0].author.name.split()[-2]:
        await ctx.send("Shiny")
    else:
        await ctx.send("Normal")
    # await ctx.send(msg.embeds[0].author.name.split())




async def start():
	await client.start(os.environ.get('token'))
	

asyncio.run(start())