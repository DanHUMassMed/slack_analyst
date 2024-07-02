# Notes on the exact steps to create your First Slack App

### Prerequisites 
* Install [ngrok](https://ngrok.com/download)
* Install Slack frameworks
```bash
pip install slack_bolt
pip install slack_sdk
```

### Create a Slack App
* Goto [Your Slack Apps Page](https://api.slack.com/apps)
* Select `Create New App` Button
* Select __Create an App from Scratch__
    * Give Your App a _Name_
    * Select a _Workspace_ for Development
    * Select `Create App` Button

* Select __Basic Information__ (On the Left Sidebar under __Settings__ section)
    * Scroll down to __Display Information__ section
    * Add a __Short description__
    * Add a __Background color__ (Not Black)
    * Click `Save Changes` Button

### Create Tokens and Install your App in the Workspace
* __NOTE__: We will be using only `Bot-Tokens`; more advanced Apps may additionally use `User-Tokens` and `App-Level-Tokens.` With `Bot-Token`
* __NOTE:__ With `Bot-Tokens` alone, you can create a full and robust Slack App.
* Select __OAuth & Permissions__ (Scroll up. On the Left Sidebar under __Features__ section)
    * Scroll down to __Scopes__ section 
    * Under __Bot Token Scopes__ click `Add an OAuth Scpoe`
    * Add all needed scopes (e.g., `commands`, `chat:write`, `chat:write.public`)
* Select __Install App__ (Scroll up. On the Left Sidebar under __Settings__ section)
    * Click `Install App to Workspace`
    * You are prompted with __[APP NAME]__ is requesting permission to access the __[WORKSPACE NAME]__ workspace
    * Click `Allow` Button
    * Copy and save the __Bot User OAuth Token__
* Select __Basic Information__ (On the Left Sidebar under __Settings__ section)
    * Scroll down to __App Credentials__
    * Copy and save the __Signing Secret__ token

### Create and Run the Base Application
* Create Environment Variables for your secrets:
```bash
    export SLACK_SIGNING_SECRET=**************************
    export SLACK_BOT_TOKEN=*******************************
```
* Create a simple App with the below code:
```python
import os
from slack_bolt import App

signing_secret=os.environ['SLACK_SIGNING_SECRET']
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
app = App(signing_secret=signing_secret,
          token=slack_bot_token)

if __name__ == "__main__":
 app.start(port=3000)
```
* Run the application `python app.py`
* Run __ngrok__ to make your App publicly addressable `ngrok http 3000.`
* Add logging if desired
* __NOTE:__ This will show bolt and SDK Debug messages
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Setting up events over HTTP
* Select __Event Subscriptions__ (On the Left Sidebar under __Features__ section)
    * Toggle __Enable Events__ `On`
    * __NOTE:__ The __slack_bolt__ framework process Events at [https://[YOUR_HOST]/slack/events]()
    * Add __Request URL__ provided by ngrok (e.g., https://7a45-24-151-99-103.ngrok-free.app/slack/events)
    * Ensure that the URL is __Verified__ before moving to the next step
    * __NOTE:__: A "Verified" Label will be added next to the __Request URL__ Label
    * Scroll down to __Subscribe to bot events__
        * Click `Add Bot User Event`
        * Add Events that the Bot will listen for (e.g., `message.channels`, `message.groups`, `message.im`)
        * Click `Save Changes` Button
    * __NOTE:__ Once Events are added, you must reinstall the App
    * Select __Install App__ (On the Left Sidebar under __Settings__ section)
    * Click `Reinstall to Workspace`
    * You are prompted with __[APP NAME]__ is requesting permission to access the __[WORKSPACE NAME]__ workspace
    * Click `Allow` Button


### Handle Events
* Add code to the `App.py` (and restart)
* __NOTE:__ Do not restart ngrok! As restarting ngrok will create a new _Forwarding URL_
```
@app.message("hello")
def message_hello(message, say):
 # say() sends a message to the channel where the event was triggered
 say(f"Hey there <@{message['user']}>!")

```
* Goto Slack and in the Workspace where the Slack App is installed
* Goto any channel message box and type `/add apps to this channel`; this will bring up a menu
* Select your App and click the `Add` Button
* __NOTE:__ You will get a message: [APP NAME] was added to #[CHANNEL] by [USER NAME]
* __NOTE:__ Test the App is working by typing "hello" You should get a response from the App

### Handle Interactivity & Shortcuts
* Select __Interactivity & Shortcuts__ (On the Left Sidebar under __Features__ section)
    * Toggle __Enable Interactivity__ `On`
    * Add __Request URL__ provided by ngrok (e.g., https://7a45-24-151-99-103.ngrok-free.app/slack/events)
    * Click `Save Changes` Button
* Add code to the `App.py`
```python
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
 say(
        blocks=[
 {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
 }
 }
 ],
        text=f"Hey there <@{message['user']}>!"
 )

@app.action("button_click")
def handle_some_action(ack, body, say):
 ack()
 say(f"<@{body['user']['id']}> clicked the button")
```
* __NOTE:__ Test the App is working by typing "hello" you should get a response from the App with a `Click Me` button
* __NOTE:__ Clicking the Button should get an addition response "[USER] clicked the button"

### Congratulations and Next Steps
* __Congradulations__ you have created your First Slack App!
* Where to go from here.
    * [Slack Dev Documenation](https://slack.dev/) is great place to dig into details
    * [GitHub Slack Source Code for bolt-python](https://github.com/slackapi/bolt-python)
    * [GitHub Slack Source Code for slack-sdk](https://github.com/slackapi/bolt-python)