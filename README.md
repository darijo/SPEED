# SPEED
SPEED (a Scalable Python wEb bEhavioural moDel) is an emulation tool for web traffic. SPEED mimics both traffic patterns and user behaviour of modern web browsers. It scales well by focusing on traffic exchange without performing demanding application level user interface functions.

Authors: Darijo Raca <draca@etf.unsa.ba>, Ahmed H. Zahran <a.zahran@cs.ucc.ie>.



Contents:

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Caveats](#caveats)
- [Acknowledgements](#acknowledgements)
- [Helpful info](#helpful-info)
- [License](#license)


## Requirements

- Python 3.6 or higher
- aiohttp library (https://docs.aiohttp.org/en/stable/)
- numpy library (https://numpy.org/)
- scipy library (https://scipy.org/)
- waitress library (https://docs.pylonsproject.org/projects/waitress/en/latest/)
- Flask (https://flask.palletsprojects.com/en/2.1.x/)

## Installation

   Clone the repository: git clone https://github.com/darijo/SPEED.git
   
   ### Install Dependencies
   - pip install Flask
   - pip install waitress
   - pip install aiohttp
   - pip install numpy
   - pip install scipy
   
   
## Usage

### Generate JSON and dummy web content

JSON files are created per user, containing all the information about each webpage, i.e., number of main and inline objects, size (in bytes) of each object. Also, this file stores information about user behaviour for each webpage, reading or dwell time (i.e., how much time user spends "reading" the content). Figure shows the example of JSON file structure.
![](json_example.png)
   

