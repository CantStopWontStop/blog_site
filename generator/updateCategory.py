import pandas as pd
import re

def convert_google_sheet_url(url):
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # Replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url

url = 'https://docs.google.com/spreadsheets/d/1bJIUEOh8yUg46dREnE_bXlha9K35nqkFk85CyQYn2eY/edit#gid=932148422'

new_url = convert_google_sheet_url(url)

onlineDF = pd.read_csv(new_url)
localDF = pd.read_csv('./videos_tbl.csv')

channel_category_dict = onlineDF.set_index('channelId')['Category'].to_dict()
channels = localDF['channelId']

categories = []

if __name__ == "__main__":
    for channelId in channels:
        categories.append(channel_category_dict.get(channelId))
    if(len(channels) == len(categories)):
        newDF = localDF.assign(category = categories)
        newDF.to_csv('./videos_tbl.csv', index=False)
    else:
        print('Unable to find some categories')

