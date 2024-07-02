# This file contains variables that create dialog interaction in the Slack App
research_dialog={
	"blocks": [
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":squirrel: *Hi , Let's get started on some Internet Research!*,\nWe just need a little info to begin."
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": True,
				"action_id": "research_topic-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Provide your research topic",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "----------------------------------"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "radio_buttons",
    			"initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "Basic Analysis"
                    },
                    "value": "basic-research"
                },
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Basic Analysis",
							"emoji": True
						},
						"value": "basic-research"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Detailed Analysis",
							"emoji": True
						},
						"value": "detailed-research"
					}
				],
				"action_id": "level_of_analysis-action"
			},
			"label": {
				"type": "plain_text",
				"text": "The level of Analysis desired",
				"emoji": True
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Submit",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "submit-research"
				}
			]
		}
	]
}

getting_started_responses = [
    "Got it, <@{user_id}>! I'll start gathering the data right away for a {level_of_analysis} Report. Please hold on for a moment.",
    "Sure thing, <@{user_id}>! Let me dive into the research and compile a {level_of_analysis} Report for you. Just a moment!",
    "Understood, <@{user_id}>. I'll work on putting together a {level_of_analysis} Report for you. Hang tight!",
    "On it, <@{user_id}>! I'll gather the necessary information and prepare a {level_of_analysis} Report. Please give me a few minutes.",
    "Absolutely, <@{user_id}>! I'll search through the data and get a {level_of_analysis} Report ready for you. One moment, please!",
    "OK <@{user_id}> I'm on it! Give me a minute or two to scour the web and put a {level_of_analysis} Report together for you."
]

