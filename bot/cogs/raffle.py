import io, traceback, sys
import discord, asyncio, os
from discord.ext import commands
import utils.database as db, utils.definitions as d
# from typing import Literal, Optional, Union
from discord import app_commands
from PIL import Image

async def setup(client: commands.Bot):
    await client.add_cog(Raffle(client))




class Raffle(commands.Cog, name = "Raffle Commands"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji.from_str("<:buizel:1025754191592951929>")

    @commands.hybrid_command(name = "raffles", help = "For checking all the ongoing raffles in the server")
    @commands.guild_only()
    async def raffles(self, ctx: commands.Context):
        await ctx.defer()
        allRaffles = db.raffles.find({"guild": ctx.guild.id})
        raffleList = []
        async for raffle in allRaffles:
            raffleList.append(raffle)

        if len(raffleList) == 0:
            rafflesEmbed = discord.Embed(
                description = "No raffles going on in this server <:F_:852865419090067476>",
                color = 0xf08080
            )
            await ctx.reply(embed = rafflesEmbed)
        else:
            formatter = d.Source(entries = raffleList, title = None, sourceType = "raffles_list", per_page = 10)
            menu = d.MenuPages(formatter)
            await menu.start(ctx)



    @commands.hybrid_group()
    @commands.guild_only()
    async def raffle(self, ctx: commands.Context):
        pass

    @raffle.command(name = "create", help = "For creating a raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.bot_has_permissions(manage_messages = True)
    @commands.guild_only()
    async def create(self, ctx: commands.Context):
        if ctx.interaction:
            NameEmbed = discord.Embed(
                description = "Enter a suitable name for the raffle!",
                color = 0xf08080
            )
            NameEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

            msg = await ctx.reply(embed = NameEmbed)
            authorcheck = lambda a: a.author == ctx.author and a.channel == ctx.channel

            try:
                name: discord.Message = await self.client.wait_for("message", check = authorcheck, timeout = 50)
            except asyncio.TimeoutError:
                
                name = None
                return

            await name.delete()
            
            if name.content.lower() == "stop" or name == None:
                await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080))

            else:
                InfoEmbed = discord.Embed(
                    description = "Do ```/mypkinfo <pokemon>``` or ```/box pk <position> <box number>``` to select pokemon for raffle\n\n:warning: **Warning!! This needs textual commands in myuu to be turned off** :warning:",
                    color = 0xf08080
                )
                InfoEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

                await msg.edit(embed = InfoEmbed)

                # infocheck = lambda message: message.author.id in [438057969251254293, ctx.author.id] and message.channel == ctx.channel and message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpk.png","boxpk","unknown.png","unknown"]
                # def infocheck(message: discord.Message):
                #     if message.channel == ctx.channel:
                #         if message.content.lower() == "stop" and message.author.id == ctx.author.id:
                #             return True
                #         elif len(message.attachments) > 1 and message.author.id == 438057969251254293:
                #             message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpk.png","boxpk","unknown.png","unknown"]

                # infocheck = lambda message: message.channel == ctx.channel and ((message.content.lower() == "stop" and message.author.id == ctx.author.id) or (len(message.attachments) > 1 and message.author.id == 438057969251254293 ))
                
                def infocheck(message: discord.Message):
                    if message.channel == ctx.channel:
                        if message.author == ctx.author:
                            if message.content.lower() == "stop" or len(message.attachments) > 1:
                                return message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpokemon.png","boxpokemon"]
                        elif message.author.id == 438057969251254293:
                            if len(message.attachments) >= 1:
                                return message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpokemon.png","boxpokemon"]
                        else:
                            return False
                    

                try:
                    info: discord.Message = await self.client.wait_for("message", check = infocheck, timeout = 50)
                except asyncio.TimeoutError:
                    
                    info = None
                    return
                
                await info.delete()

                if info.content.lower() == "stop" or info == None:
                    await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080))

                else:
                    # infoAttachments = info.attachments
                    # infoimg = await info.attachments[0].read()
                    # for attachment in info.attachments:

                    infoimgFile = await info.attachments[0].to_file()
                    channel = self.client.get_channel(1037968491246006282)
                    imgfilemsg = await channel.send(file = infoimgFile)
                    infoimgurl = imgfilemsg.attachments[0].url


                    CostEmbed = discord.Embed(
                        description = f"Enter the ticket cost of the raffle ``{name.content}``",
                        color = 0xf08080
                    )
                    CostEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

                    await msg.edit(embed = CostEmbed)
                    
                    tixcheck = lambda a: a.author.id == ctx.author.id and a.channel == ctx.channel and (a.content.isnumeric() or a.content.lower() == "stop")

                    try:
                        tixcost: discord.Message = await self.client.wait_for("message", check = tixcheck, timeout = 50)
                    except asyncio.TimeoutError:
                        
                        tixcost = None
                        return

                    await tixcost.delete()

                    if tixcost.content.lower() == "stop" or tixcost == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080))

                    else:

                        ChannelEmbed = discord.Embed(
                            description = f"Mention the channel where payment is supposed to be done\nFor example: {ctx.channel.mention}",
                            color = 0xf08080
                        )
                        ChannelEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

                        await msg.edit(embed = ChannelEmbed)

                        channelcheck = lambda cmsg: cmsg.author == ctx.author and cmsg.channel == ctx.channel and ((cmsg.content.startswith("<#") and cmsg.content.endswith(">")) or cmsg.content.lower() == "stop")
                        
                        try:
                            channelname: discord.Message = await self.client.wait_for("message", check = channelcheck, timeout = 50)
                        except asyncio.TimeoutError:
                            
                            channelname = None
                            return

                        await channelname.delete()

                        if channelname.content.lower() == "stop" or channelname == None:
                            await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080))

                        else:

                            channelid = channelname.content.lstrip("<#").rstrip(">")

                            BankEmbed = discord.Embed(
                                description = f"Mention the user where the <:PKC:1019594363183038554> raffle money needs to be stored\nFor example: {ctx.author.mention}",
                                color = 0xf08080
                            )
                            BankEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

                            await msg.edit(embed = BankEmbed)

                            bankcheck = lambda bmsg: bmsg.author == ctx.author and bmsg.channel == ctx.channel and ((bmsg.content.startswith("<@") and bmsg.content.endswith(">")) or (bmsg.content.startswith("<@!") and bmsg.content.endswith(">")) or bmsg.lower() == "stop")

                            try:
                                bankname: discord.Message = await self.client.wait_for("message", check = bankcheck, timeout = 50)
                            except asyncio.TimeoutError:
                                bankname = None
                                return

                            await bankname.delete()

                            if bankname.content.lower() == "stop" or bankname == None:
                                await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080))

                            else:

                                raffledetails = {
                                    "_id": int(channelid),
                                    "RaffleName": name.content,
                                    "Ticket Cost": int(tixcost.content),
                                    "bank": int(bankname.content.lstrip("<@!").rstrip(">")),
                                    "guild": ctx.guild.id,
                                    "info": infoimgurl,
                                    "Total Tickets": 0
                                }

                                await db.raffles.insert_one(raffledetails)

                                await msg.edit(embed = discord.Embed(
                                    title = "Raffle Created!",
                                    description = f"Raffle named ``{name.content}`` for channel <#{channelid}> created successfully!!",
                                    color = 0xf08080
                                ))
        else:
            pass
            
    @create.error
    async def create_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.CheckAnyFailure):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    

    @raffle.command(name = "delete", help = "For deleting a raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def delete(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        if ctx.interaction:
            raffledoc = await db.raffles.find_one({"RaffleName": raffle_name, "guild": ctx.guild.id})
            if raffledoc:
                guild = db.dbase[str(ctx.guild.id)]
                raffle = raffledoc["_id"]

                await guild.delete_many({"Raffle": raffle})
                await db.raffles.delete_one({"_id": raffle})

                raffleDeletedEmbed = discord.Embed(
                    description = f"Raffle named ``{raffle_name}`` deleted successfully",
                    color = 0xf08080
                )

                await ctx.reply(embed = raffleDeletedEmbed)

            else:
                noRaffleMatchEmbed = discord.Embed(
                    title = "Invalid Name",
                    description = f"No raffle named ``{raffle_name}`` exists in this server",
                    color = 0xf08080
                )
                noRaffleMatchEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

                await ctx.reply(embed = noRaffleMatchEmbed)
        else:
            pass

    @delete.error
    async def delete_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.CheckAnyFailure):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @raffle.command(name = "info", help = "For checking information about a raffle")
    @commands.guild_only()
    async def info(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        if ctx.interaction:
            raffledoc = await db.raffles.find_one({"RaffleName": raffle_name, "guild": ctx.guild.id})
            if raffledoc:
                await ctx.defer()
                guild = db.dbase[str(ctx.guild.id)]
                bank = discord.utils.get(ctx.guild.members, id = raffledoc["bank"])
                channel = raffledoc["_id"]
                raffleName = raffledoc["RaffleName"]
                totalTickets = raffledoc["Total Tickets"]
                ticketCost = raffledoc["Ticket Cost"]

                infoEmbed = discord.Embed(
                    title = "Raffle Info",
                    color = 0xf08080
                )
                infoEmbed.add_field(name = "Raffle Name", value = raffleName)
                infoEmbed.add_field(name = "Ticket Cost", value = ticketCost)
                infoEmbed.add_field(name = "Bank of Raffle", value = bank.mention)
                infoEmbed.add_field(name = "Payment Channel", value = f"<#{channel}>")
                infoEmbed.add_field(name = "Total Tickets Sold", value = f"{totalTickets} tickets")

                # if f"info{raffleName}.png" not in os.listdir(path = "/app/bot/assets/"):
                    
                #     aboutimg = Image.open(io.BytesIO(raffledoc["info"]))
                #     aboutimg.save(f"bot/assets/info{raffleName}.png", format = "png")

                # Imgfile = discord.File(raffledoc["info"], filename = f"info{raffleName}.png")
                infoEmbed.set_image(url = raffledoc["info"])
                
                await ctx.reply(embed = infoEmbed)

            else:
                noRaffleMatchEmbed = discord.Embed(
                    title = "Invalid Name",
                    description = f"No raffle named ``{raffle_name}`` exists in this server",
                    color = 0xf08080
                )
                noRaffleMatchEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

                await ctx.reply(embed = noRaffleMatchEmbed)
        else:
            pass



    @raffle.command(name = "roll", help = "For determining the winner(s) of the mentioned raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def roll(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        if ctx.interaction:
            raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name, "guild": ctx.guild.id})

            if raffleDoc:
                guild = db.dbase[str(ctx.guild.id)]     

                userlist = []
                ticketlist = []

                async for doc in guild.find({"Raffle": raffleDoc["_id"]}, {"id": 1, "tickets": 1}):
                    userlist.append(doc["id"])
                    ticketlist.append(doc["tickets"])

                if len(userlist) != 0 and len(ticketlist) != 0:
                    await ctx.defer()

                    winnerId = d.random_chooser(userlist, ticketlist)
                    winnerDoc = await guild.find_one({"id": winnerId}, {"_id": 0, "tickets": 1})
                    winnerTickets = winnerDoc["tickets"]
                    winner = discord.utils.get(ctx.guild.members, id = winnerId)

                    RollEmbed = discord.Embed(
                        title = "Congratulations",
                        color = 0xf08080
                    )
                    RollEmbed.add_field(name = "Raffle Name", value = raffle_name)
                    RollEmbed.add_field(name = "Winner", value = winner.mention)
                    RollEmbed.add_field(name = "Total Tickets", value = raffleDoc["Total Tickets"], inline = True)
                    RollEmbed.add_field(name = "Winner's Tickets", value = winnerTickets, inline = True)

                    PopperFile = discord.File("bot/assets/party_popper.gif", filename = "party_popper.gif")
                    RollEmbed.set_thumbnail(url = "attachment://party_popper.gif")

                    await ctx.reply(content = f"||<@{winnerId}>||", embed = RollEmbed, file = PopperFile)

                else:

                    noBuyers = discord.Embed(
                        title = "No Buyers yet",
                        description = "No one bought any tickets yet <:F_:852865419090067476>",
                        color = 0xf08080
                    )
                    await ctx.reply(embed = noBuyers)
            
            else:

                noRaffleEmbed = discord.Embed(
                    title = "Invalid Name",
                    description = f"No Raffle named ``{raffle_name}`` exists in this server",
                    color = 0xf08080
                )
                noRaffleEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

                await ctx.reply(embed = noRaffleEmbed)
        else:
            pass

    @roll.error
    async def roll_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.CheckAnyFailure):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @raffle.command(name = "list", help = "For checking the ticket list of a raffle")
    @commands.guild_only()
    async def list(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        if ctx.interaction:
            await ctx.defer()
            raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name, "guild": ctx.guild.id})

            if raffleDoc:
                guild = db.dbase[str(ctx.guild.id)]
                data = []

                async for doc in guild.find({"Raffle": raffleDoc["_id"]}, {"id": 1 ,"tickets": 1}).sort("tickets", -1):
                    member = discord.utils.get(ctx.guild.members, id = doc["id"])
                    if member:
                        data.append({"Member": member, "tickets": doc["tickets"]})
                    else:
                        continue

                if len(data) != 0:
                    formatter = d.Source(entries = data, title = raffle_name, sourceType = "ticket_list", per_page = 10)
                    menu = d.MenuPages(formatter)
                    await menu.start(ctx)

                else:
                    noBuyers = discord.Embed(
                        title = "No Buyers yet",
                        description = "No one bought any tickets yet <:F_:852865419090067476>",
                        color = 0xf08080
                    )
                    await ctx.reply(embed = noBuyers)

            else:

                noRaffleEmbed = discord.Embed(
                    title = "Invalid Name",
                    description = f"No Raffle named ``{raffle_name}`` exists in this server",
                    color = 0xf08080
                )
                noRaffleEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

                await ctx.reply(embed = noRaffleEmbed)
        else:
            pass


    @raffle.command(name = "edit", help = "For editing the information about the raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.bot_has_permissions(manage_messages = True)
    @commands.guild_only()
    async def edit(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        if ctx.interaction:
            raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name, "guild": ctx.guild.id})

            if raffleDoc:
                editEmbed = discord.Embed(
                    title = f"Edit Raffle {raffle_name}",
                    description = """Edit:-
                        Raffle Name- \U0001f1f3
                        Pokemon Info- \U0001f1ee
                        Ticket Cost- \U0001f1f9
                        Bank- \U0001f1e7
                        Payment Channel- \U0001f1f5
                        Stop Editing- \U000023f9""",
                    color = 0xf08080
                )
                view = d.EditChoice()

                msg = await ctx.reply(embed = editEmbed, view = view)
                await view.wait()
                authorcheck = lambda a: a.author == ctx.author and a.channel == ctx.channel

                if view.choice == "name":
                    NameEmbed = discord.Embed(
                        description = "Enter a suitable name for the raffle!",
                        color = 0xf08080
                    )
                    NameEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                    await msg.edit(embed = NameEmbed)
                    

                    try:
                        name: discord.Message = await self.client.wait_for("message", check = authorcheck, timeout = 50)
                    except asyncio.TimeoutError:
                        
                        name = None
                        return

                    await name.delete()
                    
                    if name.content.lower() == "stop" or name == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080))
                    else:
                        await db.raffles.find_one_and_update({"_id":raffleDoc["_id"]},{"$set":{"RaffleName":name.content}})
                        
                        await msg.edit(embed = discord.Embed(
                            title = "Raffle edited",
                            description = "Raffle Name edited successfully!",
                            color = 0xf08080
                        ))
                elif view.choice == "info":
                    InfoEmbed = discord.Embed(
                        description = "Do ```/mypkinfo <pokemon>``` or ```/box pk <position> <box number>```  to select pokemon for raffle\n\n:warning: **Warning!! This needs textual commands in myuu to be turned off** :warning:",
                        color = 0xf08080
                    )
                    InfoEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                    await msg.edit(embed = InfoEmbed)

                    def infocheck(message: discord.Message):
                        if message.channel == ctx.channel:
                            if message.author == ctx.author:
                                if message.content.lower() == "stop" or len(message.attachments) > 1:
                                    return True
                            elif message.author.id == 438057969251254293:
                                if len(message.attachments) >= 1:
                                    print("attachment identified")
                                    return message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpokemon.png","boxpokemon"]
                            else:
                                return False

                    try:
                        info: discord.Message = await self.client.wait_for("message", check = infocheck, timeout = 50)
                    except asyncio.TimeoutError:
                        
                        info = None
                        return
                    
                    await info.delete()

                    if info.content.lower() == "stop" or info == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080))

                    else:
                        infoimgFile = await info.attachments[0].to_file()
                        channel = self.client.get_channel(1037968491246006282)
                        infoimgmsg = await channel.send(file = infoimgFile)
                        await db.raffles.find_one_and_update({"_id": raffleDoc["_id"]}, {"$set": {"info": infoimgmsg.attachments[0].url}})

                        await msg.edit(embed = discord.Embed(
                            title = "About Raffle edited",
                            description = "About Raffle edited successfully!",
                            color = 0xf08080
                            ),delate_after = 10)
                        

                elif view.choice == "ticket":

                    CostEmbed = discord.Embed(
                        description = f"Enter the ticket cost of the raffle ``{raffle_name}``",
                        color = 0xf08080
                    )
                    CostEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                    await msg.edit(embed = CostEmbed)
                    
                    tixcheck = lambda a: a.author.id == ctx.author.id and a.channel == ctx.channel and (a.content.isnumeric() or a.content.lower() == "stop")

                    try:
                        tixcost: discord.Message = await self.client.wait_for("message", check = tixcheck, timeout = 50)
                    except asyncio.TimeoutError:
                        
                        tixcost = None
                        return

                    await tixcost.delete()

                    if tixcost.content.lower() == "stop" or tixcost == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080))
                    else:
                        await db.raffles.find_one_and_update({"_id":raffleDoc["_id"]},{"$set":{"Ticket Cost": int(tixcost.content)}})
                        await msg.edit(embed = discord.Embed(
                            title = "Cost edited", 
                            description = "Ticket Cost edited successfully", 
                            color = 0xf08080))

                elif view.choice == "bank":
                    BankEmbed = discord.Embed(
                        description = f"Mention the user where the <:PKC:1019594363183038554> raffle money needs to be stored\nFor example: {ctx.author.mention}",
                        color = 0xf08080
                    )
                    BankEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                    await msg.edit(embed = BankEmbed)

                    bankcheck = lambda bmsg: bmsg.author == ctx.author and bmsg.channel == ctx.channel and ((bmsg.content.startswith("<@") and bmsg.content.endswith(">")) or (bmsg.startswith("<@!") and bmsg.content.endswith(">")) or bmsg.content.lower() == "stop")

                    try:
                        bankname: discord.Message = await self.client.wait_for("message", check = bankcheck, timeout = 50)
                    except asyncio.TimeoutError:
                        bankname = None
                        return

                    await bankname.delete()

                    if bankname.content.lower() == "stop" or bankname == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080))
                    else:
                        await db.raffles.find_one_and_update({"_id": raffleDoc["_id"]},{"$set": {"bank": int(bankname.content.lstrip("<@!").rstrip(">"))}})
                        
                        await msg.edit(embed = discord.Embed(
                            title = "Bank ID edited", 
                            description = "Bank ID edited successfully", 
                            color = 0xf08080))
                
                elif view.choice == "channel":
                    ChannelEmbed = discord.Embed(
                            description = f"Mention the channel where payment is supposed to be done\nFor example: {ctx.channel.mention}",
                            color = 0xf08080
                        )
                    ChannelEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                    await msg.edit(embed = ChannelEmbed)

                    channelcheck = lambda cmsg: cmsg.author == ctx.author and cmsg.channel == ctx.channel and ((cmsg.content.startswith("<#") and cmsg.content.endswith(">")) or cmsg.content.lower() == "stop")
                        
                    try:
                        channelname: discord.Message = await self.client.wait_for("message", check = authorcheck, timeout = 50)
                    except asyncio.TimeoutError:
                            
                        channelname = None
                        return

                    await channelname.delete()

                    if channelname.content.lower() == "stop" or channelname == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080))
                    else:
                        channel = int(channelname.content.lstrip("<#").rstrip(">"))
                        # await db.raffles.find_one_and_update({"_id": raffleDoc["_id"]},{"$set": {"_id": channel}})
                        
                        guild = db.dbase[str(ctx.guild.id)]

                        async for doc in guild.find({"Raffle": raffleDoc["_id"]}):
                            print(channel)
                            guild.update_one(doc, {"$set":{"Raffle": channel}})

                        await db.raffles.delete_one(raffleDoc)
                        raffleDoc["_id"] = channel
                        await db.raffles.insert_one(raffleDoc)
                        
                        
                        

                        await msg.edit(embed = discord.Embed(
                            title = "Payment Channel edited",
                            description = "Payment Channel edited successfully!",
                            color = 0xf08080
                        ))

                else:
                    await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080))

            else:
                noRaffleEmbed = discord.Embed(
                    title = "Invalid Name",
                    description = f"No Raffle named ``{raffle_name}`` exists in this server",
                    color = 0xf08080
                )
                noRaffleEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

                await ctx.reply(embed = noRaffleEmbed)
        else:
            pass

    @edit.error
    async def edit_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.CheckAnyFailure):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

