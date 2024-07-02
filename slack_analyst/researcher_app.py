import os
import io
import json
import uuid
import time
import threading
import asyncio
import random
import requests
from urllib.parse import urlparse, parse_qs
import re
from urllib.parse import quote, unquote
from flask import Flask, request, jsonify
from slack_bolt import App as BoltApp
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from pathlib import Path
from dotenv import load_dotenv
import logging

from research_dialog import research_dialog, getting_started_responses
from llm_research_wrapper import process_research_request

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

research_tracker = {}

signing_secret=os.environ['SLACK_SIGNING_SECRET']
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")

bolt_app = BoltApp(signing_secret=signing_secret, token=slack_bot_token)

flask_app = Flask(__name__)

handler = SlackRequestHandler(bolt_app)
client = WebClient(token=slack_bot_token)
outstanding_research_dialogs={}

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@bolt_app.message("research")
def research_request(message, say):
    write_json_to_file(message)
        # Check if the message is a direct message
    if message['channel_type'] == 'im':
        if message['user'] in outstanding_research_dialogs:
            say("We have already started a research dialog. But you have not yet submitted the request form.")
        
        else:    
            unique_id = str(uuid.uuid4())
            outstanding_research_dialogs[message['user']]={'unique_id':unique_id,'event_ts':message['event_ts']}
            # Set a uuid for the submit button
            research_dialog['blocks'][6]['elements'][0]['value']=unique_id
            # Inject of the users name in the dialog response 
            position = 15
            intro = research_dialog['blocks'][1]['text']['text']
            intro = intro[:position] + f"<@{message['user']}>" + intro[position:]
            research_dialog['blocks'][1]['text']['text'] = intro

            say(research_dialog)
        
    else:
        say("If you would like to do some research send me a DM")
        return



@bolt_app.action("submit-research")
def handle_submit_research_action(ack, action, body, client):
    research_topic, level_of_analysis = get_research_dialog_state(body['state'])
    action_value=action['value'] # UUID for this request
    action_ts=action['action_ts'] # Timestamp for this request
    channel_id=body['channel']['id']
    user_id=body['user']['id']
    if user_id in outstanding_research_dialogs:
        unique_id = outstanding_research_dialogs[user_id]['unique_id']
        if not research_topic:
            client.chat_postMessage(channel=channel_id,text=f"Looks like you forgot the Topic please add and submit again.")
        else:
            del outstanding_research_dialogs[user_id]
            client.chat_postMessage(channel=channel_id,text=f"{action_value}=={unique_id}")
        
    
    getting_started_response = random.choice(getting_started_responses)
    level_of_analysis = "Basic Research" if level_of_analysis=='basic-research' else "Detailed Research"
    response_text = getting_started_response.format(user_id=user_id, level_of_analysis=level_of_analysis)
    client.chat_postMessage(channel=channel_id,text=response_text)
    #threading.Thread(target=process_research_request, args=(client, user_id, channel_id, level_of_analysis, research_topic)).start()
    ack()


@bolt_app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to your _App's Home tab_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")



def get_research_dialog_state(dialog_state):
    """From the dialog_state pull the research topic and level of analysis"""
    research_topic = ""
    level_of_analysis = ""
    dialog_state_values = dialog_state['values']
    for key in dialog_state_values:
        if "research_topic-action" in dialog_state_values[key]:
            research_topic_value = dialog_state_values[key]["research_topic-action"]["value"]
            if research_topic_value:
                research_topic = research_topic_value
        elif "level_of_analysis-action" in dialog_state_values[key]:
            selected_option = dialog_state_values[key]["level_of_analysis-action"]["selected_option"]
            if selected_option:
                level_of_analysis = selected_option["value"]
    return research_topic, level_of_analysis


def get_all_messages(channel_id):
    messages = []
    next_cursor = None

    has_more = True
    while has_more:
        try:
            if next_cursor:
                response = client.conversations_history(channel=channel_id, cursor=next_cursor)
            else:
                response = client.conversations_history(channel=channel_id)

            messages.extend(response['messages'])
            has_more = response['has_more']
            next_cursor = response['response_metadata']['next_cursor'] if has_more else None

        except SlackApiError as e:
            print(f"Error retrieving messages: {e.response['error']}")
            break

    return messages


def write_json_to_file(json_data,file_nm="messages.json"):
    with open(file_nm, "w") as f:
        json.dump(json_data, f, indent=4)
            
@bolt_app.command("/parse_channel_history")
def parse_channel_history(ack, body, respond):
    ack()  # Acknowledge the command request
    pretty_json= json.dumps(body,indent=4)
    logger.error(pretty_json)
    print(pretty_json)
    ack()

    channel_id = body['channel_id']

    try:
        messages = get_all_messages(channel_id)
        write_json_to_file(messages)
        process_messages(messages)
        respond(f"Retrieved {len(messages)} messages from <#{channel_id}>.")
    except SlackApiError as e:
        respond(f"Error retrieving messages: {e.response['error']}")

def process_messages(messages):
    raw_urls = []
    urls = []
    for message in messages:
        user = message['user']
        type = message['type']
        #msg_id = message['client_msg_id']
        text = message.get('text')
        files = message.get('files')
        
        if text:
            raw_urls.extend(extract_urls(text))
            
    for url in raw_urls:
        url = biorxiv_download_url(url)
        url = pubmed_download_url(url)
        urls.append(url)
    
    urls = sorted(urls)
    write_json_to_file(urls,"urls.json")

def extract_urls(text):
    url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
    urls = url_pattern.findall(text)
    encoded_urls = [quote(url, safe=':/') for url in urls]
    decoded_urls = [unquote(url) for url in encoded_urls]
    return decoded_urls

def biorxiv_download_url(url):
    base_url = 'https://www.biorxiv.org'
    if url.startswith(base_url):
        query_index = url.find('?')
        if query_index != -1:
            url = url[:query_index]
        url += '.full.pdf'
    return url

def pubmed_download_url(url):
    base_url = 'https://pubmed.ncbi.nlm.nih.gov'
    if url.startswith(base_url):
        pmid = extract_pmid(url)
        if pmid:
            convert_url = convert_to_download_url(pmid)
            if convert_url:
                url = convert_url
    return url
            
def convert_to_download_url(pmid):
    ret_url = None
    # TODO Manage retry on fail
    # Query the PubMed API to get the PMC ID
    api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=slack_download&email=daniel.higgins@umassmed.edu&ids={pmid}&format=json"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        logger.debug(f"Error querying PubMed API {pmid}")
        return None
    
    data = response.json()
    
    if 'records' in data:
        if data['records'][0].get('pmcid'):
            pmc_id = data['records'][0]['pmcid']
            ret_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
            logger.warn("DDDDD found {pmc_id} for {pmid}")
        elif data['records'][0].get('doi'):
            doi = data['records'][0]['doi']
            ret_url = f"https://www.biorxiv.org/content/{doi}.full.pdf"
            logger.warn("DDDDD found {doi} for {pmid}")
        else:
            logger.error(f"convert_to_download_url no pmcid or biorxiv found for {pmid}")
    else:
        logger.error(f"convert_to_download_url no record found for {pmid}")
        
    return ret_url

        
def extract_pmid(url):
    pmid = None
    pattern = r"https://pubmed.ncbi.nlm.nih.gov/(\d+)/?"
    match = re.match(pattern, url)
    if match:
        pmid = match.group(1)
    return pmid



if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
    #bolt_app.start(port=5000)