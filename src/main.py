from bardapi import BardCookies
import pandas as pd
import os
import time
import random
import logging
import browser_cookie3

def extract_bard_cookie():
    cookie_dict = {}
    cj = browser_cookie3.chrome(cookie_file=r"",domain_name=".google.com")
    for cookie in cj:
        if cookie.name == "__Secure-1PSID" and cookie.value.endswith("."):
            cookie_dict["__Secure-1PSID"] = cookie.value
        if cookie.name == "__Secure-1PSIDTS":
            cookie_dict["__Secure-1PSIDTS"] = cookie.value
        if cookie.name == "__Secure-1PSIDCC":
            cookie_dict["__Secure-1PSIDCC"] = cookie.value
    logging.info(cookie_dict)
    return cookie_dict

# Load CSV file of companies
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
df = pd.read_csv(os.path.join(__location__, '../data/list_companies_to_reask_final.csv'))
list_companies = df['company'].tolist()

# Load temporary CSV of production sites
df = pd.read_csv(os.path.join(__location__, '../data/production_sites_temp.csv'))
# df = pd.DataFrame(columns=['company', 'site', 'address'])
list_companies_temp = df['company'].tolist()

# start bard
cookie_dict = extract_bard_cookie()
bard = BardCookies(cookie_dict=cookie_dict)

question = "Pretend you are a database to which I make an API request . I ask you to list all the production sites of X. Be as exhaustive as possible. PLEASE LIST THEM AS\nFOLLOWS: \n\nName of Site 1 | Adress of Site 1\nName of Site 2 | Adress of Site 2\n...\nName of Site n | Adress of Site n\n\nDO NOT INCLUDE ANY OTHER TEXT as you are an API. WRITE A LONG REPLY AND BE EXHAUSTIVE. Make the address precise. ONLY USE THE GIVEN FORMAT."
# create empty lists
list_sites = []
list_addresses = []
##

# loop over companies
for company in list_companies:
    # skip if already in the temporary dataframe
    if company in list_companies_temp:
        continue

    print("Asking for company: ", company)
    cookie_dict = extract_bard_cookie()
    bard = BardCookies(cookie_dict=cookie_dict)
    question_to_bard = question.replace("X", company)

    try:
        # wait for a random ammount between 15 and 300 seconds
        time_to_wait = random.randint(15, 300)
        time.sleep(time_to_wait)
        res = bard.get_answer(question_to_bard)
        content = res['content']
        try:
            name_file = company.replace(" ", "_")
            # remove any illegal charachters
            chars_to_remove = "/\\:*?\"<>|"
            translation_table = str.maketrans("", "", chars_to_remove)
            name_file = name_file.translate(translation_table)
            f = open(os.path.join(__location__, f'../data/raw_output/{name_file}.txt'), "a")
            f.write(content)
            f.close()
        except:
            print(f"troubles storing output for {company}")
    except: 

        # append to dataframe a site in the South Pole
        df.loc[len(df)] = [company, "South Pole", "South Pole"]
        # save dataframe to csv as temporary backup
        df.to_csv(os.path.join(__location__, '../data/production_sites_temp.csv'), index=False)
        # sleep for 61 minutes
        list_companies.append(company)
        print("GOT BLOCKED! SLEEPING FOR 11 MINUTES")
        time.sleep(660)

    try:
        # split by line
        lines = content.split("\n")
        # loop over lines
        for line in lines:
            # split by |
            line = line.split("|")
            # append to dataframe
            try:
                list_sites.append(line[0])
                list_addresses.append(line[1])
            except:
                print("Error with the line: ", line)
                # print("total response: ", content)
                print("\n")
    except:
        print(content)
        # append to dataframe a site in the North Pole
        df.loc[len(df)] = [company, "North Pole", "North Pole"]
        list_companies.append(company)

    
    if list_addresses != []:
        for i in range(len(list_addresses)):    
            df.loc[len(df)] = [company, list_sites[i], list_addresses[i]]
        
    
    # save dataframe to csv as temporary backup
    df.to_csv(os.path.join(__location__, '../data/production_sites_temp.csv'), index=False)

    list_sites = []
    list_addresses = []

# save dataframe to csv
df.to_csv(os.path.join(__location__, '../data/production_sites_temp.csv'), index=False)
