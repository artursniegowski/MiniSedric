import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import spacy
from spacy.language import Language
from spacy.tokens import Span

MODEL_NAME = "en_core_web_md"
NATURAL_LANGUAGE_PROCESSING_PIPELINE = spacy.load(MODEL_NAME)


class InsightExtractor(ABC):
    """
    Abstract base class for insight extractors.
    """

    @abstractmethod
    def extract_insights(
        self, transcript_text: str, trackers: List[str]
    ) -> List[Dict[str, Any]]:
        pass


class SimpleRegexInsightExtractor(InsightExtractor):
    """
    Extract insights from the transcribed text with a simple regular expressions
    """

    def extract_insights(
        self, transcript_text: str, trackers: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract insights from the transcribed text. Searches for specific trackers
        within the transcript and extracts information about their occurrences.

        Args:
            transcript_text (str): The transcribed text.
            trackers (List[str]): List of trackers to search for in the transcript.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing insights.
        """
        insights = []
        sentences = transcript_text.split(".")
        for i, sentence in enumerate(sentences):
            for tracker in trackers:
                matched = re.search(rf"\b{tracker}\b", sentence)
                if matched:
                    insights.append(
                        {
                            "sentence_index": i,
                            "start_word_index": len(
                                sentence[: matched.start()].split()
                            ),
                            "end_word_index": len(sentence[: matched.end()].split()),
                            "tracker_value": tracker,
                            "transcribe_value": sentence.strip(),
                        }
                    )
        return insights


class SpacyNLPInsightExtractor(InsightExtractor):
    """
    Extracts insights from transcribed text using spaCy's NLP model.

    This class uses a spaCy model to analyze text and extract insights based on semantic similarity.
    It processes sentences in the transcript and compares them to tracker phrases to identify relevant insights.

    Args:
        nlp_model (spacy.language.Language): A spaCy model instance to be used for extracting insights.
    """

    def __init__(self, nlp_model: Language):
        self.nlp = nlp_model

    def extract_insights(
        self, transcript_text: str, trackers: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract insights from the transcribed text using spaCy NLP sentence embeddings.
        Searches for sentences semantically similar to the trackers.

        Args:
            transcript_text (str): The transcribed text.
            trackers (List[str]): List of trackers to search for in the transcript.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing insights.
        """
        insights = []
        doc = self.nlp(transcript_text)
        sentence_docs = list(doc.sents)
        tracker_docs = [self.nlp(tracker) for tracker in trackers]

        for i, sentence_doc in enumerate(sentence_docs):
            sentence_tokens_idexes = {
                token.text.lower(): index for index, token in enumerate(sentence_doc)
            }
            for tracker_doc in tracker_docs:
                similarity = tracker_doc.similarity(sentence_doc)
                if similarity > 0.7:

                    start_word_index, end_word_index = self._find_word_indicies(
                        sentence_tokens_idexes, tracker_doc
                    )

                    insights.append(
                        {
                            "sentence_index": i,
                            "start_word_index": start_word_index,
                            "end_word_index": end_word_index,
                            "tracker_value": tracker_doc.text,
                            "transcribe_value": sentence_doc.text.strip(),
                            "similarity_score": similarity,
                        }
                    )
        return insights

    def _find_word_indicies(
        self, sentence_token_indexes: Dict[str, int], tracker: Span
    ) -> Tuple[int, int]:
        """
        Find the start and end indices of `tracker` tokens in the sentence.

        Args:
            sentence_token_indexes (Dict[str, int]): Token texts and their indices in the sentence.
            tracker (Span): Tokens to locate within the sentence.

        Returns:
            Tuple[int, int]: Start and end indices of the tokens. Returns (-1, -1) if not found.
        """
        tracker_tokens = [token.text.lower() for token in tracker]

        start_index = float("inf")
        end_index = float("-inf")
        for tracker_token in tracker_tokens:
            if tracker_token in sentence_token_indexes:
                current_index = sentence_token_indexes[tracker_token]
                if start_index > current_index:
                    start_index = current_index
                if end_index < current_index:
                    end_index = current_index

        start_index = start_index if start_index != float("inf") else -1
        end_index = end_index if end_index != float("-inf") else -1

        return start_index, end_index
