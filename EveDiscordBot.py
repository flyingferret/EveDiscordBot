# Works with Python3.6

import datetime
import random
from datetime import timedelta
import configparser, os
from discord import errors
from discord.ext.commands import Bot

import ZkApp



BOT_PREFIX = ("?", "!")
TOKEN = ""

DEFAULT_DAYS = 7  # default days to run query back to

client = Bot(command_prefix=BOT_PREFIX)
killBoardApp = ZkApp.zkApp()

# =============
@client.event
async def on_ready():
    print('Bot Ready for commands')

# =============

@client.command(name='helphowdoimakelotsofisk',
                description="A guide to making isk",
                brief="A brief guide",
                aliases=["makeIsk", "howDoIMakeISk"],
                pass_context=True)
async def helphowdoimakelotsofisk(context):
    possible_responces = [
        'Crab',
        'PI',
        'Loot the battle field (hero salvager)',
        'gas huffing',
        'Work hard buy plex',
        'Send kalaik ISK and he will double it'
    ]
    await client.say(random.choice(possible_responces) + "," + context.message.author.mention)

@client.command(name='8Ball',
                description="Answer a yes/no question.",
                brief="Answer for the beyond",
                aliases=["eight_ball", "eightBall", "8ball"],
                pass_context=True)
async def eight_ball(context):
    possible_responces = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely'
        'Praise BOB Yes!'
    ]
    await client.say(random.choice(possible_responces) + "," + context.message.author.mention)

# ===============

@client.command(name='search_character_kb',
                description="Searches a characters kill boards for the last week. Given the Characters name. A "
                            "days argument can be added to the end of the request using the # e.g !charKB Kalaik "
                            "utama #100.  Note max number that can be returned at the moment is 200",
                brief="Killboard search Character",
                aliases=["search_Char_KB", "searchCharKB", "charKB"],
                pass_context=True)
async def search_character_kb(context, *args):
    variables = consolidateArgs(args)
    characterName = variables['mainArg']
    days = variables['days']

    print(characterName)

    characterID = killBoardApp.getID(characterName, 'character')
    # search for killMails
    if characterID:
        killMails = killBoardApp.getKillMails(characterID, getStartTime(days), 'character')

        if killMails:
            kills = 0
            deaths = 0
            for k in killMails:
                if 'character_id' in k.victim.keys() and (k.victim['character_id'] == characterID):
                    deaths += 1
            else:
                kills += 1

            await client.say('Yup they are active with %s kills and %s deaths in the last %s. Their last  killMail '
                             'being: ' % (kills, deaths, days))
            await client.say(
                "https://zkillboard.com/kill/%s/" % (killMails[0].killmail_id) + context.message.author.mention)
        else:
            await client.say("Nope possible carebear, zero kills" + context.message.author.mention)
    else:
        await client.say("Sorry I cannot find that character." + context.message.author.mention)

# ================

@client.command(name='search_Corp_KB',
                description="Searches a corporations kill boards for the last week. Given the Corporation name. A "
                            "days argument can be added to the end of the request using the # e.g !corpKB Star "
                            "seekers #100.  Note max number that can be returned at the moment is 200",
                aliases=["Corp_KB", "searchCorpKB", "corpKB"],
                brief="Killboard search Corp",
                pass_context=True)
async def search_corporation_kb(context, *args):
    variables = consolidateArgs(args)
    corpName = variables['mainArg']
    days = variables['days']
    corpID = killBoardApp.getID(corpName, 'corporation')

    # search for killMails
    if corpID:
        killMails = killBoardApp.getKillMails(corpID, getStartTime(days), 'corporation')

        # check if the queried corp was the victim or not
        kills = 0
        deaths = 0

        for k in killMails:
            victimID = k.victim['corporation_id']
            if int(victimID) == int(corpID):
                deaths += 1
            else:
                kills += 1

        if killMails:
            await client.say('Yup they are active with %s kills and %s deaths,in the last %s days. Their last '
                             ' killMail being: ' % (kills, deaths, days))
            await client.say(
                "https://zkillboard.com/kill/%s/" % (killMails[0].killmail_id) + context.message.author.mention)
        else:
            await client.say("Nope possible carebear, zero kills" + context.message.author.mention)
    else:
        await client.say("Sorry I cannot find that corp." + context.message.author.mention)

# ================
@client.command(name='systemKills',
                description="Searches a systems kill boards for the last week. Given the System name.  Default system "
                            "is out home system. A days argument can be added to the end of the request using the # "
                            "e.g !systemKB j140810 #100.  Note max number that can be returned at the moment is 200",
                aliases=["system_KB", "searchSystemKB", "systemKB"],
                brief="Killboard search Corp",
                pass_context=True)
async def systemKills(context, systemName='J140810', *args):
    # consolidate arguments
    variables = consolidateArgs(args)
    systemName = variables['mainArg']
    days = variables['days']

    if len(systemName) < 3:
        systemName = 'J140810'

    # find the sytem ID
    systemID = killBoardApp.getID(systemName, 'solar_system')
    # search for killMails
    if systemID:
        killMails = killBoardApp.getKillMails(systemID, getStartTime(days), 'solar_system')

        if killMails:
            await client.say('Yup this system (%s) is active with %s kills, in the last %s days the last  killMail '
                             'being: ' % (systemName, len(killMails), days))
            await client.say(
                "https://zkillboard.com/kill/%s/" % killMails[0].killmail_id + context.message.author.mention)
        else:
            await client.say("System not active zero kills " + context.message.author.mention)
    else:
        await client.say("Sorry I cannot find that system." + context.message.author.mention)

# Generate a formatted datetime str based on current datetime minus given number of days
def getStartTime(days):
    now = datetime.datetime.now()
    start = now - timedelta(days)
    startFormated = start.strftime("%Y%m%d%H") + '00'
    return startFormated

# Consolidate method arguments into valid varibles namely main argument and days which are superseded with '#' ie charactername#10 would be main = charactername, days = 10 (int)
def consolidateArgs(args):
    # find the main argument
    mainArg = ''
    for a in args:
        mainArg += str(a) + ' '
    mainArg = mainArg.strip()

    # Check if days parameter exist and remove it from mainArg, else revert to default (7)
    if mainArg.find('#') != -1:
        days = int(mainArg[mainArg.find('#') + 1:])
        mainArg = mainArg[:mainArg.find('#')]
    else:
        days = DEFAULT_DAYS

    return {'mainArg': mainArg, 'days': days}

def writeConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.add_section('discord')
    config.set('discord','key',' xxxxxCHANGEMExxxxx')
    with open('config.ini','w') as f:
        config.write(f)

def readConfig():
    if not os.path.exists('config.ini'):
        writeConfig()
        print('config.ini does not exist, default config.ini created')
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
            global TOKEN
            TOKEN = config.get('discord','key')
        except configparser.NoOptionError:
            print('An option is missing')

readConfig()
try:
    client.run(TOKEN)
except:
    print('Error with Token, Bot exiting.')
