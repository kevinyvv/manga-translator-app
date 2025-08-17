# Standard library imports
import os
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path
import pdb
import logging

from googletrans import Translator
from google import genai

from jikanpy import Jikan

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
jikan = Jikan()

class MangaTranslator:
    def __init__(self, translator_method="google"):
        """
        Initialize the manga translator
        
        Args:
            translator_method (str): Translation method ('google' or 'deepl')
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.logger.setLevel(logging.DEBUG)
        # Configure translation
        self.translator_method = translator_method
        self.translator = Translator()

        with open("utils/languages.json", "r") as f:
            self.languages = json.load(f)

    def get_language_full(self, lang_code: str) -> str:
        """
        Get the full language name from the language code
        
        Args:
            lang_code (str): Language code (e.g., 'ja', 'en')
            
        Returns:
            str: Full language name or None if not found
        """
        return self.languages.get(lang_code, lang_code)

    async def translate(self, text_data, source_lang:str="ja", target_lang:str="en", manga_title:str=None) -> str:
        """
        Translate text using the configured translator method
        
        Returns:
            str: Translated text
        """
        if self.translator_method == "google":
            translated_data = await self.translate_text(text_data, source_lang, target_lang)
            return translated_data
        elif self.translator_method == "genai":
            return self.translate_text_genai(text_data, source_lang, target_lang, manga_title)
        else:
            raise ValueError(f"Unsupported translator method: {self.translator_method}")
        
    
    def translate_text_genai(self, text_data, source_lang:str="ja", target_lang:str="en", manga_title:str=None) -> list:
        """
        Translate extracted text using Google GenAI
        
        Args:
            text_data (list): List of dictionaries with bubble info and text
            source_lang (str): Source language code
            target_lang (str): Target language code
            
        Returns:
            list: Updated text_data with translations added
        """
        self.logger.debug(f"Translating from {source_lang} to {target_lang} using {self.translator_method}")
        
        manga_info = ""

        if manga_title:
            search_results = jikan.search('manga', manga_title, page=1)
            if search_results["data"]:
                top_result = search_results["data"][0]
                manga_info = f"""
                Title: {top_result['title']}\n
                Synopsis: {top_result['synopsis']}\n
                Themes: {', '.join([theme['name'] for theme in top_result['themes']])}\n
                Genres: {', '.join([genre['name'] for genre in top_result['genres']])}\n
                Demographics: {', '.join([demographic['name'] for demographic in top_result['demographics']])}\n
                """
            else:
                manga_info = f"Title: {manga_title}\nNo additional information found.\n"
        
        for item in text_data:
            original_text = item["text"]
            
            # Skip empty text
            if not original_text.strip():
                item["translated_text"] = ""
                continue
            
            # slight delay to avoid rate limiting
            time.sleep(0.5)
            

            prompt = f"""
            You are a translator, translating manga text from one language to another.
            Translate the following text from {self.get_language_full(source_lang)} to {self.get_language_full(target_lang)}:
            {original_text}
            Please return only the translated text without any additional comments or formatting.
            {"Here is some context about the manga:" + 
             manga_info if manga_info else ""}
            """
            
            # print(prompt)
            
            # translate using GenAI
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                item["translated_text"] = response.text
            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                item["translated_text"] = original_text
            
            self.logger.info(f"Translated: '{original_text}' -> '{item['translated_text']}'")
        
        return text_data

    async def translate_text(self, text_data, source_lang:str="ja", target_lang:str="en") -> list:
        """
        Translate extracted text
        
        Args:
            text_data (list): List of dictionaries with bubble info and text
            source_lang (str): Source language code
            target_lang (str): Target language code
            
        Returns:
            list: Updated text_data with translations added
        """
        self.logger.debug(f"Translating from {source_lang} to {target_lang} using {self.translator_method}")
        
        for item in text_data:
            original_text = item["text"]
            
            # Skip empty text
            if not original_text.strip():
                item["translated_text"] = ""
                continue
            
            # slight delay to avoid rate limiting
            time.sleep(0.5)
            
            # translate based on method
            try:
                translation = await self.translator.translate(
                    original_text, src=source_lang, dest=target_lang
                )
                item["translated_text"] = translation.text
            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                item["translated_text"] = original_text
            
            self.logger.info(f"Translated: '{original_text}' -> '{item['translated_text']}'")
        
        return text_data