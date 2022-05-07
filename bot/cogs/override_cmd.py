import discord
from discord.ext import commands
import mongo_declarations as mn
import logical_definitions as lgd

class override_cmd(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def tickets(self, ctx, operation = None, member = None, value = None):
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
			
		elif (operation.lower() == "add" and member == None) or (operation.lower() == "add" and value == None):
			await ctx.send(embed = discord.embed(
				title = "Ticket Addition Override Command",
				description = """This command is used for manually giving the 
				tickets to a user

				For Example: ``!tickets add @someone 5``
				This will _add_ 5 tickets to the user mentioned""",
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
						  delete_after = 10)
			
		elif (operation.lower() == "del" and member == None) or (operation.lower() == "del" and value == None):
			await ctx.send(embed = discord.embed(
				title = "Ticket Addition Override Command",
				description = """This command is used for manually taking the 
				tickets from a user

				For Example: ``!tickets add @someone 5``
				This will _subtract_ 5 tickets from the user mentioned""",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
						  delete_after = 10)

		elif operation != None and member != None and value == None:
			await ctx.send(f"Please mention the number of tickets to give/take from {member.name}")

		else:
			