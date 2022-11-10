import spotify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import yt_dlp
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

youtube_api = os.getenv("YOUTUBE_API")

data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}

def GetAudio(link, path):
  ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': path + '%(title)s.%(ext)s'
  }

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([link])

def GetExistingSongs(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    songs = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
      for filename in files:
        songs.append(filename)  # Add it to the list.


    for i, song in enumerate(songs):
      # Remove file extension
      tmp = song.split('.')
      tmp = tmp[:-1]
      tmp = ".".join(tmp)
      songs[i] = tmp

    return songs  # Self-explanatory.

def GetVideos(tracks):
  youtube_data = []

  driver = webdriver.Chrome()
  for track in tracks:
    query = track['name'] + " - " + " ".join(track['artists'])

    youtube_url = "https://www.youtube.com/results"
    driver.get(youtube_url+ "?search_query=" + query)

    print('Searching for video:', query)

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

def main():

  parser = argparse.ArgumentParser()
  parser.add_argument("-o", "--output", action='store', default="songs/", help='Folder to export to')
  args = parser.parse_args()

  path = args.output

  if path[-1] != "/":
    path = f"{path}/"

  spotify_track_list = "spotify.json"
  youtube_search_list = "track_lists.json"

  if not os.path.isfile(spotify_track_list):
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

    with open(spotify_track_list, 'w') as f:
      json.dump(tracks, f)
  else:
    with open(spotify_track_list) as f:
      tracks = json.load(f)

  # If the list of tracks with links etc (already searched on YouTube) does not exist, then get 'em
  if not os.path.isfile(youtube_search_list):
    links = GetVideos(tracks)
  else:
    with open(youtube_search_list) as f:
      links = json.load(f)

  # Get a list of existing songs
  current_songs = GetExistingSongs(path)

  print(current_songs)

  # Download the songs to the given directory
  for link in links:
    print("Query title: {}".format(link['query']['name']))
    print("Found song: {}".format(link['found']['title']))
    if link['found']['title'] not in current_songs:
      GetAudio(link['found']['link'], path)
    else:
      print("Already downloaded!")


if __name__ == "__main__":
  main()