from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

import json, time, uuid
import os
import time

from azure.cognitiveservices.knowledge.qnamaker.authoring import QnAMakerClient
from azure.cognitiveservices.knowledge.qnamaker.runtime import QnAMakerRuntimeClient
from azure.cognitiveservices.knowledge.qnamaker.authoring.models import QnADTO, MetadataDTO, CreateKbDTO, OperationStateType, UpdateKbOperationDTO, UpdateKbOperationDTOAdd, EndpointKeysDTO, QnADTOContext, PromptDTO
from azure.cognitiveservices.knowledge.qnamaker.runtime.models import QueryDTO
from msrest.authentication import CognitiveServicesCredentials


class My_bot():
    def __init__(self, api_id = '9b0fd8a7-81ed-402c-a2a0-b534ee7d78cf', 
                 kb_id = '746a8b49-3d96-492b-9ba7-b5cb30de7309'):
        
        self.code = 4
        
        
        def getEndpointKeys_kb(client):
            print("Getting runtime endpoint keys...")
            keys = client.endpoint_keys.get_keys()
            print("Primary runtime endpoint key: {}.".format(keys.primary_endpoint_key))

            return keys.primary_endpoint_key
        
        self.api_id = api_id
        self.kb_id = kb_id
        
        self.authoringKey = '123007a9fbfb4ec2bd2e4cd7c88c37fa'
        self.authoringEndpoint = 'https://languep10-authoring.cognitiveservices.azure.com/'
        self.predictionKey = '75800c252f4246e9b665a9015f046091'
        self.predictionEndpoint = 'https://langue-p10.cognitiveservices.azure.com/'
        
        
        self.subscription_key = 'cbb4bcaa0a334e02a1261cf18aa1ad18'
        self.authoring_endpoint = 'https://qna0.cognitiveservices.azure.com/'
        self.runtime_endpoint = 'https://qna0.azurewebsites.net'
        self.clientKB = QnAMakerClient(endpoint=self.authoring_endpoint, 
                                       credentials=CognitiveServicesCredentials(self.subscription_key))
         
        self.queryRuntimeKey = getEndpointKeys_kb(self.clientKB)
        self.runtimeClient = QnAMakerRuntimeClient(runtime_endpoint=self.runtime_endpoint, 
                                      credentials=CognitiveServicesCredentials(self.queryRuntimeKey))
        
        # We use a UUID to avoid name collisions.
        self.versionId = "0.1"
        self.intentName = "FlyMe.Booking"
        
        self.client = LUISAuthoringClient(self.authoringEndpoint, 
                                          CognitiveServicesCredentials(self.authoringKey))
        
        self.runtimeCredentials = CognitiveServicesCredentials(self.predictionKey)
        self.clientRuntime = LUISRuntimeClient(endpoint=self.predictionEndpoint, 
                                               credentials=self.runtimeCredentials)

        
        self.data = {
            'or_city': False, 
              'dst_city': False,
              'str_date': False,
              'end_date': False,
              'budget': False
             }
        
        self.trad = {
            'or_city': "origin's city", 
              'dst_city': "destination's city",
              'str_date': "day's start",
              'end_date': "end's date",
              'budget': "your budget"
             }


    def prediction(self, text):
        
        def check_reponse(rep):
    
            for k in rep.keys():
                self.data[k] = rep[k]

            data_lost = []
            for k in self.data.keys():
                if self.data[k] == False:
                    data_lost.append(k)

            self.code = len(data_lost)
            self.data_lost = data_lost
            
            return self.get_rep()

        # Production == slot name
        self.predictionRequest = { "query" : text}

        predictionResponse = self.clientRuntime.prediction.get_slot_prediction(self.api_id, 
                                                                                    "Production", 
                                                                                    self.predictionRequest, 
                                                                                    show_all_intents=True)
        rep = predictionResponse.prediction.entities
        return check_reponse(rep)
    
    
    def generate_answer(self, text):
        print ("Querying knowledge base...")

        authHeaderValue = "EndpointKey " + self.queryRuntimeKey

        listSearchResults = self.runtimeClient.runtime.generate_answer(self.kb_id, 
                                                           QueryDTO(question = text), 
                                                           dict(Authorization=authHeaderValue))
        return listSearchResults.answers[0].answer
    
    
    def get_rep(self):
        code = self.code
        if code == 0:
            return bot.generate_answer('0').format(self.data['or_city'][0],
                                                 self.data['dst_city'][0],
                                                 self.data['str_date'][0],
                                                 self.data['end_date'][0],
                                                 self.data['budget'][0])
        elif code == 1:
            return self.generate_answer('1').format(self.trad[self.data_lost[0]])
        elif code == 2:
            return self.generate_answer('2').format(self.trad[self.data_lost[0]], self.trad[self.data_lost[0]])
        elif code == 3:
            return self.generate_answer('3')
        elif code == 4:
            return self.generate_answer('4')
        elif code == 5:
            return self.generate_answer('4')