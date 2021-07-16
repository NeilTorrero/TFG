from rasa_api import check_Run_Server, check_Kill_Server, predictText, getResponses
import spacy


def spacyPipeline(text):
    spacy_model = spacy.load("en_core_web_lg")
    result = spacy_model(text)
    # NER
    for token in result:
        print(token.ent_iob_, token.ent_type_)

    return result


def chat():
    """
    Preprocess the input
        - cleaning (stop words, uncase, spell check, etc)
        - tokenize
        - pos
        - featurize (vector representation)
        Intent Classification (from tokens or features)
        Entity Extraction (from tokens or features)
        - dependency parsing
        - lemmatize
        - ner
        - nes/d and nel (synonym/disambiguation and linking)
        Response selector
    """
    text = input("Your input: ")

    prediction = predictText(text)
    # result = spacyPipeline(text)
    # also add duckling analysis either on the rasa model or here

    intent = prediction['intent']['name']
    print(intent)
    if intent == 'inform':
        print("Searching information.")
        searchInform(prediction['entities'])
    else:
        response = getResponses(prediction)
        print("Bot: ", response['messages']['text'])


if __name__ == '__main__':
    check_Run_Server()
    chat()
    check_Kill_Server()
