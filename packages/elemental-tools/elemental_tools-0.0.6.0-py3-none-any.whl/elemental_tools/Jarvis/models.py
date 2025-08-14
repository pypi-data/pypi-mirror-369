from typing import Any

from elemental_tools.Jarvis.brainiac.decorators import ExamplesModel
from elemental_tools.Jarvis.tools import BrainiacRequest, nlp_models
from elemental_tools.Jarvis.config import logger


class Argument:

    _result = None

    def __init__(
            self,
            desired_type,
            example_model: ExamplesModel,
            parser_function: Any = None,
            required: bool = True,
            default: Any = None,
            title: str = None
        ):

        self.title = title
        self.desired_type = desired_type
        self.required = required
        self.parser = parser_function
        self.example_model = example_model
        self.default = default
        self.threshold_args = 0.5

    def _run_parser(self, text):
        if self.parser is not None:
            try:
                return self.parser(text)
            except Exception as e:
                logger('alert', f"Error on parser function: {str(self.parser)}\nException:{str(e)}", origin='grimoire-skill-argument')
                return None

    def __call__(self, request: BrainiacRequest):
        logger('info', 'Looking for function arguments in request message')

        _count = 0
        _threshold_args = request.threshold_args
        _result = None

        logger('info', f'Iterating through examples', info='argument')

        _available_args = [word for word in request.message_model if not request.rt.is_junk(word.text)]

        index = 0
        while index < len(_available_args):
            phrase = _available_args[index].text
            for i in range(index + 1, len(_available_args)):
                phrase += ' ' + _available_args[i].text

            try:
                _count += 1
                logger('info', f'Recognizing the phrase: "{phrase}" of the received message')
                logger('info', f'Attempting to parse {phrase}')

                _result = self._run_parser(phrase)

                if _result is None:
                    logger('alert', f'Parse cannot find the argument at the first attempt, running other methods...')
                    logger('info', f'Checking for similarity...')
                    # Use numpy.where with a lambda function to filter elements based on similarity score
                    max_confidence = -1.0

                    try:
                        max_confidence = max([doc.similarity(phrase) for doc in self.example_model.examples if
                                              doc.similarity(phrase) >= self.threshold_args and doc.vector_norm and phrase.vector_norm])
                    except:
                        _result = None

                    if max_confidence >= self.threshold_args:
                        logger('success',
                               f'The similarity confidence hits the target threshold of {self.threshold_args}, because its confidence was: {max_confidence}')

                        _result = self._run_parser(phrase)
                        if _result is None:
                            _result = phrase

                        for phr_idx in range(index, index + len(phrase.split())):
                            request.rt.add_junk(_available_args[phr_idx].text)
                        break

                    elif _result is None:
                        raise ValueError("The similarity confidence doesn't hit its threshold, if it was not your intent, you can reconfigure it. See documentation for further information.")

                else:
                    logger('success', f'Your custom parser function {self.parser}, do the job!')
                    break

            except ValueError:
                if _count == len(_available_args):
                    return None
            index += 1

        self._result = self.desired_type(_result)
        return self._result

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float) and isinstance(self._result, int) or isinstance(self._result, float):
            return self._result + other
        else:
            # Handle other cases or raise an exception if not supported
            raise TypeError("Unsupported operand type: {}".format(type(other)))

    def __iter__(self):
        return self._result
