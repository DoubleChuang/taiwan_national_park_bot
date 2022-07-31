# Taiwan National Park Bot

A bot to help you send the application for Taiwan National Park permits.

## Installation

This bot requires **Python >= 3.6**.
Please install it by:

```shell
git clone git@github.com:chenjr0719/taiwan_national_park_bot.git
cd taiwan_national_park_bot
pip install .
```

Or, just run it in a Docker container:

```shell
git clone git@github.com:chenjr0719/taiwan_national_park_bot.git
cd taiwan_national_park_bot
./scripts/build.sh
```

## Usage

Before using the bot, please make sure you already create a drfat on https://npm.cpami.gov.tw.
Then, your **ID** and **email** in environment variable:
```shell
export ID=...
export EMAIL=...
```

Or, create a `.env` file and run the Docker container with it:
```shell
./scripts/run.sh
```


# Taiwan National Park Bot V2
## develop

### run from source
```
export PYTHONPATH=$PYTHONPATH:`pwd`
python3 tnpb/__main__2.py

docker run -d --name=selenium-hub --rm -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome:4.2.0

ID=YOUR_ID \
EMAIL=YOUR_EMAIL \
CHROME_REMOTE_URL=http://selenium-hub:4444/wd/hub \
python3 sel.py
```

## docker-compose
#### Build tnpb docker image
```
./scripts/build.sh
```

#### Create a .env file by referring to the example below
Before using the bot, please make sure you already create a drfat on https://npm.cpami.gov.tw.
Then, your **ID** and **EMAIL** in environment variable:

```
ID=YOUR_ID
EMAIL=YOUR_EMAIL
CHROME_REMOTE_URL=http://selenium-hub:4444/wd/hub
```
> If you have not adjusted the container name and binding port, you do not need to adjust **CHROME_REMOTE_URL**

#### Create and start containers
```
docker-compose up -d
```

#### Stop and remove containers, networks
```
docker-compose down
```


### reference

[chromium driver](https://chromedriver.chromium.org/downloads)


### TODO
- [ ] v2 tnpb v2 bot code 
- [ ] check opencv-python version
- [ ] dynamic change draft date
- [ ] github action
- [ ] 