# app for running queries from eve https://zkillboard.com/
from typing import Tuple

import requests
import time
import KillMail
from esipy import App
from esipy import EsiClient


class zkApp:
    ZK_API_URL = "https://zkillboard.com/api/"
    SEARCH_CATEGORIES = ("alliance", "character", "corporation", "faction", "region", "solar_system")

    ESIapp = None
    client = None

    killMails = []
    lastKillMail = 0  # store the last killmail_id as to only check for newer killmails

    myAllianceID: int = 99007415
    starTime: int = 201808170000

    def __init__(self):
        self.setupESI()

    def checkAllianceKB(self):
        response = requests.get(self.ZK_API_URL + 'allianceID/%s/startTime/%s/' % (self.myAllianceID, self.starTime))
        zkPackage = response.json()
        if zkPackage[0]['killmail_id'] > self.lastKillMail:
            self.lastKillMail = zkPackage[0]['killmail_id']
            for k in zkPackage:
                self.killMails.append(KillMail.KillMail(k))
                print('new kill mail ' + str(k['killmail_id']))
            return k
        else:
            print('no new killmails')
            return False

    def main(self):
        self.setupESI()
        print(self.getAllianceName(99007415))
        print(self.getCharacterID('kalaik utama'))
        while True:
            self.checkAllianceKB()
            self.showKillMail(71912644)
            time.sleep(10)

    def showKillMail(self, id):
        for km in self.killMails:
            if km.killmail_id == id:
                print('found the kill')

    def setupESI(self):
        print('Setup ESI App')
        self.client = EsiClient(
            retry_requests=False,  # set to retry on http 5xx error (default False)
            headers={'User-Agent': 'podSaver Notification App'},
            raw_body_only=False,
            # default False, set to True to never parse response and only return raw JSON string content.
        )
        self.ESIapp = App.create(url="https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility")

    def getAllianceName(self, id):
        getAllianceOp = self.ESIapp.op['get_alliances_alliance_id'](
            alliance_id=id,
        )
        response = self.client.request(getAllianceOp)

        return response.data.name

    def getCharacterName(self, id):
        getCharachterOp = self.ESIapp.op['get_characters_character_id'](
            character_id=id
        )
        response = self.client.request(getCharachterOp)
        try:
            return response.data.name
        except:
            return False

    # def getCharacterKillMails(self, id, startTime):
    #     print(self.ZK_API_URL + 'characterID/%s/startTime/%s/' % (id, startTime))
    #     response = requests.get(self.ZK_API_URL + 'characterID/%s/startTime/%s/' % (id, startTime))
    #     zkPackage = response.json()
    #     if len(zkPackage) > 0:
    #         characterKills = []
    #         print(zkPackage)
    #         for k in zkPackage:
    #             characterKills.append(KillMail.KillMail(k))
    #         print('Yup he killed someone')
    #         return characterKills
    #     else:
    #         print('Nope Carebear alert')
    #         return False

    # def getCorpKillMails(self, id, startTime):
    #     print(self.ZK_API_URL + 'corporationID/%s/startTime/%s/' % (id, startTime))
    #     response = requests.get(self.ZK_API_URL + 'corporationID/%s/startTime/%s/' % (id, startTime))
    #     zkPackage = response.json()
    #     if len(zkPackage) > 0:
    #         kills = []
    #         print(zkPackage)
    #         for k in zkPackage:
    #             kills.append(KillMail.KillMail(k))
    #         print('Yup they killed someone')
    #         return kills
    #     else:
    #         print('Nope Carebear alert')
    #         return False

    def getKillMails(self, id, startTime, category):
        if category not in self.SEARCH_CATEGORIES:
            return False
        if category == 'solar_system': category = 'solarSystem'

        print(self.ZK_API_URL + '%sID/%s/startTime/%s/' % (category,id, startTime))
        response = requests.get(self.ZK_API_URL + '%sID/%s/startTime/%s/' % (category,id, startTime))
        zkPackage = response.json()
        if len(zkPackage) > 0:
            kills = []
            print(zkPackage)
            for k in zkPackage:
                kills.append(KillMail.KillMail(k))
            print('Yup they killed someone')
            return kills
        else:
            print('Nope Carebear alert')
            return False

    def getID(self, query, category):
        if category not in self.SEARCH_CATEGORIES:
            return False
        getOp = self.ESIapp.op['get_search'](
            categories=category,
            search=query,
            strict=True
        )
        responce = self.client.request(getOp)
        try:
            print(responce.data)
            idArray = getattr(responce.data, category)
            return idArray[0]
        except:
            print('Error in getID method')
            return False

# testApp = ZkApp()
# testApp.main()
