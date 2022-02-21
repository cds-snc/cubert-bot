# Cubert Slack Bot
Cubert is a slack bot that can store and remember organiational knowledge. 

Cubert can record:
  - What you know (I know Python)
  - What another user knows (@Sylvia.mclaughlin knows Python)

Cubert can inform:
  - What everyone knows (what do people know gives listing of all knowledge areas)
  - Who knows about something (who knows about Python will give listing of all users that know Python)
  - Everything you know (what do I know gives listing of all knowledge that you know)
  - Usage/help directions (help will provide usage directions)

Cubert can delete:
  - Specific knowledge that you don’t want recorded (I know know nothing about Python will deregister you from knowing storing Python in the knowledge base)

Cubert is invoked using a slash command /cubert followed by command (ie /cubert I know Python, /cubert what do I know, /cubert help, etc)

A keynote presentation on how to create a new Slack app can be found [here](https://drive.google.com/file/d/1BOODWHq-lMMqGwTluoYWh-9FjbiP8yWr/view).

# How to get Cubert up and running locally

## Prerequisites
- [Python 3.9](https://www.python.org/)
- [Redis DB](https://redis.io/)
- [Ngrok](https://ngrok.com/)
- [Slack API](https://api.slack.com/)
- A new app is created and configured. You can follow the instructions in Cubert_Presentation.key to get instructions on how to create a new app. 

Clone the repository
```
https://github.com/sylviamclaughlin/cubert.git
```
Create a virtual environment
```
python3 -m venv .venv
```
Activate the virtual environment
```
source .venv/bin/activate
```
Install dependencies in requirements.txt file
```
pip3 install -r requirements.txt 
```
## Create .env file
Create an .env file in your cubert direcotry that contains the following information:
```
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
```

## Start your app
Type the following to start your app
```
python3 app.py
```

## Start Ngrok
After you have installed ngrok, you will need to start it up tunelling to port 3000. To do that, type
```
ngrok http 3000
```
Obtain the https url from ngrok and paste and proceed to the following step.

## Update url endpoints in Slack API
In the Slack API:
1. Go to Manage Distribution -> Slash Commands and edit the slash command to change the request URL to:
```
https://your-ngrok-genenrated-url/slack/events
```

2. Go to Manage Distribution-> Interactive Components and edit the request url to:
```
https://your-ngrok-genenrated-url/slack/events
```

Now you should be able to run Cubert. Install your new app in a workspace using the Slack API and you are good to go!
