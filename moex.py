import requests
from typing import Dict, List, Optional, TypedDict
import json


class SharesAndFutures():
    sharesURL = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
    futuresURL = "https://iss.moex.com/iss/engines/futures/markets/forts/securities.json?iss.meta=off&iss.only=securities,marketdata"

    def __init__(self):
        self.sharesRequest = requests.get(self.sharesURL, timeout=30)
        self.futuresRequest = requests.get(self.futuresURL)

        self.sharesRequest.raise_for_status()
        self.futuresRequest.raise_for_status()

        self.sharesData = self.sharesRequest.json()
        self.futuresData = self.futuresRequest.json()

        self.sharesShortNames = self.getSharesShortNames()
        self.futuresSharesShortNames = self.getFuturesSharesNames()
        self.generalSharesNames = set(self.sharesShortNames) & set(self.futuresSharesShortNames)

        self.shares = self.getShares()
        self.futures = self.getFutures()

        self.sorted_shares, self.sorted_futures = self.sortByGeneralNames(generalSharesNames=self.generalSharesNames,
                                                                          shares=self.shares, futures=self.futures)

    def getShares(self) -> List[Share]:

        shares: List[Share] = []

        for shareMarketData in self.sharesData["marketdata"]["data"]:
            shares.append(
                Share(
                    secid=shareMarketData[0],
                    priceOpen=shareMarketData[9],
                    priceLow=shareMarketData[10],
                    priceHigh=shareMarketData[11],
                    priceLast=shareMarketData[12],
                    requestDateTime=shareMarketData[47],
                    updateTime=shareMarketData[51]
                )
            )

        return shares

    def getSharesShortNames(self):

        sharesShortNames: List[str] = []

        for shareMarketData in self.sharesData["marketdata"]["data"]:
            sharesShortNames.append(shareMarketData[0])

        return sharesShortNames

    def getFuturesSharesNames(self):

        futuresSharesNames: List[str] = []

        for futuresSharesName in self.futuresData["securities"]["data"]:
            futuresSharesNames.append(futuresSharesName[11])

        return futuresSharesNames

    def getFutures(self) -> List[List[Futures]]:

        futures: List[List[Futures]] = []

        for futuresSecuritiesData, futuresMarketData in zip(self.futuresData["securities"]["data"],
                                                            self.futuresData["marketdata"]["data"]):
            if futures:
                if futuresSecuritiesData[11] == futures[-1][0]["assetcode"]:
                    futures[-1].append(
                        Futures(
                            seсid=futuresSecuritiesData[0],
                            shortName=futuresSecuritiesData[2],
                            fullName=futuresSecuritiesData[4],
                            lastTradeDate=futuresSecuritiesData[7],
                            lastDelDate=futuresSecuritiesData[8],
                            assetcode=futuresSecuritiesData[11],

                            priceOpen=futuresMarketData[5],
                            priceHigh=futuresMarketData[6],
                            priceLow=futuresMarketData[7],
                            priceLast=futuresMarketData[8],
                            requestDateTime=futuresMarketData[29],  # sysTime
                            updateTime=futuresMarketData[18]
                        )
                    )
                else:
                    futures.append(
                        [
                            Futures(
                                seсid=futuresSecuritiesData[0],
                                shortName=futuresSecuritiesData[2],
                                fullName=futuresSecuritiesData[4],
                                lastTradeDate=futuresSecuritiesData[7],
                                lastDelDate=futuresSecuritiesData[8],
                                assetcode=futuresSecuritiesData[11],

                                priceOpen=futuresMarketData[5],
                                priceHigh=futuresMarketData[6],
                                priceLow=futuresMarketData[7],
                                priceLast=futuresMarketData[8],
                                requestDateTime=futuresMarketData[29],  # sysTime
                                updateTime=futuresMarketData[18]
                            )
                        ]
                    )

            else:
                futures.append(
                    [
                        Futures(
                            seсid=futuresSecuritiesData[0],
                            shortName=futuresSecuritiesData[2],
                            fullName=futuresSecuritiesData[4],
                            lastTradeDate=futuresSecuritiesData[7],
                            lastDelDate=futuresSecuritiesData[8],
                            assetcode=futuresSecuritiesData[11],

                            priceOpen=futuresMarketData[5],
                            priceHigh=futuresMarketData[6],
                            priceLow=futuresMarketData[7],
                            priceLast=futuresMarketData[8],
                            requestDateTime=futuresMarketData[29],  # sysTime
                            updateTime=futuresMarketData[18]
                        )
                    ]
                )

        return futures

    def sortByGeneralNames(self, generalSharesNames, shares, futures):

        filtred_shares: List[Share] = []
        filtred_futures: List[List[Futures]] = []

        for share in shares:
            if share["secid"] in generalSharesNames:
                filtred_shares.append(share)

        for block_of_futures in futures:
            if block_of_futures[0]["assetcode"] in generalSharesNames:
                filtred_futures.append(block_of_futures)

        sorted_shares = sorted(
            filtred_shares,
            key=lambda x: x['secid']  # сортируем акции по secid (алфавитно)
        )

        sorted_futures = sorted(
            filtred_futures,
            key=lambda x: x[0]['assetcode']  # сортируем блоки фьючерсов по assetcode
        )

        return sorted_shares, sorted_futures

    def printSharesAndFuturesSet(self):  # Выводит пару Акция - [фьюч1, фьюч2, фьюч3 и т.д если есть больше]
        for shares, futures in zip(self.sorted_shares, self.sorted_futures):
            print(shares, futures, "\n")


class Share(TypedDict):
    secid: str  # код Акции
    priceOpen: float  # Цена Откр
    priceLow: float  # Цена наименьш
    priceHigh: float  # Цена наибольш
    priceLast: float  # Цена последняя
    requestDateTime: str  # ДатаВремя Запроса
    updateTime: str  # время актуальности цен


class Futures(TypedDict):
    seсid: str  # Код фьюча
    shortName: str  # Имя фьюча
    fullName: str  # Имя фьюча полное
    lastTradeDate: str  # Последний день торгов
    lastDelDate: str  # Последний день исполнения (дата экспирации)
    assetcode: str  # код Акции на которую фьюч

    priceOpen: float  # Цена Откр
    priceLow: float  # Цена наименьш
    priceHigh: float  # Цена наибольш
    priceLast: float  # Цена последняя
    requestDateTime: str  # ДатаВремя Запроса
    updateTime: str  # время актуальности цен



sharesAndFuturesBlock = SharesAndFutures()
"""
Класс SharesAndFutures имеет два нужных тебе аттрибута
sorted_shares: [Акция1, Акция2, Акция3...] и 
sorted_futures:[[Фьючерс11, Фьючерс12, Фьючерс13...], [Фьючерс21, Фьючерс22, Фьючерс23...], [Фьючерс31..., Фьючерс32..., Фьючерс33]]
Все они отсортированы в алфавитном порядке, акции по коду (напр OZON), а списки из фьючерсов одной акции по коду соотвествующей акции.

Ещё есть метод .printSharesAndFuturesSet() он выводит пару [Акция - [фьюч1, фьюч2, фьюч3 и т.д если есть больше] + Enter] итеративно.

"""
sharesAndFuturesBlock.printSharesAndFuturesSet()
