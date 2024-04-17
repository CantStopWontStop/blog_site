# %%
import os
import pandas as pd
from datetime import date
from shutil import copy as cpy
import re
import requests
from PIL import Image
from io import BytesIO
import random


import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

# %%
#working directory for homepage

dir_path = 'c:/Digital_Projects/GitHub/afromation/blog_site'



#path for daily posts 
today = date.today().strftime("%Y-%m-%d")
path = os.path.join('c:\\Digital_Projects\\GitHub\\afromation\\blog_site\\posts', today)

dir_to_post_path = f'c:/Digital_Projects/GitHub/afromation/blog_site/posts/{today}'

os.mkdir(path)

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

# %%
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

SERVICE_ACCOUNT_FILE =  "afromation-key.json"


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

#df  = pd.read_csv('youTubeChannels.csv')

#df[['id', 'Creator', 'Category']]
#channels = ['UC12lU5ymIvSpgl8KntDQUQA']

channels = df['channelId']


if __name__ == "__main__":
    for chan in channels:
        main(chan)

# %%
thumbnail_urls = [item.get('thumbnails', {}).get('high', {}).get('url', None) for item in video_meta]

# %%
meta = pd.DataFrame.from_dict(video_meta)
video_meta_df = meta.assign(videoID = video_id,
                            thumbnail_url = thumbnail_urls)



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

# %%
meta = pd.DataFrame.from_dict(video_meta)
video_meta_df = meta.assign(videID = video_id,
                            embeds = embed_codes)
video_meta_df = pd.merge(video_meta_df, df, on='channelId')
video_meta_df = video_meta_df.sort_values(by=['publishedAt'], ascending=False)
video_meta_df.to_csv(os.path.join(path, 'videos_tbl.csv'))

# %%
today_title = date.today().strftime("%B %d, %Y")
samples     = video_meta_df['title'][0:5]
subtitles   = ['; '.join(samples[0 : 5])]
thumbnails  = random.sample(thumbnail_urls,4)

# %%
post_markdown_content = f"""
---
date: {today}
title: 'Daily Update'
author: 'Afromation Digital'
image: thumbnail.jpg
format: 
    html:
      toc: false
title-block-banner: true
execute:
    echo: false
    warning: false
    message: false

categories:
    - 'daily feed'

---
'{subtitles[0]}'

```{{r}}

library(tidyverse)

videos_tbl <- read_csv('videos_tbl.csv') |> 
  mutate(embeds = embeds |> 
           str_replace_all('480', '100%') |> 
           str_replace_all('270', '50%'))


```

```{{r}}
#| echo: false

videos_joined <- videos_tbl |> 
    select(publishedAt,title, description, embeds, 
           channelId, Category) |> 
    filter(publishedAt >= lubridate::today()-1)

videos <- videos_joined |>  
    split(videos_joined$Category) 
    

headings <- names(videos)

```

##  {today_title}

```{{r, results='asis'}}
#| warning: false

for (i in seq_along(videos)) {{
    cat("## ", headings[i], "\\n")
    current_df <- videos[[i]]
    
    cat("::: {{#listing-listing .quarto-listing .quarto-listing-container-grid}}", '\\n')
    cat('::: {{.list .grid .quarto-listing-cols-3}}', '\\n')
    
    for (i in seq_along(current_df$embeds)) {{
      if (!is.na(current_df$embeds[i])) {{  # Check if the embed is not empty
        cat("::: g-col-1", '\\n')
        cat("::: {{.quarto-grid-item .card .h-100 .card-left}}", '\\n')
        cat('::: {{.listing-item-img-placeholder .card-img-top style="height: 150px;"}}', '\\n')
        cat(current_df$embeds[i],'\\n')
        cat(":::",'\\n')
        cat("::: {{.card-body .post-contents}}",'\\n')
        cat('<h5 class="card-title listing-title">', current_df$title[i],'</h5> \\n')
        cat("::: {{.card-attribution .card-text-small .justify}} ",'\\n')
        cat("::: listing-author ",'\\n')
        cat(current_df$channelTitle[i],'\\n')
        cat(":::",'\\n')
        cat('\\n')
        cat("::: listing-date ",'\\n')
        cat(format(current_df$publishedAt[i], "%b %d"),'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
      }}
  }}
    cat(":::",'\\n')
    cat(":::",'\\n')
}}

```

"""

# Save to a Markdown file
file_name = os.path.join(path,'index.qmd')
with open(file_name, "w", encoding="utf-8") as file:
    file.write(post_markdown_content)

# %%

def open_image_from_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Download and open images
images = [open_image_from_url(url) for url in thumbnails]

# Create a 2x2 collage
collage = Image.new('RGB', (2 * images[0].width, 2 * images[0].height))

# Paste images into the collage
collage.paste(images[0], (0, 0))
collage.paste(images[1], (images[0].width, 0))
collage.paste(images[2], (0, images[0].height))
collage.paste(images[3], (images[0].width, images[0].height))


collage.save(os.path.join(path,'thumbnail.jpg'))
collage.show()


# %%
home_markdown_content = f"""
---
title: "Home"
page-layout: full
title-block-banner: true
format:
  html:
    css: assets/css/feed_header.css
    
listing:
  contents: stories
  id: stories
  sort: "date desc"
  type: grid
  categories: false
  sort-ui: false
  filter-ui: false

---
# [Stories]{{.updates}}
::: {{#stories}}
:::

```{{r}}

library(tidyverse)

videos_tbl <- read_csv('{dir_to_post_path}/videos_tbl.csv') |> 
  mutate(embeds = embeds |> 
           str_replace_all('480', '100%') |> 
           str_replace_all('height="270"', ''))


```

```{{r}}
#| echo: false

videos_joined <- videos_tbl |> 
    select(publishedAt,title, description, embeds, 
           channelId, channelTitle, Category) |> 
    filter(publishedAt >= lubridate::today()-1)


videos <- videos_joined |>  
    split(videos_joined$Category) 
    

headings <- names(videos)
```

# [Updates – {today_title}]{{.updates}}

```{{r, results='asis'}}
#| warning: false

for (i in seq_along(videos)) {{
    cat("## ", headings[i], "\\n")
    current_df <- videos[[i]]
    
    cat("::: {{#listing-listing .quarto-listing .quarto-listing-container-grid}}", '\\n')
    cat('::: {{.list .grid .quarto-listing-cols-3}}', '\\n')
    
    for (i in seq_along(current_df$embeds)) {{
      if (!is.na(current_df$embeds[i])) {{  # Check if the embed is not empty
        cat("::: g-col-1", '\\n')
        cat("::: {{.quarto-grid-item .card .h-100 .card-left}}", '\\n')
        cat('::: {{.listing-item-img-placeholder .card-img-top style="height: 150px;"}}', '\\n')
        cat(current_df$embeds[i],'\\n')
        cat(":::",'\\n')
        cat("::: {{.card-body .post-contents}}",'\\n')
        cat('<h5 class="card-title listing-title">', current_df$title[i],'</h5> \\n')
        cat("::: {{.card-attribution .card-text-small .justify}} ",'\\n')
        cat("::: listing-author ",'\\n')
        cat(current_df$channelTitle[i],'\\n')
        cat(":::",'\\n')
        cat('\\n')
        cat("::: listing-date ",'\\n')
        cat(format(current_df$publishedAt[i], "%b %d"),'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
        cat(":::",'\\n')
      }}
  }}
    cat(":::",'\\n')
    cat(":::",'\\n')
}}

```

"""

# Save to a Markdown file
file_name = os.path.join(dir_path,'index.qmd')
with open(file_name, "w", encoding="utf-8") as file:
    file.write(home_markdown_content)


