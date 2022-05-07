import random
# from discord.ext import commands

#for checking admin perms for future reference

def permscheck(ctx):
  if ctx.message.author.guild_permissions.administrator:
    return True
  else:
    return False

def random_chooser(userlist: list, tixlist: list):
	return random.choices(userlist, weights = tixlist,k=1)[0]
	

def hexConvertor(iterator):
	hexlist = []
	for i in iterator:
		hexlist.append(i["Hex"])
	hex = random.choice(hexlist)
	intcol = int(hex, 16)
	return intcol