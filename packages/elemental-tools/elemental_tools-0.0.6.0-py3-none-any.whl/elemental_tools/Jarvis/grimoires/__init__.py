import inspect
import random
from typing import Tuple

from icecream import ic

from elemental_tools.Jarvis import GrimoireClass, ExamplesModel, Argument, Grimoire
from elemental_tools.Jarvis.brainiac.decorators import GrimoireSkillsLoader
from elemental_tools.Jarvis.server.audio import AudioRequest, AudioAssistant, AudioAssistantConfig
from elemental_tools.Jarvis.tools import Tools, BrainiacRequest


class JarvisDocumentation(GrimoireClass):
    examples = ExamplesModel(examples=['options', 'help'], keywords=['options', 'help'])
    _tools = Tools()

    def _generate_doc(self, available_skills):
        internal_default_message_options = 'The current available options are:\n'
        #internal_skill_options_examples = self.examples

        def options_request(message, **kwargs):

            return BrainiacRequest()

        def method(request=options_request):
            _content = internal_default_message_options
            for skill_name, skill_information in self._available_skills.items():
                if skill_information.depends is not None:
                    for dep in skill_information.depends:
                        skill_information.auth = dep(request)
                else:
                    skill_information.auth = True
                if skill_information.auth:
                    if skill_information.suggestion_title != None:
                        _content += f"- {self._tools.beautify(skill_information.suggestion_title)}"
                    else:
                        _content += f"- {self._tools.beautify(skill_name)}"
                    if skill_information.description is not None:
                        _content += f"| Description: {skill_information.description}"
                    _content += '\n'
            return _content
        return method

    def __init__(self, *grimoires: Tuple[Grimoire]):
        """
        Default Grimoire Skill for Deploying a Fast Documentation About the Options you created;

        Args:
            *grimoires: Grimoire`s you want to have in your documentation
        """
        _grimoire_skills = GrimoireSkillsLoader(*grimoires)
        self._available_skills = _grimoire_skills.filter_hidden()

        self.grimoire = Grimoire()

        @self.grimoire(title='options', example_model=self.examples)
        def show_options():
            doc = self._generate_doc(self._available_skills)
            return doc()

        for skill_name, skill_information in self._available_skills.items():
            self.__setattr__(skill_name, self.grimoire(title=f"{skill_name} option", example_model=ExamplesModel(examples=[f"{ex} options" for ex in skill_information.examples]))(self._generate_doc(self._available_skills)))


class Greetings(GrimoireClass):
    examples = ExamplesModel(keywords=['hello', 'hi', 'namaste', 'hola', 'hey', 'oi'], examples_exclude=['howdy', 'how-do-you-do'], examples=['good morning', 'good night', 'good evening', 'are you', 'goodnight'])

    def greetings(self, request=AudioRequest):
            intro = [
                "Hello! I'm glad to see you in my contacts. ",
                "Greetings! It's a pleasure to meet you. ",
                "Hi there! How are you? ",
                "Hi! I'm happy to have you in my contacts. ",
                "Hello there! It's good you are here. ",
            ]
            question = [
                'How can I help you?',
                "I'm here to help you!",
                "Can I assist you?",
                "Is there anything I can do to help you?"
            ]
            intro_result = random.choice(intro)
            invite_result = random.choice(question)
            result = str(intro_result) + str(invite_result)
            return str(result)


class RepeatWithMe(GrimoireClass):
    examples = ExamplesModel(keywords=['repeat'], examples=['repeat with me', 'say it again'])

    def repeat(self, request=AudioRequest):
        _result = str(request.message)
        for e in request.skill_examples:
            _result = str(request.message).lower().replace(e, '')
        return _result


class Thanks(GrimoireClass):
    examples = ExamplesModel(keywords=['thanks'], examples=['thanks'])

    def thanks(self, request=AudioRequest):
        possible_thanks = ["Anytime", "You're welcome", "No problem"]
        return str(random.choice(possible_thanks))

