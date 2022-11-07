import spotify
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import time
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

youtube_api = os.getenv("YOUTUBE_API")

data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}

tracks_file = "tracks.json"

if not os.path.isfile(tracks_file):
  s = spotify.spotify(client_id, client_secret)

  playlists = s.GetPlaylists('fraser148')

  the_playlist_id = ""

  for playlist in playlists:
    print(playlist['name'])
    if playlist['name'] == "The Playlist":
      the_playlist_id = playlist['href'].split('/')[-1]

  tracks_output = s.GetTracks(the_playlist_id)

  tracks = []


  for track in tracks_output:
    artists = []
    for artist in track['track']['artists']:
      artists.append(artist['name'])

    tracks.append({
      'name': track['track']['name'],
      'artists': artists
    })

  with open(tracks_file, 'w') as f:
    json.dump(tracks, f)
else:
  with open(tracks_file) as f:
    tracks = json.load(f)

def GetAudio(link):
  ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'songs/%(title)s.%(ext)s'
  }

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([link])


def GetVideos(tracks):
  youtube_data = []

  driver = webdriver.Chrome()
  for track in tracks:
    query = track['name'] + " - " + " ".join(track['artists'])

    youtube_url = "https://www.youtube.com/results"
    driver.get(youtube_url+ "?search_query=" + query)

    print('Extracting results. It might take a while...')

    try:
      button = driver.find_element(By.CSS_SELECTOR, '.yt-spec-button-shape-next.yt-spec-button-shape-next--filled.yt-spec-button-shape-next--call-to-action.yt-spec-button-shape-next--size-m')
      button.click()
    except NoSuchElementException:
      print('no button')

    list = driver.find_element(By.CSS_SELECTOR, '#contents.style-scope.ytd-item-section-renderer')
    searches = list.find_elements(By.CSS_SELECTOR, '.style-scope.ytd-item-section-renderer')
    found = False
    i = 0

    while not found and i < len(searches):
      try:
        title = searches[i].find_element(By.CSS_SELECTOR, '.title-and-badge.style-scope.ytd-video-renderer').text
        link = searches[i].find_element(By.CSS_SELECTOR, '.title-and-badge.style-scope.ytd-video-renderer a').get_attribute('href')
        views = searches[i].find_element(By.CSS_SELECTOR, '.style-scope.ytd-video-meta-block').text.split('\n')[0]

        found = True

        youtube_data.append({
          'query': track,
          'found': {
            'title': title,
            'link': link,
            'views': views,
          }
        })

      except:
        print("Error, moving to next")
        i += 1
        

  print(json.dumps(youtube_data, indent=2, ensure_ascii=False))

  with open('track_lists.json', 'w') as f:
    json.dump(youtube_data, f)

  driver.quit()

  return youtube_data

print(tracks)

links = GetVideos(tracks)

with open('track_lists.json') as f:
  links = json.load(f)

# print(links)

# for link in links:
#   GetAudio(link['found']['link'])