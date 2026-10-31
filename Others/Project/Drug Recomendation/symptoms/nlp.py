"""
Lightweight Clinical NLP Engine for Symptom Normalization and Extraction.
Tokenizes, stems, handles negations, and matches clinical synonyms against controlled medical vocabulary.
"""

import re
from typing import List, Dict, Set, Tuple
from medical.models import Symptom


# Common negations in medical complaints (e.g. "no fever", "denies chest pain")
NEGATION_PATTERNS = [
    r'\bno\b\s+([a-z\s]+)',
    r'\bnot\b\s+([a-z\s]+)',
    r'\bwithout\b\s+([a-z\s]+)',
    r'\bdenies\b\s+([a-z\s]+)',
    r'\bruled out\b\s+([a-z\s]+)',
    r'\bfree of\b\s+([a-z\s]+)',
]

# Standard emergency / red-flag symptom triggers
EMERGENCY_TRIGGERS = [
    "severe chest pain",
    "crushing chest pressure",
    "shortness of breath",
    "difficulty breathing",
    "sudden numbness",
    "facial drooping",
    "slurred speech",
    "coughing up blood",
    "unconsciousness",
    "anaphylaxis",
    "severe allergic reaction",
    "loss of vision",
    "sudden severe headache",
]


class SymptomNLPEngine:
    def __init__(self):
        self._symptom_cache: List[Tuple[Symptom, Set[str]]] = []
        self._load_vocabulary()

    def _load_vocabulary(self):
        """Loads and indexes symptoms with their synonyms and token n-grams."""
        self._symptom_cache = []
        try:
            for symptom in Symptom.objects.all():
                aliases = set()
                # Normalized name tokens
                aliases.add(symptom.name.lower().replace('_', ' '))
                aliases.add(symptom.display_name.lower())
                
                # Synonyms
                if symptom.synonyms:
                    for syn in symptom.synonyms.split(','):
                        clean_syn = syn.strip().lower()
                        if clean_syn:
                            aliases.add(clean_syn)
                
                self._symptom_cache.append((symptom, aliases))
        except Exception:
            # When database is not yet migrated/empty
            pass

    def clean_text(self, text: str) -> str:
        """Lowercases and cleans punctuation while preserving word boundaries."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_negated_phrases(self, text: str) -> Set[str]:
        """Detects symptoms that the patient explicitly denies having."""
        negated = set()
        cleaned = text.lower()
        for pattern in NEGATION_PATTERNS:
            matches = re.finditer(pattern, cleaned)
            for m in matches:
                # Capture up to 4 words following negation
                clause = m.group(1).split()[:4]
                negated.add(" ".join(clause))
        return negated

    def parse_symptoms_from_text(self, natural_text: str) -> Dict[str, any]:
        """
        Parses free-text clinical description into normalized Symptom objects.
        Returns:
            - matched_symptoms: List[Symptom]
            - negated_mentions: List[str]
            - emergency_flags: List[str]
        """
        if not self._symptom_cache:
            self._load_vocabulary()

        cleaned_text = self.clean_text(natural_text)
        if not cleaned_text:
            return {
                'matched_symptoms': [],
                'negated_mentions': [],
                'emergency_flags': [],
                'raw_tokens': [],
            }

        negated_clauses = self.extract_negated_phrases(natural_text)
        matched_symptoms = []
        emergency_flags = []

        # Check for immediate emergency triggers
        for em in EMERGENCY_TRIGGERS:
            if em in cleaned_text:
                # Ensure not negated
                is_neg = any(em in neg for neg in negated_clauses)
                if not is_neg:
                    emergency_flags.append(em)

        # Match against controlled symptom vocabulary
        for symptom, aliases in self._symptom_cache:
            matched = False
            for alias in aliases:
                # Regex word boundary check for each alias phrase
                alias_pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(alias_pattern, cleaned_text):
                    # Verify phrase is not part of a negated clause
                    is_negated = any(alias in neg for neg in negated_clauses)
                    if not is_negated:
                        matched = True
                        break

            if matched:
                matched_symptoms.append(symptom)
                if symptom.is_emergency and symptom.display_name not in emergency_flags:
                    emergency_flags.append(symptom.display_name)

        return {
            'matched_symptoms': list(set(matched_symptoms)),
            'negated_mentions': list(negated_clauses),
            'emergency_flags': emergency_flags,
            'word_count': len(cleaned_text.split()),
        }


# Singleton engine instance
nlp_engine = SymptomNLPEngine()
