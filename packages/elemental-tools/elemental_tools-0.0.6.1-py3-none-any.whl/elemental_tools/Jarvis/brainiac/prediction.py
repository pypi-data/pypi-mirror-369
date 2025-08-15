from datetime import datetime

from fuzzywuzzy import fuzz
from icecream import ic

from elemental_tools.Jarvis import config
from elemental_tools.logger import Logger
from elemental_tools.Jarvis.tools import BrainiacRequest
from elemental_tools.Jarvis.brainiac.decorators import nlp_models, ExamplesModel

log_owner = 'prediction'


def quick_look(request: BrainiacRequest, example_models: ExamplesModel, threshold: float = 0.8):
    logger = Logger(app_name='brainiac', owner=log_owner).log
    start = datetime.now()
    _max_similarity = 0.0

    logger('info', f"Taking a quick look at analysis with examples: {example_models.examples}, message: {request.message}")

    try:
        _max_similarity = max([max([fuzz.ratio(str(message_word), str(example)) for example in example_models.examples if example.vector_norm]) for message_word in request.message_model]) / 100
    except UserWarning:
        pass

    if _max_similarity >= threshold:
        return _max_similarity

    ql_lemmas = [True for word in request.message_model_lemma.text.split(' ') if word in str(example_models.examples_lemmas) and len(word) >= 2 and not request.rt.is_junk(word)]
    ql_examples = [True for word in str(request.message).split(' ') if word in str(example_models.examples) and len(word) >= 2 and not request.rt.is_junk(word)]

    if any(ql_lemmas) or any(ql_examples):
        try:
            _max_similarity = max([example.similarity(request.message_model) for example in example_models.examples if example.vector_norm])
        except UserWarning:
            _max_similarity = 0.0
        end = datetime.now()
    else:
        end = datetime.now()
        logger('alert',
               f"Quick look results: {False} in a meantime of: {end - start} cause the validations: ql_lemmas and ql_examples doesn't returns True")
        return False

    logger('success',
           f"Quick look results: {_max_similarity} in a meantime of: {end - start} because of validations: ql_lemmas = {ql_lemmas} and ql_examples = {ql_examples}")

    return _max_similarity


def max_similarity(request_model: BrainiacRequest, example_models: ExamplesModel, threshold: float = 1.0):
    logger = Logger(app_name='brainiac', owner=log_owner).log
    start = datetime.now()
    logger('info', f"Starting similarity analysis with examples: {example_models.examples}, message_model: {request_model.message_model}")
    similarity_stats = [0]

    #print(f"example_models.examples: {example_models.examples} request.message_model: {request.message_model}")

    current_max_score = 0.0

    for m_word in request_model.message_model:
        if m_word.vector_norm and not request_model.rt.is_junk(m_word.text):
            matching_word = m_word.text

            logger('info', f"Iterating on word of the request message: {matching_word} with the following examples_lemmas: {example_models.examples_lemmas}")

            logger('info', f"Checking if the word is part of the example_lemmas string")
            if m_word.text in str(example_models.examples_lemmas):
                similarity_stats.append(1.0)
            logger('alert', f"It was not.")

            logger('info', f"Checking if the word is part of the examples string if it is bigger or equal than three characters")
            if m_word.text in str(example_models.examples) and len(m_word.text) >= 3:
                similarity_stats.append(1.0)
            logger('alert', f"It was not.")

            logger('info', f"Checking for word similarity using Spacy Score")

            try:
                current_max_score = max([nlp_models(m_word).similarity(example) for example in example_models.examples if nlp_models(m_word).vector_norm])
            except:
                current_max_score = 0.0

                for lemma in example_models.examples_lemmas:
                    # Create a SpaCy document for the current lemma
                    lemma_doc = nlp_models(str(lemma))
                    if lemma_doc.vector_norm:
                        similarity_score = m_word.similarity(lemma_doc)

                        if similarity_score > current_max_score:
                            current_max_score = similarity_score

            similarity_stats.append(current_max_score)

            if max(similarity_stats) >= threshold:
                current_max_score = max(similarity_stats)
                end = datetime.now()
                logger('success', f"Similarity analysis ending successfully. It takes: {end - start} and returns: {current_max_score} because of the matching word {matching_word}")

                return current_max_score

        else:
            continue

    overall_similarity = current_max_score

    end = datetime.now()

    logger('alert', f"Similarity analysis ending successfully. It takes: {end - start} and returns: {overall_similarity}")

