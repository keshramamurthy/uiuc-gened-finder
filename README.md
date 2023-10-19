# UIUC General Education Course Finder

This is a public project available [here](https://try.keshav.best/coursefinder/geneds.html) for UIUC students to be able to find General Education courses based on what categories and part of term they're looking for. Students can also use the tool to filter by online/offline courses.

This project has been made available publicly to allow for forking and open-source contribution to the project, or for other students to make their own variations of it.

# Contact me!
I am open to collaboration and additions to this project! You can open an issue on this repo or email me at: keshav4@illinois.edu

## Access
Click [here](https://try.keshav.best/coursefinder/geneds.html) to check out the General Education Course Finder.

Click [here](https://try.keshav.best/coursefinder/index.html) to view some interesting data about the current semester (Spring 2024)!

## Installation
### Requirements
- NodeJS v20+ and NPM v10+
- Python 3.7
- A web server with the port you have specified in `/api/src/index.ts` open (default: 8080)

### Installation Guide
1. `cd` into the `/scraper` directory after installing `requests` with `pip`
2. Edit `store_data.py` with the term, year and database path you are looking to use
3. Run `main.py`
4. `cd` into the `/api` directory and run `npm i -g typescript ts-node-dev`
5. Once done, run `npm i`
6. All necessary prerequisites should be installed now. Run `npm run dev` to test the site on your local machine
7. To run a production-ready version of the site, run `npm run build` and `npm start`