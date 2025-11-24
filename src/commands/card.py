import copy

import discord
import peewee

from src.database import Card, CardSide
from src.discord_client import icon_emojis, sphere_colors, sphere_emojis, tree
from src.helpers.card_text_formatting import format_card_text, format_number


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
    card = Card.get_or_none(Card.Slug == name)

    if not card:
        await interaction.response.send_message(
            "Something went wrong, couldn't find that card.", ephemeral=True
        )
        return

    embed = discord.Embed()

    ## Build embed title
    sphere_emoji = f"{sphere_emojis[card.Front.Sphere]} " if card.Front.Sphere else ""
    unique_emoji = f"{icon_emojis['Unique']} " if card.Front.IsUnique else ""

    embed.title = f"{sphere_emoji}{unique_emoji}{card.Front.Title}"

    embed.url = f"https://lotr.cardgame.tools/#/cards/{card.Slug}"

    if card.Front.Sphere:
        embed.color = discord.Color.from_str(sphere_colors[card.Front.Sphere])

    if not image_only:
        ## Build embed description
        description_parts = []

        description_parts.append(
            f"""*{f"{card.Front.Sphere} " if card.Front.Sphere else ""}{card.Front.Type}{f" ({card.Front.Subtype})" if card.Front.Subtype else ""}{" - " if card.Front.Traits or card.Front.Keywords else ""}{f"{card.Front.Traits.replace(',', ' ')}" if card.Front.Traits else ""}{" - " if card.Front.Traits and card.Front.Keywords else ""}{f"{card.Front.Keywords.replace(',', ' ')}" if card.Front.Keywords else ""}*"""
        )

        stats_string = f"""{f"{format_number(card.Front.Willpower)} {icon_emojis['Willpower']} " if card.Front.Willpower else ""}{f"{format_number(card.Front.ThreatStrength)} {icon_emojis['Threat']} " if card.Front.ThreatStrength else ""}{f"{format_number(card.Front.Attack)} {icon_emojis['Attack']} " if card.Front.Attack else ""}{f"{format_number(card.Front.Defense)} {icon_emojis['Defense']} " if card.Front.Defense else ""}{f"{format_number(card.Front.HitPoints)} {icon_emojis['HitPoints']} " if card.Front.HitPoints else ""}"""

        if card.Front.EngagementCost:
            stats_string += (
                f"\nEngagement cost: {format_number(card.Front.EngagementCost)}"
            )
        if card.Front.ResourceCost:
            stats_string += f"\nResource cost: {format_number(card.Front.ResourceCost)}"
        if card.Front.ThreatCost:
            stats_string += f"\nStarting threat: {format_number(card.Front.ThreatCost)}"
        if card.Front.QuestPoints:
            stats_string += f"\nQuest points: {format_number(card.Front.QuestPoints)}"

        description_parts.append(stats_string.strip())

        description_parts.append(
            format_card_text(card.Front.Text) if card.Front.Text else ""
        )
        description_parts.append(" ** **")

        embed.description = "\n\n".join(
            [parts for parts in description_parts if len(parts) > 0]
        )

        ## Build embed fields

        if card.Front.ShadowEffect:
            embed.add_field(
                name="Shadow Effect",
                value=f"*{format_card_text(card.Front.ShadowEffect)}*",
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
                        f"- {productCard.Quantity}x card #{productCard.Number} in [{productCard.Product.Name}](https://lotr.cardgame.tools/#/products/{productCard.Product.Code}){' Nightmare Deck' if productCard.Product.Type == 'Nightmare_Expansion' else ''}"
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
                        f"- {productCard.Quantity}x card #{productCard.Number} in [{productCard.Product.Name}](https://lotr.cardgame.tools/#/products/{productCard.Product.Code}){' Nightmare Deck' if productCard.Product.Type == 'Nightmare_Expansion' else ''}{f' ({productCard.Product.Cycle} cycle)' if productCard.Product.Cycle else ''}"
                        for productCard in card.ProductCards
                        if not productCard.Product.IsRepackage
                    ]
                ),
                inline=False,
            )

    image_urls = set(
        [
            x
            for xs in [
                (
                    [
                        f"https://images.cardgame.tools/lotr/sm/{productCard.FrontImageUrl}",
                        f"https://images.cardgame.tools/lotr/sm/{productCard.BackImageUrl}",
                    ]
                    if productCard.BackImageUrl
                    else [
                        f"https://images.cardgame.tools/lotr/sm/{productCard.FrontImageUrl}"
                    ]
                )
                for productCard in card.ProductCards
            ]
            for x in xs
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
            "name": f"{f'{card.Front.Sphere} ' if card.Front.Sphere else ''}{card.Front.Type} - {card.Front.Title}",
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
            name = f"{f'{card.Front.Sphere} ' if card.Front.Sphere else ''}{card.Front.Type} - {card.Front.Title}"

            if len([n for n in simple_choices_names if n == name]) > 1:
                name += f" ({', '.join(set([productCard.Product.Name for productCard in card.ProductCards]))})"

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
