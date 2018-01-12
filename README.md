# Concert Crawler - Live Show Finder for Spotify

*Enjoy listening to live shows from your favorite artists on Spotify? Ever want to listen to a show from a specific year, but could only find the albums organized by release date?* 

This project solves this issue by isolating an artist's live albums and sorting them by the date of the show, not the album release. Built around the Spotify Python2.7 Wrapper, [Spotipy](https://github.com/plamere/spotipy), this project identifies albums that have a full date in their title, and extracts the date using regular expressions in order to generate an HTML page showing the live albums in chronological order, with their cover art and links to stream each album in Spotify. 
#### Features
* Isolate the live albums for a given artist and generate an HTML page to easily browse their live recordings ordered by the date of the show, as opposed to the album release date.
* Additional function to recursively explore related artists from a source artist, calculating the number of live albums for each artist, and displaying those with the most live albums to try to find other artists to generate HTML pages for.
* Uses regular expressions to match a wide variety of date formats including:
  * MM/DD/YYYY or MM-DD-YYYY or MM.DD.YYYY
  * Month DD, YYYY
  * Month DD & DD, YYYY or Month DD - DD, YYYY
  * Other variations, including a *th* or *rd* after the day, and dates with only one digit in the month or day, or only two digits in the year *(These are assumed to be from either the 20th or 21st century based on the last two digits).*
* Option to include albums that don't have a full date (Such as *"Live at the Fillmore"* or *"Live in NYC"*) and sort these albums by their release date instead. *Note: this may lead to incorrect ordering, so it is not recommended but it is available.*

#### Usage
* **python live_albums.py [-a Artist_ID] [-i]**
  * Isolates live albums for the given Artist_ID (defaults to *Grateful Dead*) and generates the HTML to browse live albums in chronological order.
  * The -i flag can be set to include albums with no full dates found in the title, however this will affect ordering (Defaults to *False*).
* **python live_albums.py -x [-a Artist_ID] [-n N] [-i]**
  * Recursively explores related artists starting at Artist_ID (defaults to *Grateful Dead*) using N recursive hops (defaults to *2*) and displays the artists explored who had the highest number of live albums.
  * The -i flag can be set to include albums with no full dates found (Defaults to *False*).

*Note: This project relies on application credentials issued through Spotify that are stored in my_info.py, which is hidden from GitHub, so it will not run properly if forked or cloned from GitHub. Please see the sample_output folder for examples for each function.*
#### Sample Output
The output of several example configurations can be found in the sample_output folder, and are described below. *Note: The HTML pages are pretty barebones, as the focus of this project is not on the front-end.*
* **[grateful_dead.html](https://www.matt-levin.com/ConcertCrawler/sample_output/grateful_dead.html)**
  * Shows the usefulness of the tool, since they have 81 live albums (as identified by the regular expressions) on Spotify, spanning many years.
* **[jerry_garcia_band.html](https://www.matt-levin.com/ConcertCrawler/sample_output/jerry_garcia_band.html)**
  * More varied dates are used in these album names, compared to the Grateful Dead albums which had a more uniform style.
* **[allman_brothers_-i.html](https://www.matt-levin.com/ConcertCrawler/sample_output/allman_brothers_-i.html)**
  * Example of what can go wrong using the -i flag, the *Live at Ludlow Garage* album is sorted under 1990 (the album release date) not the show's date (1970) since there is no date in the album name and the -i flag was set to true so it was not skipped.
* **[find_artists_1_hop.txt](https://www.matt-levin.com/ConcertCrawler/sample_output/find_artists_1_hop.txt)**
  * The results of running explore with only 1 hop, starting at *The Allman Brohters* and not including any albums without full dates.
* **[find_artists_1_hop_-i.txt](https://www.matt-levin.com/ConcertCrawler/sample_output/find_artists_1_hop_-i.txt)**
  * The same configuration as above except this time the -i flag is set, which shows that there are several artists who have live albums, that just don't have a full date in the album name and are thus unable to be sorted by show date.
* **[find_artists_10_hops.txt](https://www.matt-levin.com/ConcertCrawler/sample_output/find_artists_10_hops.txt)**
  * The output of explore using 10 hops starting at *Grateful Dead* which explored a grand total of 3849 artists, and displays those with the most live albums.  



&nbsp;

---



*I have no affiliation with Spotify, I just wanted to explore the API and make an easy way to browse live shows by the date of the show itself. All data provided by [Spotify](https://www.spotify.com)'s web API.*
