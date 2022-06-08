from discord.ext import commands
import discord
import logical_definitions as lgd
import mongo_declarations as mn
import asyncio

def setup(client):
    client.add_cog(rafflelist(client))

class rafflelist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["Rafflelist","RaffleList","rl","RL","Rl"])
    async def rafflelist(self, ctx):
        if not str(ctx.guild.id) in mn.raffledbase.list_collection_names():
            noRaffleEmbed = discord.Embed(
                title = "No Raffles Found", 
                description = "There are no raffles in this guild going on\nIf you wanna create new raffle then try ``rafflecreate`` command", 
                color = 0xf08080
            )
            await ctx.send(embed = noRaffleEmbed)
        else:
            guild = mn.raffledbase[str(ctx.guild.id)]
            rafflename = guild.find_one({"_id": "Raffle"},{"_id":0,"RaffleName":1})["RaffleName"]
            ticketcost = guild.find_one({"_id":"Raffle"},{"_id":0,"Ticket Cost":1})["Ticket Cost"]
            find = guild.find({"type":"buyer"},{"type":0})
            rafflelist1 = discord.Embed(
                title = f"{rafflename}", 
                color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1})))
            
            if guild.count_documents({"type":"buyer"}) == 0:
                rafflelist1.add_field(name = "No One bought tickets yet", value = "<:lol:878270233754869811>")
                totaltickets = 0
            else:
                buyers = guild.count_documents({"type":"buyer"})
                Embeds = (buyers//10)+1

                rafflelist2 = discord.Embed(
                    title = rafflename,
                    color = 0xf08080
                )
                rafflelist3 = discord.Embed(
                    title = rafflename,
                    color = 0xf08080
                )
                rafflelist4 = discord.Embed(
                    title = rafflename,
                    color = 0xf08080
                )
                rafflelist5 = discord.Embed(
                    title = rafflename,
                    color = 0xf08080
                )
                rafflelist6 = discord.Embed(
                    title = rafflename,
                    color = 0xf08080
                )
                rafflelist7 = discord.Embed(
				title = rafflename,
				color = 0xf08080
			    )

                
                rafflelist1.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 1 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                rafflelist2.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 2 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                rafflelist3.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 3 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                rafflelist4.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 4 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                rafflelist5.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 5 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                rafflelist6.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 6 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                rafflelist7.set_footer(text= f"Requested by {ctx.author.name+ctx.author.discriminator} | Page 7 of {Embeds} | Type next or prev to switch between pages", icon_url=ctx.author.avatar_url)
                
                membercursor = guild.find({"type":"buyer"},{"tickets":1}).sort("tickets",-1)

                a = 0
                for i in membercursor:
                    try:
                        member = await self.client.fetch_user(i["_id"])
                    except discord.NotFound:
                        member = None
                        return
                    if member != None:
                        if 0 <= a < 10:
                            rafflelist1.add_field(
                                name = member.name + "#" + member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )

                        elif (10 <= a < 20):
                            rafflelist2.add_field(
                                name = member.name + "#" + member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )
                        
                        elif (20 <= a < 30):
                            rafflelist3.add_field(
                                name = member.name+"#"+member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )
                        elif (30 <= a < 40):
                            rafflelist4.add_field(
                                name = member.name+"#"+member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )
                        elif (40 <= a < 50):
                            rafflelist5.add_field(
                                name = member.name+"#"+member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )
                        elif (50 <= a < 60):
                            rafflelist6.add_field(
                                name = member.name+"#"+member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )
                        else:
                            rafflelist7.add_field(
                                name = member.name+"#"+member.discriminator,
                                value = i["tickets"],
                                inline = False
                            )
                    a += 1

                msg = await ctx.reply(embed = rafflelist1)
                currentpage = 1
                check = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["next", "prev"]
                
                def embedprovider(page: int):
                    match page:
                        case 1:
                            return rafflelist1
                        case 2:
                            return rafflelist2
                        case 3:
                            return rafflelist3
                        case 4:
                            return rafflelist4
                        case 5:
                            return rafflelist5
                        case 6:
                            return rafflelist6
                        case 7:
                            return rafflelist7

                while True:
                    try:
                        choice = await self.client.wait_for("message", check = check, timeout = 30)
                    
                        if choice.content.lower() == "next":
                            if currentpage == Embeds:
                                await choice.reply("You can't go to next page because there is no next page", delete_after = 10)
                            else:
                                currentpage += 1
                                await msg.edit(embed = embedprovider(currentpage))
                        else:
                            if currentpage == 1:
                                await choice.reply("You can't go to previous page because there is no previous page", delete_after = 10)
                            else:
                                currentpage -= 1
                                await msg.edit(embed = embedprovider(currentpage))

                    except asyncio.exceptions.TimeoutError:
                        return
                        break
