import os
import discord
from discord.ext import commands
import asyncio
import mongo_declarations as mn
import logical_definitions as lgd

raffleguilds = mn.raffledbase.list_collection_names()

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
	guildDetails = {"_id": str(guild.id), "Prefix": "!", "Logs": False}
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

	helpEmbed.add_field(name="`ping`", value="Shows the latency of the bot | Bot Utility\n Aliases | pong", inline = False)
	helpEmbed.add_field(name = "`rafflecreate`", value = "Creates a raffle for the guild \nRaffle Utility\n Aliases | CreateRaffle, RafCreate, CreateRaf, RC", inline = False)
	helpEmbed.add_field(name = "`raffledelete`", value = "Deletes the server's raffle | Raffle Utility\n Aliases | DeleteRaffle, DelRaf, RafDel, RD", inline = False)
	helpEmbed.add_field(name = "`rafflelist`", value = "Shows the tickets for the raffle | Raffle Utility\n Aliases | ", inline = False)
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

@client.command(aliases = [])
async def rafflelist(ctx):
	if not str(ctx.guild.id) in raffleguilds:
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
		else:
			for i in find:
				member = discord.utils.get(ctx.guild.members, id = i["_id"])
				raffles.add_field(
					name = member.name+member.discriminator, 
					value = i["tickets"], 
					inline = False
				)
	
		await ctx.send(embed = raffles)

@client.listen("on_message")
async def on_message(message):
	
	if message.guild == None:
		pass

	elif str(message.guild.id) in raffleguilds:
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
			# if message.clean_content.startswith(f".gift @{bank}"):
			# 	stringEnding = len(f".gift @{bank}")
			# 	pkc = int(message.clean_content[stringEnding:])
			# 	tickets = pkc // tixcost
			# 	buyerid = message.author.id
						if tickets > 0:
							buyersCursor = guild.find({"type":"buyer"})
							buyers = []
							for i in buyersCursor:
								buyers.append(i["_id"])
							if buyerid not in buyers:
								ticketlog = {"_id":buyerid,"type":"buyer","tickets":tickets}
								guild.insert_one(ticketlog)
							else:
								prevtix = guild.find_one({"_id":buyerid},{"_id":0,"tickets":1})["tickets"]
								prevtix+= tickets
								guild.find_one_and_update({"_id":buyerid},{"$set":{"tickets":prevtix}})
							tixboughtEmbed = discord.Embed(
							title = "Tickets bought", 
							description = f"Yay! {tickets} tickets bought!", 
							color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
							)
							await message.channel.send(embed = tixboughtEmbed, delete_after = 30)
						else:
							await message.channel.send(f"Dude, <@{buyerid}> hold up! the ticket cost is {tixcost} pkc")

@client.command()
async def raffleinfo(ctx):
	if str(ctx.guild.id) not in raffleguilds:
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
		
@client.command()
async def raffleinfoedit(ctx):
	if not str(ctx.guild.id) in raffleguilds:
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
			reaction, user = await client.wait_for("reaction_add", check = check, timeout = 30)
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
				name = await client.wait_for("message", check = authorcheck, timeout = 30)
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
				description = "Edit info about raffle",
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
			))
			await editing.clear_reactions()
			try:
				about = await client.wait_for("message", check = authorcheck, timeout = 30)
			except asyncio.exceptions.TimeoutError:
				await editing.edit(content = "timed out", delete_after = 10)
				return
			guild.find_one_and_update({"_id":"Raffle"},{"$set":{"info":about.content}})
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
				cost = await client.wait_for("message", check = authorcheck, timeout = 30)
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
				bank = await client.wait_for("message", check = authorcheck, timeout = 30)
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
				channel = await client.wait_for("message", check = authorcheck, timeout = 30)
			except asyncio.exceptions.TimeoutError:
				await editing.edit(content = "timed out", delete_after = 10)
				return
			guild.find_one_and_replace({"_id":"Raffle"},{"$set":{"Channel":channel.clean_content.lstrip("#")}})
			await editing.edit(embed = discord.Embed(
				title = "Payment Channel edited",
				description = "Payment Channel edited successfully!",
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
			), delete_after = 10)
			await channel.delete()
			

# @client.event
# async def on_command_error(ctx, error):
# 	if isinstance(error, commands.CommandNotFound):
# 		unknownEmbed = discord.Embed(title = "Command not found",description = "What command are you trying to use?\n``Protip:`` Use ``!help`` to see all the available commands!", color = lgd.hexConvertor(colorCollection.find({},{"_id":0,"Hex":1})))
# 		await ctx.send(embed = unknownEmbed)

@client.command()
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
		description = f"Congractulations {winner.mention}, You won {rafflename}",
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
async def disable(ctx,*, cogname = None):
	if cogname == None:
		return
    
	try:
		client.unload_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not unload cog {cogname}: {str(e)}')

	else:
		await ctx.send('Disabled Commands Successfully')



client.run("OTQ1MzAxNTE0OTQ2MjQ0NjI5.YhOKpA.0Ze-mC3F1YzzOoB_M4DFWFxPsgg")