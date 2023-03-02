import datetime

import disnake
from disnake.ext import commands, tasks
from pymongo import MongoClient

from utils.DBhandlers import GuildNewsHandler
from utils.bot import OGIROID
from utils.config import Guilds
from utils.exceptions import GuildNewsAlreadyExists, GuildNewsNotFound
from utils.models import GuildNewsModel
from utils.CONSTANTS import TIMES

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

    @commands.slash_command(description="Setup the news channel")
    async def setup(self, inter):
        pass

    @commands.has_permissions(administrator=True)
    @setup.sub_command(name="create", description="Setup the news channel")
    async def create(
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
        guardian: bool = commands.Param(description="Should I send Guardian news?"),
        theverge: bool = commands.Param(description="Should I send The Verge news?"),
        techcrunch: bool = commands.Param(description="Should I send TechCrunch news?"),
        gmt: bool = commands.Param(description="Should i send GMT news"),
        time: str = commands.Param(
            description="What time should I send the news? (UTC timezone)",
            choices=TIMES,
        ),
    ):
        await inter.response.defer()
        news_list = ""

        news_sources = {
            "bbc": bbc,
            "guardian": guardian,
            "verge": theverge,
            "techcrunch": techcrunch,
            "gmt": gmt,
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
                # lowering it so it matches the db
                news=news_list.lower(),
                extras=None,
            )
        except GuildNewsAlreadyExists:
            return await inter.send(
                f"Your server already has a news channel setup, to change it use `/setup edit`"
            )

        await inter.send(
            f"Successfully setup the news channel to {channel.mention}",
            ephemeral=True,
            delete_after=10,
        )

    @commands.has_permissions(administrator=True)
    @setup.sub_command(
        name="edit",
        description="Edit the news config. Leave the parameters unchanged if you don't want to change them",
    )
    async def edit(
        self,
        inter,
        channel: disnake.TextChannel = commands.Param(
            description="The news channel, make sure to give me the permissions to send messages and embeds",
            default=None,
        ),
        frequency: str = commands.Param(
            description="How often should I send the news",
            choices=["everyday", "weekdays", "weekends"],
            default=None,
        ),
        bbc: bool = commands.Param(description="Should I send BBC news?", default=None),
        guardian: bool = commands.Param(
            description="Should I send Guardian news?", default=None
        ),
        theverge: bool = commands.Param(
            description="Should I send The Verge news?", default=None
        ),
        techcrunch: bool = commands.Param(
            description="Should I send TechCrunch news?", default=None
        ),
        gmt: bool = commands.Param(description="Should i send GMT news", default=None),
        time: str = commands.Param(
            description="What time should I send the news? (UTC timezone)",
            choices=TIMES,
            default=None,
        ),
    ):
        await inter.response.defer()
        news_list = ""

        news_sources = {
            "bbc": bbc,
            "guardian": guardian,
            "verge": theverge,
            "techcrunch": techcrunch,
            "gmt": gmt,
        }
        current_config = await self.news_handler.get_config(inter.guild.id)
        current_news = current_config.news.split(",")

        for name, value in news_sources.items():
            if value is False and name in current_news:
                # doesn't really serve a purpose but it's cool
                current_news.remove(name)
            elif value is True or name in current_news:
                # if it gets selected, or it's already in the list, we add it
                news_list += f"{name},"
            elif value is None and name in current_news:
                # this means it's unchanged, and it has been part of it, so we add it, doesn't really serve a purpose
                news_list += f"{name},"

        if news_list.endswith(","):
            news_list = news_list[:-1]

        try:
            await self.news_handler.update_config(
                guild_id=inter.guild.id,
                channel_id=channel.id if channel else current_config.channel_id,
                frequency=frequency if frequency else current_config.frequency,
                time=time if time else current_config.time,
                # lowering it so it matches the news sources
                news=news_list.lower() if news_list else current_config.news,
                extras=None,
            )
        except GuildNewsNotFound:
            return await inter.send(
                f"Your server doesn't have a news channel setup, to set it up use `/setup create`"
            )

        await inter.send(
            f"Successfully edited your configuration.", ephemeral=True, delete_after=10
        )

    @commands.has_permissions(administrator=True)
    @setup.sub_command(name="delete", description="Delete the news config")
    async def delete(
        self,
        inter,
        confirm: bool = commands.Param(
            description="Confirm deletion. No further confirmation will be asked"
        ),
    ):
        try:
            if not confirm:
                return await inter.send(f"Please confirm the deletion.")
            await self.news_handler.delete_config(inter.guild.id)
        except GuildNewsNotFound:
            return await inter.send(
                f"Your server doesn't have a news channel setup, to set it up use `/setup create`"
            )

        await inter.send(
            f"Successfully deleted your configuration.", ephemeral=True, delete_after=10
        )

    @commands.has_permissions()
    @setup.sub_command(name="get", description="Get the news config")
    async def get(self, inter: disnake.ApplicationCommandInteraction):
        try:
            config = await self.news_handler.get_config(inter.guild.id)
        except GuildNewsNotFound:
            return await inter.send(
                f"Your server doesn't have a news channel setup, to set it up use `/setup create`"
            )

        channel = inter.guild.get_channel(config.channel_id)

        await inter.send(
            f"Your news channel is {channel.mention}, it sends news {'on ' if not config.frequency == 'everyday' else ''}{config.frequency} at"
            f" {config.time} UTC, and it sends news from {config.news}",
            ephemeral=True,
        )

    @tasks.loop(minutes=60)
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
        source_names = {
            "bbc": "BBC",
            "cnn": "CNN",
            "guardian": "Guardian",
            "verge": "Verge",
            "techcrunch": "TechCrunch",
            "gmt": "GMT",
        }
        channel = self.bot.get_channel(guild.channel_id)
        if channel is None:
            return

        history = await channel.history(limit=1).flatten()

        try:
            if history[0].author.id == self.bot.user.id and history[
                0
            ].created_at > disnake.utils.utcnow() - datetime.timedelta(minutes=10):
                # we don't want to send two messages in a row
                return
        except IndexError:
            pass

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
                description=f"{article['description']}\n[Read more]({article['url']})\n**Source**: {source_names[article['source']]}",
                color=self.bot.config.colors.red,
            ).set_image(url=article["thumbnail"])
            embed.set_footer(text="Powered by Good Morning Tech")
            await channel.send(embed=embed)

        embed = disnake.Embed(
            title="Powered by Good Morning Tech. Check out our Website and join our Discord.",
            color=self.bot.config.colors.red,
        )
        embed.set_image(url="https://cdn.goodmorningtech.news/logo.png")
        await channel.send(
            embed=embed,
            components=[
                disnake.ui.Button(label="Website", url="https://goodmorningtech.news"),
                disnake.ui.Button(
                    label="Discord", url="https://discord.goodmorningtech.news"
                ),
            ],
        )


def setup(bot: commands.Bot):
    bot.add_cog(GuildNews(bot))
