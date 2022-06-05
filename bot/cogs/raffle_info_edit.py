import discord
from discord.ext import commands
import logical_definitions as lgd
import mongo_declarations as mn
import asyncio

class raffle_info_edit(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["RaffleInfoEdit","RIE","rie","raffleeditinfo","RaffleEditInfo","REI","rei"])
    @commands.has_guild_permissions(administrator = True)
    async def raffleinfoedit(self,ctx):
        if not str(ctx.guild.id) in mn.raffledbase.list_collection_names():
            noRaffleEmbed = discord.Embed(
                title = "No Raffles Found", 
                description = "There are no raffles in this guild going on\nIf you wanna create new raffle then try ``rafflecreate`` command", 
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            )
            await ctx.send(embed = noRaffleEmbed)
        else:
            guild = mn.raffledbase[str(ctx.guild.id)]
            authorcheck = lambda m: m.author == ctx.author and m.channel == ctx.channel
            editEmbed = discord.Embed(title = "Edit Raffle", description = """
                                    Edit:-
                                        Raffle name- :regional_indicator_n:
                                        About raffle- :regional_indicator_a:
                                        Ticket Cost- :regional_indicator_t:
                                        Bank- :regional_indicator_b:
                                        Payment Channel- :regional_indicator_p:""", 
                                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
            editEmojis = [
                "🇳",
                "🇦",
                "🇹",
                "🇧",
                "🇵"
            ]
            
            editing = await ctx.send(embed = editEmbed)
            for emoji in editEmojis:
                await editing.add_reaction(emoji)
            check = lambda r,u: u == ctx.author and str(r.emoji) in editEmojis

            try:
                reaction, user = await self.client.wait_for("reaction_add", check = check, timeout = 30)
            except asyncio.exceptions.TimeoutError:
                await editing.edit(content = "Timed Out")
                return
            if str(reaction.emoji) == editEmojis[0]:
                await editing.edit(embed = discord.Embed(
                    title = "Editing Name",
                    description = "Choose a wise name for the Raffle",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
                ))
                await editing.clear_reactions()
                try:
                    name = await self.client.wait_for("message", check = authorcheck, timeout = 30)
                except asyncio.exceptions.TimeoutError:
                    await editing.edit(content = "timed out", delete_after = 10)
                    return
                guild.find_one_and_update({"_id":"Raffle"},{"$set":{"RaffleName":name.content}})
                await editing.edit(embed = discord.Embed(
                    title = "Raffle edited",
                    description = "Raffle Name edited successfully!",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
                ),delete_after = 10)
                await name.delete()

            elif str(reaction.emoji) == editEmojis[1]:
                await editing.edit(embed = discord.Embed(
                    title = "Editing About Raffle",
                    description = "Do .mypkinfo or .boxpk to edit the about",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
                ))
                await editing.clear_reactions()
                
                try:
                    myuucheck = lambda m: m.author.id == 438057969251254293 and m.channel == ctx.channel
                    about = await self.client.wait_for("message", check = myuucheck, timeout = 30)
                except asyncio.exceptions.TimeoutError:
                    await editing.edit(content = "timed out", delete_after = 10)
                    return
                
                for attachment in about.attachments:
                    infoimg = await attachment.read()

                guild.find_one_and_update({"_id":"Raffle"},{"$set":{"info":infoimg}})

                await editing.edit(embed = discord.Embed(
                    title = "About Raffle edited",
                    description = "About Raffle edited successfully!",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
                                delate_after = 10)
                await about.delete()

            elif str(reaction.emoji) == editEmojis[2]:
                await editing.edit(embed = discord.Embed(
                    title = "Editing Ticket Cost", 		   
                    description = "Choose the price of tickets wisely", 
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
                ))
                await editing.clear_reactions()
                try:
                    cost = await self.client.wait_for("message", check = authorcheck, timeout = 30)
                except asyncio.exceptions.TimeoutError:
                    await editing.edit(content = "timed out", delete_after = 10)
                    return
                guild.find_one_and_update({"_id":"Raffle"},{"$set":{"Ticket Cost":int(cost.clean_content)}})
                await editing.edit(embed = discord.Embed(
                    title = "Cost edited", 
                    description = "Ticket Cost edited successfully", 
                    color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))),
                                    delete_after = 10)
                await cost.delete()

            elif str(reaction.emoji) == editEmojis[3]:
                await editing.edit(embed = discord.Embed(
                    title = "Editing Bank ID",
                    description = "Which ID do you want to be as your raffle's bank?\n _Mention it here_",
                    color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
                ))
                await editing.clear_reactions()
                try:
                    bank = await self.client.wait_for("message", check = authorcheck, timeout = 30)
                except asyncio.exceptions.TimeoutError:
                    await editing.edit(content = "timed out", delete_after = 10)
                    return
                print(int(bank.content.lstrip("<@!").rstrip(">")))
                id = int(bank.content.lstrip("<@!").rstrip(">"))
                guild.find_one_and_update({"_id":"Raffle"},{"$set":{"bank":id}})
                await editing.edit(embed = discord.Embed(
                    title = "Bank ID edited", 
                    description = "Bank ID edited successfully", 
                    color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))),
                                    delete_after = 10)
                await bank.delete()

            elif str(reaction.emoji) == editEmojis[4]:
                await editing.edit(embed = discord.Embed(
                    title = "Editing Payment Channel",
                    description = "Which channel do you want to be as your raffle's payment channel?\nMention the channel here:",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))))
                await editing.clear_reactions()
                try:
                    channel = await self.client.wait_for("message", check = authorcheck, timeout = 30)
                except asyncio.exceptions.TimeoutError:
                    await editing.edit(content = "timed out", delete_after = 10)
                    return
                guild.find_one_and_update({"_id":"Raffle"},{"$set":{"Channel":channel.clean_content.lstrip("#")}})
                await editing.edit(embed = discord.Embed(
                    title = "Payment Channel edited",
                    description = "Payment Channel edited successfully!",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
                ), delete_after = 10)
                await channel.delete()

def setup(client):
    client.add_cog(raffle_info_edit(client))