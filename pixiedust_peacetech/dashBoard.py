from pixiedust_peacetech import *
from pixiedust.display.app import *
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as features
from pixiedust.utils.shellAccess import ShellAccess
import requests

@PixieApp
@Logger()
class PixieAppBoard(BaseWelcome):
    # colombia is 23424787 and egypt is 23424802
    # /places/search/{english name}

    def onCountrySelected(self):
        self.pixieapp_entity=self.getAlerts(self.selectedCountry)
        self.pixieapp_entity['count']=1
        self.alerts=self.pixieapp_entity
        if self.selectedCountry == "23424802":
            self.countryName = "Egypt"
        else:
            self.countryName = "Colombia"
        self.newsstories=self.getNews()
        self.allalerts = self.getMappedAlerts()
        self.violentalerts=self.alerts[self.alerts['violent'] == 'Violent']
        self.commentary = self.getCommentary()
        self.hashtags = self.getHashtags()

    def showWatsonResults(self):
        if self.alert is None:
            print("No Audit Trail found")
            return
        
        html=""
        for ar in self.alert.values.tolist()[:10]:
            oembed = "https://publish.twitter.com/oembed?url={}".format(ar[4])
            try:
                html+=requests.get(oembed).json()['html']
            except Exception as e:
                self.error("OOPS got exception {} for url {}".format(e, ar[4]))

        response = ShellAccess.natural_language_understanding.analyze(
            html= html,
            features=[features.Concepts(), features.Entities(), features.Keywords()],
            language="ES"
        )        
        print("<pre>" + json.dumps(response, indent=2) + "</pre>")
    
    
    def getDialogOptions(self):
        return {
            "title": "groundTruth global",
            "maximize": "true"
        }

    def selectProfile(self, profile):
        self.selectedProfile = profile

        if profile == "profile1":
            self.selectedCountry = "23424802"
            self.countryName = "Egypt"
        elif profile == "profile2":
            self.selectedCountry = "23424787"
            self.countryName = "Colombia"

        if not hasattr(self, 'selectedCountry'):
            self.selectedCountry = "23424802"


        self.onCountrySelected()

    def updateCountry(self, country):
        self.selectedCountry = country
        self.onCountrySelected()

    @route(selectedCountry="*")
    def routeDashboard(self):
        # body = self.renderTemplate("dashboard/main.html")
        return self._addHTMLTemplate("dashboard/main.html")

    @route()
    def startPage(self):
        return super(PixieAppBoard, self).baseWelcome("dashboard/landing.html")