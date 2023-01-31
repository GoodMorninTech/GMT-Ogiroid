import disnake
from disnake.ext import commands

from utils.bot import OGIROID
from utils.config import Guilds

main_guild = Guilds.main_guild


class Animals(commands.Cog):
    """Animals related commands!"""

    def __init__(self, bot: OGIROID):
        self.bot = bot

    @commands.slash_command(
        guild_ids=[main_guild],
        description="Gets a random picture of the specified animal",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def animal(self, inter):
        pass

    @animal.sub_command(guild_ids=[main_guild], name="cat", description="Get a random cat picture")
    async def cat(self, inter):
        """Get a random cat picture!"""
        response = await self.bot.session.get("https://some-random-api.ml/animal/cat")
        data = await response.json()
        embed = disnake.Embed(
            title="Cat Picture! 🐱",
            description="Get a picture of a cat!",
            color=0xFFFFFF,
        )
        embed.set_image(url=data["image"])
        embed.set_footer(
            text=f"Command issued by: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        await inter.response.send_message(f"**Fun Fact: **" + data["fact"], embed=embed)

    @animal.sub_command(guild_ids=[main_guild], name="dog", description="Get a random dog picture")
    async def dog(self, inter):
        """Get a random dog picture!"""
        response = await self.bot.session.get("https://some-random-api.ml/animal/dog")
        data = await response.json()
        embed = disnake.Embed(
            title="Dog Picture! 🐶",
            description="Get a picture of a dog!",
            color=0xFFFFFF,
        )
        embed.set_image(url=data["image"])
        embed.set_footer(
            text=f"Command issued by: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        await inter.response.send_message("**Fun Fact: **" + data["fact"], embed=embed)

    @animal.sub_command(guild_ids=[main_guild], name="bird", description="Get a random bird picture")
    async def bird(self, inter):
        """Get a random bird picture!"""
        response = await self.bot.session.get("https://some-random-api.ml/animal/bird")
        data = await response.json()
        embed = disnake.Embed(
            title="Bird Picture! 🐦",
            description="Get a picture of a bird!",
            color=0xFFFFFF,
        )
        embed.set_image(url=data["image"])
        embed.set_footer(
            text=f"Command issued by: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        await inter.response.send_message("**Fun Fact: **" + data["fact"], embed=embed)

    @animal.sub_command(guild_ids=[main_guild], name="fox", description="Get a random fox picture")
    async def fox(self, inter):
        """Get a random fox picture!"""
        response = await self.bot.session.get("https://some-random-api.ml/animal/fox")
        data = await response.json()
        embed = disnake.Embed(
            title="Fox Picture! 🦊",
            description="Get a picture of a fox!",
            color=0xFFFFFF,
        )
        embed.set_image(url=data["image"])
        embed.set_footer(
            text=f"Command issued by: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        await inter.response.send_message("**Fun Fact: **" + data["fact"], embed=embed)

    @animal.sub_command(guild_ids=[main_guild], name="panda", description="Get a random panda picture")
    async def panda(self, inter):
        """Get a random panda picture!"""
        response = await self.bot.session.get("https://some-random-api.ml/animal/panda")
        data = await response.json()
        embed = disnake.Embed(
            title="Panda Picture! 🐼",
            description="Get a picture of a panda!",
            color=0xFFFFFF,
        )
        embed.set_image(url=data["image"])
        embed.set_footer(
            text=f"Command issued by: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        await inter.response.send_message("**Fun Fact: **" + data["fact"], embed=embed)

    @animal.sub_command(guild_ids=[main_guild], name="koala", description="Get a random cat picture")
    async def koala(self, inter):
        """Get a random koala picture!"""
        response = await self.bot.session.get("https://some-random-api.ml/animal/koala")
        data = await response.json()
        embed = disnake.Embed(
            title="Koala Picture! 🐨",
            description="Get a picture of a koala!",
            color=0xFFFFFF,
        )
        embed.set_image(url=data["image"])
        embed.set_footer(
            text=f"Command issued by: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        await inter.response.send_message("**Fun Fact: **" + data["fact"], embed=embed)


def setup(bot):
    bot.add_cog(Animals(bot))
