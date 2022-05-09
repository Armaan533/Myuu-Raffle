import discord
from discord.ext import commands
import mongo_declarations as mn
import logical_definitions as lgd

class override_cmd(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.has_guild_permissions(administrator = True)
	async def tickets(self, ctx, operation = None, member = None, value = None):
		print(member)
		if str(ctx.guild.id) in mn.raffledbase.list_collection_names():
			if operation == None and member == None and value == None:
				await ctx.send(embed = discord.Embed(
					title = "Tickets Override Command",
					description = """This command is used for manually giving 
					or taking tickets to or from a user
					
					Example 1: ``!tickets add @someone 5``
					This will _add_ 5 tickets to the user mentioned
					
					Example 2: ``!tickets del @someone 5``
					This will _subtract_ 5 tickets from the user mentioned""",
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
							delete_after = 10)
				
			elif operation.lower() == "add":
				if value in [None,0] or member == None:
					await ctx.send(embed = discord.embed(
						title = "Ticket Addition Override Command",
						description = """This command is used for manually giving the 
						tickets to a user

						For Example: ``!tickets add @someone 5``
						This will _add_ 5 tickets to the user mentioned""",
						color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
								delete_after = 10)
				else:
					guild = mn.raffledbase[str(ctx.guild.id)]
					buyersCursor = guild.find({"type":"buyer"})
					buyers = []
					for i in buyersCursor:
						buyers.append(i["_id"])

					if member.id not in buyers:
						ticketlog = {"_id":member.id,"type":"buyer","tickets":value}
						guild.insert_one(ticketlog)
						currenttix = value
					else:
						prevtix = guild.find_one({"_id":member.id},{"_id":0,"tickets":1})["tickets"]
						currenttix = prevtix + value
						guild.find_one_and_update({"_id":member.id},{"$set":{"tickets":prevtix}})
					
					tixboughtEmbed = discord.Embed(
							title = "Tickets bought", 
							description = f"""Yay! {value} tickets bought for {member.mention} by {ctx.author.mention}!
							Total tickets bought by {member.mention}: ``{currenttix}``""",
							color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
							)
					await ctx.send(embed = tixboughtEmbed, delete_after = 30)
				
			elif operation.lower() == "del":
				if value in [None,0] or member == None:
					await ctx.send(embed = discord.embed(
						title = "Ticket Addition Override Command",
						description = """This command is used for manually taking the 
						tickets from a user

						For Example: ``!tickets add @someone 5``
						This will _subtract_ 5 tickets from the user mentioned""",
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
								delete_after = 10)
				else:
					guild = mn.raffledbase[str(ctx.guild.id)]
					buyersCursor = guild.find({"type":"buyer"})
					buyers = []
					for i in buyersCursor:
						buyers.append(i["_id"])

					if member.id not in buyers:
						await ctx.send(embed = discord.Embed(
							title = "Hold Up!",
							description = "This user has no tickets yet so you can't delete his/her tickets",
							color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
						))
					else:
						prevtix = guild.find_one({"_id":member.id},{"_id":0,"tickets":1})["tickets"]
						currenttix = prevtix - value
						guild.find_one_and_update({"_id":member.id},{"$set":{"tickets":prevtix}})
					
						tixdeletedEmbed = discord.Embed(
								title = "Ticket(s) deleted", 
								description = f"""{value} tickets deleted for {member.mention} by {ctx.author.mention}!
								Total tickets left for {member.mention}: ``{currenttix}``""",
								color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
								)
						await ctx.send(embed = tixdeletedEmbed, delete_after = 30)

			elif operation != None and member != None and value == None:
				await ctx.send(f"Please mention the number of tickets to give/take from {member.name}")

			else:
				pass
		else:
			await ctx.send(embed = discord.Embed(
				title = "No Raffle Created",
				description = "Create a raffle for this guild using ``rafflecreate`` command",
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
			))

def setup(client):
	client.add_cog(override_cmd(client))