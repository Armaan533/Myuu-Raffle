import os
from unicodedata import name
import discord
from discord.ext import commands
import asyncio
import mongo_declarations as mn
import logical_definitions as lgd


intents = discord.Intents.default()
intents.members = True
intents.messages = True

defaultPrefix = "!"

def get_prefix(client, message):
	Gprefix = mn.guildpref.find_one({"_id": str(message.guild.id)},{"_id": 0,"Prefix": 1})["Prefix"]
	return commands.when_mentioned_or(Gprefix)(client, message)

client = commands.Bot(command_prefix = get_prefix, intents = intents)

client.remove_command("help")


@client.event
async def on_ready():
	activity = discord.Game(name="with raffles", type=3)
	await client.change_presence(status=discord.Status.idle, activity=activity)
	print("We are online!")


@client.event
async def on_guild_join(guild):
	guildDetails = {"_id": str(guild.id), "Prefix": "!"}
	mn.guildpref.insert_one(guildDetails)

@client.event
async def on_guild_remove(guild):
	mn.guildpref.delete_one({"_id": str(guild.id)})



@client.command(aliases = ["Help","helpme","Helpme"])
async def help(ctx):
	helpEmbed = discord.Embed(
		title = "Commands", 
		color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
	)
	#	Add more commands here

	helpEmbed.add_field(name="`ping`", value=">>> Shows the latency of the bot | Bot Utility\n Aliases | pong", inline = False)
	helpEmbed.add_field(name = "`rafflecreate`", value = ">>> Creates a raffle for the guild \nRaffle Utility\n Aliases | CreateRaffle, RafCreate, CreateRaf, RC", inline = False)
	helpEmbed.add_field(name = "`raffledelete`", value = ">>> Deletes the server's raffle | Raffle Utility\n Aliases | DeleteRaffle, DelRaf, RafDel, RD", inline = False)
	helpEmbed.add_field(name = "`rafflelist`", value = ">>> Shows the tickets for the raffle | Raffle Info\n Aliases | None", inline = False)
	helpEmbed.add_field(name = "`raffleinfo`", value = ">>> Shows info of the raffle | Raffle Info\n Aliases | None", inline = False)
	helpEmbed.add_field(name = "`raffleinfoedit`", value = ">>> To edit info of the raffle | Raffle Info\n Aliases | RaffleEditInfo, ")
	helpEmbed.set_footer(text=f"Requested by {ctx.author.name}", icon_url = ctx.author.avatar_url)

	await ctx.send(embed = helpEmbed)

@client.command(aliases = ["Prefix"])
@commands.has_guild_permissions(administrator = True)
async def prefix(ctx, newPrefix: str):
	if len(newPrefix) >= 5:
		await ctx.send(embed = discord.embed(title = "Prefix too long.",
											 description = "Please choose a shorter prefix!\nMaximum length of Prefix is 5 characters.",
											 color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))))
	else:
		prev = {"_id":str(ctx.guild.id)} 
		next = {"$set":{"Prefix": newPrefix}}
		mn.guildpref.update_one(prev, next)
		prefixSuccess = discord.Embed(title = "Prefix changed!",
									  description = f"Prefix changed successfully to ``{newPrefix}``",
									  color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = prefixSuccess)

@prefix.error
async def prefix_error(ctx: commands.Context, error: commands.errors):
	if isinstance(error, commands.MissingPermissions):
		missingPermsEmbed = discord.Embed(
			title = "Hold Up!",
			description = "You need ``Administrator`` Permissions to use this command!",
			color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.send(embed = missingPermsEmbed , delete_after = 20)
	elif isinstance(error, commands.MissingRequiredArgument):
		missingArgEmbed = discord.Embed(
			title = "Prefix needed",
			description = "You need to give prefix with command\n For example:- ``+prefix {newprefix}\n Put the new prefix in place of {newprefix}``",
			color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.send(embed = missingArgEmbed)


@client.command(aliases = ["Ping","pong","Pong"])
async def ping(ctx):
	pingem = discord.Embed(description = f"Pong! In {round(client.latency * 1000)}ms",
						   color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
	await ctx.send(embed=pingem)


@client.command(aliases = ["RaffleCreate","createraffle","CreateRaffle","RafCreate","rafcreate","createraf","CreateRaf","RC","rc"])
@commands.has_permissions(administrator = True)
async def rafflecreate(ctx):
	guilds = mn.raffledbase.list_collection_names()
	guild = ctx.guild.id
	if str(guild) in guilds:
		existsEmbed = discord.Embed(
			title = "Raffle exists",
			description = "Raffle for this guild exists\n you can make only one raffle in a guild", 
			colour = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.send(embed = existsEmbed)
	else:
		NameEmbed = discord.Embed(
			title = "Raffle Name", 
			description = "Enter the name for Raffle!", 
			color  = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)

		Message = await ctx.send(embed = NameEmbed)
		authorcheck = lambda m: m.author == ctx.author and m.channel == ctx.channel
		try:
			name = await client.wait_for("message", check = authorcheck, timeout = 30)
		except asyncio.exceptions.TimeoutError:
			await Message.edit(content = "timed out", delete_after = 10)
			return
		await name.delete()


		CostEmbed = discord.Embed(
			title = "Ticket Cost", 
			description = f"Enter the cost for {name.content}!", 
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await Message.edit(embed = CostEmbed)
		try:
			tixcost = await client.wait_for("message", check = authorcheck, timeout = 30)
		except asyncio.exceptions.TimeoutError:
			await Message.edit(content = "_timed out_", delete_after = 10)
			return
		await tixcost.delete()


		ChannelEmbed = discord.Embed(
			title = "Payments Channel",
			description = "Mention the channel", 
			color  = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await Message.edit(embed = ChannelEmbed)
		try:
			channelname = await client.wait_for("message", check = authorcheck, timeout = 30)
		except asyncio.exceptions.TimeoutError:
			await Message.edit(content = "timed out", delete_after = 10)
			return
		channelid = channelname.content.lstrip("<#").rstrip(">")
		await channelname.delete()
		await Message.delete()


		bankEmbed = discord.Embed(
			title = "Raffle Bank",
			description = "Mention the bank id",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		bankMessage = await ctx.send(embed = bankEmbed)
		try:
			bankname = await client.wait_for("message", check = authorcheck, timeout = 30)
		except asyncio.exceptions.TimeoutError:
			await Message.edit(content = "time out", delete_after = 10)
			return
		await bankname.delete()
		raffledetails = {"_id":"Raffle","RaffleName":name.content,"Ticket Cost":int(tixcost.content),"Channel":int(channelid), "bank":int(bankname.content.lstrip("<@!").rstrip(">")), "info":"Just a plain raffle."}
		guild = mn.raffledbase[str(ctx.guild.id)]
		guild.insert_one(raffledetails)
		await bankMessage.edit(embed = discord.Embed(
			title = "Raffle created!!",
			description = f"Raffle named {name.content} created successfully!",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		))


@rafflecreate.error
async def rafflecreate_error(ctx, error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(embed = discord.Embed(description = "Get the damn admin first, Noob!\n then try to use this command", 
											 color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
											))
	else:
		await ctx.send(error)
	
@client.command(aliases = ["RaffleDelete","DeleteRaffle","deleteraffle","delraf", "DelRaf","rafdel","RafDel", "RD", "rd"])
@commands.has_permissions(administrator = True)
async def raffledelete(ctx):
	guild = mn.raffledbase[str(ctx.guild.id)]
	rafflename = guild.find_one({"_id":"Raffle"},{"_id":0,"RaffleName":1})["RaffleName"]
	response = mn.raffledbase.drop_collection(str(ctx.guild.id))
	if "ns" in response:
		await ctx.send(embed = discord.Embed(description = f"Raffle {rafflename} deleted successfully", 
											 color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
											))
	else:
		error = response["errmsg"]
		await ctx.send(embed = discord.Embed(
			title = "Operation Failed", 
			description = f"Error:- {error}"
		))

@client.command(aliases = ["Rafflelist","RaffleList","rl","RL","Rl"])
async def rafflelist(ctx):
	if not str(ctx.guild.id) in mn.raffledbase.list_collection_names():
		noRaffleEmbed = discord.Embed(
			title = "No Raffles Found", 
			description = "There are no raffles in this guild going on\nIf you wanna create new raffle then try ``rafflecreate`` command", 
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.send(embed = noRaffleEmbed)
	else:
		guild = mn.raffledbase[str(ctx.guild.id)]
		rafflename = guild.find_one({"_id": "Raffle"},{"_id":0,"RaffleName":1})["RaffleName"]
		find = guild.find({"type":"buyer"},{"type":0})
		raffles = discord.Embed(
			title = f"{rafflename}", 
			color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1})))
	    
		if guild.count_documents({"type":"buyer"}) == 0:
			raffles.add_field(name = "No One bought tickets yet", value = "<:lol:878270233754869811>")
			totaltickets = 0
		else:
			totaltickets = 0
			for i in find:
				member = discord.utils.get(ctx.guild.members, id = i["_id"])
				totaltickets += i["tickets"]
				raffles.add_field(
					name = member.name+"#"+member.discriminator, 
					value = i["tickets"], 
					inline = False
				)

		raffles.add_field(
			name = "Total Tickets",
			value = f"`{totaltickets}`",
			inline = False
		)
		await ctx.send(embed = raffles)

@client.listen("on_message")
async def on_message(message):
	
	if message.guild == None:
		pass

	elif str(message.guild.id) in mn.raffledbase.list_collection_names():
		guild = mn.raffledbase[str(message.guild.id)]
		if message.channel.id == guild.find_one({"_id":"Raffle"},{"_id":0,"Channel":1})["Channel"] and message.author.id!= 945301514946244629 and message.author.id == 438057969251254293:
			bankid = guild.find_one({"_id":"Raffle"},{"_id":0,"bank":1})["bank"]
			# bank = discord.utils.get(message.guild.members, id = bankid)
			tixcost = guild.find_one({"_id":"Raffle"},{"_id":0,"Ticket Cost":1})["Ticket Cost"]
			if message.embeds != None:
				for i in message.embeds:
					if i.description.startswith(f"<@{bankid}>, you have just been gifted"):
						splitList = i.description.split()
						pkc = int(splitList[6])
						tickets = pkc // tixcost
						buyerid = int(splitList[9][2:-2])
						if tickets > 0:
							buyersCursor = guild.find({"type":"buyer"})
							buyers = []
							for i in buyersCursor:
								buyers.append(i["_id"])
							if buyerid not in buyers:
								ticketlog = {"_id":buyerid,"type":"buyer","tickets":tickets}
								guild.insert_one(ticketlog)
								currenttix = tickets
							else:
								prevtix = guild.find_one({"_id":buyerid},{"_id":0,"tickets":1})["tickets"]
								# prevtix+= tickets
								currenttix = prevtix + tickets
								guild.find_one_and_update({"_id":buyerid},{"$set":{"tickets":currenttix}})
							tixboughtEmbed = discord.Embed(
							title = "Tickets bought", 
							description = f"""Yay! {tickets} tickets bought by <@{buyerid}>!
							Total tickets bought by <@{buyerid}>: ``{currenttix}``""",
							color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
							)
							await message.channel.send(embed = tixboughtEmbed, delete_after = 30)
						else:
							await message.channel.send(f"Dude, <@{buyerid}> hold up! the ticket cost is {tixcost} pkc")

@client.command(aliases = ["Raffleinfo","RaffleInfo","RI","ri","Ri"])
async def raffleinfo(ctx):
	if str(ctx.guild.id) not in mn.raffledbase.list_collection_names():
		await ctx.send(embed = discord.Embed(
			title = "Raffle Not Found", 
			description = "There is no raffle made for this server",
			color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
		))
	else:
		guild = mn.raffledbase[str(ctx.guild.id)]
		info = 	guild.find_one({"_id":"Raffle"},{"_id":0})
		bank = discord.utils.get(ctx.guild.members, id = info["bank"])
		channel = str(info["Channel"])
		infoEmbed = discord.Embed(
			title = "Raffle Info", 
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		infoEmbed.add_field(name = "Raffle Name", value = info["RaffleName"])
		infoEmbed.add_field(name = "About Raffle", value = info["info"])
		infoEmbed.add_field(name = "Ticket Cost", value = info["Ticket Cost"])
		infoEmbed.add_field(name = "Bank of Raffle", value = bank.mention)
		infoEmbed.add_field(name = "Payment Channel", value = f"<#{channel}>")
		await ctx.send(embed = infoEmbed)		
			

# @client.event
# async def on_command_error(ctx, error):
# 	if isinstance(error, commands.CommandNotFound):
# 		unknownEmbed = discord.Embed(title = "Command not found",description = "What command are you trying to use?\n``Protip:`` Use ``!help`` to see all the available commands!", color = lgd.hexConvertor(colorCollection.find({},{"_id":0,"Hex":1})))
# 		await ctx.send(embed = unknownEmbed)

@client.command(aliases = ["Raffleroll","raffleroll","choosewinner","ChooseWinner","Choosewinner","cw","CW","Cw"])
@commands.has_guild_permissions(administrator = True)
async def choose_winner(ctx):
	guildcollection = mn.raffledbase[str(ctx.guild.id)]
	userlist = []
	ticketlist = []
	rafflename = guildcollection.find_one({"_id":"Raffle"},{"_id":0,"RaffleName":1})["RaffleName"]
	for i in guildcollection.find({"type":"buyer"},{"tickets":1}):
		userlist.append(i["_id"])
		ticketlist.append(i["tickets"])

	winnerId = lgd.random_chooser(userlist,ticketlist)
	winner = discord.utils.get(ctx.guild.members,id = winnerId)
	winnerEmbed = discord.Embed(
		title = "Winner Chosen",
		description = f"Congratulations {winner.mention}, You won {rafflename}",
		color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
	)
	await ctx.send(embed = winnerEmbed)
	

@client.command()
async def testing(ctx):
	nick = ctx.author.nick
	if nick != None:
		await ctx.send(nick)
	else:
		await ctx.send(ctx.author.name)



@client.command()
@commands.has_guild_permissions(administrator = True)
async def enable(ctx, *, cogname = None):
	if cogname == None:
		return
	
	try:
		client.load_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not load cog {cogname}: {str(e)}')

	else:
		await ctx.send('Enabled Commands Successfully')



@client.command()
@commands.has_guild_permissions(administrator = True)
async def disable(ctx,*, cogname = None):
	if cogname == None:
		return
    
	try:
		client.unload_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not unload cog {cogname}: {str(e)}')

	else:
		await ctx.send('Disabled Commands Successfully')

client.load_extension("cogs.raffle_info_edit")
client.load_extension("cogs.override_cmd")
client.load_extension("cogs.invite")
client.load_extension("cogs.mytickets")
client.run("OTQ1MzAxNTE0OTQ2MjQ0NjI5.YhOKpA.0Ze-mC3F1YzzOoB_M4DFWFxPsgg")