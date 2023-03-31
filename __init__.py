from mycroft import MycroftSkill, intent_file_handler


class GptIntentParser(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('parser.intent.gpt.intent')
    def handle_parser_intent_gpt(self, message):
        self.speak_dialog('parser.intent.gpt')


def create_skill():
    return GptIntentParser()

