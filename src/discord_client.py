import discord


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


sphere_emojis = {
    "Baggins": "<:baggins:1412792677212098611>",
    "Fellowship": "<:fellowship:1412792695100805191>",
    "Leadership": "<:leadership:1412792716143628438>",
    "Lore": "<:lore:1412792726033797130>",
    "Neutral": "<:neutral:1412798425598136461>",
    "Spirit": "<:spirit:1412792758527070343>",
    "Tactics": "<:tactics:1412792768627085464>",
}

sphere_colors = {
    "Baggins": "#744110",
    "Fellowship": "#7B341E",
    "Leadership": "#44337A",
    "Lore": "#21543D",
    "Neutral": "#747474",
    "Spirit": "#0A6E83",
    "Tactics": "#822727",
}

icon_emojis = {
    "Attack": "<:attack:1412792650024620174>",
    "Defense": "<:defense:1412792686414528594>",
    "HitPoints": "<:hit_points:1412792703653122180>",
    "SauronsEye": "<:saurons_eye:1412792743616319488>",
    "Threat": "<:threat:1412792778089300208>",
    "Unique": "<:unique:1412792791620391002>",
    "Willpower": "<:willpower:1412792800671436820>",
}
