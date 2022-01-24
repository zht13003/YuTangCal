import os
import sys
from typing import List
import requests
from bs4 import BeautifulSoup
import json
from player import player


def getScore(play: player, rank: int) -> None:
    T = play.T
    score = 11 - 2 * rank
    threshold = 9 - T * 2
    if rank == 1:
        if T == 0:
            score = 10
        else:
            score = 9.5 - T
    elif T != 0 and score > threshold:
        score = threshold + (score - threshold) / 2
    play.score = score


def ranking(blueTeam: List[player], redTeam: List[player], rule: str) -> List:
    redScore = blueScore = 0
    highScoreRed = highScoreBlue = 0
    if len(redTeam) + len(blueTeam) != 8:
        raise Exception('获取选手信息不足8人，请检查数据文件是否正确。也可能是因为players.txt文件内选手名称与实际名称由于选手改名导致对不上')
    for redPlayer in redTeam:
        blueTeam.append(redPlayer)
        if rule == 'acc':
            blueTeam.sort(key=lambda x: x.acc)
        else:
            blueTeam.sort(key=lambda x: x.rank)
        rankings = blueTeam.index(redPlayer)
        getScore(redPlayer, rankings + 1)
        redScore += redPlayer.score
        if rule == 'v1' and rankings < 4 and redPlayer.sc > 2 * blueTeam[rankings + 1].sc and blueTeam[rankings + 1].highscoreFlag:
            highScoreRed += 0.5
            blueTeam[rankings + 1].highscoreFlag = False
        blueTeam.pop(rankings)
    for bluePlayer in blueTeam:
        redTeam.append(bluePlayer)
        if rule == 'acc':
            redTeam.sort(key=lambda x: x.acc)
        else:
            redTeam.sort(key=lambda x: x.rank)
        rankings = redTeam.index(bluePlayer)
        getScore(bluePlayer, rankings + 1)
        blueScore += bluePlayer.score
        if rule == 'v1' and rankings < 4 and bluePlayer.sc > 2 * redTeam[rankings + 1].sc and redTeam[rankings + 1].highscoreFlag:
            highScoreBlue += 0.5
            redTeam[rankings + 1].highscoreFlag = False
        redTeam.pop(rankings)

    redScore += highScoreRed
    blueScore += highScoreBlue
    result = [redTeam, blueTeam, redScore, blueScore, highScoreRed, highScoreBlue]
    return result


def getPlayersFromFile(rule: str) -> List:
    playerList = []
    with open('players.txt', encoding='utf-8') as f:
        temp = f.readlines()
        for i in range(len(temp)):
            playerList.append(temp[i].replace('\n', '').split(',')[0])
    team = []
    for i in range(8):
        temp = []
        for j in range(4):
            temp.append(playerList[(j * 2 + i * 8): ((j + 1) * 2 + i * 8)])
        team.append(temp)
    red = []
    blue = []

    score = open('YTC.txt', encoding='utf-8').readlines()
    if score[0] == '\n':
        score.pop(0)

    redTeam = []
    blueTeam = []

    for i in range(len(score)):
        score[i] = score[i].replace("\n", '').replace(',', '')
        if score[i] == '' or score[i] == '失败':
            score.pop(i)
        if i == len(score) - 1:
            break
    for i in range(8):
        competitor = score[i * 15]
        if len(red) == 0:
            flag = 0
            for n in range(len(team)):
                for m in range(4):
                    if competitor in team[n][m]:
                        red = team[n]
                        flag = n
            team.pop(flag)
        if len(blue) == 0:
            for n in range(len(team)):
                for m in range(4):
                    if competitor in team[n][m]:
                        blue = team[n]
        sc = int(score[6 + i * 15])
        acc = 100 - float(score[4 + i * 15].replace('%', ''))
        for T in range(4):
            if len(red) != 0 and competitor in red[T]:
                redTeam.append(player(T, i, competitor, sc, acc))
            if len(blue) != 0 and competitor in blue[T]:
                blueTeam.append(player(T, i, competitor, sc, acc))

    return ranking(blueTeam, redTeam, rule)


def getPlayersFromMplink(mplink: str, rule: str, use_proxy: int) -> List:
    # 73526660
    url = "https://osu.ppy.sh/community/matches/" + mplink

    # solved by
    # https://stackoverflow.com/questions/27726815/requests-exceptions-sslerror-errno-2-no-such-file-or-directory
    if use_proxy == 1:
        soup = BeautifulSoup(requests.get(url, verify='cacert.pem').content, features="html.parser")
    else:
        proxy = {"http": "", "https": ""}
        soup = BeautifulSoup(requests.get(url, verify='cacert.pem', proxies=proxy).content, features="html.parser")

    # For test
    # soup = BeautifulSoup(open('1.html', encoding='utf-8'), features="html.parser")

    data = json.loads(soup.find(id='json-events').string)
    match = []
    for i in data['events']:
        if i['detail']['type'] == 'other':
            match.append(i)
    latest_match = match[-1]['game']
    scoring_type = latest_match['scoring_type']
    map_name = latest_match['beatmap']['beatmapset']['title_unicode']
    scores = latest_match['scores']

    playerIdToName = {}
    playerList = []

    with open("players.txt", encoding='utf-8') as f:
        playerLists = f.readlines()
        for i in playerLists:
            temp = i.replace('\n', '').split(',')
            playerIdToName[int(temp[1])] = temp[0]
            playerList.append(temp[0])

    team = []
    for i in range(8):
        temp = []
        for j in range(4):
            temp.append(playerList[(j * 2 + i * 8): ((j + 1) * 2 + i * 8)])
        team.append(temp)

    red = []
    blue = []

    redTeam = []
    blueTeam = []

    playersMessage = []
    for i in range(8):
        temp = {'name': playerIdToName[scores[i]['user_id']],
                'score': scores[i]['score'],
                'acc': scores[i]['accuracy']}
        playersMessage.append(temp)
    playersMessage.sort(key=lambda x: x['score'], reverse=True)

    for i in range(8):
        competitor = playersMessage[i]['name']
        if len(red) == 0:
            flag = 0
            for n in range(len(team)):
                for m in range(4):
                    if competitor in team[n][m]:
                        red = team[n]
                        flag = n
            team.pop(flag)
        if len(blue) == 0:
            for n in range(len(team)):
                for m in range(4):
                    if competitor in team[n][m]:
                        blue = team[n]
        sc = int(playersMessage[i]['score'])
        acc = 100 - float(playersMessage[i]['acc'])
        for T in range(4):
            if len(red) != 0 and competitor in red[T]:
                redTeam.append(player(T, i, competitor, sc, acc))
            if len(blue) != 0 and competitor in blue[T]:
                blueTeam.append(player(T, i, competitor, sc, acc))

    return ranking(blueTeam, redTeam, rule)
