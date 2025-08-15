"""
Language Detection Utilities

Fast and accurate language detection for text content using langdetect
with optimizations for short texts and technical content.
"""

import re
from typing import Dict, List, Optional, Tuple

from langdetect import DetectorFactory, LangDetectException, detect, detect_langs

from unrealon_llm.src.dto import LanguageCode, LanguageDetection
from unrealon_llm.src.exceptions import LanguageDetectionError


class LanguageDetector:
    """Advanced language detection with fallback strategies"""
    
    def __init__(self):
        """Initialize language detector with deterministic results"""
        # Set seed for consistent results
        DetectorFactory.seed = 0
        
        # Language patterns for fallback detection
        self.language_patterns = {
            LanguageCode.EN: [
                r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b',
                r'\b(this|that|these|those|what|where|when|why|how)\b',
                r'\b(is|are|was|were|be|been|being|have|has|had)\b'
            ],
            LanguageCode.KO: [
                r'[가-힣]+',  # Korean characters
                r'\b(이|그|저|의|을|를|에|에서|으로|와|과)\b',
                r'\b(입니다|습니다|했습니다|있습니다|없습니다)\b'
            ],
            LanguageCode.ZH: [
                r'[\u4e00-\u9fff]+',  # Chinese characters
                r'\b(的|了|在|是|我|你|他|她|我们|你们|他们)\b',
                r'\b(这|那|什么|哪里|什么时候|为什么|怎么)\b'
            ],
            LanguageCode.JA: [
                r'[ひらがな\u3040-\u309f\u30a0-\u30ff]+',  # Hiragana + Katakana
                r'\b(の|を|に|で|から|まで|と|や|が|は)\b',
                r'\b(です|である|します|しました|いる|ある)\b'
            ],
            LanguageCode.RU: [
                r'[а-яё]+',  # Cyrillic characters
                r'\b(и|или|но|в|на|за|для|от|с|по|о)\b',
                r'\b(это|тот|эти|те|что|где|когда|почему|как)\b'
            ],
            LanguageCode.ES: [
                r'\b(el|la|los|las|un|una|de|en|y|o|pero)\b',
                r'\b(que|donde|cuando|por|para|con|sin|sobre)\b',
                r'\b(es|son|fue|fueron|ser|estar|haber|tener)\b'
            ],
            LanguageCode.FR: [
                r'\b(le|la|les|un|une|des|de|du|en|et|ou)\b',
                r'\b(que|où|quand|pourquoi|comment|avec|sans)\b',
                r'\b(est|sont|était|étaient|être|avoir|faire)\b'
            ],
            LanguageCode.DE: [
                r'\b(der|die|das|ein|eine|und|oder|aber|in|auf)\b',
                r'\b(das|was|wo|wann|warum|wie|mit|ohne|für)\b',
                r'\b(ist|sind|war|waren|sein|haben|werden)\b'
            ]
        }
    
    def detect_language(self, text: str) -> LanguageDetection:
        """
        Detect language of given text with high accuracy
        
        Args:
            text: Input text to analyze
            
        Returns:
            LanguageDetection with detected language and confidence
            
        Raises:
            LanguageDetectionError: If detection fails
        """
        if not text or not text.strip():
            raise LanguageDetectionError("Empty text provided for language detection")
        
        # Clean text for better detection
        cleaned_text = self._clean_text(text)
        
        if len(cleaned_text) < 3:
            raise LanguageDetectionError("Text too short for reliable language detection")
        
        try:
            # Try primary detection with langdetect
            result = self._detect_with_langdetect(cleaned_text)
            if result.confidence >= 0.8:
                return result
            
            # Fallback to pattern-based detection
            pattern_result = self._detect_with_patterns(cleaned_text)
            if pattern_result.confidence >= 0.7:
                return pattern_result
            
            # If both methods have low confidence, use langdetect result
            if result.confidence > 0.5:
                return result
            
            # Last resort: assume English
            return LanguageDetection(
                detected_language=LanguageCode.EN,
                confidence=0.3,
                alternative_languages=[
                    {"language": LanguageCode.EN, "confidence": 0.3}
                ]
            )
            
        except Exception as e:
            raise LanguageDetectionError(f"Language detection failed: {str(e)}")
    
    def detect_multiple_languages(self, text: str, top_n: int = 3) -> List[Dict[str, float]]:
        """
        Detect multiple possible languages with probabilities
        
        Args:
            text: Input text to analyze
            top_n: Number of top languages to return
            
        Returns:
            List of language-confidence pairs
        """
        # Use langdetect for multiple language detection
        
        try:
            cleaned_text = self._clean_text(text)
            languages = detect_langs(cleaned_text)
            
            results = []
            for lang_info in languages[:top_n]:
                # Map to our language codes
                our_lang_code = self._map_to_our_language_code(lang_info.lang)
                if our_lang_code:
                    results.append({
                        "language": our_lang_code,
                        "confidence": float(lang_info.prob)
                    })
            
            return results
            
        except LangDetectException:
            # Fallback to single detection
            single_result = self.detect_language(text)
            return [{"language": single_result.detected_language, "confidence": single_result.confidence}]
    
    def is_language(self, text: str, expected_language: LanguageCode, threshold: float = 0.8) -> bool:
        """
        Check if text is in expected language with given confidence threshold
        
        Args:
            text: Text to check
            expected_language: Expected language code
            threshold: Minimum confidence threshold
            
        Returns:
            True if text is likely in expected language
        """
        try:
            detection = self.detect_language(text)
            return (detection.detected_language == expected_language and 
                   detection.confidence >= threshold)
        except LanguageDetectionError:
            return False
    
    def _detect_with_langdetect(self, text: str) -> LanguageDetection:
        """Detect language using langdetect library"""
        try:
            # Single detection for primary language
            detected_lang = detect(text)
            
            # Get probabilities for all languages
            lang_probs = detect_langs(text)
            
            # Find our language code and confidence
            our_lang_code = self._map_to_our_language_code(detected_lang)
            confidence = 0.0
            alternatives = []
            
            for lang_info in lang_probs:
                mapped_code = self._map_to_our_language_code(lang_info.lang)
                if mapped_code:
                    if mapped_code == our_lang_code:
                        confidence = float(lang_info.prob)
                    else:
                        alternatives.append({
                            "language": mapped_code,
                            "confidence": float(lang_info.prob)
                        })
            
            if not our_lang_code:
                our_lang_code = LanguageCode.EN  # Default fallback
                confidence = 0.5
            
            return LanguageDetection(
                detected_language=our_lang_code,
                confidence=confidence,
                alternative_languages=alternatives
            )
            
        except LangDetectException as e:
            raise LanguageDetectionError(f"langdetect failed: {str(e)}")
    
    def _detect_with_patterns(self, text: str) -> LanguageDetection:
        """Fallback pattern-based language detection"""
        text_lower = text.lower()
        language_scores = {}
        
        for lang_code, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            # Normalize score by text length
            if len(text) > 0:
                language_scores[lang_code] = score / len(text.split())
        
        if not language_scores:
            return LanguageDetection(
                detected_language=LanguageCode.EN,
                confidence=0.3,
                alternative_languages=[]
            )
        
        # Find best match
        best_lang = max(language_scores.items(), key=lambda x: x[1])
        confidence = min(best_lang[1] * 2, 1.0)  # Scale confidence
        
        # Create alternatives
        alternatives = []
        for lang, score in sorted(language_scores.items(), key=lambda x: x[1], reverse=True)[1:3]:
            if score > 0:
                alternatives.append({
                    "language": lang,
                    "confidence": min(score * 2, 1.0)
                })
        
        return LanguageDetection(
            detected_language=best_lang[0],
            confidence=confidence,
            alternative_languages=alternatives
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better language detection"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers (but keep words with numbers)
        text = re.sub(r'\b\d+\b', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    def _map_to_our_language_code(self, langdetect_code: str) -> Optional[LanguageCode]:
        """Map langdetect language codes to our enum"""
        mapping = {
            'en': LanguageCode.EN,
            'ko': LanguageCode.KO,
            'zh-cn': LanguageCode.ZH,
            'zh': LanguageCode.ZH,
            'ja': LanguageCode.JA,
            'ru': LanguageCode.RU,
            'es': LanguageCode.ES,
            'fr': LanguageCode.FR,
            'de': LanguageCode.DE,
            'it': LanguageCode.IT,
            'pt': LanguageCode.PT,
            'ar': LanguageCode.AR,
            'hi': LanguageCode.HI,
            'tr': LanguageCode.TR,
            'pl': LanguageCode.PL,
            'uk': LanguageCode.UK,
        }
        return mapping.get(langdetect_code.lower())


# Convenience functions
def detect_language(text: str) -> LanguageDetection:
    """Quick language detection"""
    detector = LanguageDetector()
    return detector.detect_language(text)


def is_language(text: str, expected_language: LanguageCode, threshold: float = 0.8) -> bool:
    """Quick language verification"""
    detector = LanguageDetector()
    return detector.is_language(text, expected_language, threshold)


def detect_multiple_languages(text: str, top_n: int = 3) -> List[Dict[str, float]]:
    """Quick multiple language detection"""
    detector = LanguageDetector()
    return detector.detect_multiple_languages(text, top_n)
