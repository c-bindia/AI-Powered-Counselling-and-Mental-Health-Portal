# counsellingapp/services/ai_assistant.py

import google.generativeai as genai
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.conf import settings

class MentalHealthAIAssistant:
    def __init__(self, conversation_id=None):
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        # Define safety settings here
        # These will apply to all generations from this model instance
        safety_settings = [
            {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_NONE},
            {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": HarmBlockThreshold.BLOCK_NONE},
            {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
            {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
        ]

        # Initialize the model with safety settings
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            safety_settings=safety_settings # Pass safety_settings here
        )
        self.chat = self.model.start_chat(history=[])
        self.conversation_id = conversation_id
        self.response = None

    def get_ai_response(self, user_message):
        try:
            print(f"DEBUG: Attempting AI response for message: '{user_message}'")
            print(f"DEBUG: Current API Key (first 5 chars): {settings.GOOGLE_API_KEY[:5]}...")

            # Send only the text message
            response = self.chat.send_message(user_message)

            # --- REMOVE THIS BLOCK ---
            # Do NOT try to modify response.candidates[0].safety_ratings after the fact.
            # The error explicitly tells you this is wrong.
            # if response.candidates and hasattr(response.candidates[0], 'safety_ratings'):
            #     response.candidates[0].safety_ratings = [
            #         HarmCategory.HARM_CATEGORY_HATE_SPEECH, HarmBlockThreshold.BLOCK_NONE,
            #         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, HarmBlockThreshold.BLOCK_NONE,
            #         HarmCategory.HARM_CATEGORY_HARASSMENT, HarmBlockThreshold.BLOCK_NONE,
            #         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, HarmBlockThreshold.BLOCK_NONE,
            #     ]
            # --- END REMOVED BLOCK ---


            ai_response = response.text
            return ai_response

        except genai.types.BlockedPromptException as e:
            error_message = f"AI response blocked due to safety concerns: {e}"
            print(f"!!!!!!! CRITICAL AI GENERATION ERROR !!!!!!!: {error_message}")
            return "I'm sorry, I cannot respond to that. Your message might violate safety guidelines."
        except Exception as e:
            error_message = f"Critical AI generation error: {e}"
            print(f"!!!!!!! CRITICAL AI GENERATION ERROR !!!!!!!: {error_message}")
            raise # Re-raise the exception to be caught in the view