# import requests
# import json

# # Define the URL for the translation endpoint
# url = "https://translate.googleapis.com/translate_a/single"

# # Define the parameters for the GET request
# params = {
#     "client": "gtx",
#     "dt": "t",
#     "sl": "en",
#     "tl": "ne",
#     "q": "Cam you provide some tips for maintaining a healthy lifestyle, especially in terms of diet and excercise?"
# }

# # Send a GET request to the translation endpoint
# response = requests.get(url, params=params)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the JSON response
#     data = response.json()

#     # Extract the translation from the JSON response
#     translation = data[0][0][0]

#     # Print the translation
#     print("Translation:", translation)

#     # Save the translation to a file
#     with open("translation.txt", "w", encoding="utf-8") as file:
#         file.write(translation)
# else:
#     print("Failed to retrieve translation. Status code:", response.status_code)



######version 2##################
import requests
import json
import time
import urllib.parse

# Function to translate a text using the translation endpoint
def translate_text(text, source_lang, target_lang):
    # text = urllib.parse.quote(text)
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "dt": "t",
        "sl": source_lang,
        "tl": target_lang,
        "q": text
    }
    response = requests.get(url, params=params)
    print("status code: "+str(response.status_code))
    if response.status_code == 200:
        data = response.json()
        translated_string = ""

        for outer_list in data:
            if outer_list is not None:
                # print(outer_list)
                for inner_list in outer_list:
                    if inner_list is not None and len(inner_list) > 0:
                        if inner_list[0] != 'e' or inner_list[0] != 'n':
                            # print(inner_list[0])
                            
                            translated_string += inner_list[0]
                        # print(translated_string)

        #last two letter at the end of translated sentence is "en", truncate them
        translated_string = translated_string[:-2]
        print(translated_string)
        # translation = data[0][0][0]
        # print(translation)
        return translated_string
    else:
        return None

# Load your combined_dataset JSON file line by line and translate each line
count = 0
input_file = 'combined_dataset.json'
output_file = 'translated_dataset.json'
chunk_size = 10 
with open(input_file, 'r', encoding='utf-8') as file:
    
    current_chunk = []
    total_records_processed = 0

    for line in file:
        json_object = json.loads(line)
        new_json_object = json.loads('{}')
        context = json_object['Context']
        # print(context)
        response = json_object['Response']

        # Translate the context and response
        translated_context = translate_text(context, source_lang='en', target_lang='ne')
        time.sleep(3)
        count += 1
        translated_response = translate_text(response, source_lang='en', target_lang='ne')
        time.sleep(2)
        count += 1
        # Update the JSON object with translations
        new_json_object['Translated_Context'] = translated_context
        new_json_object['Translated_Response'] = translated_response

        # Append the updated JSON object to the translated dataset
        current_chunk.append(new_json_object)
        total_records_processed += 1

        if total_records_processed % chunk_size == 0:
            # Save the current chunk to the output file
            with open(output_file, 'a', encoding='utf-8') as output:
                for obj in current_chunk:
                    json.dump(obj, output, ensure_ascii=False)
                    output.write('\n')
            current_chunk = []
        print("Translation count: "+str(count))

# Save the updated dataset with translations
with open(output_file, 'a', encoding='utf-8') as output:
    for obj in current_chunk:
        json.dump(obj, output, ensure_ascii=False)
        output.write('\n')
