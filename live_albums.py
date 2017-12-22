"""
Matt Levin - 2017

Isolates albums that are a single live show (or several nights of live shows) for the given artist (Spotify ID
as command-line argument, defaults to Grateful Dead). Then extracts the dates and generates (and opens) an 
HTML page with these albums in chronological order, with links to open each in Spotify and cover art, as well 
as a navigation bar to quickly jump to a given year. Also contains a function called find_artists which 
recursively explores related artists to find other artists that have a lot of live albums.

I made this because by default albums are ordered by their release date on Spotify, however it would be nice to 
be able to navigate live shows by the date of the show, not when it was released as an album. 

Note: I made the design decision to include albums that are multiple nights (i.e. 5/7/72 & 5/10/72) but not 
compilations from a year or month (i.e. April 1971) -- Sometimes it's impossible to tell (without looking at 
each song title) if it's a compilation or just 2 or 3 different almost-full live sets. 


Usage:
     python live_albums_sorted.py [-a Artist_ID] [-i]
        - Generates and opens HTML for artist's live albums (Grateful Dead by default)
	- The -i flag can be set to include albums with no live date found, using their release date to sort
     python live_albums_sorted.py -x [-a Artist_ID] [-n Number of Hops] [-i]
        - Explores related artists starting from Artist_ID (defaults to Grateful Dead) with 
	   n recursive hops (defaults to 2) and prints the ones with the most live albums found
	- The -i flag can be set to include albums with no live date found in the counts


~ I have no affiliation with Spotify ~

"""
import spotipy # Spotify Python wrapper (https://github.com/plamere/spotipy)
import spotipy.util as util
import re # Regular Expressions for parsing dates from album names
import os # for path when opening the HTML file
import webbrowser # for opening HTML in webpage
import heapq # for ordering albums automatically by the extracted date
import sys
import time
try:
    import my_info # Spotify info (i.e. username, client secret) hidden from Git
except ImportError: # Will get this error if you forked / copied from Git
    print('This script requires credentials, see README.md for details' +
           ' or sample_output folder for example output.')
    sys.exit(1)


#debugging = True # Show debug messages
debugging = False # Hide debug messages
def debug(s):
    if debugging:
	print(s)

""" 
Isolates live albums (based on the album name containing a full date or not) and returns a heap, using
the date (show date, as opposed to album release date) as the key for sorting (YYYYMMDD).

Note: Albums such as "Best of 2015", "Live April 1995", or "Live at RFK Stadium" were excluded due to 
either not being a contiguous show, or not having a specific date to be used in sorting.

PARAMS:
     artist_id - The Spotify ID for the artist
     include_no_date [Optional] - Include albums that say "Live At/In/From", defaults to False (TODO)
RETURN:
     heapq of (date : album_object) of the albums that had a full date in their name

"""		                                 
def get_live_albums(artist_id, include_no_date=False):
        # Get all the albums for the artist, 50 at a time (API limit)
        albums, offset = [], 0
        while True:
	    next_batch = sp.artist_albums(artist_id, album_type='album', limit=50, offset=offset)['items']
	    albums += next_batch
	    offset += 50
	    if len(next_batch) != 50: # If this is the last batch, break loop
		break
        
        live_albums = [] # Albums that are a single* live show, not live compilations
	# *I decided to also include albums that are several live shows (i.e. 5/12/80 & 5/14/80)
        #debug(len(albums)) # Print the total number of albums if in debug mode
        
        months = ['January','February','March','April','May','June','July',
	            'August','September','October','November','December']  # Month strings

        for album in albums:
            name = album['name'].encode('utf-8')
	    # Note: Albums are determined to be live if a date is found in their album title
	    #        this is obviously not 100% effective, and albums such as "Live at the Fillmore"
	    #        can be optionally included, sorted by album release date, if include_no_date is True.
            
            # Match: ', YYYY' or '# YYYY'
            year_re = re.search('(,|[0-9]|-)\s*([0-9]{4})', name)
	    # Match: 'MM/DD/YYYY' or 'MM.DD.YYYY' (or 1 M or 1 D or 2 Y)
            date_re = re.findall('([^0-9]|^)([0-9]+)[/\.\-]([0-9]+)[/\.\-]([0-9]+)([^0-9]|$)', name) 
            # Match: 'Live at/from/in' for including albums with no date in the title (won't be sorted right)
	    if include_no_date:
		live_re = re.search('Live (From|At|In)\s[^Concert]', name, re.IGNORECASE)
	    else:
		live_re = False
             
            # Format with the month as a string then day and year as numbers
            if year_re:
		month_day_re = re.search(r'({})'.format('|'.join(months)) + r' ([0-9]{1,2})([^0-9]|$)', name)
            	day_re = re.findall('[^0-9]([0-9]{1,2})[^0-9]', name) # Finds all 1 or 2 digit numbers (day)
            	if(len(day_re) > 1): # Include albums that are multiple nights?
		    # continue # No, skip
		    pass # Yes, keep going using the first night listed for sorting
		if(len(day_re) == 0): # If no day was found, skip this album
		    continue
            	
            	if month_day_re == None:
		    continue # No Month Day pattern found, skip
            	# Add '0' to day if needed
		day = month_day_re.group(2)
            	if(len(day) == 1):
		    day = '0' + day
                # Add '0' to month if needed
		month = months.index(month_day_re.group(1))
                if(month < 9):
		    month = '0' + str(month + 1)
                else:
		    month = str(month + 1)
                # Generate the key for sorting - YYYYMMDD
                key = year_re.group(2) + month + day
                # print(name)
                # print(key)
                heapq.heappush(live_albums, (key, album))

            # Simpler MM/DD/YYYY format (1 M or 1 D or 2 Y digits all valid too i.e. 8/4/72 --> 08/04/1972)
            elif len(date_re) > 0:
            	date = date_re[0]
                y = date[3]
                if(len(y) == 2):
                    if(int(y) < 25): # Educated guess on the century
                        y = '20' + y
                    else:
                        y = '19' + y
                m = date[1]
                if(len(m) == 1):
                    m = '0' + m
                d = date[2]
                if(len(d) == 1):
                    d = '0' + d
                #debug('{}/{}/{}'.format(m,d,y))
                key = y + m + d # Key for sorting - YYYYMMDD
                heapq.heappush(live_albums, (key, album))
            
            elif live_re:
		# If there is no full date in the album name, just use the release date of the album
		# This relies on the album being released near the time of the show, which isn't always true,
		# which is why including this is an option and is excluded by default (include_no_date=False).
		album_full = sp.album(album['id']) # Need to get full album object to get release date
		key = "".join(album_full['release_date'].split('-')) # Extract release data as YYYYMMDD
		if(len(key) == 4): # Year precision
		    key += "9999" # Pad with 9's, will be shown last of the year
		elif(len(key) == 6): # Month precision
		    key += "99" # Pad with 9's, will be shown last of the month
		heapq.heappush(live_albums, (key, album))
	
	# Return the heap to be processed in generate_html
	return live_albums


"""
Generates the HTML page for this artist's live albums in chronological order, with cover art and 
links to stream each album on Spotify. 

PARAMS: 
     artist_id - Spotify ID for this artist
     live_albums - Heap of (date_key, album_object) produced by get_live_albums(artist_id)
RETURN:
     HTML string that shows the artist's live albums (with cover art and links to albums on Spotify)
"""
def generate_html(artist_id, live_albums):
        artist_name = sp.artist(artist_id)['name'] # Query Spotify for the artist's name
	# Start the HTML string, very barebones CSS
        background = "#AFCDD3"
        html = """<html><head>
	            <title>Live Albums (""" + artist_name + """)</title>
	            <link rel="icon" href="https://findicons.com/files/icons/2332/super_mono/64/music.png">
	            <style>
	                    img {margin: 1em;}
	                    html {background-color: """ + background + """; font-family: Arial;}
	                    #title {font-size: 250%;}
	                    a {text-decoration: none;}
	                    #menu {float:right; position:fixed; top:4em; right:3em; background:"""+background+""";"}
	            </style>
	        </head><body><h1 id='title'>""" + artist_name + """ Live Albums in Chronological Order</h1><table>\n"""
        year = [-1, -1] # (Year, Count of Albums from Year)
        years = [] # List of above "tuples" used to create the menu bar
        debug(len(live_albums))
        for (key, album) in heapq.nsmallest(len(live_albums), live_albums):
            # New year
            if(key[0:4] != year[0]):
		if(year[0] != -1): # If this isn't the very first time (initialized to -1)
		    years.append(year) # Enter the last year's entry		    
                year = [key[0:4], 1] # New entry for this year, count starts at 1
		if(year[0] == '9999'):
		    break # This is for any that were unsorted (Live At/From/In), just ignore these
                html += "<tr><td id=\"{}\"><h1>{}</h1><hr></td></tr>\n".format(year[0], year[0])
            else:
                year[1] += 1 # Increment count for this year (this is why I used an array, not immutable tuple)
                
            # Extrct album name, link to it on Spotify, and album art
            link = album['external_urls']['spotify']
            name = album['name']
            img = album['images'][0] # Just use the first image and scale it down
            # Create the <img> tag
            img_html = "<img src={} width={} height={}>".format(img['url'], 
                                                            int(img['width']/4), int(img['height']/4))
            
            # Write the HTML entry for this album as a table row (link, name, img)
            html += "<tr><td><a target=\"_blank\" href={}>{}<br>{}</a><hr></td></tr>\n".format(link, name, img_html)
        
        if(len(live_albums) == 0): # No live albums were found
	    html += "<tr><td>Unable to extract any albums with a full date in the name for sorting.</td></tr>"
        
        html += "</table>\n" # Close the <table> tag
        
        # Year menu to skip to a certain year using it's HTML ID
	# It just floats awkwardly on the top right for now, I'm not focusing on UI/UX
        html += "<div id='menu'>\n"
        for (year, count) in years:
            html += "<a href=#{}><strong>{} ({})</strong></a><br>\n".format(year, year, count)
        html += "<div>\n"
        
        # Close HTML and return it to be written to an HTML file in main
        html += "</body></html>"
	return html


"""
Recursively explores (Depth-First) related artists and calculates how many live albums are found using
the get_live_albums function. Maintains a heap of the artists in order to keep track of which had the 
most live albums (according to the regular expressions) in order to try to find other artists to experiment
with.

Note: If the optional parameter include_no_date is set to True, albums that don't have a full date in their 
name will also be included in the count, however will still be excluded if HTML is later generated since 
they can not be sorted without a full date. (Defaults to False)

PARAMS:
     seed_artist [Optional] - The ID of the artist to begin the search with, deafaults to Grateful Dead's ID
     recursion_limit [Optional] - The number of recursive hops to make in the depth first search, default is 2
     include_no_date [Optional] - Include albums with no full date in their name? i.e 'Live At/From/In...'
RETURN:
     Nothing for now, perhaps later it could return ~5 artists with the highest number of live albums found
     (Just using this as a tool to find other artists that would be interesting to generate HTML for)
"""
def find_artists(seed_artist='4TMHGUX5WI7OOm53PqSDAT', recursion_limit=2, include_no_date=False):
    artists_heap = [] # Heap of (live_album_count : (artist_id, artist_name))
    seen = [] # List of artists explored already (IDs)
    
    # Explores an artist - Adds ID to seen, updates artists_heap with their entry, and 
    # if there are still recursive hops to be made, explores related artists.
    def explore(artist_id, artist_name, limit):
	debug("Exploring {} with {} hops remaining.".format(artist_name, limit))
	seen.append(artist_id) # Avoid exploring the same artist twice / loops
	# Calculate the number of live albums, defaults to including those with no date in the name
	num_live = len(get_live_albums(artist_id, include_no_date=include_no_date))
	# This DFS could be modified to do anything, not just count live albums... endless possibilities
	#debug('# Live Albums = {}'.format(num_live))
	# Add entry to the heap
	heapq.heappush(artists_heap, (num_live, (artist_id, artist_name)))
	if limit == 0: # Stop recursing if reached the limit
	    return
	# Get the related artists for this artist
	related_artists = sp.artist_related_artists(artist_id)['artists']
	for other_artist in related_artists: # For each related artist (DFS used instead of BFS)
	    other_id = other_artist['id'].encode('utf-8') # Extract ID
	    if other_id not in seen: # If not explored already, explore it (with decremented recursion limit)
		explore(other_id, other_artist['name'].encode('utf-8'), limit - 1)
		# TODO: Multi-Threading? Would need thread-safe artists_heap and seen structures

    # Explore the initial seed artist with the initial recursion hop limit
    seed_name = sp.artist(seed_artist)['name'].encode('utf-8') # First extract the name
    print('Exploring related artists starting from {} with {} recursive hops...'.format(seed_name, recursion_limit))
    # Explore the initial seed artist with the initial recursion hop limit    
    t = time.time()
    explore(seed_artist, seed_name, recursion_limit) # Call explore
    elapsed_time = time.time() - t
    
    # Print info about how many explored, the source artist, number of hops used
    print("Explored {} artists in {} recursive hops, starting from {}.".
          format(len(artists_heap), recursion_limit, seed_name))
    # Print the artists with the most live albums found
    msg = "Artists with most live albums found"
    if include_no_date:
	msg += " (Including albums with no full date in the title)"
    print(msg + ":")
    for (count, artist) in heapq.nlargest(10, artists_heap):
	print("{:<3}- {:30} - {}".format(count, artist[1], artist[0]))
    
    print("Elapsed Time: {}s".format(elapsed_time))
    

"""
Main Method, acquires access token using the info from my_info.py then extracts the live albums for
the artist specified in the command line argument (or the Grateful Dead by default) and then sorts them
and creates an HTML file (live_albums.html) containing the live albums in order, with cover art and 
links to stream each on Spotify.
"""
if __name__ == "__main__":  
    
    scope = ' ' # Just needs public access for this script
    token = util.prompt_for_user_token(my_info.username, scope, 
                                       client_id=my_info.client_id, 
                                       client_secret=my_info.client_secret, 
                                       redirect_uri=my_info.redirect_uri)   

    # If successfully created an authentication token with Spotify
    if token:
	sp = spotipy.Spotify(auth=token)
	
	# Default arguments - Don't do explore, isolate live albums and make HTML for Grateful Dead
	explore = False # -x Flag
	include = False # -i Flag (Include live albums with no date in title, may mess up ordering)
	num_hops = 2
	artist_id = "4TMHGUX5WI7OOm53PqSDAT"  # Grateful Dead
	#artist_id = "5wbIWUzTPuTxTyG6ouQKqz" # Phish
	#artist_id = "1YTe4dNIoWX3iHX8H4xVeM" # Jerry Garcia Band
	#artist_id = "4wQ3PyMz3WwJGI5uEqHUVR" # Allman Brothers	
	
	# Parse command line arguments
	i = 1
	try:
	    while(i < len(sys.argv)):
		if(sys.argv[i] == '-x'): # Run explore, not generate HTML
		    explore = True
		elif(sys.argv[i] == '-i'): # Include albums with no full date in title (affects ordering)
		    include = True
		elif(sys.argv[i] == '-a'): # Artist ID, defaults to Grateful Dead (above)
		    i += 1
		    artist_id = sys.argv[i]
		elif(sys.argv[i] == '-n'): # Number of recursive hops if using explore
		    i += 1
		    num_hops = int(sys.argv[i]) # Note: This exponentially affects the big-Oh runtime
		else:
		    raise Exception
		i += 1
	except:
	    print("Invalid arguments provided. See README.md for correct usage.")
	    sys.exit(1)	    	
    
	# If they accidentally pass the full URI or link instead of just ID, isolate the ID
	if ':' in artist_id:
	    artist_id = artist_id.split(':')[-1]
	if '/' in artist_id:
	    if artist_id[-1] == '/':
		artist_id = artist_id[:-1] # Remove trailing / if present
	    artist_id = artist_id.split('/')[-1]
	
	if explore: # If using -x flag, explore related artists
	    find_artists(artist_id, recursion_limit=num_hops, include_no_date=include) # Finding new artists to try out
	    sys.exit(1)
	else: # Not using -x flag, isolate the live albums and generate HTML
	    # Isolate live albums, return a heap with the date (YYYYMMDD) as the key
	    artist_live_albums = get_live_albums(artist_id, include_no_date=include)
	    
	    # Generate the HTML string that shows live albums in order with cover art and links to Spotify
	    html = generate_html(artist_id, artist_live_albums)
	    
	    # Write HTML to outfile    
	    f = open("live_albums.html", "w+")
	    f.write(html)
	    f.close()
	    
	    # Open in web browser
	    webbrowser.open('file://' + os.path.realpath('live_albums.html'))	
    
    else:
	print("Unable to get access token.")