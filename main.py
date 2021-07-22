import data_file, func_file

print("----------start---------------")
bobs_name = ['강자석', '강찬밥', 'maengsdog']

func_file.crawling_more(bobs_name[0])
func_file.crawling_more(bobs_name[1])
func_file.crawling_more(bobs_name[2])
# puuid = func_file.get_puuid_by_name('maengsdog')
# name = func_file.get_name_by_puuid(puuid)

# all_match_ids = func_file.get_all_match_ids(puuid)
# print("length all_match_ids : ", len(all_match_ids))

# func_file.get_all_match_details(all_match_ids, puuid)

# master_d = func_file.find_hidden_zilbbug()
# func_file.print_master_d(master_d)

print("-----------end----------------")
print(data_file.error_arr)
print(data_file.error_arr_match_id)