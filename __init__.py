from mycroft import FallbackSkill, intent_handler
from mycroft.messagebus import Message
import requests
import urllib
import json
import os
import re
from pathlib import Path
from padatious.util import expand_parentheses

def read_config() -> dict:
	filename = os.path.join(os.path.dirname(__file__), 'config.json')
	try:
		with open(filename, mode='r') as f:
			return json.loads(f.read())
	except FileNotFoundError:
		return {}

confs = read_config()

api_endpoint = confs["API_ENDPOINT"]
api_key = confs["API_KEY"]
model = confs["MODEL"]
#api_endpoint = "https://api.openai.com/v1/completions"
#model = "code-davinci-002"

# Define the request headers
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer " + api_key
}

class FallbackGptIntentParser(FallbackSkill):

	_conversation_history = []

	def __init__(self):
		FallbackSkill.__init__(self)

	def initialize(self):
		self.register_fallback(self.handle_fallback_GptIntentParser, 70)

	def handle_fallback_GptIntentParser(self, message):
		self.log.info("Using GPTIntentParser fallback")
		try:
			intents = Path('/opt/mycroft/skills/fallback-gpt-intent-parser-skill/intents.txt').read_text()
			self._conversation_history.append({"role": "system", "content": intents})
			self._conversation_history.append({"role": "system", "content": "Use the following JSON template: { \"intent\": <exact intent from the list>, \"params\": [ { \"name\": <matched parameter name>, \"value\": <corresponding entity value> }, ...  ] }"})
			self._conversation_history.append({"role": "user", "content": "Match the one - only 1 - intent from the above list that best matches this prompt: " +  message.data['utterance'] + ". Answer with a JSON object that follows the template provided above and absolutely nothing else. If no listed intent matches, reply with {} and nothing else."})
			payload = {
				"temperature": 1,
				"model": model,
				"messages": self._conversation_history
			}
			response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload))
#			self.log.error(json.dumps(response.json()))
			response_json = response.json()
			freason = response_json["choices"][0]["finish_reason"]
#			self.log.info(freason)
			response = response_json["choices"][0]["message"]["content"]

			params = {}
			intent_obj_json = json.loads(response)
			for item in intent_obj_json["params"]:
				params[item["name"]] = item["value"]

			expansion = expand_parentheses(intent_obj_json["intent"])[0]
			new_intent = re.sub(' +', ' ', ''.join(expansion)).strip(" ")
			self.log.info(new_intent)

			new_final_intent = new_intent.format(**params)
			self.log.info(new_final_intent)

			self.bus.emit(Message("recognizer_loop:utterance", {'utterances': [new_final_intent], 'lang': 'en-us'}))

			return True
		except Exception as e:
			self.log.error("error in GptIntentParser fallback request " + str(e))
			return False

def create_skill():
	return FallbackGptIntentParser()
