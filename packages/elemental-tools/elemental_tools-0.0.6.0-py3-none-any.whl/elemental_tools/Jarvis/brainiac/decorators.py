import spacy
import inspect
import numpy as np
from icecream import ic
from datetime import datetime
from typing import Any, Union, Dict, Tuple
from deep_translator import GoogleTranslator

from elemental_tools.logger import Logger
from elemental_tools.Jarvis.tools import Tools, nlp_models


tools = Tools()


class ExamplesModel:
    function: Any = None
    examples_lemmas = []

    def __init__(
            self,
            examples: Union[list, np.array],
            depends: dict = None,
            keywords: Union[list, np.array, None] = None,
            examples_exclude: Union[list, np.array, None] = None,
            suggestion_title: str = None,
            bypass_translation: bool = True,
            languages: list = ['pt', 'es']
    ):

        """
        :param examples: A list of matching examples that will be processed and generate models to the brainiac recognition system.
        :param keywords: This contains a list of keywords, that will be used for fast lookup, and will be improved with synonyms to corroborate with the examples list for a better accuracy.
        :param depends: A function that must returns a boolean value indicating the authorization status to this skill execution. If the dependency returns True, it triggers the authorization to this skill execution. Otherwise it triggers the authorization exception as a result. To overwrite the authorization exception...
        """

        self.keywords = keywords
        self.examples = examples
        self.depends = depends
        self.examples_exclude = examples_exclude
        self.examples_lemmas = []
        self.exception = None
        self.args = {}

        self.bypass_translation = bypass_translation
        self.languages = languages

        self.suggestion_title = suggestion_title

        self.generate_models()

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_depends(self):
        return self.depends

    def generate_models(self):

        # Convert examples to np array if not yet
        if isinstance(self.examples, list):
            # print(f"examples {self.examples}")
            self.examples = np.array(self.examples)

        if self.keywords is not None:
            for suggestion in self.keywords:
                self.examples = np.concatenate((self.examples, tools.get_syn_list(suggestion), np.array([suggestion])),
                                               axis=0)

        # Convert examples_exclude to np array if not yet
        if isinstance(self.examples_exclude, list):
            self.examples_exclude = np.array(self.examples_exclude)
            self.examples_exclude = np.isin(self.examples, self.examples_exclude)

        if self.examples_exclude is not None:
            self.examples = self.examples[~self.examples_exclude]

        self.examples = tools.to_nlp(nlp_models, self.examples)

        for example in self.examples:

            for token in example:
                self.examples_lemmas.append(token.lemma_)

        self.examples_lemmas = np.array(self.examples_lemmas)

        return self


class GrimoireStorage:
    """
    Class responsible for storing skill data.

    Attributes:
        data (Dict[str, ExamplesModel]): A dictionary storing skill names as keys and ExamplesModel instances as values.
    """

    data: Dict[str, ExamplesModel] = {}

    def include(self, name: str, request_model: ExamplesModel):
        """
        Include a new skill into the storage.

        Args:
            name (str): The name of the skill.
            request_model (ExamplesModel): An instance of ExamplesModel representing the skill model.

        Returns:
            Dict[str, ExamplesModel]: Updated dictionary containing the stored skills.
        """
        self.data[name] = request_model
        return self.data


def Grimoire():
    """
    Decorator to store Jarvis skills;

    Example with Audio Assistant:
        grimoire = Grimoire()

        @grimoire(title='thanks', example_model=Examples.thanks)
        def thanks(request=AudioRequest):
            return "Nothing"

    Store Skill Information About Its Execution;
    """

    _storage = GrimoireStorage()

    class GrimoireManagement:
        from elemental_tools.logger import Logger

        """
        Class for managing skills and generating skill models.
        """

        # here's your decorator definition
        def __call__(self, title: str, example_model: ExamplesModel, suggestion_title: str = None, depends: list = None,
                     description: str = None, hidden: bool = False):
            """
            Decorator function for generating and storing skill models.

            Args:
                title (str): The title of the skill.
                example_model (ExamplesModel): An instance of ExamplesModel representing the skill model.
                suggestion_title (str): The title of the suggestion.
                depends (list): List of dependencies.
                description (str): Description of the skill.
                hidden (bool): Flag indicating if the skill is hidden.

            Returns:
                Callable: The decorated function.
            """

            def decorator(func):
                logger = Logger(app_name='brainiac', owner='model-generator').log

                start = datetime.now()

                logger('start', f"Generating {title.capitalize()} Models...")

                _skill_model = example_model

                _skill_model.name = title
                _skill_model.function = func
                _skill_model.parameters = inspect.signature(_skill_model.function).parameters
                _skill_model.suggestion_title = suggestion_title
                _skill_model.description = description
                _skill_model.hidden = hidden
                _skill_model.depends = depends

                _storage.include(_skill_model.name, _skill_model)

                end = datetime.now()
                logger('success',
                       f"{title.capitalize()} Models Generated Successfully! It Takes: {end - start} and Renders up to: {len(_skill_model.examples)} examples",
                       )

            return decorator

        @staticmethod
        def skills():
            return _storage.data

    _instance = GrimoireManagement()
    return _instance


class GrimoireClass:
    examples: ExamplesModel
    grimoire: Grimoire = Grimoire()

    def __call__(self, *args, **kwargs):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_'):
                _decorated_method = self.grimoire(title=name, example_model=self.examples)(method)
                self.__setattr__(name, _decorated_method)

        return self.grimoire


class GrimoireSkillsLoader:
    grimoire_skills = {}

    def __init__(self, *args: Tuple[Grimoire]):
        for grimoire in [*args]:
            try:
                self.grimoire_skills = {**self.grimoire_skills, **grimoire.skills()}
            except:
                raise TypeError(f"Could not load Grimoire: {grimoire}")

    def __call__(self, *args: Tuple[Grimoire]):
        return super().__init__(*args)

    def filter_hidden(self):
        _available_skills = {}
        for skill_name, skill_decorator in self.grimoire_skills.items():

            if not skill_decorator.hidden:
                _available_skills[skill_name] = skill_decorator
        return _available_skills

    def query_all(self):
        return self.grimoire_skills

    def include_grimoire(self, *args: Tuple[Grimoire]):
        return self(*args)
