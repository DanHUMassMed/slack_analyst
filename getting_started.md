# Notes on Development

### Prerequisites 
* Install [ngrok](https://ngrok.com/download)
* `pip install slack_bolt`
* `pip install slack_sdk`

### Create a Slack App
* Goto [Your Apps Page](https://api.slack.com/apps)
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
* __NOTE__: We will be using only `Bot-Tokens` more advanced Apps may additionally use `User-Tokens` and `App-Level-Tokens`. With `Bot-Token` ONLY you can create a full and robust App.
* Select __OAuth & Permissions__ (On the Left Sidebar under __Features__ section)
    * Scroll down to __Scopes__ section 
    * Under __Bot Token Scopes__ click `Add an OAuth Scpoe`
    * Add all needed scopes (e.g., `commands`, `chat:write`, `chat:write.public`)
* Select __Install App__ (On the Left Sidebar under __Settings__ section)
    * Click `Install App to Workspace`
    * You are prompted with __[APP NAME]__ is requesting permission to access the __[WORKSPACE NAME]__ workspace
    * Click `Allow` Button
    * Copy and save the __Bot User OAuth Token__
* Select __Basic Information__ (On the Left Sidebar under __Settings__ section)
    * Scroll down to __App Credentials__
    * Copy and save the __Signing Secret__ token

### Create and Run the Base Application
* Create Environment Variables for:
    * `SLACK_SIGNING_SECRET=**************************`
    * `SLACK_BOT_TOKEN=*******************************`
* Create a simple App with the below code
```
import os
from slack_bolt import App

signing_secret=os.environ['SLACK_SIGNING_SECRET']
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
app = App(signing_secret=signing_secret,
          token=slack_bot_token)

if __name__ == "__main__":
    app.start(port=5000)
```
* Run the application `python app.py`
* Run __ngrok__ to make you app publicly addressable `ngrok http 5000`

### Setting up events over HTTP
* Select __Event Subscriptions__ (On the Left Sidebar under __Features__ section)
    * Toggle __Enable Events__ `On`
    * __NOTE:__ The __slack_bolt__ framework process Events at [https://[YOUR_HOST]/slack/events]()
    * Add __Request URL__ https://7a45-24-151-99-103.ngrok-free.app/slack/events
    * Ensure that the URL is __Verified__ before moveing to the next step
    * Scroll down to __Subscribe to bot events_
        * Click `Add Bot User Event`
        * Add Events that the Bot will listen for (e.g., `message.channels`, `message.groups`, `message.im`)
        * Clisk `Save Changes` Button
    * __NOTE:__ Once Events are added you must reinstall the App
    * Select __Install App__ (On the Left Sidebar under __Settings__ section)
    * Click `Reinstall to Workspace`
    * You are prompted with __[APP NAME]__ is requesting permission to access the __[WORKSPACE NAME]__ workspace
    * Click `Allow` Button


### Handle Events
* Add code to the `App.py`
```
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

```
* In a Slack in the Workspace that the app is installed
* In a message box hit `/` this will bring up a menu
* select `Add apps to this channel`
* Select your App and click the `Add` Button
* __NOTE:__ You will get a message: [APP NAME] was added to #[CHANNEL] by [USER NAME]
* __NOTE:__ Test the App is working by typing "hello" you should get a response from the App

### Handle Interactivity & Shortcuts
* Select __Interactivity & Shortcuts__ (On the Left Sidebar under __Features__ section)
    * Toggle __Enable Interactivity__ `On`
    * Add __Request URL__ https://7a45-24-151-99-103.ngrok-free.app/slack/events
    * Click `Save Changes` Button
* Add code to the `App.py`
```
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
* __NOTE:__ Test the App is working by typing "hello" you should get a response from the App

