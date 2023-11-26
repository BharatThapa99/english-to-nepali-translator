#collect proxies from file

#read source file line by line

#translate without proxy how much you can

# upon error use proxy

# if one proxy fails use another one from the collected proxies

# on finding succesful proxy keep it using until error occurs and when error occurs use next one

import requests
import json
import time
import os
from requests.auth import HTTPProxyAuth

from proxy_utils import scrape_proxies



api_endpoint = "http://translate.googleapis.com/translate_a/single"

count = 0
input_file = 'Datasets/english_dataset_5000_1.json'

base_name, extension = os.path.splitext(os.path.basename(input_file))
output_file = os.path.join(os.path.dirname(input_file), f'{base_name}_trans_nepali{extension}')

# output_file = 'Datasets/ChatMed_Consult_2500-1_Nepali_test.json'
checkpoint_file = str(base_name)+'_Checkpoint.txt'
# chunk_size = 2

working_proxy = ""
working_proxy_list = []
proxies = []
proxy_index = 0
proxy_username = "bvvredao"
proxy_password = "lk19of6p6d92"
# if the loop completes two cycles through the list update the proxy list
proxy_list_error_count = 0 #if it reaches 2 update proxy list
# working_proxies = []

def read_proxy_list():
    global proxies
    proxies_list_file = "proxy-list.txt"
    with open(proxies_list_file, 'r') as file:
            proxies = file.read().splitlines()
    
read_proxy_list()

def translate(text, target_lang, source_lang,proxy=None):
    # text = urllib.parse.quote(text)
    params = {
        "client": "gtx",
        "dt": "t",
        "sl": source_lang,
        "tl": target_lang,
        "q": text
    }
    proxies = {
         'http':proxy,
         'https':proxy,
    }
    proxy_auth = HTTPProxyAuth(proxy_username, proxy_password)

    try:
        #try with original ip until it gets blocked. Then use proxies.

        if proxy:
            response = requests.get(api_endpoint,params=params, proxies=proxies,timeout=4,auth=proxy_auth)
            print(f"Using proxy: {proxy},\n {response}")
        else:
            # print(f"No proxy is used for this request.")
            response = requests.get(api_endpoint,params=params, timeout=10)
        
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            # if the translated data is not nepali
            if data[0][0][4] != 3: #api returns 3 for Nepali target language
                return None
            translated_string = ""
            # print(type(data))
            for middle_list in data[0]:
                
                if middle_list is not None:
                    translated_string += middle_list[0]

            return translated_string
        else:
            return None
        # return response
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: {e}")    
    except requests.exceptions.ProxyError as e:
        print(f"Proxy connection error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def set_proxy():
    print(f"Checking working proxy from pool...")
    global proxy_index
    global proxy_list_error_count
    # print(f"proxy list error count - {proxy_list_error_count}")
    for i in range(proxy_index, len(proxies)+1):
        proxy_index = i
        # print(f"proxy index = {proxy_index} and length of proxies = {len(proxies)}")
        if proxy_index == len(proxies):
            print("All proxies checked. Reusing from start...\n") #TODO: fetch new list of proxy
            proxy_list_error_count += 1
            if proxy_list_error_count > 1:
                scrape_proxies() #update the proxies list
                read_proxy_list() #read updated proxies list
                proxy_list_error_count = 0
            proxy_index = 0
            working_proxy = ""
            break
        # print(proxies[i])
        # exit()
        proxy = {
                'http':proxies[i],
                'https':proxies[i],
        }
        proxy_auth = HTTPProxyAuth(proxy_username, proxy_password)
        try:
            test = requests.get("http://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=en&tl=ne&q=",proxies=proxy,timeout=2, auth=proxy_auth)
            if test.status_code == 200:
                # print(test.text)
                working_proxy = str(proxies[i]).strip()
                print(f"{working_proxy} succesfully connected: {test.text} ")
                return working_proxy
                
                
                # break
            else:
                print(f"{proxies[i]} failed to connect")
        except requests.exceptions.Timeout as e:
            print(f"Timeout error: {proxies[i]}")    
        except requests.exceptions.ProxyError as e:
            print(f"Proxy connection error: {proxies[i]}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {proxies[i]}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def save_result(trans_query, trans_response):
    current_chunk = []

    new_json_object = json.loads('{}')
    new_json_object['query'] = str(trans_query)
    new_json_object['response'] = str(trans_response)

    current_chunk.append(new_json_object)

    # if total_records_processed % chunk_size == 0:
        # Save the current chunk to the output file
    with open(output_file, 'a', encoding='utf-8') as output:
        for obj in current_chunk:
            json.dump(obj, output, ensure_ascii=False)
            output.write('\n')
    print("\n--- Translation Appended to output file ---\n")

def save_checkpoint(line_number,json_obj):
    try:
        checkpoint_data = {
            'line_number': line_number,
            'json_object': json_obj
        }
        with open(checkpoint_file, 'w', encoding='utf-8') as output:
            output.write("This file contains last translated row information.\n")
            json.dump(checkpoint_data, output, ensure_ascii=False)
            output.write("\n")
    except Exception as e:
        print(f"Error saving {e}")
        raise
        



try:
    with open(input_file, 'r', encoding='utf-8') as source:

        line_number = 0
        total_records_processed = 0

        for line in source:
            line_number += 1
            json_object = json.loads(line)
            query = json_object['query']
            # print(context)
            response = json_object['response']

            #if no proxy is set then use no proxy
            if working_proxy != "":
                trans_query_without_proxy =  translate(query, 'ne', 'auto')

                if trans_query_without_proxy:
                    time.sleep(2)
                    trans_response_without_proxy = translate(response,'ne','auto') #translate response
                    if trans_response_without_proxy:
                        time.sleep(2)

                        print("Request without proxy was successful. ")
                        # print(f"query w/o proxy: {trans_query_without_proxy}")
                        
                        #Save the translation
                        save_result(trans_query_without_proxy,trans_response_without_proxy)
                        save_checkpoint(line_number,json_object)
                        count += 2
                        total_records_processed += 1
                        # current_chunk = []
                        print("Translation count: "+str(count))
                        print("Translated Rows: "+str(total_records_processed))
                        print("\n")


                else: # if error occurs on our own ip we use proy
                    working_proxy = "set"
                    print("Switching to proxy...")


            #use the set proy
            else:
                proxy = set_proxy()
                if proxy is not None:
                    print(f"Proxy set: the new proxy is {proxy}")
                    trans_query_with_proxy =  translate(query, 'ne', 'auto',str(proxy))

                    if trans_query_with_proxy:
                        time.sleep(2)
                        trans_response_with_proxy = translate(response,'ne','auto',str(proxy)) #translate response
                        if trans_response_with_proxy:
                            time.sleep(2)
                            working_proxy_list.append(str(proxy))
                            # print(f"Request with proxy {proxy} was successful. ")
                            # print(f"query with proxy: {trans_query_with_proxy}")

                            #Save the translation
                            save_result(trans_query_with_proxy,trans_response_with_proxy)
                            save_checkpoint(line_number,json_object)
                            count += 2
                            total_records_processed += 1
                            # current_chunk = []
                            print("Translation count: "+str(count))
                            print("Translated Rows: "+str(total_records_processed))
                            print("\n")
                        else:
                            print(f"Response: None occured... The row is skipped")

                    else: # if proxy error occurs then, change another one
                        set_proxy()

    print("Translation completed....")
except Exception as e:
    print(f"An error occurred: {str(e)}")


#find and set working proxy
