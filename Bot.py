import os
import discord
import requests, urllib.request
from requests_html import AsyncHTMLSession
import json
import mysql.connector
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX")
OWNERID = os.getenv("OWNER_ID")
CDRIVER = "CDriver/chromedriver.exe"
PICTURES = "https://steamcommunity-a.akamaihd.net/economy/image/"
PICPATH = "pictures/"
GAMEURLS = {
    "csgo":  "https://steamcommunity.com/market/listings/$appid/$weapon%20%7C%20$name%20%28$quality%29/render?start=0&count=1&currency=$currency&format=json"

}
asession = AsyncHTMLSession()

#TODO:
#-Use requests_html - Done
#-Use the steam search - Done
#-Change session to use AsyncHTMLSession - Done
#-Store results in a database

bot = commands.Bot(command_prefix=PREFIX)

@bot.command(
    name="price"
)
async def price(ctx, game = "csgo", *args):
    gameUrl = "https://store.steampowered.com/search/?term=$app" #"https://steamdb.info/search/?a=app&q=$app&type=1&category=0"
    priceUrl = "https://steamcommunity.com/market/search/render/?norender=1&appid=$appid&count=$count&query=$query"#"https://steamcommunity.com/market/search/render/?norender=1&appid=578080&count=5&query=PGC+2019+-+M416"
    descUrl = "https://steamcommunity.com/market/listings/$appid/$query/render?start=0&count=$count&currency=9&format=json"
    query = ""

    #Get query
    for arg in args:
        query += arg
    if query == "":
        query = "!\"#¤%&))"

    #Get game URL
    gameUrl = gameUrl.replace("$app", game)

    #Get game id
    r = await asession.get(gameUrl)
    await r.html.arender()

    try:
        gameDiv = r.html.xpath("/html/body/div[1]/div[7]/div[5]/form/div[1]/div/div[1]/div[3]/div[2]/div[3]/a[1]")
        gameId = gameDiv[0].attrs["data-ds-appid"]
    except:
        await ctx.send("Game not found")
        return

    #Get price URL
    priceUrl = priceUrl.replace("$count", "1")
    priceUrl = priceUrl.replace("$appid", gameId)
    priceUrl = priceUrl.replace("$query", query)

    #Get description URL
    descUrl = descUrl.replace("$count", "1")
    descUrl = descUrl.replace("$appid", gameId)
    descUrl = descUrl.replace("$query", query)

    #Get description
    with urllib.request.urlopen(descUrl) as u:
        try:
            descData = json.loads(u.read().decode())
        except:
            await ctx.send("No results found")
            return
    try:#TODO: A better way of cheking for descriptions
        descKey = list(descData["assets"]["578080"]["2"].keys())
        desc = descData["assets"]["730"]["2"][descKey[0]]["descriptions"][2]["value"]
        desc = desc.replace("<i>", "*")
        desc = desc.replace("</i>", "*")
    except:
        desc = ""

    #Get price
    with urllib.request.urlopen(priceUrl) as u:
        priceData = json.loads(u.read().decode())
    try:
        price = str(priceData["results"][0]["sell_price"])
        priceLen = len(price) - 2
        price = price[:priceLen] + "." + price[priceLen:]
        price = float(price)
        price = round(price, 2)
    except:
        await ctx.send("No results found")
        print(gameUrl)
        print(priceUrl)
        print(descUrl)
        return

    #Get picture of item
    picture = PICTURES + priceData["results"][0]["asset_description"]["icon_url"]

    #Create embed with picture and thumbnail
    emb = discord.Embed(title=priceData["results"][0]["app_name"], description=desc)
    emb.add_field(name="Item", value=priceData["results"][0]["name"], inline=True)
    emb.add_field(name="Price", value=price)
    emb.set_image(url=picture)
    emb.set_thumbnail(url=priceData["results"][0]["app_icon"])

    print(priceData["results"][0]["app_name"] + ": " + str(priceData["results"][0]["name"]))
    await ctx.send(ctx.author.mention + " here is your result", embed=emb)

@bot.command(
    name = "kill"
)
async def kill(ctx):
    if ctx.author.id == int(OWNERID):
        print("Bot shuting down...")
        await asession.close()
        await ctx.send("Stopping bot...")
        await bot.logout()
    else:
        
        await ctx.send(ctx.author.mention + ", men dont try turn me off you mother you")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f'They are connetced to the following guild(s):')
    for guild in bot.guilds:
        print(f'{guild.name} (id:{guild.id})')
    print()
bot.run(TOKEN)