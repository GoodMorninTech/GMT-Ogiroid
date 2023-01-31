import datetime

import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient

from utils.DBhandlers import GuildNewsHandler
from utils.bot import OGIROID
from utils.config import Guilds
from utils.exceptions import GuildNewsAlreadyExists
from utils.models import GuildNewsModel

main_guild = Guilds.main_guild


class GuildNews(commands.Cog):
    def __init__(self, bot: OGIROID):
        self.bot = bot
        self.news_handler: GuildNewsHandler = None
        self.mongo: MongoClient = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.send_news.start()
        self.news_handler = GuildNewsHandler(self.bot, self.bot.db)
        self.mongo = MongoClient(self.bot.config.mongo_uri)

    def cog_unload(self) -> None:
        self.send_news.cancel()

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="setup", description="Setup the news channel")
    async def setup(
        self,
        inter,
        channel: disnake.TextChannel = commands.Param(
            description="The news channel, make sure to give me the permissions to send messages and embeds"
        ),
        frequency: str = commands.Param(
            description="How often should I send the news",
            choices=["everyday", "weekdays", "weekends"],
        ),
        bbc: bool = commands.Param(description="Should I send BBC news?"),
        cnn: bool = commands.Param(description="Should I send CNN news?"),
        guardian: bool = commands.Param(description="Should I send Guardian news?"),
        theverge: bool = commands.Param(description="Should I send The Verge news?"),
        techcrunch: bool = commands.Param(description="Should I send TechCrunch news?"),
        gmt: bool = commands.Param(description="Should i send GMT news"),
        time: str = commands.Param(
            description="What time should I send the news? (UTC timezone)",
            choices=[
                "00:00",
                "01:00",
                "02:00",
                "03:00",
                "04:00",
                "05:00",
                "06:00",
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
                "23:00",
            ],
        ),
    ):
        await inter.response.defer()
        news_list = ""

        news_sources = {
            "BBC": bbc,
            "CNN": cnn,
            "Guardian": guardian,
            "Verge": theverge,
            "TechCrunch": techcrunch,
            "GMT": gmt,
        }

        for name, value in news_sources.items():
            if value:
                news_list += f"{name},"

        if news_list.endswith(","):
            news_list = news_list[:-1]

        if news_list == "":
            return await inter.send("You need to select at least one news source")

        try:
            await self.news_handler.create_config(
                guild_id=inter.guild.id,
                channel_id=channel.id,
                frequency=frequency,
                time=time,
                news=news_list,
                extras=None,
            )
        except GuildNewsAlreadyExists:
            return await inter.send(
                f"Your guild already has a news channel setup, to change it use `/edit-config`"
            )

        await inter.send(
            f"Successfully setup the news channel to {channel.mention}", ephemeral=True
        )

    @tasks.loop(minutes=50)
    async def send_news(self):
        guilds = await self.news_handler.get_configs()
        current_time = datetime.datetime.utcnow().strftime("%H:00")
        for guild in guilds:
            if guild.frequency == "everyday" and guild.time == current_time:
                await self.send_news_to_channel(guild)
            elif guild.frequency == "weekdays" and guild.time == current_time:
                if datetime.datetime.today().weekday() < 5:
                    await self.send_news_to_channel(guild)
            elif guild.frequency == "weekends" and guild.time == current_time:
                if datetime.datetime.today().weekday() > 4:
                    await self.send_news_to_channel(guild)

    async def send_news_to_channel(self, guild: GuildNewsModel):
        channel = self.bot.get_channel(guild.channel_id)
        if channel is None:
            return

        articles = self.mongo.goodmorningtech.articles.find(
            {
                "date": {
                    "$gte": datetime.datetime.utcnow() - datetime.timedelta(days=1)
                },
                "source": {"$in": guild.news.split(",")},
            }
        )
        await channel.send(
            embed=disnake.Embed(
                title="News",
                description="Here are the latest tech news",
                color=self.bot.config.colors.red,
            )
        )

        for article in articles:
            embed = disnake.Embed(
                title=article["title"],
                description=f"{article['description']}\n[Read more]({article['url']})\n**Source**: {article['source']}",
                color=self.bot.config.colors.red,
            ).set_image(url=article["thumbnail"])
            embed.set_footer(text="Powered by Good Morning Tech")
            await channel.send(embed=embed)

        embed = disnake.Embed(
            title="Powered by Good Morning Tech. Check out our Website.",
            color=self.bot.config.colors.red,
        )
        embed.set_image(url="https://cdn.goodmorningtech.news/logo.png")
        await channel.send(
            embed=embed,
            components=[
                disnake.ui.Button(label="Website", url="https://goodmorningtech.news")
            ],
        )


def setup(bot: commands.Bot):
    bot.add_cog(GuildNews(bot))
