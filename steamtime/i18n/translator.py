"""
Internationalization module for GabeGardener.

This module provides translation functionality for the application.
"""
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("gabegardener")

class Translator:
    """
    Translator class for handling internationalization.
    
    This class loads and provides translations for different languages.
    """
    
    def __init__(self, language="en"):
        """
        Initialize a new translator.
        
        Args:
            language (str): Language code (default: en)
        """
        self.language = language
        self.translations = {}
        self.fallback_translations = {}
        
        # Load translations
        self._load_translations()
    
    def _load_translations(self):
        """Load translations from files."""
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        translations_dir = os.path.join(current_dir, "translations")
        
        # Load fallback (English) translations
        fallback_file = os.path.join(translations_dir, "en.json")
        if os.path.exists(fallback_file):
            try:
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.fallback_translations = json.load(f)
            except Exception as e:
                logger.error(f"Error loading fallback translations: {e}")
        
        # Load requested language translations
        if self.language != "en":
            lang_file = os.path.join(translations_dir, f"{self.language}.json")
            if os.path.exists(lang_file):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading {self.language} translations: {e}")
            else:
                logger.warning(f"Translation file for {self.language} not found")
    
    def get(self, key, **kwargs):
        """
        Get a translation for a key.
        
        Args:
            key (str): Translation key
            **kwargs: Format arguments for the translation
            
        Returns:
            str: Translated string
        """
        # Try to get from requested language
        translation = self.translations.get(key)
        
        # Fall back to English if not found
        if translation is None:
            translation = self.fallback_translations.get(key)
        
        # Fall back to key if still not found
        if translation is None:
            return key
        
        # Format with provided arguments
        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError as e:
                logger.error(f"Missing format argument in translation: {e}")
                return translation
            except Exception as e:
                logger.error(f"Error formatting translation: {e}")
                return translation
        
        return translation

# Global translator instance
_translator = None

def get_translator(language=None):
    """
    Get the global translator instance.
    
    Args:
        language (str, optional): Language code to use
        
    Returns:
        Translator: Translator instance
    """
    global _translator
    
    if language or _translator is None:
        _translator = Translator(language or "en")
    
    return _translator

def translate(key, **kwargs):
    """
    Translate a key.
    
    Args:
        key (str): Translation key
        **kwargs: Format arguments for the translation
        
    Returns:
        str: Translated string
    """
    return get_translator().get(key, **kwargs)

# Shorthand function
_ = translate
