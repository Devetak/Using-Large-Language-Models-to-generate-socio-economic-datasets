import pandas as pd
import os
import random


def parse(company, df):

    # raw output file name
    name_file = company.replace(" ", "_")
    chars_to_remove = "/\\:*?\"<>|"
    translation_table = str.maketrans("", "", chars_to_remove)
    name_file = name_file.translate(translation_table)

    try:
        f = open(os.path.join(__location__, f'../data/raw_output/{name_file}.txt'), "r")
    except:
        return "missing"
    answer = f.read()
    flag = "no data"
    lines = answer.splitlines()
    for line in lines:
        line = line.split("|")
    
        if len(line) > 1 and line[0] != "" and line[1] != "":
            site = line[0]
            address = line[1]
            df.loc[len(df)] = [company, site, address]
            flag = "ok"
        elif len(line) > 2 and line[1] != "" and line[2] != "":
            site = line[1]
            address = line[2]
            df.loc[len(df)] = [company, site, address]
            flag = "ok"
        else:
            pass

    return flag

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
df = pd.read_csv(os.path.join(__location__, '../data/list_companies.csv'))
list_companies = df['company'].unique().tolist()
llm_mistakes = []
missing = []

final_dataframe = pd.DataFrame(columns=['company', 'site', 'address'])

for company in list_companies:
    flag = parse(company, final_dataframe)
    if flag == "missing":
        missing.append(company)
    elif flag == "no data":
        llm_mistakes.append(company)
    else:
        pass

final_dataframe.to_csv(os.path.join(__location__, '../data/production_sites_raw.csv'), index=False)
companies_in_final_dataframe_raw = final_dataframe['company'].unique().tolist()

print(f"rows at the beginning: {len(final_dataframe)}")

# convert to string
final_dataframe['site'] = final_dataframe['site'].astype(str)
final_dataframe['address'] = final_dataframe['address'].astype(str)
final_dataframe['company'] = final_dataframe['company'].astype(str)

# change name to df
df = final_dataframe

# turn all entries into strings
df['site'] = df['site'].astype(str)
df['address'] = df['address'].astype(str)

# remove all rows with "", "---", "Name of Site", "Name of Company", "Address", "Name", "Address of Site"
df = df[df['site'] != ""]
for i in range(1, 40):
    df = df[df['site'] != "-"*i]
df = df[df['site'] != "Name of Site"]
df = df[df['site'] != "Name of Company"]
df = df[df['address'] != "Address"]
df = df[df['site'] != "Name"]
df = df[df['address'] != "Address of Site"]
df = df[df['site'] != "Name of Office"]
df = df[df['site'] != "Name of Site"]
df = df[df['site'] != "Address of Office"]
df = df[df['site'] != "Name of Office"]
df = df[df['site'] != "Country"]
df = df[df['site'] != "City"]
df = df[df['site'] != "Address of Site"]
df = df[df['site'] != "Address of Office"]
df = df[df['site'] != "Address of Site"]

df = df[~df['address'].str.contains("Address")]
df = df[~df['address'].str.contains("address")]
df = df[~df['site'].str.contains("site")]
df = df[~df['site'].str.contains("Site")]

print(f"rows after removing empty sites: {len(df)}")
df.to_csv(os.path.join(__location__, '../data/production_sites.csv'), index=False)

# clean the string of * and # and " and ' and trailing/leading spaces
df['site'] = df['site'].str.replace('*', '')
df['site'] = df['site'].str.replace('#', '')
df['site'] = df['site'].str.replace('"', '')
df['site'] = df['site'].str.replace("'", "")
df['site'] = df['site'].str.replace("-", "")
df['site'] = df['site'].str.strip()
df['address'] = df['address'].str.replace('*', '')
df['address'] = df['address'].str.replace('#', '')
df['address'] = df['address'].str.replace('"', '')
df['address'] = df['address'].str.replace("'", "")
df['address'] = df['address'].str.strip()

df = df[df['site'] != ""]
df = df[df['site'] != "nan"]
df = df[df['address'] != ""]
df = df[df['address'] != "nan"]

print(f"rows after cleaning: {len(df)}")
df.to_csv(os.path.join(__location__, '../data/production_sites_cleaned.csv'), index=False)

companies_in_final_dataframe_cleaned = df['company'].unique().tolist()
companies_with_no_valid_answers = []
for company in companies_in_final_dataframe_raw:
    if company not in companies_in_final_dataframe_cleaned:
        companies_with_no_valid_answers.append(company)

print(f"there are {len(missing)} companies with missing files")
print(f"there are {len(llm_mistakes)} companies with language model mistakes")
print(f"there are {len(companies_with_no_valid_answers)} companies with no valid answers")
print(f"there are {len(companies_in_final_dataframe_cleaned)} in final dataframe")

# select random 100 lines from the dataframe and save them to a separate CSV
df = df.sample(n=100)
df.to_csv(os.path.join(__location__, '../data/production_sites_sample.csv'), index=False)

# save to CSV the companies with no valid answers
df = pd.DataFrame(companies_with_no_valid_answers, columns=['company'])
df.to_csv(os.path.join(__location__, '../data/mistakes_lists/no_good_answer.csv'), index=False)

# save to CSV the companies with missing files
df = pd.DataFrame(missing, columns=['company'])
df.to_csv(os.path.join(__location__, '../data/mistakes_lists/missing_files.csv'), index=False)

# save to CSV the companies with language model mistakes
df = pd.DataFrame(llm_mistakes, columns=['company'])
df.to_csv(os.path.join(__location__, '../data/mistakes_lists/language_model_mistakes.csv'), index=False)

# select 10 random companies with LLM mistakes and combine the .txt files in a single text file
random.shuffle(llm_mistakes)
llm_mistakes = llm_mistakes[:10]

new_file = ""

for company in llm_mistakes:
    name_file = company.replace(" ", "_")
    chars_to_remove = "/\\:*?\"<>|"
    translation_table = str.maketrans("", "", chars_to_remove)
    name_file = name_file.translate(translation_table)
    f = open(os.path.join(__location__, f'../data/raw_output/{name_file}.txt'), "r")
    answer = f.read()
    new_file += f"Company: {company}\n"
    new_file += answer
    new_file += "\n\n\n"

f = open(os.path.join(__location__, f'../data/mistakes_lists/llm_mistakes.txt'), "w")
f.write(new_file)
f.close()