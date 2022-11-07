import requests

class spotify:
  def __init__(self, client_id, client_secret):
    self.client_id = client_id
    self.client_secret = client_secret
    self.base_url = 'https://api.spotify.com/v1/'

    auth_url = 'https://accounts.spotify.com/api/token'

    data = {
      'grant_type': 'client_credentials',
      'client_id': client_id,
      'client_secret': client_secret,
    }
    auth_response = requests.post(auth_url, data=data)

    try:
      self.access_token = auth_response.json().get('access_token')
      print(self.access_token)
    except:
      raise Exception("Issue authenticating")
  

  def GetPlaylists(self, user):
    url = self.base_url + "users/" + user + "/playlists"
    headers = {
      'Authorization': 'Bearer {}'.format(self.access_token)
    }
    print(headers)

    r = requests.get(url, headers=headers, params={'limit': 5})
    return r.json()['items']

  def GetTracks(self, id):
    url = self.base_url + "playlists/" + id + "/tracks"

    headers = {
      'Authorization': 'Bearer {}'.format(self.access_token)
    }

    r = requests.get(url, headers=headers)
    # print(r.json())
    return r.json()['items']
