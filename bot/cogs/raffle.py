import io
import discord, asyncio, os
from discord.ext import commands
import utils.database as db, utils.definitions as d
# from typing import Literal, Optional, Union
from discord import app_commands
from PIL import Image

async def setup(client: commands.Bot):
    await client.add_cog(Raffle(client))




class Raffle(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_group()
    @commands.guild_only()
    async def raffle():
        pass

    @raffle.command(name = "create", help = "For creating a raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def create(self, ctx: commands.Context):
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
            await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080), delete_after = 10)

        else:
            InfoEmbed = discord.Embed(
                description = "Do ```.mypkinfo <pokemon>``` or ```.boxpk <box> <position>``` or ```send the image containing info of the pokemon``` to select pokemon for raffle",
                color = 0xf08080
            )
            InfoEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

            await msg.edit(embed = InfoEmbed)

            infocheck = lambda message: message.author.id in [438057969251254293, ctx.author.id] and message.channel == ctx.channel and message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpk.png","boxpk","unknown.png","unknown"]

            try:
                info: discord.Message = await self.client.wait_for("message", check = infocheck, timeout = 50)
            except asyncio.TimeoutError:
                
                info = None
                return
            
            await info.delete()

            if info.content.lower() == "stop" or info == None:
                await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080), delete_after = 10)

            else:
                infoimg = await info.attachments[0].read()

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
                    await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080), delete_after = 10)

                else:

                    ChannelEmbed = discord.Embed(
                        description = f"Mention the channel where payment is supposed to be done\nFor example: {ctx.channel.mention}",
                        color = 0xf08080
                    )
                    ChannelEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

                    await msg.edit(embed = ChannelEmbed)

                    channelcheck = lambda cmsg: cmsg.author == ctx.author and cmsg.channel == ctx.channel and ((cmsg.startswith("<#") and cmsg.endswith(">")) or cmsg.lower() == "stop")
                    
                    try:
                        channelname: discord.Message = self.client.wait_for("message", check = authorcheck, timeout = 50)
                    except asyncio.TimeoutError:
                        
                        channelname = None
                        return

                    await channelname.delete()

                    if channelname.content.lower() == "stop" or channelname == None:
                        await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080), delete_after = 10)

                    else:

                        channelid = channelname.content.lstrip("<#").rstrip(">")

                        BankEmbed = discord.Embed(
                            description = f"Mention the user where the <:PKC:1019594363183038554> raffle money needs to be stored\nFor example: {ctx.author.mention}",
                            color = 0xf08080
                        )
                        BankEmbed.set_footer(text = "Send 'stop' to stop the creation of raffle")

                        await msg.edit(embed = BankEmbed)

                        bankcheck = lambda bmsg: bmsg.author == ctx.author and bmsg.channel == ctx.channel and ((bmsg.startswith("<@") and bmsg.endswith(">")) or (bmsg.startswith("<@!") and bmsg.endswith(">")) or bmsg.lower() == "stop")

                        try:
                            bankname: discord.Message = await self.client.wait_for("message", check = bankcheck, timeout = 50)
                        except asyncio.TimeoutError:
                            bankname = None
                            return

                        await bankname.delete()

                        if bankname.content.lower() == "stop" or bankname == None:
                            await msg.edit(embed = discord.Embed(description = "Raffle Creation Process Stopped", color = 0xf08080), delete_after = 10)

                        else:

                            raffledetails = {
                                "_id": int(channelid),
                                "RaffleName": name.content,
                                "Ticket Cost": int(tixcost.content),
                                "bank": int(bankname.content.lstrip("<@!").rstrip(">")),
                                "guild": ctx.guild.id,
                                "info": infoimg
                            }

                            await db.raffles.insert_one(raffledetails)

                            await msg.edit(embed = discord.Embed(
                                title = "Raffle Created!",
                                description = f"Raffle named ``{name.content}`` for channel <#{channelid}> created successfully!!",
                                color = 0xf08080
                            ))
            
    @create.error
    async def create_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))
        else:
            await ctx.send(error)


    

    @raffle.command(name = "delete", help = "For deleting a raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.guild_only()
    # @app_commands.rename(raffle_name = "raffle name")
    async def delete(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        raffledoc = await db.raffles.find_one({"RaffleName": raffle_name})
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

    @delete.error
    async def delete_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))


    @raffle.command(name = "info", help = "For checking information about a raffle")
    @commands.guild_only()
    # @app_commands.rename(raffle_name = "raffle name")
    async def info(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        raffledoc = await db.raffles.find_one({"RaffleName": raffle_name})
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

            if f"info{raffleName}.png" not in os.listdir(path = "/app/bot/assets/"):
                
                aboutimg = Image.open(io.BytesIO(raffledoc["info"]))
                buffer = io.BytesIO()
                aboutimg.save(f"bot/assets/info{raffleName}.png", format = "png")

            else:
                Imgfile = discord.File(f"bot/assets/info{raffleName}.png", filename = f"info{raffleName}.png")
                infoEmbed.set_image(url = f"attachment://info{raffleName}.png")
            
            await ctx.reply(file = Imgfile, embed = infoEmbed)

        else:
            noRaffleMatchEmbed = discord.Embed(
                title = "Invalid Name",
                description = f"No raffle named ``{raffle_name}`` exists in this server",
                color = 0xf08080
            )
            noRaffleMatchEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

            await ctx.reply(embed = noRaffleMatchEmbed)



    @raffle.command(name = "roll", help = "For determining the winner(s) of the mentioned raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.guild_only()
    # @app_commands.rename(raffle_name = "raffle name")
    async def roll(self, ctx: commands.Context, raffle_name = app_commands.Transform[str, d.ChoiceTransformer]):
        raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name})

        if raffleDoc:
            guild = db.dbase[str(ctx.guild.id)]     

            userlist = []
            ticketlist = []

            async for doc in guild.find({"Raffle": raffleDoc["_id"]}, {"tickets": 1}):
                userlist.append(doc["_id"])
                ticketlist.append(doc["tickets"])

            if len(userlist) != 0 and len(ticketlist) != 0:
                await ctx.defer()

                winnerId = d.random_chooser(userlist, ticketlist)
                winnerTickets = await guild.find_one({"_id": winnerId}, {"_id": 0, "tickets": 1})["tickets"]
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

    @roll.error
    async def roll_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))

    @raffle.command(name = "list", help = "For checking the ticket list of a raffle")
    @commands.guild_only()
    # @app_commands.rename(raffle_name = "raffle name")
    async def list(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name})

        if raffleDoc:
            guild = db.raffles[str(ctx.guild.id)]
            data = []

            async for doc in guild.find({"Raffle": raffleDoc["_id"]}, {"tickets": 1}):
                member = discord.utils.get(ctx.guild.members, id = doc["_id"])
                if member:
                    data.append({"Member": member, "tickets": doc["tickets"]})
                else:
                    continue

            if len(data) != 0:
                formatter = d.Source(entries = data, name = raffle_name, per_page = 10)
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


    @raffle.command(name = "edit", help = "For editing the information about the raffle")
    @commands.check_any(commands.has_role("Raffle Permissions"),commands.has_permissions(administrator = True))
    @commands.guild_only()
    # @app_commands.rename(raffle_name = "raffle name")
    async def edit(self, ctx: commands.Context, raffle_name: app_commands.Transform[str, d.ChoiceTransformer]):
        raffleDoc = await db.raffles.find_one({"RaffleName": raffle_name})

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

            if view.choice == "name":
                NameEmbed = discord.Embed(
                    description = "Enter a suitable name for the raffle!",
                    color = 0xf08080
                )
                NameEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                await msg.edit(embed = NameEmbed)
                authorcheck = lambda a: a.author == ctx.author and a.channel == ctx.channel

                try:
                    name: discord.Message = await self.client.wait_for("message", check = authorcheck, timeout = 50)
                except asyncio.TimeoutError:
                    
                    name = None
                    return

                await name.delete()
                
                if name.content.lower() == "stop" or name == None:
                    await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080), delete_after = 10)
                else:
                    await db.raffles.find_one_and_update({"_id":raffleDoc["_id"]},{"$set":{"RaffleName":name.content}})
                    
                    await msg.edit(embed = discord.Embed(
                        title = "Raffle edited",
                        description = "Raffle Name edited successfully!",
                        color = 0xf08080
                    ), delete_after = 10)
            elif view.choice == "info":
                InfoEmbed = discord.Embed(
                    description = "Do ```.mypkinfo <pokemon>``` or ```.boxpk <box> <position>``` or ```send the image containing info of the pokemon``` to select pokemon for raffle",
                    color = 0xf08080
                )
                InfoEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                await msg.edit(embed = InfoEmbed)

                infocheck = lambda message: message.author.id in [438057969251254293, ctx.author.id] and message.channel == ctx.channel and message.attachments[0].filename in ["mypkinfo.png","mypkinfo","boxpk.png","boxpk","unknown.png","unknown"]

                try:
                    info: discord.Message = await self.client.wait_for("message", check = infocheck, timeout = 50)
                except asyncio.TimeoutError:
                    
                    info = None
                    return
                
                await info.delete()

                if info.content.lower() == "stop" or info == None:
                    await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080), delete_after = 10)

                else:
                    infoimg = await info.attachments[0].read()
                    await db.raffles.find_one_and_update({"_id": raffleDoc["_id"]}, {"$set": {"info": infoimg}})

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
                    await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080), delete_after = 10)
                else:
                    await db.raffles.find_one_and_update({"_id":raffleDoc["_id"]},{"$set":{"Ticket Cost": int(tixcost.content)}})
                    await msg.edit(embed = discord.Embed(
                        title = "Cost edited", 
                        description = "Ticket Cost edited successfully", 
                        color = 0xf08080),
                        delete_after = 10)

            elif view.choice == "bank":
                BankEmbed = discord.Embed(
                    description = f"Mention the user where the <:PKC:1019594363183038554> raffle money needs to be stored\nFor example: {ctx.author.mention}",
                    color = 0xf08080
                )
                BankEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                await msg.edit(embed = BankEmbed)

                bankcheck = lambda bmsg: bmsg.author == ctx.author and bmsg.channel == ctx.channel and ((bmsg.startswith("<@") and bmsg.endswith(">")) or (bmsg.startswith("<@!") and bmsg.endswith(">")) or bmsg.lower() == "stop")

                try:
                    bankname: discord.Message = await self.client.wait_for("message", check = bankcheck, timeout = 50)
                except asyncio.TimeoutError:
                    bankname = None
                    return

                await bankname.delete()

                if bankname.content.lower() == "stop" or bankname == None:
                    await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080), delete_after = 10)
                else:
                    await db.raffles.find_one_and_update({"_id": raffleDoc["_id"]},{"$set": {"bank": int(bankname.content.lstrip("<@!").rstrip(">"))}})
                    
                    await msg.edit(embed = discord.Embed(
                        title = "Bank ID edited", 
                        description = "Bank ID edited successfully", 
                        color = 0xf08080),
                        delete_after = 10)
            
            elif view.choice == "channel":
                ChannelEmbed = discord.Embed(
                        description = f"Mention the channel where payment is supposed to be done\nFor example: {ctx.channel.mention}",
                        color = 0xf08080
                    )
                ChannelEmbed.set_footer(text = "Send 'stop' to stop the editing of raffle")

                await msg.edit(embed = ChannelEmbed)

                channelcheck = lambda cmsg: cmsg.author == ctx.author and cmsg.channel == ctx.channel and ((cmsg.startswith("<#") and cmsg.endswith(">")) or cmsg.lower() == "stop")
                    
                try:
                    channelname: discord.Message = self.client.wait_for("message", check = authorcheck, timeout = 50)
                except asyncio.TimeoutError:
                        
                    channelname = None
                    return

                await channelname.delete()

                if channelname.content.lower() == "stop" or channelname == None:
                    await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080), delete_after = 10)
                else:
                    await db.raffles.find_one_and_update({"_id": raffleDoc["_id"]},{"$set": {"_id": int(channelname.content.lstrip("<#").rstrip(">"))}})
                    await msg.edit(embed = discord.Embed(
                        title = "Payment Channel edited",
                        description = "Payment Channel edited successfully!",
                        color = 0xf08080
                    ), delete_after = 10)

            else:
                await msg.edit(embed = discord.Embed(description = "Raffle Editing Process Stopped", color = 0xf08080), delete_after = 10)

        else:
            noRaffleEmbed = discord.Embed(
                title = "Invalid Name",
                description = f"No Raffle named ``{raffle_name}`` exists in this server",
                color = 0xf08080
            )
            noRaffleEmbed.set_footer(text = "ProTip: Use ``/raffles`` command to check list of ongoing raffles")

            await ctx.reply(embed = noRaffleEmbed)

    @edit.error
    async def edit_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.reply(embed = discord.Embed(
                description = "You don't have proper permissions to use this command\nPlease ask your admin to provide the role named ``Raffle Permissions`` created by bot",
                color = 0xf08080
            ))


