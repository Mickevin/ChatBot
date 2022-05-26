# Scripts développés stockés sur Github permettant l’exécution du pipeline complet pour générer l’application web chatbot, entraîner et évaluer le modèle.
import json, time, uuid, logging, os, time, random

from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

from opencensus.ext.azure.log_exporter import AzureLogHandler
from sklearn.model_selection import train_test_split


class My_bot():
    def __init__(self, api_id = '9b0fd8a7-81ed-402c-a2a0-b534ee7d78cf', 
                 connection_string='InstrumentationKey=adea8d73-a6d0-4c32-a83d-8e7f6380a431'):
        
        self.connection_string = connection_string
        self.api_id = api_id
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(AzureLogHandler(connection_string=self.connection_string))
        
        self.authoringKey = '123007a9fbfb4ec2bd2e4cd7c88c37fa'
        self.authoringEndpoint = 'https://languep10-authoring.cognitiveservices.azure.com/'
        self.predictionKey = '75800c252f4246e9b665a9015f046091'
        self.predictionEndpoint = 'https://langue-p10.cognitiveservices.azure.com/'
        self.data_test = False

    # Création d'un Bot LUIS
    def create_bot(self, Bot_name:str, creat_entities=False):
        
        self.appName = Bot_name
        self.versionId = "0.1"
        self.intentName = "FlyMe_Booking"
        
        self.client = LUISAuthoringClient(self.authoringEndpoint, 
                                          CognitiveServicesCredentials(self.authoringKey))
        
        self.runtimeCredentials = CognitiveServicesCredentials(self.predictionKey)
        self.clientRuntime = LUISRuntimeClient(endpoint=self.predictionEndpoint, 
                                               credentials=self.runtimeCredentials)
        
        # define app basics
        self.appDefinition = ApplicationCreateObject(name=self.appName, 
                                                     initial_version_id=self.versionId, culture='en-us')
        self.api_id = self.client.apps.add(self.appDefinition)
        
        print('New botLUIS created !')
        if creat_entities:
            return self.creat_intentant()
        
        
    # Création des entités 
    def creat_intentant(self, mlEntityDefinition = ['or_city', 'dst_city','str_date','end_date', 'budget']):
        return [self.client.model.add_entity(self.api_id, 
                                             self.versionId, name=Entity) for Entity in mlEntityDefinition]
    
    # Envoie de phrase d'exemple au BotLUIS
    def send_example_sentance(self, data, split_train=False, start_train=False):
        """Le jeu de données data doit être un dataframe possédant trois colone:
        1. text : Le texte 
        2. entit : le label de l'entité présente dans le texte
        3. val : la valeur textuelle de l'entité
        """
        
        if split_train:
                data , self.data_test = train_test_split(data)
            
        
        # Fonction permettant de localiser les entités dans le text
        def get_example_label(utterance, entity_name, value):
            """Build a EntityLabelObject.
            This will find the "value" start/end index in "utterance", and assign it to "entity name"
            """
            utterance = utterance.lower()
            value = value.lower()
            return {
                'entity_name': entity_name,
                'start_char_index': utterance.find(value),
                'end_char_index': utterance.find(value) + len(value)
            }
        
        def labeledExampleUtterance(data, intentName = "FlyMe_Booking"):
    
            data_Uterance = []
            for text in data.text.unique():
                data_temp = data[data.text == text][['entit','val']]
                data_json = {
                    "text": text,
                    "intentName": intentName,
                    "entityLabels": [get_example_label(text, data_temp.entit.iloc[n], data_temp.val.iloc[n]) 
                                     for n in range(len(data_temp))]
                }
                data_Uterance.append(data_json)

            return data_Uterance
        
        labeledExampleUtteranceWithMLEntity = labeledExampleUtterance(data)
        n = 0
        for example in labeledExampleUtteranceWithMLEntity:
            try: client.examples.add(self.api_id, self.versionId, example)
            except : n+=1
        print('ExampleUtteranceWithMLEntity send successfully')
        print(f'Faill to send {n} example')
        
        if start_train:
            self.train_model()
        
    def train_model(self):
        self.client.train.train_version(self.api_id, self.versionId)
        waiting = True
        while waiting:
            info = self.client.train.get_status(self.api_id, self.versionId)

            waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
            if waiting:
                print ("Waiting 10 seconds for training to complete...")
                time.sleep(10)
            else: 
                print ("trained")
                waiting = False
                
    def publish(self):
        self.client.apps.update_settings(self.api_id, is_public=True)
        self.responseEndpointInfo = self.client.apps.publish(app_id, versionId, is_staging=False)
        

    def prediction(self, text:str):
        self.runtimeCredentials = CognitiveServicesCredentials(self.predictionKey)
        self.clientRuntime = LUISRuntimeClient(endpoint=self.predictionEndpoint, credentials=self.runtimeCredentials)

        # Production == slot name
        predictionRequest = { "query" : text }

        predictionResponse = self.clientRuntime.prediction.get_slot_prediction(self.api_id, 
                                                                               "Production", 
                                                                               predictionRequest, 
                                                                               show_all_intents=False)
        return predictionResponse.prediction.entities
    
    def scoring(self, data, set_=False):
        if set_==False and self.data_test:
            label = self.data_test.entit.unique()
            score = []

            for n in range(len(label)):
                rep = self.data_test[self.data_test.entit == label[n]].text.apply(lambda x: self.prediction(x))

                score.append(np.array([label[n] in u for u in  rep]).sum()/50*100)
                print(f'Score "{label[n]}" : {score[n]}%.')

            return score
        
        else:
            label = data.entit.unique()
            score = []

            for n in range(len(label)):
                rep = data[data.entit == label[n]].text.apply(lambda x: self.prediction(x))

                score.append(np.array([label[n] in u for u in  rep]).sum()/len(rep)*100)
                print(f'Score "{label[n]}" : {score[n]}%.')

            return score


    # Fonction permettant d'envoyer des allerte de niveau info
    def info(self, message, dic=None):
        properties = {'custom_dimensions': dic}

        self.logger.setLevel(logging.INFO)
        self.logger.info(message, properties)

    # Fonction permettant d'envoyer des allerte de niveau warning  
    def warning(self, message, dic=None):
        properties = {'custom_dimensions': dic}

        self.logger.setLevel(logging.WARNING)
        self.logger.warning(message, properties)

    # Fonction permettant d'envoyer des allerte de niveau error  
    def error(self, message, dic=None):
        properties = {'custom_dimensions': dic}

        self.logger.setLevel(logging.ERROR)
        self.logger.error(message, properties)

    # Fonction permettant d'envoyer des allerte de niveau critical  
    def critical(self, message, dic=None):
        properties = {'custom_dimensions': dic}

        self.logger.setLevel(logging.CRITICAL)
        self.logger.exception(message, extra=properties)
        
        
class AppInsights():
    def __init__(self, UserID, key):
        self.key = key
        self.UserID = UserID
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(AzureEventHandler(connection_string=self.key))
        self.logger.setLevel(logging.INFO)
        self.entity = None
        self.trace = {}
        self.n_message = 0
        self.err = 0
    
    def n_messages(self):
        self.n_message+=1
        if self.n_message >10 and self.n_message <15:
            self.warning(f'Warning, to many message User{self.UserID}')

        elif self.n_message >15:
            self.critical(f'Warning, to many message User{self.UserID}')

    def message_error(self):
        self.err+=1
        if self.err >3:
            self.error(f'To many message eroro UserID {DefaultConfig.CLIENT_ID}')

    # Fonction permettant d'envoyer des allerte de niveau info
    def info(self, message, entities=False):
        if entities:
            self.trace['entities'] = str(list(self.entity.values()))
            self.trace['errors'] = self.err
        properties = {'custom_dimensions': self.trace}
        self.logger.setLevel(logging.INFO)
        self.logger.info(message, extra=properties)
        
    # Fonction permettant d'envoyer des allerte de niveau warning  
    def warning(self, message):
        properties = {'custom_dimensions': self.trace}
        
        self.logger.setLevel(logging.WARNING)
        self.logger.warning(message, extra=properties)
        
    # Fonction permettant d'envoyer des allerte de niveau error  
    def error(self, message):
        properties = {'custom_dimensions': self.trace}
        
        self.logger.setLevel(logging.ERROR)
        self.logger.error(message, extra=properties)
        
    # Fonction permettant d'envoyer des allerte de niveau critical  
    def critical(self, message,entities=False):
        if entities:
            self.trace['entities'] = str(list(self.entity.values()))
            self.trace['errors'] = self.err
        properties = {'custom_dimensions': self.trace}
        
        self.logger.setLevel(logging.CRITICAL)
        self.logger.critical(message, extra=properties)
