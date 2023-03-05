import pymongo
import time
import pprint


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["1xbet_2"]

# tables
# {time, break_point, attemps, bet, won, amount}
transactions = mydb["transactions"]
# {time, started, balance}
balance = mydb["balance"]
# crashes
crashes = mydb["crashes"]


# ======================================================================
# ======================== TRANSACTIONS ================================
# ======================================================================
def addTransaction(trans):
    val = {
        'time'          : round(time.time() * 1000),
        'break_point'   : trans['break_point'],
        'attemps'       : trans['attemps'],
        'bet'           : trans['bet'],
        'xbet_wins'     : trans['xbet_wins'],
        'won'           : trans['won'],
        'crashed_at'    : trans['crashed_at'],
        'amount'        : trans['amount'],
        'balance'       : trans['balance'],
        'confidence'    : trans['confidence']
    }

    transactions.insert_one(val)
    
    return val

def getTransactionsByTime(time, oprerator = '<'):
    opr = ""
    if(oprerator == '<'):
        opr = '$lt'
    else:
        opr = '$gt'

    return transactions.find({"time": {opr: time}})

def getTransactionsByBet(bet, oprerator = ""):
    opr = ""
    if(oprerator == '<'):
        opr = '$lt'
    elif(oprerator == '>'):
        opr = '$gt'

    if(opr == "" or opr == "="):
        return transactions.find({"bet": bet})
    else:
        return transactions.find({"bet": {opr: bet}})



def getWonOrLostTransactions(won = True):
    return transactions.find({"won": won})

# ======================================================================
# ================================ BANK ================================
# ======================================================================

def getBalance():
    return balance.find().sort('time', -1)[0]

def initBalance(amount = 1000):
    val = {
        'time'          : round(time.time() * 1000),
        'started'       : amount,
        'balance'        : amount
    }

    balance.insert_one(val)


def addToBalance(amount):
    blnc = getBalance()
    
    id = blnc['_id']
    blnc['balance'] = float(blnc['balance']) + float(amount)

    balance.update_one({'_id': id}, {"$set": blnc})
    
    return blnc

def substractFromBalance(amount):
    blnc = getBalance()
    
    id = blnc['_id']
    blnc['balance'] = float(blnc['balance']) - float(amount)
    
    balance.update_one({'_id': id}, {"$set": blnc})

    return blnc


# ======================================================================
# ================================ CRASHES =============================
# ======================================================================
def storeCrashes(crash):
    val = {
        'time'          : round(time.time() * 1000),
        'crashed_at'    : crash['crashed_at'],
        'total_bets'    : crash['total_bets'],
        'total_wins'    : crash['total_wins'],
        'xbet_wins'     : crash['xbet_wins'],
        'crashed_at'    : crash['crashed_at']
    }

    crashes.insert_one(val)

# print("=================== DEBUGGUING ===================")

# print("\n\n\n")
# print("=================== BALANCE ===================")
# pprint.pprint(getBalance())
# print("\n\n\n")

# print("\n\n\n")
# print("=================== BANK ===================")
# pprint.pprint(getBalance()['balance'])
# print("\n\n\n")


# print("\n\n\n")
# print("=================== ADD TO BALANCE ===================")
# pprint.pprint(addToBalance(20))
# print("\n\n\n")

# print("\n\n\n")
# print("=================== BALANCE ===================")
# pprint.pprint(getBalance())
# print("\n\n\n")


# print("\n\n\n")
# print("=================== REMOVE FROM BALANCE ===================")
# pprint.pprint(substractFromBalance(200))
# print("\n\n\n")


# print("\n\n\n")
# print("=================== ADD TRANSACTION ===================")
# addTransaction({
#                 'break_point'   : 4,
#                 'attemps'       : 4,
#                 'bet'           : 4,
#                 'won'           : 1,
#                 'amount'        : 4
#             })
# print("\n\n\n")
