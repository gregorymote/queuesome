import os
import sys
import json
import spotipy
import webbrowser
import time
import spotipy.util as util
from json.decoder import JSONDecodeError

# Get the username from terminal
username = input("Enter in your spotify user name: ")
scope = 'user-read-private user-read-playback-state user-modify-playback-state'

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope, client_id='6de276d9e60548d5b05a7af92a5db3bb',client_secret='4ebf1b0ef7a34002bf95f8c2aa8365b0',redirect_uri='http://google.com/') # add scope
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id='6de276d9e60548d5b05a7af92a5db3bb',client_secret='4ebf1b0ef7a34002bf95f8c2aa8365b0',redirect_uri='http://google.com/') # add scope

# Create our spotify object with permissions
spotifyObject = spotipy.Spotify(auth=token)

user = spotifyObject.current_user()

displayName = user['display_name']


deviceResults = spotifyObject.devices()
deviceResults = deviceResults['devices']


print("Hi "+ displayName + " Here are your available playback devices: ")
n = 0
for devices in deviceResults:
    print(str(n) + " DEVICE: " + devices['name'])
    n+=1
print()

deviceResults = spotifyObject.devices()
deviceNumber = input("Enter the number associated with the Device you would like for playback: ")
deviceID = deviceResults['devices'][int(deviceNumber)]['id']

players = input("Enter the number of players: ")

#Initialize queue lists 
trackSelectionList = []
trackArtList = []

while True:
    trackSelectionList = []
    trackArtList = []
    for x in range(0, int(players)):
        print()
        print(">>> Welcome to Queue it Up Player " + str(x) + " ")
        print()
        print("0 - Search for an artist")
        print("1 - Search for a track")
        print("2 - Exit")
        print()
        choice = input("Your choice: ")

        # Search for the artist
        if choice == "0":
            print()
            searchQuery = input ("What's the Artist Name?: ")
            print()

            #Get Search Results
            searchResults = spotifyObject.search(searchQuery, 5, 0, "artist")
            a = 0
            artist = searchResults['artists']['items']
            for items in artist:
                print(str(a) + " " + items['name'])
                a+=1
            artistNumber = input("Enter the number associated with the Artist: ")

            #Artist details
            artist = searchResults['artists']['items'][int(artistNumber)]
            print(artist['name'])
            print()
            artistID = artist['id']
            
            #Albums and Track Details
            trackURIs = []
            trackArt = []
            z = 0
            
            #Display the artist's top 10 songs
            topTracks = spotifyObject.artist_top_tracks(artistID)
            track = topTracks['tracks']
           
            for tracks in track:
                albumArt = tracks['album']['images'][0]['url']
                print (str(z) + " " 'track    : ' + tracks['name'])
                trackURIs.append(tracks['uri'])
                trackArt.append(albumArt)
                z+=1
            
            songSelection = input("Player " + str(x) + " Enter the number associated with the Song youre tryna queue (or x to exit): ")
            if songSelection == "x":
                break
            trackArtList.append(trackArt[int(songSelection)])
            trackSelectionList.append(trackURIs[int(songSelection)])
            
  
    # Search for the track
        if choice == "1":
            print()
            searchQuery = input ("What's the Song Name?: ")
            print()

            #Get Search Results
            searchResults = spotifyObject.search(searchQuery, 5, 0, 'track')
            trackURIs = []
            trackArt = []
            a = 0

            track = searchResults['tracks']['items'] 
            for items in track:
                albumArt = items['album']['images'][0]['url']
                artistName = items['artists'][0]['name']  
                print(str(a) + " " + items['name'] + " by " + artistName)
                trackURIs.append(items['uri'])
                trackArt.append(albumArt)
                a+=1
   
                
            songSelection = input("Player " + str(x) + " Enter the number associated with the Song youre tryna queue (or x to exit): ")
            if songSelection == "x":
                break
            
            trackArtList.append(trackArt[int(songSelection)])
            trackSelectionList.append(trackURIs[int(songSelection)])
   
    #End the program
        if choice == "2":
            break
            
    #print(json.dumps(trackSelectionList, sort_keys=True, indent=4))
    spotifyObject.start_playback(deviceID, None, trackSelectionList) 
    for x in range(len(trackSelectionList)): 
        webbrowser.open(trackArtList[x])    
        #Time of song play
        time.sleep(10)
        if x+1 < len(trackSelectionList):
            spotifyObject.next_track(deviceID)
        else: 
            spotifyObject.pause_playback(deviceID)

    
#print(json.dumps(user, sort_keys=True, indent=4))
