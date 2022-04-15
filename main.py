from datetime import time
import json
import os
import random
import re

import discord
from discord.ext import commands, tasks
from discord.ext.commands.errors import (
    CheckFailure,
    CommandNotFound,
    MissingRequiredArgument,
)

from files.logger import Logger
from files.my_calendar import myCalendar


bot = commands.Bot(command_prefix="!", help_command=None, case_insensitive=True)


@bot.event
async def on_command_error(ctx, error):
    errors_list = (CheckFailure, CommandNotFound)
    if isinstance(error, MissingRequiredArgument):
        embed = discord.Embed(
            description="You need to specify something after the command !  :x:",
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)
    elif isinstance(error, errors_list):
        pass


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


def checkAuthorized(ctx):
    """Used as a decorator to make some commands
    as admin commands"""
    return ctx.message.author.id in ["ADMIN DISCORD ID"]


###################################################################################


@bot.event
async def on_ready():
    print("Ready.")


@bot.command()
@commands.check(checkAuthorized)
async def db(ctx):
    await ctx.author.send(file=discord.File("files/bdd/db.json"))
    await ctx.message.delete()
    await ctx.reply("Check your DM !")


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        description=f"**MADISON COMMANDS**  :gear:\n\n"
        f":arrow_forward:  **!pic**\n\n- sends a random picture.\n\n"
        f":arrow_forward:  **!addResponse**\n\n- adding the message written after the command in "
        f"the random responses of Madison.\n\nex: *!addResponse fuck Enki*"
        f"\n\n:arrow_forward:  **!gas**\n\n- returns the current gasPrice on the chain mentionned in your message."
        f"\n\nex: *!gas ETH* will return the current gasPrice on ETH, in gwei."
        f"\n\n:arrow_forward:  **!gasList**\n\n- returns the list of supported chains for the *!gas* command.\n\n"
        f":arrow_forward:  **!gasAlert**\n\n- sets a private custom gas alert on any chain that is mentionned in the "
        f"**!gasList** command. To cancel an alert, set it to 0. You can set 1 alert per chain.\n\n"
        f"ex: *!gasAlert AVAX 50* will trigger an alert as soon as the gasPrice "
        f"is at 50 gwei on Avax chain, and Madison will notify you. Each alert is sent once, then reset.\n\n"
        f":arrow_forward:  **!myAlerts**\n\n- check the gas alerts you have set and waiting to be triggered.\n\n"
        f":arrow_forward:  **!save**\n\n- enables you to save a link in a private database. You can save as much links as you"
        f" want. For privacy reasons, your message will be deleted right after the link is saved.\n\n"
        f"ex: *!save https://pbs.twimg.com/media/E3hsoMuVUAMk91Z.jpg*\n\n"
        f":arrow_forward:  **!myLinks**\n\n- Madison will send you a private message with all your saved links.\n\n"
        f":arrow_forward:  **!deleteLink**\n\n- Removes a link from your list with its index.\n\n"
        f"ex: *!deleteLink 1*\n\n"
        f":arrow_forward:  **!savePic**\n\n- Enables you to add pictures in Madison folder "
        "(*.png* / *.jpg* only) :fire:\n\n"
        f":arrow_forward:  **!addCalendar**\n\n- Create a new calendar in which you can add events.\n\nex: "
        f"*!addCalendar Ethereum*\n\n:arrow_forward:  **!events**\n\n- get the saved events of a particular calendar.\n\n"
        f"ex: *!events Ethereum*\n\n:arrow_forward:  **!calendars**\n\n- gives you the list of all the registered calendars."
        f"\n\n:arrow_forward:  **!addEvent**\n\n- add an event in a particular calendar. You must respect the right format.\n\n"
        f"ex: *!addEvent Ethereum, Launch Shitcoin, 13/04*\n\n:arrow_forward:  **!delEvent**\n\n- to delete an event from a "
        f"particular calendar using his number.\n\nex: *!delEvent Ethereum 2* will delete the second event in the Ethereum calendar."
        f"\n\n:arrow_forward:  **!allEvents**\n\n- To get the list of all saved events.\n\n"
        f"Admin Commands: !delResponse, !delCalendar, !deleteLastResponse, !responsesList, !db\n\n",
        color=discord.Colour.blue(),
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()
    user.add_count(ctx.author.id)


###################################################################################


@bot.command()
async def pic(ctx):
    with open("files/bdd/responses.json", "r", encoding="utf8") as file:
        responses = json.load(file)
    try:
        await ctx.reply(
            random.choice(responses["list"]),
            file=discord.File(f"files/photos/{random.choice(photos)}"),
        )
    except IndexError:
        embed = discord.Embed(
            description="No picture saved at the moment ! Use **!savePic** command.",
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)

    user.add_count(ctx.author.id)


@bot.command()
async def savePic(ctx):
    try:
        embed = discord.Embed(
            description=user.saveImage(ctx.message.attachments[0].url),
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)
        await ctx.message.delete()
        user.add_count(ctx.author.id)

        refresh_pictures()

    except IndexError:
        embed = discord.Embed(
            description="No picture attached. Please send a picture along with "
            "the **!savePic** command.",
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)


@bot.command()
async def addResponse(ctx, *args):
    rsp = ""
    for arg in args:
        rsp += f" {arg}"
    rsp = str(rsp.strip())

    embed = discord.Embed(
        description=user.add_response(ctx.author.id, rsp),
        color=discord.Colour.blue(),
    )
    await ctx.reply(embed=embed)
    user.add_count(ctx.author.id)


@bot.command()
@commands.check(checkAuthorized)
async def delResponse(ctx, *args):
    rsp = ""
    for arg in args:
        rsp += f" {arg}"
    rsp = str(rsp).strip()

    embed = discord.Embed(
        description=user.del_response(rsp),
        color=discord.Colour.blue(),
    )
    await ctx.reply(embed=embed)


@bot.command()
@commands.check(checkAuthorized)
async def deleteLastResponse(ctx):

    embed = discord.Embed(
        description=user.delete_last_response(),
        color=discord.Colour.blue(),
    )
    await ctx.reply(embed=embed)


@bot.command()
@commands.check(checkAuthorized)
async def responsesList(ctx):
    embed = discord.Embed(
        description=user.allResponses(),
        color=discord.Colour.blue(),
    )
    await ctx.author.send(embed=embed)

    embed = discord.Embed(
        description="Responses list sent, check your DM !",
        color=discord.Colour.blue(),
    )
    await ctx.reply(embed=embed)


###################################################################################


@bot.command()
async def gas(ctx, arg):
    if arg.upper() in user.chains:
        try:
            url = "GAS_API_LINK"
            r = user.session.get(url).json()
            gasPrice = round(r["data"]["normal"]["price"] * 0.000000001, 2)

            embed = discord.Embed(
                description=f"Current gasPrice on {arg.upper()} is {gasPrice} gwei.",
                color=discord.Colour.blue(),
            )
            user.add_count(ctx.author.id)

        except KeyError:
            embed = discord.Embed(
                description="Error with the request. Try again.",
                color=discord.Colour.blue(),
            )
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(
            description="Wrong chain ! Use **!gasList** to check available chains.",
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)


@bot.command()
async def gasList(ctx):
    embed = discord.Embed(
        description=f"**Supported networks for !gas command are:**\n\n"
        f"{', '.join(user.chains)}",
        color=discord.Colour.blue(),
    )

    await ctx.reply(embed=embed)
    user.add_count(ctx.author.id)


@bot.command()
async def gasAlert(ctx, *args):
    if len(args) == 2:
        embed = discord.Embed(
            description=user.add_gas_alert(ctx.author.id, args[0], args[1]),
            color=discord.Colour.blue(),
        )

        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(
            description="Please send the correct parameters for your alert.  :x:\n\n"
            "ex: *!gasAlert ETH 50*",
            color=discord.Colour.blue(),
        )

        await ctx.reply(embed=embed)


@bot.command()
async def myAlerts(ctx):
    embed = discord.Embed(
        description=user.my_alerts(ctx.author.id),
        color=discord.Colour.blue(),
    )

    await ctx.reply(embed=embed)


@bot.command()
async def resetAlerts(ctx):
    embed = discord.Embed(
        description=user.reset_gas_alerts(ctx.author.id),
        color=discord.Colour.blue(),
    )

    await ctx.reply(embed=embed)


@tasks.loop(minutes=5)
async def checkGasAlerts():
    await bot.wait_until_ready()
    user.check_gas_alerts()


###################################################################################


@bot.command()
async def save(ctx, arg):
    embed = discord.Embed(
        description=user.add_link(ctx.author.id, arg),
        color=discord.Colour.blue(),
    )

    await ctx.reply(embed=embed)
    await ctx.message.delete()


@bot.command()
async def myLinks(ctx):
    links = user.user_links(ctx.author.id)

    if links:
        embed = discord.Embed(
            description="\n\n".join(links),
            color=discord.Colour.blue(),
        )

        await ctx.author.send(embed=embed)

        embed = discord.Embed(
            description="Check your DM !",
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)

    elif not links:
        embed = discord.Embed(
            description="No link saved yet. Use **!save** command to save your first.",
            color=discord.Colour.blue(),
        )

        await ctx.reply(embed=embed)


@bot.command()
async def deleteLink(ctx, arg):
    index = int(arg.strip())
    embed = discord.Embed(
        description=user.del_link(ctx.author.id, index),
        color=discord.Colour.blue(),
    )

    await ctx.reply(embed=embed)

    await ctx.message.delete()


###################################################################################


@bot.command()
async def addCalendar(ctx, arg):
    embed = discord.Embed(
        description=eventsCalendar.create_calendar(arg),
        color=discord.Colour.blue(),
    )
    user.add_count(ctx.author.id)
    await ctx.reply(embed=embed)


@bot.command()
async def events(ctx, arg):
    embed = discord.Embed(
        description=eventsCalendar.get_calendar(arg),
        color=discord.Colour.blue(),
    )
    user.add_count(ctx.author.id)
    await ctx.reply(embed=embed)
    embed = discord.Embed(
        description="You need to specify a calendar. Use **!allCalendars**\n\n"
        "to get the list of all the calendard saved.",
        color=discord.Colour.blue(),
    )


@bot.command()
@commands.check(checkAuthorized)
async def delCalendar(ctx, arg):
    embed = discord.Embed(
        description=eventsCalendar.delete_calendar(arg),
        color=discord.Colour.blue(),
    )
    user.add_count(ctx.author.id)
    await ctx.reply(embed=embed)


@bot.command()
async def calendars(ctx):
    embed = discord.Embed(
        description=eventsCalendar.get_all_calendars(),
        color=discord.Colour.blue(),
    )
    user.add_count(ctx.author.id)
    await ctx.reply(embed=embed)


@bot.command()
async def addEvent(ctx, *args):
    try:
        event = " ".join(args).split(",")
        calendar = event[0].strip()
        title = event[1].strip()
        date = event[2].strip()
        month = int(date[3:])
        day = int(date[:2])
    except Exception:
        embed = discord.Embed(
            description="Wrong format.  :x: Please use:\n\n"
            "**!newEvent CALENDAR, EVENT NAME, EVENT DATE**\n\nex: "
            "!addEvent Ethereum**,** lancement plateforme bitcogne**,** 01/04",
            color=discord.Colour.blue(),
        )
        return await ctx.reply(embed=embed)

    if re.match(r"\d{2}.\d{2}", date) and day < 32 and month < 13:
        embed = discord.Embed(
            description=eventsCalendar.create_event(calendar, title, date),
            color=discord.Colour.blue(),
        )
        user.add_count(ctx.author.id)
        return await ctx.reply(embed=embed)

    elif not re.match(r"\d{2}.\d{2}", date) or int(date[:2]) > 32 or int(date[3:]) > 13:
        embed = discord.Embed(
            description="Wrong date format.  :x: Accepted formats are:\n\n- **01/01**\n\n"
            "- **01.01**\n\n- **01-01**",
            color=discord.Colour.blue(),
        )
        return await ctx.reply(embed=embed)


@bot.command()
async def delEvent(ctx, *args):
    try:
        calendar = args[0].strip()
        index = int(args[1].strip())
    except Exception:
        embed = discord.Embed(
            description="Wrong format.  :x: Please use this format:\n\n"
            "**!delEvent CALENDAR NUMBER**\n\nex: "
            "*!delEvent Ethereum 2*",
            color=discord.Colour.blue(),
        )
        return await ctx.reply(embed=embed)
    user.add_count(ctx.author.id)

    embed = discord.Embed(
        description=eventsCalendar.delete_event(calendar, index),
        color=discord.Colour.blue(),
    )
    return await ctx.reply(embed=embed)


@bot.command()
async def allEvents(ctx):
    user.add_count(ctx.author.id)
    embed = discord.Embed(
        description=eventsCalendar.get_all_events(),
        color=discord.Colour.blue(),
    )
    return await ctx.reply(embed=embed)


@tasks.loop(hours=5)
async def check_events():
    await bot.wait_until_ready()
    eventsCalendar.checkEvents()


@tasks.loop(hours=16)
async def daily_events():
    await bot.wait_until_ready()
    eventsCalendar.send_daily_events()


###################################################################################

photos = []


def refresh_pictures():
    with os.scandir("files/photos/") as folder:
        for file in folder:
            if file.is_file():
                photos.append(file.name)


def create_files():
    
    if not os.path.isdir("files/photos"):
        os.mkdir("files/photos")

    if not os.path.isdir("files/bdd"):
        os.mkdir("files/bdd")

    if not os.path.exists("files/bdd/db.json"):
        with open("files/bdd/db.json", "w", encoding="utf8") as file:
            file.write("{}")

    if not os.path.exists("files/bdd/responses.json"):
        with open("files/bdd/responses.json", "w", encoding="utf8") as file:
            json.dump({"list": ["First"]}, file)

    if not os.path.exists("files/bdd/events.json"):
        with open("files/bdd/events.json", "w", encoding="utf8") as file:
            file.write("{}")

    print("Directories and files ok.")


create_files()
refresh_pictures()

user = Logger()
eventsCalendar = myCalendar()

checkGasAlerts.start()
check_events.start()
daily_events.start()
bot.run("DISCORD_BOT_TOKEN")
