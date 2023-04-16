import re
import tempfile
from datetime import datetime
from decimal import Decimal

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from ofxparse import OfxParser

from app.parsers.pdfParser import PdfParser

APP_KEY = "pj28mos1i05rp2d"
APP_SECRET = "h1u0k3ygnvoum7p"
TOKEN = "sl.BWZ0larFIDCisMg2tuWI0z1Db8Utoef0awU25BvfX5jSBqJcdkIMArJUgpAmxSlEzBOiVoFg7rw_c19VYy4_18prYpd8cFVmBGPmcRKsHPAnFm789NKgDA_Q_ytb_IA8BPWgF84"
REFRESHTOKEN = "uM5qB7tOCnYAAAAAAAAAAdOb61tg5k7Zi4rI-1dq1v178oSOv4FR3ocpje9DbusZ"
TIMEOUT = "2023-01-06 23:23:31.002587"
TIMEOUT = datetime.strptime(TIMEOUT, "%Y-%m-%d %H:%M:%S.%f")


def reconnectDropbox():
    with dropbox.Dropbox(
        oauth2_access_token=TOKEN,
        oauth2_refresh_token=REFRESHTOKEN,
        oauth2_access_token_expiration=TIMEOUT,
        app_secret=APP_SECRET,
        app_key=APP_KEY,
    ) as dbx:
        dbx.users_get_current_account()
        print(dbx.check_and_refresh_access_token())
        print(dbx._oauth2_access_token_expiration)
        print(dbx._oauth2_access_token)
        print(dbx._oauth2_refresh_token)
        print("Successfully set up client!")
    return dbx


def getDropboxToken():

    auth_flow = DropboxOAuth2FlowNoRedirect(
        APP_KEY, APP_SECRET, token_access_type="offline"
    )

    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print('2. Click "Allow" (you might have to log in first).')
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print("Error: %s" % (e,))
        exit(1)

    print(oauth_result.access_token)
    print("refresh", oauth_result.refresh_token)
    print("timeout", oauth_result.expires_at)
    return
    # with dropbox.Dropbox(oauth2_access_token=oauth_result.access_token) as dbx:
    #     return dbx

    # return dropbox.Dropbox(
    #     "ZiVe7BWvfOcAAAAAAACL1Ad0pxPzFgUcj97FNC4XiVs"
    # )


def dropbox_connect():

    # with dropbox.Dropbox(oauth2_refresh_token=TOKEN, app_key=APP_KEY) as dbx:
    #     return dbx
    dbx = dropbox.Dropbox(TOKEN)
    # print('oauth',dbx._oauth2_access_token)
    # print('refresh',dbx._oauth2_refresh_token)
    # print('timeout',dbx._oauth2_access_token_expiration)

    return dbx


def dropbox_download_file(dropbox_file_path):
    """Download a file from Dropbox to the local machine."""

    dbx = dropbox_connect()

    metadata, result = dbx.files_download(path=dropbox_file_path)
    return metadata, result


def obtemVenc(dictFat, content):

    m = re.search(r"Vencimento:\s+(?P<dt>\d{2}/\d{2}/\d{4})\b", content, re.MULTILINE)
    if m:
        dictFat["venc"] = datetime.strptime(m.group("dt"), "%d/%m/%Y").date()


def obtemCorte(dictFat, content):

    m = re.search(r"Emissão:\s+(?P<dt>\d{2}/\d{2}/\d{4})\b", content, re.MULTILINE)
    if m:
        dictFat["corte"] = datetime.strptime(m.group("dt"), "%d/%m/%Y").date()


def obtemTotFatAnt(dictFat, content):

    m = re.search(
        r"Total da fatura anterior\s+(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
        content,
        re.MULTILINE,
    )
    if m:
        vlr = m.group("vlr").replace(".", "").replace(",", ".")
        dictFat["valFatAnt"] = Decimal(vlr)


def obtemTotFat(dictFat, content):

    m = re.search(
        r"Total desta fatura\s+(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
        content,
        re.MULTILINE,
    )
    if m:
        vlr = m.group("vlr").replace(".", "").replace(",", ".")
        dictFat["valFat"] = Decimal(vlr)


def obtemSldFin(dictFat, content):

    m = re.search(
        r"Saldo financiado\s+(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
        content,
        re.MULTILINE,
    )
    if m:
        vlr = m.group("vlr").replace(".", "").replace(",", ".")
        dictFat["valSldFin"] = Decimal(vlr)


def obtemLancAtuais(dictFat, content):

    m = re.search(
        r"Lançamentos atuais\s+(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
        content,
        re.MULTILINE,
    )
    if m:
        vlr = m.group("vlr").replace(".", "").replace(",", ".")
        dictFat["valLancAtuais"] = Decimal(vlr)


def obtemPgto(dictFat, content):

    m = re.search(
        r"Pagamento efetuado em\s+(?P<dt>\d{2}/\d{2}/\d{4})\s+((?P<negativo>-)\s+)?(?P<vlr>\d\d{0,2}(?:\.\d{3})*,\d{2}+)",
        content,
        re.MULTILINE,
    )
    if m:
        vlr = m.group("vlr").replace(".", "").replace(",", ".")
        dictFat["pgtoAnt"] = Decimal(vlr)
        if m.group("negativo"):
            dictFat["pgtoAnt"] *= -1
        dictFat["dtPgto"] = datetime.strptime(m.group("dt"), "%d/%m/%Y").date()


def validaTotaisIniciais(dictFat):

    if dictFat["valSldFin"] != dictFat["valFatAnt"] + dictFat["pgtoAnt"]:
        raise RuntimeError(
            "Saldo Financiado não bate",
            dictFat["valFatAnt"] - dictFat["pgtoAnt"],
            dictFat["valSldFin"],
        )

    if dictFat["valFat"] != dictFat["valSldFin"] + dictFat["valLancAtuais"]:
        raise RuntimeError(
            "Saldo Atual não bate",
            dictFat["valSldFin"] + dictFat["valLancAtuais"],
            dictFat["valFat"],
        )


def extraiTotais(dictFat, content):

    obtemVenc(dictFat, content)
    obtemCorte(dictFat, content)
    obtemTotFatAnt(dictFat, content)
    obtemSldFin(dictFat, content)
    obtemLancAtuais(dictFat, content)
    obtemTotFat(dictFat, content)
    obtemPgto(dictFat, content)
    validaTotaisIniciais(dictFat)


def parseCartaoItau(content):

    dictFat = {}
    extraiTotais(dictFat, content)

    print(content)

    return dictFat


def readPDF(content):

    pdf = PdfParser(content)
    if pdf.OK():
        print(pdf.venc, pdf.sumTransaction, pdf.totLancAtuais)


def readOFX(content):

    tp = tempfile.TemporaryFile()
    tp.write(content)
    ofx = OfxParser.parse(tp)
    tp.close()

    # account.routing_number    # The bank routing number
    # account.branch_id         # Transit ID / branch number
    # account.type              # An AccountType object
    # account.statement         # A Statement object
    # account.institution       # An Institution object

    print(
        ofx.account.institution,
        ofx.account.account_type,
        ofx.account.statement.start_date,
        ofx.account.statement.end_date,
        ofx.account.statement.balance,
    )
    print(ofx.account.account_id, ofx.account.branch_id)
    # for transaction in ofx.account.statement.transactions:
    #     print(  transaction.payee,
    #             transaction.type,
    #             transaction.date,
    #             transaction.user_date,
    #             transaction.amount,
    #             transaction.id,
    #             transaction.memo,
    #             transaction.sic,
    #             transaction.mcc,
    #             transaction.checknum
    #         )


def processaFiles(entry):

    match entry.name.split(".")[-1].lower():
        case "pdf":
            _, result = dropbox_download_file(entry.path_display)
            readPDF(result.content)
        case "ofx":
            _, result = dropbox_download_file(entry.path_display)
            readOFX(result.content)
        case __:
            raise NotImplementedError("Load", entry.name.split(".")[-1])


# getDropboxToken()
dbx = reconnectDropbox()

# dbx = dropbox_connect()
for entry in dbx.files_list_folder("/666-Finance/2022").entries:
    if entry.name.split(".")[-1].lower() == "ofx":
        # if  entry.name == "Extrato Conta Corrente-301220222257.ofx":
        try:
            processaFiles(entry)
        except Exception as e:
            print(entry.name)
            print(e)
