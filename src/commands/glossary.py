from src.discord_client import *
from src.database import *


@tree.command(name="glossary", description="Lookup a term in the glossary")
# @discord.app_commands.guilds(discord.Object(id=383115373039321088))
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.describe(
    term="The term to look up.",
    just_for_me="Only share the definition with me. (Default: False)",
)
async def glossary(
    interaction: discord.Interaction,
    term: str,
    just_for_me: bool = False,
) -> None:
    db_term = Glossary.get_or_none(Glossary.Term == term)

    if not db_term:
        await interaction.response.send_message(
            "Something went wrong, couldn't find that term.", ephemeral=True
        )
        return

    embed = discord.Embed()

    ## Build embed title
    embed.title = f"{db_term.Term}"

    # embed.url = f"https://lotr.cardgame.tools/#/cards/{card.Slug}"

    ## Build embed description
    description_parts: list[str] = []

    description_parts.append(f"*({db_term.Type})*")
    description_parts += db_term.Definition.split("\n")

    embed.description = "\n\n".join(
        [parts for parts in description_parts if len(parts) > 0]
    )

    await interaction.response.send_message(embed=embed, ephemeral=just_for_me)


@glossary.autocomplete("term")
async def term_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    input = current  # can be empty/None

    if len(input) < 2:
        return []

    query = (
        Glossary.select()
        .where(Glossary.Term.contains(input))
        .order_by(Glossary.Term)
        .limit(25)
    )

    return [
        discord.app_commands.Choice(
            name=f"{entry.Term} {f"({entry.Type})" if entry.Type != "TBD" else ""}",
            value=entry.Term,
        )
        for entry in query
    ]
