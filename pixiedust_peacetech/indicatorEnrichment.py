from pixiedust.display.app import *
from pixiedust import Logger
from pixiedust_peacetech import *
from pixiedust_peacetech.watsonTrainNLCApp import NLCTrainer
from .storedAlerts import StoredAlerts
import requests
from bs4 import BeautifulSoup

@PixieApp
@Logger()
class IndicatorEnrichment(BaseWelcome, NLCTrainer):
    def setup(self):
        self.enrichedAlerts=[]
    def classify(self,url):
        try:
            oembed = "https://publish.twitter.com/oembed?url={}".format(url)
            html = requests.get(oembed).json()['html']
            inputText = "\n".join(BeautifulSoup(html, "lxml").findAll(text=True))
            s = self.natural_language_classifier.classify(self.getPixieAppEntity()['classifierId'], inputText)
            ar = [t for t in s['classes'] if t['class_name'] == s['top_class']]
            if len(ar) > 0:
                self.enrichedAlerts.append(
                    (url, ar[0]['class_name'], ar[0]['confidence'])
                )
            return "".join(['{} ({})'.format(t['class_name'], t['confidence']) for t in s['classes'] if t['class_name'] == s['top_class']])
        except Exception as e:
            return str(e)

    def onCountrySelected(self):
        message = self.initNLC();
        if message is not None:
            return message
        self.alerts=self.getAlerts(self.selectedCountry)
        self.storedAlerts = StoredAlerts(self.selectedCountry)
        
    @route(selectedCountry="*", listAlerts="*")
    def showListAlerts(self):
        self._addHTMLTemplate("enrichment/showListAlerts.html")
        
    @route(selectedCountry="*")
    def showAlerts(self):
        self._addHTMLTemplate("enrichment/showAlerts.html")