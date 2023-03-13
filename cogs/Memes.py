from datetime import datetime

import disnake
from disnake.ext import commands

from utils.bot import OGIROID
from utils.config import Guilds

main_guild = Guilds.main_guild


class Memes(commands.Cog):
    """Meme Commands"""

    def __init__(self, bot: OGIROID):
        self.bot = bot


    @commands.slash_command(
        guild_ids=[main_guild],
        name="meme",
        aliases=["dankmeme"],
        description="Random meme from r/memes",
    )
    async def meme(self, inter):
        """Random meme from r/memes"""
        subreddit = "memes"
        await self.get_posts(inter, subreddit)

    @commands.slash_command(
        guild_ids=[main_guild],
        name="programmerhumor",
        aliases=["progmeme", "programmermeme", "memeprogrammer"],
        description="Random meme from r/programmerhumor",
    )
    async def programmerhumor(self, inter):
        """Random meme from r/programmerhumor"""
        subreddit = "ProgrammerHumor"
        await self.get_posts(inter, subreddit)

    async def get_posts(self, inter, subreddit):
        url = f"https://api.reddit.com/r/{subreddit}/random"
        response = await self.bot.session.get(url)
        r = await response.json()
        upvotes = r[0]["data"]["children"][0]["data"]["ups"]
        embed = disnake.Embed(
            title=f'{r[0]["data"]["children"][0]["data"]["title"]}',
            description=f'{r[0]["data"]["children"][0]["data"]["selftext"]}',
            colour=0x00B8FF,
            timestamp=datetime.now(),
            url=f"https://www.reddit.com{r[0]['data']['children'][0]['data']['permalink']}",
        )
        embed.set_image(url=r[0]["data"]["children"][0]["data"]["url"])
        embed.set_footer(
            text=f"{upvotes} Upvotes ",
            icon_url="https://cdn.discordapp.com/attachments/925750381840064525/925755794669047899/PngItem_715538.png",
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        guild_ids=[main_guild], name="freemoney", description="Get free money!"
    )
    async def free_money(self, inter):
        """Get free money"""
        await inter.send(
            "Free money hack!\n[Click here for free money](<https://youtu.be/dQw4w9WgXcQ>)"
        )


def setup(bot: OGIROID):
    bot.add_cog(Memes(bot))
