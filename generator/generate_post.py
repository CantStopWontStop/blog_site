# %%
import os
import pandas as pd
from datetime import date
from shutil import copy as cpy
import re

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

# %%
today = date.today().strftime("%Y-%m-%d")
post_path ='../posts'
path = os.path.join(post_path, today)
path

os.makedirs(path, exist_ok=True)

# %%
cpy('index.qmd', os.path.join(path,'index.qmd'))

# %%
def convert_google_sheet_url(url):
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # Replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url

# %%
# Replace with your modified URL
url = 'https://docs.google.com/spreadsheets/d/1bJIUEOh8yUg46dREnE_bXlha9K35nqkFk85CyQYn2eY/edit#gid=932148422'

new_url = convert_google_sheet_url(url)

df = pd.read_csv(new_url)
df

# %%
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

SERVICE_ACCOUNT_FILE =  "/root/afromation-key.json"


def get_authenticated_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

# %%
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

creds

# %%
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

# %%
video_meta = []
video_id  = []

def main(channelID):
    request = youtube.search().list(
        part='snippet',
        # id="UC12lU5ymIvSpgl8KntDQUQA"
        channelId=channelID,
        order="date",
        type="video",
        maxResults=1
    )

    response = request.execute()

    snippet = response['items'][0]['snippet']
    videoid = response['items'][0]['id']['videoId']
    video_meta.append(snippet)
    video_id.append(videoid)
    print(snippet)
    print(videoid)


# df  = pd.read_csv('youTubeChannels.csv')

#df[['id', 'Creator', 'Category']]
#channels = ['UC12lU5ymIvSpgl8KntDQUQA']

channels = df['id']


if __name__ == "__main__":
    for chan in channels:
        main(chan)

# %%
meta = pd.DataFrame.from_dict(video_meta)
video_meta_df = meta.assign(videoID = video_id)


# %%
video  = []

def main(id):
    request = youtube.videos().list(
        part="player",
        id=id
    )

    response = request.execute()

    video.append(response['items'])



#df[['id', 'Creator', 'Category']]
# channels = ['jh4ln6QcYVE']

vids = video_meta_df['videoID']


if __name__ == "__main__":
    for vid in vids:
        main(vid)

# %%
embed_codes = [item[0]['player']['embedHtml'] for item in video]

embed_codes

# %%
meta = pd.DataFrame.from_dict(video_meta)
video_meta_df = meta.assign(videID = video_id,
                            embeds = embed_codes)
video_meta_df.to_csv(os.path.join(path, 'videos_tbl.csv'))
video_meta_df


