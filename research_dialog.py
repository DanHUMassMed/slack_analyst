research_dialog={
	"blocks": [
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":squirrel: *Hi, Let's get started on some Research!*,\nWe just need a little info to begin."
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