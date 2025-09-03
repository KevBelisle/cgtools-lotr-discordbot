from dataclasses import fields
import copy
import os
import logging
from dotenv import load_dotenv

import peewee
import discord

load_dotenv()
TOKEN: str = os.getenv("TOKEN") or ""

database = peewee.SqliteDatabase("lotr_lcg.db")


class CardSide(peewee.Model):
    Slug = peewee.CharField(primary_key=True)
    Title = peewee.CharField()
    Sphere = peewee.CharField(null=True)
    Type = peewee.CharField()
    Subtype = peewee.CharField(null=True)
    Text = peewee.CharField()
    FlavorText = peewee.CharField(null=True)
    Traits = peewee.CharField()
    Keywords = peewee.CharField()

    Attack = peewee.IntegerField(null=True)
    Defense = peewee.IntegerField(null=True)
    HitPoints = peewee.IntegerField(null=True)
    IsUnique = peewee.BooleanField(null=True)
    ThreatCost = peewee.IntegerField(null=True)
    Willpower = peewee.IntegerField(null=True)
    ResourceCost = peewee.IntegerField(null=True)
    VictoryPoints = peewee.IntegerField(null=True)
    QuestPoints = peewee.IntegerField(null=True)
    ThreatStrength = peewee.IntegerField(null=True)
    EngagementCost = peewee.IntegerField(null=True)
    ShadowEffect = peewee.CharField(null=True)
    MaxPerDeck = peewee.IntegerField(null=True)
    Orientation = peewee.CharField()
    Direction = peewee.CharField(null=True)
    Stage = peewee.CharField(null=True)

    Search_Title = peewee.CharField()

    class Meta:
        database = database
        table_name = "cardSides"


class Card(peewee.Model):
    Slug = peewee.CharField(primary_key=True)
    Front = peewee.ForeignKeyField(CardSide, db_column="FrontSlug")
    Back = peewee.ForeignKeyField(CardSide, db_column="BackSlug", null=True)
    IsRCO = peewee.BooleanField()

    class Meta:
        database = database
        table_name = "cards"


class Product(peewee.Model):
    Code = peewee.CharField(primary_key=True)
    Name = peewee.CharField()
    Type = peewee.CharField()
    Cycle = peewee.CharField(null=True)
    IsRepackage = peewee.BooleanField()

    class Meta:
        database = database
        table_name = "products"


class ProductCard(peewee.Model):
    Product = peewee.ForeignKeyField(Product, db_column="ProductCode")
    Number = peewee.CharField()
    Card = peewee.ForeignKeyField(Card, db_column="CardSlug", backref="ProductCards")
    Quantity = peewee.IntegerField()
    FrontImageUrl = peewee.CharField()
    BackImageUrl = peewee.CharField(null=True)
    BackNumber = peewee.CharField(null=True)

    class Meta:
        database = database
        table_name = "productCards"
        primary_key = False


database.connect()


client = discord.Client(intents=discord.Intents.default())

tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}")
    await tree.sync()
    await tree.sync(guild=discord.Object(id=383115373039321088))
    print("Synced!")
    print([k.name for k in tree.walk_commands()])
    print(
        [
            k.name
            for k in tree.walk_commands(guild=discord.Object(id=383115373039321088))
        ]
    )


# @tree.command(name="echo_global", description="Echoes a message - available globally.")
# @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
# @discord.app_commands.allowed_installs(guilds=True, users=True)
# @discord.app_commands.describe(message="The message to echo.")
# async def echo(interaction: discord.Interaction, message: str) -> None:
#     await interaction.response.send_message(message)


# @tree.command(name="echo_specific", description="Echoes a message - only in my guild.")
# @discord.app_commands.guilds(discord.Object(id=383115373039321088))
# @discord.app_commands.describe(message="The message to echo.")
# async def echo_specific(interaction: discord.Interaction, message: str) -> None:
#     await interaction.response.send_message(message)


@tree.command(name="card", description="Find a card")
# @discord.app_commands.guilds(discord.Object(id=383115373039321088))
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.describe(
    name="The name of the card to find.",
    image_only="Only include the card image. (Default: False)",
    just_for_me="Only show this card to me. (Default: False)",
)
async def card(
    interaction: discord.Interaction,
    name: str,
    image_only: bool = False,
    just_for_me: bool = False,
) -> None:
    # await interaction.response.send_message(
    #     f"Card command invoked with name: {name}, image_only: {image_only}, and just_for_me: {just_for_me}"
    # )

    card = Card.get_or_none(Card.Slug == name)

    if not card:
        await interaction.response.send_message(
            "Something went wrong, couldn't find that card.", ephemeral=True
        )
        return

    embed = discord.Embed()

    ## Build embed title
    sphere_emoji = (
        f":{card.Front.Sphere.lower()}: "
        if card.Front.Sphere and card.Front.Sphere != "Neutral"
        else ""
    )
    unique_emoji = "<:unique:1412289547831742464> " if card.Front.IsUnique else ""

    embed.title = f"{sphere_emoji}{unique_emoji}{card.Front.Title}"

    embed.url = f"https://lotr.cardgame.tools/#/cards/{card.Slug}"

    if not image_only:
        ## Build embed description
        description_parts = []

        description_parts.append(
            f"*{f"{card.Front.Sphere} " if card.Front.Sphere else ''}{card.Front.Type}{f" ({card.Front.Subtype})" if card.Front.Subtype else ""}{" - " if card.Front.Traits or card.Front.Keywords else ""}{f"{card.Front.Traits.replace(",", " ")}" if card.Front.Traits else ""}{" - " if card.Front.Traits and card.Front.Keywords else ""}{f"{card.Front.Keywords.replace(",", " ")}" if card.Front.Keywords else ""}*"
        )
        description_parts.append(
            f"{f"{card.Front.Willpower}:willpower: __ __" if card.Front.Willpower else ""}{f"{card.Front.ThreatStrength}:threat: __ __" if card.Front.ThreatStrength else ""}{f"{card.Front.Attack}<:attack:1412288381848653934> __ __" if card.Front.Attack else ""}{f"{card.Front.Defense}<:defense:1412288556092883067> __ __" if card.Front.Defense else ""}{f"{card.Front.HitPoints}:hitpoints: __ __" if card.Front.HitPoints else ""}"
        )
        description_parts.append(card.Front.Text)
        description_parts.append(" __ __")

        embed.description = "\n\n".join(
            [parts for parts in description_parts if len(parts) > 0]
        )

        ## Build embed fields

        if card.Front.ShadowEffect:
            embed.add_field(
                name="Shadow Effect",
                value=f"*{card.Front.ShadowEffect}*",
                inline=False,
            )

        if card.Front.FlavorText:
            embed.add_field(
                name="Flavor Text",
                value=f"*{card.Front.FlavorText}*",
                inline=False,
            )

        if any(productCard.Product.IsRepackage for productCard in card.ProductCards):
            embed.add_field(
                name="Found in Repackaged Products",
                value="\n".join(
                    [
                        f"{productCard.Quantity}x card #{productCard.Number} in [{productCard.Product.Name}](https://lotr.cardgame.tools/#/products/{productCard.Product.Code}){" Nightmare Deck" if productCard.Product.Type == "Nightmare_Expansion" else ""}"
                        for productCard in card.ProductCards
                        if productCard.Product.IsRepackage
                    ]
                ),
                inline=False,
            )

        if any(
            not productCard.Product.IsRepackage for productCard in card.ProductCards
        ):
            embed.add_field(
                name="Found in Original Releases",
                value="\n".join(
                    [
                        f"{productCard.Quantity}x card #{productCard.Number} in [{productCard.Product.Name}](https://lotr.cardgame.tools/#/products/{productCard.Product.Code}){" Nightmare Deck" if productCard.Product.Type == "Nightmare_Expansion" else ""}{f" ({productCard.Product.Cycle} cycle)" if productCard.Product.Cycle else ""}"
                        for productCard in card.ProductCards
                        if not productCard.Product.IsRepackage
                    ]
                ),
                inline=False,
            )

    image_urls = set(
        [
            f"https://images.cardgame.tools/lotr/sm/{productCard.FrontImageUrl}"
            for productCard in card.ProductCards
        ]
    )

    embeds = [add_image_to_embed(embed, url) for url in image_urls]

    await interaction.response.send_message(embeds=embeds, ephemeral=just_for_me)


def add_image_to_embed(embed: discord.Embed, image_url: str) -> discord.Embed:
    new_embed = copy.copy(embed)
    new_embed.set_image(url=image_url)
    return new_embed


@card.autocomplete("name")
async def card_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    input = current  # can be empty/None

    if len(input) < 2:
        return []

    query = (
        Card.select()
        .join(CardSide, on=Card.Front)
        .switch(Card)
        .join(CardSide.alias(), peewee.JOIN.LEFT_OUTER, on=Card.Back)
        .where(
            Card.Front.Search_Title.contains(input)
            | Card.Back.Search_Title.contains(input)
        )
        .order_by(Card.Slug)
        .limit(25)
    )

    simple_choices: list[dict[str, str]] = [
        {
            "name": f"{f"{card.Front.Sphere} " if card.Front.Sphere else ''}{card.Front.Type} - {card.Front.Title}",
            "value": card.Slug,
        }
        for card in query
    ]
    simple_choices_names = [choice["name"] for choice in simple_choices]

    if len(simple_choices) == len(set(simple_choices_names)):
        return [
            discord.app_commands.Choice(name=choice["name"], value=choice["value"])
            for choice in simple_choices
        ]
    else:
        choices: list[dict[str, str]] = []

        for card in query:
            name = f"{f"{card.Front.Sphere} " if card.Front.Sphere else ''}{card.Front.Type} - {card.Front.Title}"

            if len([n for n in simple_choices_names if n == name]) > 1:
                name += f" ({", ".join(set([ productCard.Product.Name for productCard in card.ProductCards ]))})"

            choices.append(
                {
                    "name": name[:100],
                    "value": card.Slug,
                }
            )

        return [
            discord.app_commands.Choice(name=choice["name"], value=choice["value"])
            for choice in choices
        ]


client.run(TOKEN, log_level=logging.INFO)
