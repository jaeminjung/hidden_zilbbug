
import data_file
import requests, time, os, json, datetime

API_KEY = data_file.API_KEY

def save_json(address, name, data):
    with open(address + name, "w") as f:
        json.dump(data, f)
    
def read_json(address, name):
    with open(address + name, "r") as f:
        data = json.load(f)
    return data

def get_puuid_by_name(name):
    info_URL = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}"
    response = requests.get(info_URL.format(name, API_KEY))
    # print(response.json())
    return response.json()["puuid"]

def get_name_by_puuid(puuid):
    puuid_to_name_URL = "https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{}?api_key={}"
    response = requests.get(puuid_to_name_URL.format(puuid, API_KEY))
    # print(response.json())
    return response.json()["gameName"]

def get_match_ids(puuid, start, count):
    match_id_URL = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?start={}&count={}&api_key={}"
    response = requests.get(match_id_URL.format(puuid, start, count, API_KEY))
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        os.system('say "waiting"')
        print("waiting 20 secs")
        time.sleep(20)
        get_match_ids(puuid, start, count)
    else:
        os.system('say "ids error"')
        print(response)
        print("error is append - puuid is : ", puuid + "  , start : " + str(start) )
        data_file.error_arr.append("puuid, " + str(puuid) + ", start, " + str(start) +", "+ str(response.status_code))
        return None

def get_match_detail(match_id):
    match_detail_URL = "https://asia.api.riotgames.com/lol/match/v5/matches/{}?api_key={}"
    response = requests.get(match_detail_URL.format(match_id, API_KEY))
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        os.system('say "waiting"')
        print("waiting 20 secs")
        time.sleep(20)
        get_match_detail(match_id)
    else:
        os.system('say "match error"')
        print(response)
        print("error_arr is append - match_id : ", match_id)
        data_file.error_arr.append("match_id, " + str(match_id) + ", status_code, " + str(response.status_code))
        data_file.error_arr_match_id.append(match_id)
        return None
    

def get_all_match_ids(puuid):
    end = False
    start = 0
    count = 50
    all_match_ids = []
    while not end:
        match_ids = get_match_ids(puuid, start, count)
        if match_ids:
            all_match_ids += match_ids
        else:
            end = True
        start += count
    return all_match_ids

def check_datetime(num):
    date = datetime.datetime.fromtimestamp(num).strftime('%Y')
    return date == 2020

def match_filter(match_detail):
    if check_datetime(match_detail["info"]["gameCreation"]//1000): # check game created in 2021
        os.system('say "datetime datetime"')
        print("datetime in 2020 game found")
        return True
        date_cond = True    
    if match_detail["info"]["queueId"] != 420: # check 5vs5 solo rank
        print("found not solo queue game")
        return True
    if match_detail["info"]["gameDuration"]/1000/60 < 8: # ignore draw game
        print("found less than 8 mins game")
        return True
    return False

def get_all_match_details(all_match_ids, puuid):
    match_detail_d = data_file.match_detail_d
    for match_id in all_match_ids:
        match_detail = get_match_detail(match_id)
        if match_detail == None:
            continue
        if match_filter(match_detail):
            continue
        else:
            # dictionary
            if match_id in match_detail_d:
                print("found duplicated")
            else:
                print("found solo queue")
                match_detail_d[match_id] = match_detail

    print("match_detail_d length : ", len(match_detail_d))
    save_json('match_detail/', puuid, match_detail_d)
    match_detail_d = {}
    return 0

def cal_kda(numerator, denominator):
    if denominator == 0:
        return numerator
    return numerator / denominator

def crawling_more(sum_Name):
    puuid = get_puuid_by_name(sum_Name)
    all_match_ids = get_all_match_ids(puuid)

    match_details = read_json('match_detail/', puuid)
    print(len(match_details))
    # for match_id in all_match_ids:
    #     if match_id in match_details:
    #         continue
    #     else:
    #         match_detail = get_match_detail(match_id)
    #         if get_match_detail != None:
    #             match_details[match_id] = match_detail
    # save_json('match_detail/', puuid, match_details)
    # print("done crawling_more")
    return 0

def find_hidden_zilbbug():
    bobs_name = ['강자석', '강찬밥', 'maengsdog']
    master_d = {}
    for bob in bobs_name:
        bob_puuid = get_puuid_by_name(bob)
        match_details = read_json('match_detail/', bob_puuid)
        
        for match_detail in match_details.values():
            participants = match_detail["info"]["participants"]
            game_duration = match_detail["info"]["gameDuration"]/1000/60
            # find bob
            for participant in participants:
                if participant["puuid"] == bob_puuid:
                    bob_puuid = participant["puuid"]
                    bob_summonerName = participant["summonerName"]
                    bob_totalDamageDealtToChampions = participant["totalDamageDealtToChampions"] / game_duration
                    bob_numerator = participant["assists"] + participant["kills"]
                    bob_denominator = participant["deaths"]
                    bob_kda = cal_kda(bob_numerator, bob_denominator)
                    bob_win = participant["win"]
                    break

            for participant in participants:
                if participant["puuid"] == bob_puuid:
                    continue
                else:
                    zb_puuid = participant["puuid"]
                    zb_summonerName = participant["summonerName"]
                    zb_totalDamageDealtToChampions = participant["totalDamageDealtToChampions"] / game_duration
                    zb_numerator = participant["assists"] + participant["kills"]
                    zb_denominator = participant["deaths"]
                    zb_kda = cal_kda(zb_numerator, zb_denominator)
                    zb_win = participant["win"]

                    # put into dict
                    
                    if not zb_puuid in master_d: # initialize
                        master_d[zb_puuid] = {
                            "zb_summonerName":[],
                            "same_team" : {
                                "count": 0, "zb_kda": 0, "zb_totalDamageDealtToChampions":0, "zb_win_count":0,
                                "bob_kda": 0, "bob_totalDamageDealtToChampions": 0
                                }, 
                            "diff_team" : {
                                "count": 0, "zb_kda": 0, "zb_totalDamageDealtToChampions":0, "zb_win_count":0,
                                "bob_kda": 0, "bob_totalDamageDealtToChampions": 0
                                },  
                            "total_count" : 1
                            }
                        if zb_win == bob_win: # same team
                            master_d[zb_puuid]["same_team"]["count"] += 1
                            master_d[zb_puuid]["same_team"]["zb_kda"] += zb_kda
                            master_d[zb_puuid]["same_team"]["zb_totalDamageDealtToChampions"] += zb_totalDamageDealtToChampions
                            if zb_win:
                                master_d[zb_puuid]["same_team"]["zb_win_count"] += 1
                            if not zb_summonerName in master_d[zb_puuid]["zb_summonerName"]:
                                master_d[zb_puuid]["zb_summonerName"].append(zb_summonerName)
                            master_d[zb_puuid]["same_team"]["bob_kda"] += bob_kda
                            master_d[zb_puuid]["same_team"]["bob_totalDamageDealtToChampions"] += bob_totalDamageDealtToChampions

                        else: # diff team
                            master_d[zb_puuid]["diff_team"]["count"] += 1
                            master_d[zb_puuid]["diff_team"]["zb_kda"] += zb_kda
                            master_d[zb_puuid]["diff_team"]["zb_totalDamageDealtToChampions"] += zb_totalDamageDealtToChampions
                            if zb_win:
                                master_d[zb_puuid]["diff_team"]["zb_win_count"] += 1
                            if not zb_summonerName in master_d[zb_puuid]["zb_summonerName"]:
                                master_d[zb_puuid]["zb_summonerName"].append(zb_summonerName)
                            master_d[zb_puuid]["diff_team"]["bob_kda"] += bob_kda
                            master_d[zb_puuid]["diff_team"]["bob_totalDamageDealtToChampions"] += bob_totalDamageDealtToChampions

                    else:
                        master_d[zb_puuid]["total_count"] += 1
                        if zb_win == bob_win: # same team
                            master_d[zb_puuid]["same_team"]["count"] += 1
                            master_d[zb_puuid]["same_team"]["zb_kda"] += zb_kda
                            master_d[zb_puuid]["same_team"]["zb_totalDamageDealtToChampions"] += zb_totalDamageDealtToChampions
                            if zb_win:
                                master_d[zb_puuid]["same_team"]["zb_win_count"] += 1
                            if not zb_summonerName in master_d[zb_puuid]["zb_summonerName"]:
                                master_d[zb_puuid]["zb_summonerName"].append(zb_summonerName)
                            master_d[zb_puuid]["same_team"]["bob_kda"] += bob_kda
                            master_d[zb_puuid]["same_team"]["bob_totalDamageDealtToChampions"] += bob_totalDamageDealtToChampions
                        
                        else: # diff team
                            master_d[zb_puuid]["diff_team"]["count"] += 1
                            master_d[zb_puuid]["diff_team"]["zb_kda"] += zb_kda
                            master_d[zb_puuid]["diff_team"]["zb_totalDamageDealtToChampions"] += zb_totalDamageDealtToChampions
                            if zb_win:
                                master_d[zb_puuid]["diff_team"]["zb_win_count"] += 1
                            if not zb_summonerName in master_d[zb_puuid]["zb_summonerName"]:
                                master_d[zb_puuid]["zb_summonerName"].append(zb_summonerName)
                            master_d[zb_puuid]["diff_team"]["bob_kda"] += bob_kda
                            master_d[zb_puuid]["diff_team"]["bob_totalDamageDealtToChampions"] += bob_totalDamageDealtToChampions

    return master_d

def print_master_d(master_d):
    a = [['sum_Name', '총게임수', '같은팀게임수', '같은팀이긴횟수', '같은팀일때승률','질뻐기평균kda', '질뻐기평균분당데미지', 
    '밥의kda', '밥의평균분당데미지', 
    '다른팀게임수', '다른팀이긴횟수', '다른팀일때승률', '질뻐기평균kda', '질뻐기평균분당데미지', '밥의kda', '밥의평균분당데미지']]
    master_d = read_json('match_detail/', 'master')
    for key, val in master_d.items():
        ex = []
        sum_name = ''
        same_team_count = val['same_team']['count']
        diff_team_count = val['diff_team']['count']
        if same_team_count == 0:
            same_team_count = 1
        if diff_team_count == 0:
            diff_team_count = 1
        
        for nm in val['zb_summonerName']:
            sum_name += nm + " || "
        ex.append(sum_name)
        ex.append(val['total_count'])
        ex.append(val['same_team']['count'])
        ex.append(val['same_team']['zb_win_count'])
        ex.append(val['same_team']['zb_win_count']/same_team_count)
        ex.append(val['same_team']['zb_kda']/same_team_count)
        ex.append(val['same_team']['zb_totalDamageDealtToChampions']/same_team_count)
        ex.append(val['same_team']['bob_kda']/same_team_count)
        ex.append(val['same_team']['bob_totalDamageDealtToChampions']/same_team_count)
        ex.append(val['diff_team']['count'])
        ex.append(val['diff_team']['zb_win_count'])
        ex.append(val['diff_team']['zb_win_count']/diff_team_count)
        ex.append(val['diff_team']['zb_kda']/diff_team_count)
        ex.append(val['diff_team']['zb_totalDamageDealtToChampions']/diff_team_count)
        ex.append(val['diff_team']['bob_kda']/diff_team_count)
        ex.append(val['diff_team']['bob_totalDamageDealtToChampions']/diff_team_count)
        
        a.append(ex)
        # print(key, val)
        # time.sleep(2)
    f = open('match_detail/a.csv', "w")
    for element in a:
        line = ''
        for e in element:
            line += str(e) + ", "
        line += '\n'
        f.write(line)
    f.close()

    print("같이 플레이한 총 인원 : ", len(master_d))

    
    # for val in master_d.values():
    #     a.append(val)
    
    # master_d = sorted(a, key = lambda x : x["total_count"], reverse=True)
    # short_arr = []
    # for i, val in enumerate(master_d):
    #     short_arr.append(val)
    #     # print("-------------", val["zb_summonerName"], "------------", val["total_count"], val["same_team"]["zb_win_count"])
    #     # print("총 게임 수 : ", val["total_count"])
    #     # print("same_team")
    #     # print(val["same_team"])
    #     # print("diff_team")
    #     # print(val["diff_team"])
    #     # time.sleep(5)
    #     if i == 55:
    #         break
    
    # for val in short_arr:
    #     win_rate = val["same_team"]["zb_win_count"] / val["same_team"]["count"] * 100
    #     try:
    #         against_win_rate = val['diff_team']["zb_win_count"] / val["diff_team"]["count"] * 100
    #     except:
    #         against_win_rate = 0
    #     val["win_rate"] = win_rate
    #     val["against_win_rate"] = against_win_rate

    # short_arr = sorted(short_arr, key = lambda x : x["win_rate"])
    # for val in short_arr:
    #     print("--", val["zb_summonerName"], "----------------")
    #     print("총 게임 수 : ", val["total_count"])
    #     print("같은팀일때 : ", val["same_team"]["zb_win_count"], "승 /", 
    #     val["same_team"]["count"] - val["same_team"]["zb_win_count"], "패, 승률 : ", val["win_rate"])

    # short_arr = sorted(short_arr, key = lambda x : x["against_win_rate"])
    # for val in short_arr:
    #     print("--", val["zb_summonerName"], "------------")
    #     print("총 게임 수 : ", val["total_count"])
    #     print("다른팀일떄 : ", val["diff_team"]["zb_win_count"], "승 /", 
    #     val["diff_team"]["count"] - val["diff_team"]["zb_win_count"] ,"패, 승률 : ", val["against_win_rate"])
    