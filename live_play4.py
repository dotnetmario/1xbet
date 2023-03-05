# Heroku - Heroku is a cloud-based platform that supports several programming languages, including Python. You can sign up for a free account with just your email address and get started quickly.
# PythonAnywhere - PythonAnywhere is a Python-specific hosting site that offers free accounts with limited resources. You can sign up with just your email address and start using their web-based Python console and file editor.
# OpenShift - OpenShift is a cloud-based platform that supports Python and other programming languages. You can sign up for a free account with just your email address and get started quickly.
# Google Colab - Google Colab is a free cloud-based Jupyter notebook platform that supports Python. You can sign up with your Google account and start using it right away.
# Keep in mind that free hosting sites may have limitations in terms of resources and support. If you need more resources or features, you may need to consider a paid hosting plan.

import websocket
import json
import pprint
import dblogic


# init balance
dblogic.initBalance(1000)


def on_message(ws, message):
    if message=='{"type":6}\x1e':
        # print("innn")
        ws.send('{"arguments":["00000000-0000-0000-0000-000000000000",0,99,"en",30,71],"invocationId":"0","target":"RegInHub2","type":1}')

    new_message=message.replace("\u001e",'')
    new_messages=json.loads(new_message)
    
    play(new_messages)

def on_error(ws, error):
    # print("\n\n")
    # print("================================== ERROR ==================================")
    # print(error)
    # print("\n\n")
    return 1
    

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    # print("Opened connection")
    ws.send('{"protocol":"json","version":1})\x1e')

# =========================================================
# =========================================================
# make memoire that holda the last bets, 
# check for the number of wining bets out of the last 100, 50 and 20 bets
# fix the gap between the reset point for xbet_wins and entry points 
# make entry points dynamique ex: [breakpoint: 2,entry point]

betted = 0
betnext = 0
break_point = 3
max_attemps = 5
entry_point = 0


mem_last_crashes = []

current_bet = {
    'bet': 3,
    'attemps': 0
}

current_game = {
    'total_bets': 0,
    'total_wins': 0,
    'xbet_wins': 0,
    'crashed_at': 0
}

def memLastCrashes(last = 20, mem = -1):
    global mem_last_crashes

    if(mem != -1):
        mem_last_crashes.append(mem)
        
    if(len(mem_last_crashes) > 100):
        # mem_last_crashes = mem_last_crashes[(len(mem_last_crashes) - 100):]
        mem_last_crashes = mem_last_crashes[-100:]

    return mem_last_crashes[-last:]

def checkMemAvg(last = 20, of = 2):
    last_n_crashes = memLastCrashes(last)

    if(len(last_n_crashes) < last):
        return 0

    len_ = len([n for n in last_n_crashes if n >= of])
    
    if(len_ <= 0):
        return 0
    
    return len(last_n_crashes) / len_

def checkMemOccurence(last = 20, of = 2, above = False):
    last_n_crashes = memLastCrashes(last)

    if(len(last_n_crashes) < last):
        return 0

    if(above):
        len_ = len([n for n in last_n_crashes if int(n) >= of])
    else:
        len_ = len([n for n in last_n_crashes if int(n) == of])
    
    return len_

def checkBetConfidence(of = 2):
    last_20 = checkMemAvg(20, of)
    last_50 = checkMemAvg(50, of)
    last_100 = checkMemAvg(100, of)
    total_avg = (last_20 + last_50 + last_100) / 3

    return {
        'last_20': last_20,
        'last_50': last_50,
        'last_100': last_100,
        'total_avg': total_avg,
    }


def resetXbetWins():
    global current_game
    current_game['xbet_wins'] = 0

def in_bet(val = -1):
    global betted
    if(val != -1):
        betted = val
    
    return betted

def bet_next(val = -1):
    global betnext
    if(val != -1):
        betnext = val
    
    return betnext

def breakpoint_(val = -1):
    global break_point
    if(val != -1):
        break_point = val
    return break_point

def maxattemps(val = -1):
    global max_attemps
    if(val != -1):
        max_attemps = val
    return max_attemps

def entrypoint(val = -1):
    global entry_point
    if(val != -1):
        entry_point = val
    return entry_point

def currentgame(key = '', val = -1):
    global current_game
    if(key != ''):
        if(val != -1):
            current_game[key] = val
        return float(current_game[key])
    return current_game

def currentbet(key = '', val = -1):
    global current_bet
    if(key != ''):
        if(val != -1):
            current_bet[key] = val
        return float(current_bet[key])
    return current_bet

def balance(key = ''):
    if(key != ''):
        return float(dblogic.getBalance()[key])
    return dblogic.getBalance()

def log(key = '', val = -1):
    if(key != ''):
        # print("========================= {} =========================".format(key))
        # return key
        if(val != -1):
            # pprint.pprint(val)
            return val
            
        


def play(message):
    
    if(not message['target']):
        return
    
    # reset xbet_wins
    if(currentgame('xbet_wins') > 1000000):
        currentgame('xbet_wins', 0)
        
    
    target = message['target']
    # print("heeeeererrererwr")
    # exit()
    
    # sts : 4 => game ended, 3 => game in progress, 2 => betting phase, 1 => waiting phase
    # sts = message['arguments'][0]['sts']
    
    # waiting phase
    if(target == "OnStageChange" and message['arguments'][0]['sts'] == 1):
        placeBet()

        log("NEW GAME STARTING SOON !!!!")
        log("STATS", {
            "1, 2, 3 IN 20"     : str(checkMemOccurence(20, 1, True))+" / "+str(checkMemOccurence(20, 2, True))+" / "+str(checkMemOccurence(20, 3, True)),
            "1, 2, 3 IN 50"     : str(checkMemOccurence(50, 1, True))+" / "+str(checkMemOccurence(50, 2, True))+" / "+str(checkMemOccurence(50, 3, True)),
            "1, 2, 3 IN 100"    : str(checkMemOccurence(100, 1, True))+" / "+str(checkMemOccurence(100, 2, True))+" / "+str(checkMemOccurence(100, 3, True)),
        })
        log("ALL CRASHES", {
            "COUNT"     : len(memLastCrashes(100)),
            "CRASHES"   : memLastCrashes(10)
        })
        log("CURRENT GAMES", currentgame())


    # betting phase
    if(target == "OnStageChange" and message['arguments'][0]['sts'] == 2):
        log("BETTING PHASE !!!!")
        # current_game['total_bets'] = message['arguments'][0]['tb']
        currentgame(
            'total_bets',
            float(message['arguments'][0]['tb']) / 8.0
        )


    # plane took off
    if(target == 'OnStageChange' and message['arguments'][0]['sts'] == 3):
        log("WATCH, THE PLANE TOOK OFF !!!!")
        # current_game['total_bets'] = float(message['arguments'][0]['tb']) / 7.9596
        # current_game['total_wins'] = float(message['arguments'][0]['tw']) / 7.9596
        currentgame(
            'total_bets',
            float(message['arguments'][0]['tb']) / 8.0
        )

        currentgame(
            'total_wins',
            float(message['arguments'][0]['tw']) / 8.0
        )

    # plane took off
    if(target == 'OnStageChange' and message['arguments'][0]['sts'] == 4):
        # log("WATCH, THE PLANE TOOK OFF !!!!")
        # current_game['total_bets'] = float(message['arguments'][0]['tb']) / 7.9596
        # current_game['total_wins'] = float(message['arguments'][0]['tw']) / 7.9596
        currentgame(
            'total_bets',
            float(message['arguments'][0]['tb']) / 8.0
        )
        
        currentgame(
            'total_wins',
            float(message['arguments'][0]['tw']) / 8.0
        )

    # games ended
    if(target == 'OnCoeffChange' and message['arguments'][0]['ic'] == True):
        log("PLANE EXPLODED !!!!")
        currentgame(
            'xbet_wins',
            currentgame('xbet_wins') + (currentgame('total_bets') - currentgame('total_wins'))
        )
        currentgame(
            'crashed_at',
            message['arguments'][0]['cf']
        )
        
        memLastCrashes(100, float(message['arguments'][0]['cf']))
        # current_game['xbet_wins'] += current_game['total_bets'] - current_game['total_wins']
        # current_game['crashed_at'] = message['arguments'][0]['cf']
        log("CURRENT GAME", currentgame())
        dblogic.storeCrashes(currentgame())
        
        takeBet()

        # pprint.pprint("========================== HISTORY ==========================")
        # pprint.pprint(crashes_history)
        

def placeBet():
    
    if(balance('balance') < currentbet('bet') * 2):
        log("YOU LOST ALL YOUR MONEY")
        exit()

    if(in_bet() == 0 and canBet2()):
        in_bet(1)

        currentbet(
            'attemps',
            currentbet('attemps') + 1
        )

        # updating balance
        dblogic.substractFromBalance(currentbet('bet'))

        log("PLACED FIRST TIME BET")
        log("STATS", {
            "CURRENT BET": currentbet(),
            "XBET WINS": currentgame('xbet_wins'),

            "EXITING AT": breakpoint_(),
            "OCCURENCE": {
                "1, 2, 3 IN 20"     : str(checkMemOccurence(20, 1, True))+" / "+str(checkMemOccurence(20, 2, True))+" / "+str(checkMemOccurence(20, 3, True)),
                "1, 2, 3 IN 50"     : str(checkMemOccurence(50, 1, True))+" / "+str(checkMemOccurence(50, 2, True))+" / "+str(checkMemOccurence(50, 3, True)),
                "1, 2, 3 IN 100"    : str(checkMemOccurence(100, 1, True))+" / "+str(checkMemOccurence(100, 2, True))+" / "+str(checkMemOccurence(100, 3, True)),
            }
        })


    if(in_bet() == 1 and bet_next() == 1 and currentbet('attemps') < maxattemps()):
        currentbet(
            'attemps',
            currentbet('attemps') + 1
        )
        
        currentbet(
            'bet',
            currentbet('bet') * 2
        )

        # updating balance
        dblogic.substractFromBalance(currentbet('bet'))

        log("PLACED ANOTHER BET")
        log("STATS", {
            "CURRENT BET": currentbet(),
            "XBET WINS": currentgame('xbet_wins'),

            "EXITING AT": breakpoint_(),
            "OCCURENCE": {
                "1, 2, 3 IN 20"     : str(checkMemOccurence(20, 1, True))+" / "+str(checkMemOccurence(20, 2, True))+" / "+str(checkMemOccurence(20, 3, True)),
                "1, 2, 3 IN 50"     : str(checkMemOccurence(50, 1, True))+" / "+str(checkMemOccurence(50, 2, True))+" / "+str(checkMemOccurence(50, 3, True)),
                "1, 2, 3 IN 100"    : str(checkMemOccurence(100, 1, True))+" / "+str(checkMemOccurence(100, 2, True))+" / "+str(checkMemOccurence(100, 3, True)),
            }
        })




def takeBet():
    if(in_bet() == 1):
        # check if the plane crashed above or below the breaking point
        if(currentgame('crashed_at') > breakpoint_()): # you won
            wins = float(currentbet('bet') * breakpoint_())
            # update balance
            dblogic.addToBalance(wins)
            trans = dblogic.addTransaction({
                        'break_point'   : breakpoint_(),
                        'attemps'       : currentbet('attemps'),
                        'bet'           : currentbet("bet"),
                        'xbet_wins'     : currentgame("xbet_wins"),
                        'won'           : 1,
                        'amount'        : wins,
                        'crashed_at'    : currentgame('crashed_at'),
                        'balance'       : balance('balance'),
                        'confidence'    : checkBetConfidence(breakpoint_())
                    })
            log("!!!!!!!!!!!! YOU WON !!!!!!!!!!!!")
            log("STATS", {
                "CURRENT GAME": currentgame(),
                "CURRENT BET": currentbet(),
                "BALANCE": dblogic.getBalance(),
                "EXITING AT": breakpoint_(),
                "OCCURENCE": {
                    "1, 2, 3 IN 20"     : str(checkMemOccurence(20, 1, True))+" / "+str(checkMemOccurence(20, 2, True))+" / "+str(checkMemOccurence(20, 3, True)),
                    "1, 2, 3 IN 50"     : str(checkMemOccurence(50, 1, True))+" / "+str(checkMemOccurence(50, 2, True))+" / "+str(checkMemOccurence(50, 3, True)),
                    "1, 2, 3 IN 100"    : str(checkMemOccurence(100, 1, True))+" / "+str(checkMemOccurence(100, 2, True))+" / "+str(checkMemOccurence(100, 3, True)),
                }
            })

            in_bet(0)
            bet_next(0)
            currentbet('bet', 3)
            currentbet('attemps', 0)
            currentgame('crashed_at', 0)
            return

        if(currentgame('crashed_at') <= breakpoint_() and currentbet('attemps') < maxattemps()):
            trans = dblogic.addTransaction({
                        'break_point'   : breakpoint_(),
                        'attemps'       : currentbet('attemps'),
                        'bet'           : currentbet("bet"),
                        'xbet_wins'     : currentgame("xbet_wins"),
                        'won'           : 0,
                        'amount'        : currentbet("bet"),
                        'crashed_at'    : currentgame('crashed_at'),
                        'balance'       : balance('balance'),
                        'confidence'    : checkBetConfidence(breakpoint_())
                    })
            log("!!!!!!!!!!!! YOU LOST, STILL CAN BET !!!!!!!!!!!!")
            log("STATS", {
                "CURRENT GAME": currentgame(),
                "CURRENT BET": currentbet(),
                "BALANCE": dblogic.getBalance(),
                "EXITING AT": breakpoint_(),
                "OCCURENCE": {
                    "1, 2, 3 IN 20"     : str(checkMemOccurence(20, 1, True))+" / "+str(checkMemOccurence(20, 2, True))+" / "+str(checkMemOccurence(20, 3, True)),
                    "1, 2, 3 IN 50"     : str(checkMemOccurence(50, 1, True))+" / "+str(checkMemOccurence(50, 2, True))+" / "+str(checkMemOccurence(50, 3, True)),
                    "1, 2, 3 IN 100"    : str(checkMemOccurence(100, 1, True))+" / "+str(checkMemOccurence(100, 2, True))+" / "+str(checkMemOccurence(100, 3, True)),
                }
            })

            bet_next(1)
            currentgame('crashed_at', 0)
            return

        elif(currentgame('crashed_at') <= breakpoint_() and currentbet('attemps') >= maxattemps()):
            trans = dblogic.addTransaction({
                        'break_point'   : breakpoint_(),
                        'attemps'       : currentbet('attemps'),
                        'bet'           : currentbet("bet"),
                        'xbet_wins'     : currentgame("xbet_wins"),
                        'won'           : 0,
                        'amount'        : currentbet("bet"),
                        'crashed_at'    : currentgame('crashed_at'),
                        'balance'       : balance('balance'),
                        'confidence'    : checkBetConfidence(breakpoint_())
                    })

            log("STATS", {
                "CURRENT GAME": currentgame(),
                "CURRENT BET": currentbet(),
                "BALANCE": dblogic.getBalance(),
                "EXITING AT": breakpoint_(),
                "OCCURENCE": {
                    "1, 2, 3 IN 20"     : str(checkMemOccurence(20, 1, True))+" / "+str(checkMemOccurence(20, 2, True))+" / "+str(checkMemOccurence(20, 3, True)),
                    "1, 2, 3 IN 50"     : str(checkMemOccurence(50, 1, True))+" / "+str(checkMemOccurence(50, 2, True))+" / "+str(checkMemOccurence(50, 3, True)),
                    "1, 2, 3 IN 100"    : str(checkMemOccurence(100, 1, True))+" / "+str(checkMemOccurence(100, 2, True))+" / "+str(checkMemOccurence(100, 3, True)),
                }
            })

            in_bet(0)
            bet_next(0)
            currentbet('bet', 3)
            currentbet('attemps', 0)
            currentgame('crashed_at', 0)
            return 


def canBet():
    can_bet = False
    xbet_wins = currentgame('xbet_wins')

    # {
    #     'last_20': last_20,
    #     'last_50': last_50,
    #     'last_100': last_100,
    #     'total_avg': total_avg,
    # }

    # xbet_wins from 1000000 to 20000
    # if(xbet_wins < 1000000):
    #     can_bet = True
    #     entrypoint(1000000)
    #     breakpoint_(5)
        # confidence = checkBetConfidence(5)

        # if(confidence['total_avg'] > 30):
        #     can_bet = True
        
        

    # if(xbet_wins < 700000):
    #     can_bet = True
    #     entrypoint(700000)
    #     breakpoint_(4)
        # confidence = checkBetConfidence(4)

        # if(confidence['total_avg'] > 30):
        #     can_bet = True

    # if(xbet_wins < 900000):
    #     # can_bet = True
    #     entrypoint(900000)
    #     breakpoint_(3)
    #     confidence = checkBetConfidence(3)

    #     if(confidence['last_20'] > 3):
    #         can_bet = True

    if(xbet_wins < 990000):
        # can_bet = True
        entrypoint(990000)
        breakpoint_(2)
        confidence = checkBetConfidence(2)

        if(confidence['last_20'] > 2):
            can_bet = True

    if(xbet_wins < 50000):
        can_bet = False

    return can_bet



def canBet2():
    can_bet = False
    crashes = [2]
    last_n_crashes = 20
    
    
    # if(checkMemOccurence(1) < 35):
    #     return False
    # 100 - x > 2 => 40% ?
    # 50 - x > 2 => 20% ?
    # 20 - x > 2 => 10% ?
    # ========================= CONDITION ON 2 =========================
    # {'1-OCCURENCE': 8, '2-FIRST': False, '3-SECOND': True, '4-ALL': False}
    # ========================= CONDITION ON 3 =========================
    # {'1-OCCURENCE': 3, '2-FIRST': False, '3-SECOND': True, '4-ALL': False}
    # ========================= NEW GAME STARTING SOON !!!! =========================
    occurence_1 = checkMemOccurence(last_n_crashes, 1)
    log("OCCURENCE OF 1", occurence_1)
    if(occurence_1 > 13):
        return False

    for crh in crashes:
        # checkMemOccurence(last = 20, of = 2, above = False)
        occurence = checkMemOccurence(last_n_crashes, int(crh), True)
        cond1 = ((occurence * (last_n_crashes / crh)) / last_n_crashes) < 10
        cond2 = ((occurence * (last_n_crashes / crh)) / last_n_crashes) > 2

        log("CONDITION ON "+str(crh), {
            "1-OCCURENCE"       : occurence,
            "2-FIRST"           : cond1,
            "3-SECOND"          : cond2,
            "4-ALL"             : cond1 and cond2
        })
        # if(occurence < (10 / crh) and occurence >= (10 / crh * 2)):
        if(cond1 and cond2):
            breakpoint_(crh)
            can_bet = True

    return can_bet
            


# def checkMemOccurence(last = 20, of = 2):
#     last_n_crashes = memLastCrashes(last)

#     if(len(last_n_crashes) < last):
#         return 0

#     len_ = len([n for n in last_n_crashes if int(n) == of])
    
#     return len_
# def checkMemAvg(last = 20, of = 2):
#     last_n_crashes = memLastCrashes(last)

#     if(len(last_n_crashes) < last):
#         return 0

#     len_ = len([n for n in last_n_crashes if n >= of])
    
#     if(len_ <= 0):
#         return 0
    
#     return len(last_n_crashes) / len_

# def checkBetConfidence(of = 2):
#     last_20 = checkMemAvg(20, of)
#     last_50 = checkMemAvg(50, of)
#     last_100 = checkMemAvg(100, of)
#     total_avg = (last_20 + last_50 + last_100) / 3

#     return {
#         'last_20': last_20,
#         'last_50': last_50,
#         'last_100': last_100,
#         'total_avg': total_avg,
#     }





        
if __name__ == "__main__":
    try:
    
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://in.1xbet.com/games-frame/sockets/cafeed/",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
        ws.run_forever()
    except:
        log("ERROR")