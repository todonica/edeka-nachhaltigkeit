# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
import googlemaps
import datetime
from ask_sdk_model import Response

from getsunshinetime import getsunshinetime

import requests
import pytz
import json

global googlekey
googlekey = 'AIzaSyBYNoAfHhpJ-mS9KzzOJZkZGxooFVZdKos'
global owm_key
owm_key = "1e4f0d6278aa8de56f419ed1baae3052"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hallo wie kann ich dir helfen?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class ShoppingWeatherIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ShoppingWeather")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        slots = handler_input.request_envelope.request.intent.slots # Get slots
        city = slots['city'] # Get City from Slot
        gmaps = googlemaps.Client(key=googlekey) # Init google api
        results = gmaps.places_autocomplete_query("Edeka "+city.value) # Get Edekas near city
        details = gmaps.place(results[1]['place_id'])
        address = details['result']['formatted_address']
        lat = details['result']['geometry']['location']['lat']
        lon = details['result']['geometry']['location']['lng'] # Get coordinates
        url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric&exclude=current,minutely,daily,alerts" % (lat, lon, owm_key) # get weather at coordinates
        opentime = None 
        closetime = None
        if "opening_hours" in details["result"]: # Check if opening
            opening =  details["result"]["opening_hours"]["periods"]["day" == datetime.datetime.now().weekday()]["open"]["time"] 
            closing =  details["result"]["opening_hours"]["periods"]["day" == datetime.datetime.now().weekday()]["close"]["time"]
            opentime = datetime.datetime.strptime(opening,"%H%M").time()      
            closetime = datetime.datetime.strptime(closing,"%H%M").time()
        else:
            opentime = datetime.time(8,0)      
            closetime = datetime.time(21,0)
        answerAddress = "Ich empfehle den EDEKA in der Straße "+address +". "
        response = requests.get(url)
        weather = json.loads(response.text)
        start,end,getwet = getsunshinetime(weather,opentime,closetime)
        answerWeather = None
        if datetime.datetime.now().time()>closetime:
            logger.info(str(datetime.datetime.now()))
            answerWeather = "Geöffnet war heute zwischen: " + opentime.strftime("%H:%M") + " Uhr und " + closetime.strftime("%H:%M") + " Uhr."
        elif getwet:
            answerWeather =  "Geöffnet ist heute zwischen: " + opentime.strftime("%H:%M") + " Uhr und " + closetime.strftime("%H:%M") + " Uhr. Du wirst heute nass"
        else:
            answerWeather = "Wenn du heute zwischen: " + start.strftime("%H:%M") + " Uhr und " + end.strftime("%H:%M") + " einkaufst bleibst du trocken"

        speak_output = answerAddress + answerWeather

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Du kannst mich fragen, wann der bester Zeitpunkt ist einkaufen zu gehen!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Tschüß und schönen Tag noch!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Das habe ich leider nicht verstanden, bitte mich um Hilfe, um meine Fähigkeiten kennenzulernen"
        reprompt = "Das habe ich nicht verstanden. Wie kann ich dir helfen?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Du hast " + intent_name + " getriggert."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry ich habe das nicht verstanden, versuche es nochmal"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(ShoppingWeatherIntentHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()