import csv
import json
import re

with open("/data/user/data2/STAR/STAR/Questions, Answers and Situation Graphs/STAR_val.json", "r") as json_file:
    json_data = json.load(json_file)
    csv_rows = [["gif_name", "question", "a1", "a2", "a3", "a4", "answer"]]
    for each in json_data :
        gif_name = each['video_id'] + ".mp4"
        a1 = each['choices'][0]['choice']
        a2 = each['choices'][1]['choice']
        a3 = each['choices'][2]['choice']
        a4 = each['choices'][3]['choice']    
        for choice in each['choices']:
            if choice["choice"] == each['answer']:
                answer = choice['choice_id']
        question = each["question"]
#         state += each["contents"]

        csv_rows.append([gif_name] + [question] + [a1] + [a2] + [a3] + [a4] + [answer])

#         each["state"] = [state]
#         each["proof"] = [proof]

# #with open('naturalproofs_both_split.json', 'w') as f:
# #    json.dump(json_data, f)

# with open('naturalproofs_stein_adjust.json', 'w') as f1:
#     json.dump(json_data, f1, indent=2)
          
with open("STAR_test.csv", 'w') as file:
    writer = csv.writer(file)
    writer.writerows(csv_rows)
