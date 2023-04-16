import re
import typing
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from dateutil.relativedelta import relativedelta
from tika import parser


@dataclass
class Transaction:
    data: datetime
    descricao: str
    valor: Decimal
    nbrParc: Optional[int] = None
    totParc: Optional[int] = None

    def __post_init__(self):
        self.descricao = self.descricao.strip()
        regex = r"(?P<nbrParc>\d{2})/(?P<totParc>\d{2})\s*$"
        m = re.search(regex, self.descricao)
        if m:
            self.nbrParc = m.group("nbrParc")
            self.totParc = m.group("totParc")
            self.descricao = re.sub(regex, "", self.descricao).strip()


class PdfParser:

    typeDoc = None
    venc = None
    corte = None
    totFatAnt = None
    totFat = None
    totFatProx = None
    totSldFin = None
    totLancAtuais = None
    totPgto = None
    dtPgto = None
    __raw = None
    trans = []
    prox_trans = []
    trans_iof = []

    def __init__(self, content):
        self.trans = []
        self.prox_trans = []
        self.trans_iof = []
        self.typeDoc = None
        self.venc = None
        self.corte = None
        self.totFatAnt = None
        self.totFatProx = None
        self.totFat = None
        self.totSldFin = None
        self.totLancAtuais = None
        self.totPgto = None
        self.dtPgto = None
        self.content = content
        self.__raw = parser.from_buffer(self.content)
        self.__checkProducer()
        self.__parseProducer()

    def __checkMetadata(self):
        if "metadata" not in self.__raw:
            raise RuntimeError("Metadata não existe no documento")

    def __checkProducer(self):
        self.__checkMetadata()
        if "pdf:docinfo:producer" not in self.__raw["metadata"]:
            raise RuntimeError("Producer não existe no Documento Metadata")
        match self.__raw["metadata"]["pdf:docinfo:producer"]:
            case "PDF Export":
                ...
            case __:
                raise NotImplementedError(
                    self.__raw["metadata"]["pdf:docinfo:producer"]
                )

    def info(self):
        self.__checkMetadata()
        self.__parseProducer()
        return {"meta": self.__raw["metadata"], "typeDoc": self.typeDoc}

    def OK(self):
        self.__parseProducer()
        return self.typeDoc

    def __formatTransactions(self, m):

        if isinstance(m, dict):
            trans = Transaction(m["dt"], m["descr"], self.__formatValorDecimal(m))
        else:
            trans = Transaction(
                self.__normalizeDate(m.group("dt")),
                m.group("descr"),
                self.__formatValorDecimal(m),
            )
        return trans

    def transacoes(self) -> typing.Iterable[Transaction]:

        for tran in self.trans:
            yield tran

    def parcelados(self) -> typing.Iterable[Transaction]:

        for tran in self.trans:
            if not tran.totParc:
                continue
            yield tran

    def iof(self) -> typing.Iterable[Transaction]:

        for tran in self.trans_iof:
            yield tran

    def prox_parcelados(self) -> typing.Iterable[Transaction]:

        for tran in self.prox_trans:
            if not tran.totParc:
                continue
            yield tran

    @property
    def sumTransaction(self) -> Decimal:

        sumT = Decimal("0.00")
        for tran in self.trans:
            sumT += tran.valor

        return sumT

    def __obtemVenc(self):

        if self.venc != None:
            return

        m = re.search(
            r"Vencimento:\s+(?P<dt>\d{2}/\d{2}/\d{4})\b",
            self.__raw["content"],
            re.MULTILINE,
        )
        if m:
            self.venc = self.__formatDataDatetime(m)

    def __obtemCorte(self):

        if self.corte != None:
            return

        m = re.search(
            r"Emissão:\s+(?P<dt>\d{2}/\d{2}/\d{4})\b",
            self.__raw["content"],
            re.MULTILINE,
        )
        if m:
            self.corte = self.__formatDataDatetime(m)

    def __extractValorStr(self, startStr):
        m = re.search(
            re.escape(startStr)
            + r"\s+((?P<negativo>-)\s)?(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
            self.__raw["content"],
            re.MULTILINE,
        )
        return m

    def __formatDataDatetime(self, m):
        return datetime.strptime(m.group("dt"), "%d/%m/%Y").date()

    def __normalizeDate(self, dt):
        dt += "/"
        dt += str(self.corte.year)
        newDate = datetime.strptime(dt, "%d/%m/%Y").date()
        if newDate > self.corte:
            newDate = newDate - relativedelta(years=1)
        return newDate

    def __formatValorDecimal(self, m):

        decimalVlr = None
        if isinstance(m, dict):
            vlr = m["vlr"].replace(".", "").replace(",", ".")
            decimalVlr = Decimal(vlr)
            if m["negativo"]:
                decimalVlr *= -1
        else:
            vlr = m.group("vlr").replace(".", "").replace(",", ".")
            decimalVlr = Decimal(vlr)
            if m.group("negativo"):
                decimalVlr *= -1
        return decimalVlr

    def __obtemTotFatAnt(self):

        if self.totFatAnt != None:
            return
        m = self.__extractValorStr("Total da fatura anterior")
        if m:
            self.totFatAnt = self.__formatValorDecimal(m)

    def __obtemTotFatProx(self):

        if self.totFatProx != None:
            return
        m = self.__extractValorStr("Próxima fatura")
        if m:
            self.totFatProx = self.__formatValorDecimal(m)

    def __obtemTotFat(self):

        if self.totFat != None:
            return
        m = self.__extractValorStr("Total desta fatura")
        if m:
            self.totFat = self.__formatValorDecimal(m)

    def __obtemSldFin(self):

        if self.totSldFin != None:
            return
        m = self.__extractValorStr("Saldo financiado")
        if m:
            self.totSldFin = self.__formatValorDecimal(m)

    def __obtemLancAtuais(self):

        if self.totLancAtuais != None:
            return
        m = self.__extractValorStr("Lançamentos atuais")
        if m:
            self.totLancAtuais = self.__formatValorDecimal(m)

    def __obtemPgto(self):

        if self.totPgto != None:
            return

        m = re.search(
            r"Pagamento efetuado em\s+(?P<dt>\d{2}/\d{2}/\d{4})\s+((?P<negativo>-)\s)?(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
            self.__raw["content"],
            re.MULTILINE,
        )
        if m:
            if m:
                self.totPgto = self.__formatValorDecimal(m)
            self.dtPgto = self.__formatDataDatetime(m)

    def __checkFatItau(self):

        if self.totSldFin != self.totFatAnt + self.totPgto:
            raise RuntimeError(
                "Saldo Financiado não bate",
                self.totFatAnt - self.totPgto,
                self.totSldFin,
            )

        if self.totFat != self.totSldFin + self.totLancAtuais:
            raise RuntimeError(
                "Saldo Atual não bate",
                self.totSldFin + self.totLancAtuais,
                self.totFat,
            )

        if self.totLancAtuais != self.sumTransaction:
            raise RuntimeError(
                "Lançamentos não bate com Total de Transações",
                self.totLancAtuais,
                self.sumTransaction,
                self.sumTransaction - self.totLancAtuais,
            )

        if (
            self.venc != None
            and self.corte != None
            and self.totFatAnt != None
            and self.totFat != None
            and self.totSldFin != None
            and self.totLancAtuais != None
            and self.totPgto != None
            and self.dtPgto != None
        ):
            self.typeDoc = "FatItau"

    def __obtemTrans(self):

        if len(self.trans) > 0:
            return
        trans = []
        # Elimina Lixos Iniciais
        content = re.sub(r"\(\d{2}/\d{2} a \d{2}/\d{2}\)", "", self.__raw["content"])
        # Obtem transacoes
        regex = r"(?P<dt>\d{2}/\d{2})\s+(?P<descr>\w.*?)\s+((?P<negativo>-)\s)?(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2})"

        def subst(g):
            trans.append(self.__formatTransactions(g))
            return ""

        content = re.sub(regex, subst, content, 0, re.MULTILINE)
        # for g in re.finditer(regex,content,re.MULTILINE):
        #     trans.append(self.__formatTransactions(g))

        # Monta Dicionario com Parcelados
        dictTran = {}
        for tran in trans:
            if not tran.totParc:
                continue
            uK = (
                str(tran.data)
                + str(tran.descricao)
                + str(tran.valor)
                + str(tran.totParc)
            )
            if uK in dictTran:
                dictTran[uK].append(tran.nbrParc)
            else:
                dictTran[uK] = [tran.nbrParc]

        # Classifica parcelas para parcelados
        newDictTrans = {}
        for item, value in dictTran.items():
            newDictTrans[item] = sorted(value)
        dictTran = newDictTrans

        # elimina quem tem apenas uma parcela
        newDictTrans = {}
        for item, value in dictTran.items():
            if len(value) == 1:
                continue
            value.pop(0)
            newDictTrans[item] = value
        dictTran = newDictTrans
        for tran in trans:
            if not tran.totParc:
                self.trans.append(tran)
                continue
            uK = (
                str(tran.data)
                + str(tran.descricao)
                + str(tran.valor)
                + str(tran.totParc)
            )
            if uK not in dictTran:
                self.trans.append(tran)
                continue
            if tran.nbrParc in dictTran[uK]:
                self.prox_trans.append(tran)
            else:
                self.trans.append(tran)

    def __obtemTransIOF(self):
        if len(self.trans_iof) > 0:
            return
        regex = r"(?P<descr>Repasse de IOF em R\$)\s+((?P<negativo>-)\s)?(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)"
        for g in re.finditer(regex, self.__raw["content"], re.MULTILINE):
            dictTrans = g.groupdict()
            dictTrans["dt"] = self.corte
            self.trans.append(self.__formatTransactions(dictTrans))
            self.trans_iof.append(self.__formatTransactions(dictTrans))

    def __parseProducer(self):

        self.__obtemVenc()
        self.__obtemCorte()
        self.__obtemTotFatAnt()
        self.__obtemSldFin()
        self.__obtemLancAtuais()
        self.__obtemTotFat()
        self.__obtemPgto()
        self.__obtemTotFatProx()
        self.__obtemTrans()
        self.__obtemTransIOF()
        self.__checkFatItau()
