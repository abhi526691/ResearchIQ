import re
import emoji
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords

from supporting_docs.slang_dict import abbreviations


class Preprocessing:
    """
    Pre-Processing
    - There are lots of things which we have to do to preprocess the text data
    - Handle Emojis, Slangs, Punctuations, ShortForm
    - Spelling Corrections
    - POS Tagging
    - Handling Pronouns and Special Characters
    - Tokenize
    - Lowercase and En-grams
    - Remove Special Character
    - Remove Extra WhiteSpaces
    """

    def __init__(self):
        # Download necessary NLTK data
        nltk.download("punkt")
        nltk.download("punkt_tab")  # Ensure punkt_tab is downloaded
        nltk.download("wordnet")
        nltk.download("stopwords")
        nltk.download("averaged_perceptron_tagger")

    def clean_string(self, input_string):
        """
        Removes special characters and extra whitespaces from the input string.

        Args:
            input_string (str): The string to process.

        Returns:
            str: The cleaned string without special characters or extra whitespaces.
        """
        # Remove special characters
        cleaned_string = re.sub(r'[^A-Za-z0-9\s]', '', input_string)
        # Remove extra whitespaces by splitting and rejoining
        cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
        return cleaned_string

    def convert_abbrev(self, word):
        final_word = []
        for i in word.split(" "):
            final_word.append(
                abbreviations[i.lower()] if i.lower() in abbreviations.keys() else i)
        return " ".join(final_word)

    def remove_urls(self, text):
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub(r'', text)

    def remove_html(self, text):
        html_pattern = re.compile('<.*?>')
        return html_pattern.sub(r'', text)

    def lemmatize_text_nltk(self, text):
        lemmatizer = WordNetLemmatizer()
        words = nltk.word_tokenize(text)  # Tokenize the text
        lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)

    def remove_stopwords(self, text):
        # Get the set of English stopwords
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)  # Tokenize the text
        filtered_words = [
            word for word in words if word.lower() not in stop_words]
        return ' '.join(filtered_words)

    def handle_emoji(self, text):
        # Handling Emoji's
        return emoji.demojize(text)


def preprocess_pipeline(text):
    preprocessor = Preprocessing()
    methods = [method for method in dir(preprocessor) if callable(getattr(preprocessor, method))
               and not method.startswith("__")]
    print(methods)

    # Apply each function to the text
    for method_name in methods:
        # Print the name of the current function being applied
        print(f"Applying function: {method_name}")
        text = getattr(preprocessor, method_name)(text)
    return text
