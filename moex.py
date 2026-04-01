import requests
from typing import Dict, List, Optional, TypedDict
from datetime import datetime
import json
import pandas as pd
pd.set_option('display.max_columns', None)


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

        self.sorted_shares, self.sorted_futures = self.sortByGeneralNames(
            generalSharesNames=self.generalSharesNames,
            shares=self.shares,
            futures=self.futures
            )

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
                            fullName=futuresSecuritiesData[3],
                            lastTradeDate=futuresSecuritiesData[7],
                            lastDelDate=futuresSecuritiesData[8],
                            assetcode=futuresSecuritiesData[11],
                            initialMargin=futuresSecuritiesData[14],
                            lotVolume=futuresSecuritiesData[13],
                            stepPrice=futuresSecuritiesData[17],
                            sectype=futuresSecuritiesData[9],

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
                                fullName=futuresSecuritiesData[3],
                                lastTradeDate=futuresSecuritiesData[7],
                                lastDelDate=futuresSecuritiesData[8],
                                assetcode=futuresSecuritiesData[11],
                                initialMargin=futuresSecuritiesData[14],
                                lotVolume=futuresSecuritiesData[13],
                                stepPrice=futuresSecuritiesData[17],
                                sectype=futuresSecuritiesData[9],

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
                            fullName=futuresSecuritiesData[3],
                            lastTradeDate=futuresSecuritiesData[7],
                            lastDelDate=futuresSecuritiesData[8],
                            assetcode=futuresSecuritiesData[11],
                            initialMargin=futuresSecuritiesData[14],
                            lotVolume=futuresSecuritiesData[13],
                            stepPrice=futuresSecuritiesData[17],
                            sectype=futuresSecuritiesData[9],

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

    def calculate_contango(
        self,
        commission_share: float = 0.0006,   # комиссия на покупку акции (например 0.06%)
        commission_future: float = 0.00015,   # комиссия на продажу фьючерса
        sort_by_annual_percentage: bool = True
    ):
        contangos = []

        for share, futures in zip(self.sorted_shares, self.sorted_futures):
            share_price_last = share.get("priceLast")
            share_name = share.get("secid")

            for future in futures:
                lot_volume = future.get("lotVolume")
                future_price = future.get("priceLast")
                initialMargin = future.get("initialMargin")

                if not share_price_last or not future_price or not lot_volume:
                    continue

                spot_price = share_price_last * lot_volume

                # Учет комиссий
                spot_price_with_commission = spot_price * (1 + commission_share)
                future_price_with_commission = future_price * (1 - commission_future)

                # Контанго (обычное)
                if future_price_with_commission > spot_price_with_commission:
                    contango = (
                        (future_price_with_commission - spot_price_with_commission)
                        / spot_price_with_commission
                    ) * 100

                    # --- ГОДОВОЕ КОНТАНГО ---
                    try:
                        expiry = datetime.strptime(future.get("lastTradeDate"), "%Y-%m-%d")

                        now = datetime.now()
                        days_to_expiry = (expiry - now).days

                        if days_to_expiry <= 0:
                            continue

                        contango_annual = contango * (365 / days_to_expiry)

                    except Exception:
                        contango_annual = None

                    #Начальные траты
                    initial_margin = 2.1 * initialMargin
                    initial_expenses = 1.1 * initial_margin + spot_price_with_commission

                    contangos.append({
                        "share": share_name,
                        "future": future.get("shortName"),
                        "UpdateTime": future.get("updateTime"),
                        "contango_percent": round(contango, 2),
                        "contango_annual_percent": round(contango_annual, 2) if contango_annual else None,
                        "days_to_expiry": days_to_expiry,
                        "expiry": future.get("lastTradeDate"),
                        "initial_margin": initial_margin,
                        "initial_expenses": initial_expenses
                    })

                sort_by = "contango_annual_percent" if sort_by_annual_percentage else "contango_percent"

        return sorted(contangos, key=lambda x: -x[sort_by])


    def ContangoDataFrame(
            self,
            commission_share: float = 0.0006,  # комиссия на покупку акции (например 0.06%)
            commission_future: float = 0.00015,  # комиссия на продажу фьючерса
            sort_by_annual_percentage: bool = True,
            nums: int = 10
    ):
        return pd.DataFrame(self.calculate_contango(commission_share, commission_future, sort_by_annual_percentage))[:nums]

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
    initialMargin: float #гарантийное обеспечение
    lotVolume: float #кол-во базового актива в контракте
    stepPrice: float #стоймость пункта цены
    sectype: str #тип контракта

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

print(sharesAndFuturesBlock.getContangoSet(sort_by_annual_percentage=False))
