import random

import aiofiles
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

async def save_image(path: str, image: memoryview):
	async with aiofiles.open(path, "wb") as file:
		await file.write(image)


def perms(ctx):
	role = False
	for i in ctx.author.roles:
		if i.endswith("name='Raffle Permissions'>"):
			role = True
			break
	return (ctx.author.guild_permissions.administrator) or role