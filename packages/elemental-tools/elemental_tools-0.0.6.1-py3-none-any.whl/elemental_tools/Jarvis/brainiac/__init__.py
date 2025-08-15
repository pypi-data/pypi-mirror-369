import inspect
import multiprocessing
from typing import Any, Dict, Tuple

from elemental_tools.logger import Logger
from icecream import ic

from elemental_tools.Jarvis.brainiac.prediction import max_similarity, quick_look
from elemental_tools.Jarvis.exceptions import Unauthorized, InvalidOption, Error
from elemental_tools.Jarvis.tools import BrainiacRequest, MessageStats, nlp_models, Tools
from elemental_tools.Jarvis.brainiac.decorators import ExamplesModel, Grimoire, GrimoireClass, GrimoireSkillsLoader

module_name = 'brainiac'


def NewRequest(message, **kwargs):
    _request = BrainiacRequest()

    # retrieve message information
    _request.message = message.lower()
    _request.message_stats = MessageStats(_request.message)

    for param, value in kwargs.items():
        _request.__setattr__(param, value)

    return _request


_tools = Tools()


class Brainiac:
    quick_look_threshold = 0.50

    default_error = "The informed option cannot be found."

    suggested_skill = []
    possible_functions = []
    function_valid = False

    # protected stuff
    _available_skills = {}

    class Depends:
        options: list = []

    def __init__(self, *grimoires: Grimoire, threshold_skill: float = 0.50, threshold_args: float = 0.50,
                 threshold_suggestion: float = 0.05, error_unauthorized: Any = default_error,
                 error_not_found_message: Any = default_error):
        """
		Brainiac class for intelligent decision-making.

		Attributes:
		    quick_look_threshold (float): The default threshold for quick look comparisons. Default is 0.50.
		    default_error (str): The default error message for cases when the informed option cannot be found. Default is "The informed option cannot be found."
		    suggested_skill (list): A list to store suggested skills.
		    possible_functions (list): A list to store possible functions.
		    function_valid (bool): A flag indicating whether a valid function has been identified.

		Parameters:
		    *args (Grimoire): Variable-length arguments representing Grimoire instances.
		    threshold_skill (float): The threshold for skill comparison. Default is 0.50.
		    threshold_args (float): The threshold for arguments comparison. Default is 0.50.
		    threshold_suggestion (float): The threshold for suggestion comparison. Default is 0.05.
		    error_unauthorized (Any): An optional custom error message for unauthorized access. Default is default_error.
		    error_not_found_message (Any): An optional custom error message for not found cases. Default is default_error.

		Note:
		    Parameters that accept Any type can be callables that return random.choices from custom models.

		Methods:
		    __init__(*args, threshold_skill=0.50, threshold_args=0.50, threshold_suggestion=0.05, error_unauthorized=default_error, error_not_found_message=default_error):
		        Constructor method for Brainiac class. Initializes thresholds, error messages, and other attributes.
		"""

        self.logger = Logger(app_name='brainiac', owner='brain').log

        self.logger('start', f"Initializing Brainiac", owner='initialization')

        _grimoire_skills = GrimoireSkillsLoader(*grimoires)

        self.grimoire_skills = _grimoire_skills.query_all()

        self._available_skills = _grimoire_skills.filter_hidden()

        self.logger('success', f"Loaded Successfully. Here's your Brainiac Skill List: {[self.grimoire_skills.keys()]}",
                    owner='initialization')
        self.logger('success', f"Here's your Documented Brainiac Skill List: {[self._available_skills.keys()]}",
                    owner='initialization')

        self.threshold_skills = threshold_skill
        self.threshold_suggestion = threshold_suggestion
        self.threshold_args = threshold_args

        self.error_not_found_message = error_not_found_message
        self.error_unauthorized = error_unauthorized

    def execute_function(self, request):

        if request.skill.exception is None:
            self.logger('info', f"Starting Skill Function: {request.skill.function}")
            if len(request.skill.parameters):
                self.logger('info',
                            f"Generating Skill Function Execution from Param Definitions: {request.skill.parameters}")

                for param, param_default in request.skill.parameters.items():
                    self.logger('info', f"Attempting to Retrieve: {param} with {param_default.default}")
                    request.threshold_args = self.threshold_args

                    if not param_default.default == inspect._empty:
                        request.skill.args[param] = param_default.default(request)
                    else:
                        request.skill.args[param] = request

                    # if parameter was not retrieved with RS
                    if request.skill.args[param] is None \
                            and param_default.default.required \
                            and param_default.default.default is None:

                        if param_default.default.title is None:
                            raise InvalidOption(missing=request.rt.beautify(param))

                    elif request.skill.args[param] is None and param_default.default.default is not None:
                        request.skill.args[param] = param_default.default.default

                    request.rt = request.rt

            if not len(request.skill.args):

                self.logger('info', f"without parameters")

                request.skill.result = request.skill.function()
            else:

                self.logger('info', f"with parameters and args: {request.skill.args}")

                request.skill.result = request.skill.function(**request.skill.args)

            if request.output_function is not None:
                self.logger('info', f"Running output function: {request.output_function}")

                request.output_function(request)

            _result = request.skill.result.replace('"', "").replace("'", "")
            return _result

        if request.output_function is not None:
            request.output_function(request)

        return request.skill.exception

    def retrieve_function(self, request: BrainiacRequest):

        self.logger('info', "Retrieving function for request message...")

        def process_request():

            self.logger('info', "Processing request message...")

            if request.skill.depends is not None:
                request.skill.authorized = all([depend(request) for depend in request.skill.depends])
            else:
                request.skill.authorized = True

            self.logger(f'info', f'Checking Depends for {request.skill.name}')

            if request.skill.authorized:
                self.logger(f'success', f'Depends returns True to {request.skill.name}')
                return request
            else:

                try:
                    if callable(self.error_not_found_message):
                        _this_error_unauthorized = self.error_unauthorized()
                    else:
                        _this_error_unauthorized = str(self.error_unauthorized)
                except:
                    _this_error_unauthorized = str(self.error_unauthorized)

                raise Unauthorized(_this_error_unauthorized)

        self.possible_functions = []
        self.possible_functions = []

        self.logger('info', "Iterating over skill list to find the right option with quick look")

        # iterate over skills to find the correct option with quick look
        current_max_similarity = 0.0

        _g_skill_subprocesses = []

        for skill_id, skill_request_model in self.grimoire_skills.items():

            ql = quick_look(request, skill_request_model)

            if ql > current_max_similarity:
                current_max_similarity = ql
                request.skill = skill_request_model

            if current_max_similarity >= 1.0:
                self.logger('success', "Quick look works awesome! Processing the perfect matched skill...")
                return process_request()

        if current_max_similarity > self.threshold_skills:
            self.logger('success', "Quick look find a most similar function!")
            return process_request()

        self.logger('alert', "Cannot find what is not there! (Not by quick looking)")

        self.logger('info', "We must iterate over the skills, to find the right one...")
        # iterate over skills to find the correct option
        for skill_id, skill_request_model in self.grimoire_skills.items():
            self.logger('info', f"Processing skill: {str(skill_id)}")
            request.skill = skill_request_model
            self.logger('info', f"Checking for Max Similarity")
            request.skill.confidence = max_similarity(request, skill_request_model, self.threshold_skills)

            if request.skill.confidence is not None:
                if request.skill.confidence >= 1.0:
                    self.logger('success', "Max similarity works awesome!")
                    return process_request()

                if request.skill.confidence > self.threshold_skills or request.skill.confidence > self.threshold_suggestion:
                    if request.skill.depends is not None:
                        request.skill.authorized = all([depend(request) for depend in request.skill.depends])
                    else:
                        request.skill.authorized = True

                if request.skill.confidence >= self.threshold_suggestion:
                    self.possible_functions.append(request.skill)

        self.logger('alert', f"Reiteration reached the end")

        self.logger('info', f"Checking dependencies for the similar options.")

        try:
            if callable(self.error_not_found_message):
                _this_error = self.error_not_found_message()
            else:
                _this_error = str(self.error_not_found_message)
        except:
            _this_error = str(self.error_not_found_message)

        try:
            if all([dp() for dp in [pf.depends for pf in self.possible_functions if pf.confidence == max(
                    [fn.confidence for fn in self.possible_functions]) and pf.depends is not None]]) or all(
                [True for pf in self.possible_functions if pf.depends is None]):

                _suggested_skill = max(self.possible_functions, key=lambda x: x.confidence)

                if _suggested_skill.suggestion_title is not None:
                    self.possible_functions = _suggested_skill.suggestion_title
                else:
                    _most_similar_example = None
                    _last_sim = 0.0

                    for m_word in request.message_model:
                        if m_word.vector_norm:

                            for example in _suggested_skill.examples:

                                for example_word in example:

                                    if example_word.vector_norm:
                                        _this_sim = example_word.similarity(m_word)

                                        if _this_sim > _last_sim:
                                            self.possible_functions = example.text
                                            _last_sim = _this_sim

                raise Error(request, f"{_this_error}\nSuggested Option: {self.possible_functions}")

            elif self.possible_functions:
                self.logger('error', f"One dependency blocks the suggested options.")
                raise Error(request, _this_error)

        except:
            raise Error(request=request, message=_this_error)

    def include_grimoire(self, *grimoires: Grimoire):
        for grimoire in grimoires:
            _add_this_grimoire = multiprocessing.Process(target=self._include_grimoire,
                                                         args=(self._set_grimoire_skills, grimoire.skills))
            _add_this_grimoire.start()

    def _set_grimoire_skills(self, skills):
        self.grimoire_skills = {**self.grimoire_skills, **skills}

    @staticmethod
    def _include_grimoire(_set_grimoire_skills, skills_to_add):
        _set_grimoire_skills(skills_to_add)

    def process_message(self, request):
        _request = request

        self.logger('info', "Building input nlp models...")
        _request.message_model = nlp_models(_request.message)
        self.logger('success', "Nlp models successfully built!")
        self.logger('info',
                    f"Creating Lemma's for the input message based on the list comprehension: {str([token.lemma_ for token in _request.message_model if token.vector_norm and not _request.rt.is_junk(token.lemma_)])}")
        _request.message_model_lemma = nlp_models(' '.join([token.lemma_ for token in _request.message_model if
                                                            token.vector_norm and not _request.rt.is_junk(
                                                                token.lemma_)]))

        if _request.message_model_lemma:
            self.logger('success', "Lemmas were generated for the message to be processed!")
        else:
            self.logger('alert', "Failed to generate lemmas for the message")

        self.retrieve_function(_request)

        return self.execute_function(_request)
