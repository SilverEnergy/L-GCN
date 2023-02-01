import json

with open("/data/user/data2/STAR/STAR/Questions, Answers and Situation Graphs/STAR_val.json", "r") as star_json:
    star_read = json.load(star_json)
    
gif_name = star_read[0]['video_id']
a1 = star_read[0]['choices'][0]['choice']
a2 = star_read[0]['choices'][1]['choice']
a3 = star_read[0]['choices'][2]['choice']
a4 = star_read[0]['choices'][3]['choice']
print(gif_name, a1, a2, a3, a4)
print(len(star_read))
print(type(star_read))
print(type(star_read[0]))
# for element in star_read[0]:
#     print(element)
#     print(type(star_read[0][element]))
#     print("#########")

for choice in star_read[0]['choices']:
    print(choice)
    print("!!!!!!!!!!")

for choice in star_read[0]['choices']:
    if choice["choice"] == star_read[0]['answer']:
        print(choice['choice_id'])
print(star_read[0]['answer'])