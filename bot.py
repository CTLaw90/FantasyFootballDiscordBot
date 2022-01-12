#fantasy football bot

import discord
import os, sys
import requests
import random
import json


#a way for me to translate ESPN team owner into irl names
ownerName = [   '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
                '12'    ]

#i included a way to get bobby hill quotes... as our channel is a king of the hill themed channel... dont ask...

bobbyQuotes = open('bobby.txt')
bobbyQuotes = bobbyQuotes.read()
bobbyQuotes = bobbyQuotes.split('\n')

playerDataFile = open("ESPNdata.json", "r")
playerData = json.load(playerDataFile)

'''
COOKIE DATA
swid = 'INSERT SWID HERE'
espn_s2 = 'INSERT ESPN_S2 HERE'
'''

#get league data from espn as json file
def getLeague():

    url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/2021/segments/0/leagues/(league_id)?view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&view=mPositionalRatings&view=mSettings&view=mTeam&view=modular&view=mNav'

    r = requests.get(url, cookies={"swid":"", "espn_s2":""})
    d = r.json()
    return(d)

#begin client
client = discord.Client()

#if refreshing data from espn is necessary
def refresh():
    global myLeague
    myLeague = getLeague()

#on connect
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#main body, listens for messages and executes appropriate command
@client.event
async def on_message(message):
    if message.content.startswith('!commands'):
        refresh()
        await message.channel.send("I CAN:\n!matchups (!mu)\n!points (!pts)\n!standings (!std)\n!projected (!proj)\n!playoff (!play)")

    elif message.content.startswith('!quit'):
        await message.channel.send("I DONT KNOW YOU")
        sys.exit()

    elif message.content.startswith("!league"):
        refresh()
        tmp = message.content
        tmp = tmp.split()
        tmp = tmp[1:len(tmp)]
        tmp = ' '.join(tmp)
        await message.channel.send(myLeague['settings']['name'])

    elif message.content.startswith("!matchups")  or message.content.startswith("!mu"):
        refresh()
        curweek = myLeague['status']['currentMatchupPeriod']
        week = curweek
        tmpa = message.content
        tmpa = tmpa.split()
        tmpa = tmpa[1:len(tmpa)]
        for y in tmpa:
            if y.isdigit():
                if int(y) > 0 and int(y) < 17:
                    week = int(y)
                    break
            else:
                continue

        tmp = []
        curpointsH = ''
        curpointsA = ''
        for x in range(6*(week-1), 6*(week-1)+6):
            homeT = ownerName[myLeague['schedule'][x]['home']['teamId']-1] + ' - ' +myLeague['teams'][myLeague['schedule'][x]['home']['teamId']-1]['location'] + ' ' + myLeague['teams'][myLeague['schedule'][x]['home']['teamId']-1]['nickname']
            awayT = ownerName[myLeague['schedule'][x]['away']['teamId']-1] + ' - ' +myLeague['teams'][myLeague['schedule'][x]['away']['teamId']-1]['location'] + ' ' + myLeague['teams'][myLeague['schedule'][x]['away']['teamId']-1]['nickname']

            if week < curweek:
                curpointsH = myLeague['schedule'][x]['home']['totalPoints']
                curpointsA = myLeague['schedule'][x]['away']['totalPoints']
            if week == curweek:
                curpointsH = myLeague['schedule'][x]['home']['totalPointsLive']
                curpointsA = myLeague['schedule'][x]['away']['totalPointsLive']
            tmp.append('\t\t' + awayT + '\t\t' + str(round(curpointsA,2)) + '\t\tVS\t\t' + str(round(curpointsH,2)) + '\t\t' + homeT)

        tmp = '\n\n'.join(tmp)
        await message.channel.send('MATCHUPS FOR WEEK ' + str(week) + '\n\n' + tmp)

    elif message.content.startswith("!points") or message.content.startswith("!pts"):
        refresh()
        tmp = {}
        for x in myLeague['teams']:
            tmp[ownerName[x['id'] -  1] + ' - ' + x['location']+' '+x['nickname']] = x['points']
        
        tmp = (dict(sorted(tmp.items(), key=lambda item: item[1], reverse = True)))
        msg = []
        for y in tmp:
            msg.append('\t\t' + y + ' : ' + str(round(tmp[y], 2)))
        msg = 'CURRENT POINT TOTALS:\n' + '\n'.join(msg)
        await message.channel.send(msg)

    elif message.content.startswith("!standings") or message.content.startswith("!std"):
        refresh()
        tmp = {}
        div = ['EAST', 'WEST']
        for x in myLeague['teams']:
            tmp[ownerName[x['id'] -  1] + ' - ' + x['location']+' '+x['nickname']] = ''.join(div[x['divisionId']] + ' ' + str(x['record']['overall']['wins'])  + ' - ' + str(x['record']['overall']['losses'])  + ' - ' + str(x['record']['overall']['ties']))
        
        tmp = (dict(sorted(tmp.items(), key=lambda item: item[1], reverse = True)))
        msg = []
        for y in tmp:
            msg.append('\t\t' + y + '  :  ' + (tmp[y]))
        msg = 'CURRENT STANDINGS:\n' + '\n'.join(msg)
        await message.channel.send(msg)

    elif message.content.startswith("!projected") or message.content.startswith("!proj"):
        refresh()
        tmp = {}
        for x in myLeague['teams']:
            tmp[ownerName[x['id'] -  1] + ' - ' + x['location']+' '+x['nickname']] = (x['currentProjectedRank'])

        tmp = (dict(sorted(tmp.items(), key=lambda item: item[1], reverse = False)))
        msg = []
        for y in tmp:
            msg.append('\t\t' + y + '  :  ' + (str(tmp[y])))
        msg = 'CURRENT PROJECTED RANKINGS:\n' + '\n'.join(msg)
        await message.channel.send(msg)

    elif message.content.startswith("!playoff") or message.content.startswith("!play"):
        refresh()
        tmp = {}
        for x in myLeague['teams']:
            tmp[ownerName[x['id'] -  1] + ' - ' + x['location']+' '+x['nickname']] = (x['playoffSeed'])

        tmp = (dict(sorted(tmp.items(), key=lambda item: item[1], reverse = False)))
        msg = []
        for y in tmp:
            msg.append('\t\t' + y + '  :  ' + (str(tmp[y])))
        msg = 'CURRENT PLAYOFF SEEDS:\n' + '\n'.join(msg)
        await message.channel.send(msg)

    elif message.content.startswith("!dangit"):
        await message.channel.send(random.choice(bobbyQuotes))

    elif message.content.startswith("!stat"):
        await message.channel.send(str(playerData['players'][0]['id']))
client.run('discord bot id')