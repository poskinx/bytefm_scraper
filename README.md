<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>
<br />
This work and all the resulting documents (CSV, and others) are licensed under a 
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

# bytefm_scraper
This project is the result of PRAC1 of the subject "Tipologia i cicle de vida de les dades" of the Master of Data 
Science of the UOC (Universitat Oberta de Catalunya).

## Description

The bytefm_scraper project scraps content from the online radio https://www.byte.fm/.
You can filter content by periods of time and program name.
The results are store in a csv output file.

## Installation

### virtualenv

1. Create a virtualenv.
    ```bash
    virtualenv venv
    ```
2. Activate your new virtualenv
    ```bash
    source venv/bin/activate
    ```
3. Install the project requirements in your virtualenv.
    ```bash
    pip install -r requirements.txt
    ```

### Optional installation

The code comes with a handy mongodb wraper to store downloaded content.

1. You can install mongo service from: https://docs.mongodb.com/manual/installation/.

2. After that, you have to install the cache-requirements.txt:
    ```bash
    pip install -r cache-requirements.txt
    ```

## Usage

The main.py script file is the one in charge of starting the scraper.
It contains some parameters to control some options.

```bash
$ python main.py -h
usage: main.py [-h] --output-dir OUTPUT_DIR --start-date START_DATE --end-date
               END_DATE [--radio-show RADIO_SHOW]
               [--log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}] [--use-cache]

Run Byte FM scraper.

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Directory to write output file. (default: None)
  --start-date START_DATE
                        Start date. Date format: YYYY-MM-DD. (default: None)
  --end-date END_DATE   End date. Date format: YYYY-MM-DD. (default: None)
  --radio-show RADIO_SHOW
                        Radio show name to crawl. (default: None)
  --log_level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        Set the logging output level. (default: INFO)
  --use-cache           Wheter to use mongo cache db. (default: False)
```

### Example

```bash
$ python main.py --output-dir $(pwd -P) --start-date '2020-04-11' --end-date '2020-04-13' --radio-show 'bytefm-am-morgen' --log_level 'INFO' --use-cache
```

In this example, the _output.csv_ will contain the songs played in the program 'ByteFM am Morgen' during 11th and 13th of April of 2020.
And the downloaded content will be stored in mongo because of the --use-cache flag, which is not mandatory.

### Cache performance:

```bash
# Without cache, we have to take into account requests delays:
$ python main.py --output-dir $(pwd -P) --start-date '2020-04-11' --end-date '2020-04-13' --radio-show 'bytefm-am-morgen' --log_level 'INFO'
[ ... ]
Total run: 50.3276078701 seconds

# Getting content from cache:
$ python main.py --output-dir $(pwd -P) --start-date '2020-04-11' --end-date '2020-04-13' --radio-show 'bytefm-am-morgen' --log_level 'INFO'  -
-use-cache
[ ... ]
Total run: 0.358304023743 seconds
```
## Output

The csv columns names are:
* program
* date
* artist
* title
* album (can be missing)
* label (can be missing)

## Structure
```bash
├── main.py                
├── README.md
├── requirements.txt
└── src
    ├── bytefm_scraper.py
    ├── common.py
    ├── downloader.py
    ├── html_parser.py
    ├── __init__.py
    └── mongo_cache.py
```
