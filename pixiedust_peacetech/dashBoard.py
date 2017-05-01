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
        self.pixieapp_entity=self.getAlerts("20170223", "20170406", self.selectedCountry)
        self.pixieapp_entity['count']=1
        self.alerts=self.pixieapp_entity
        if self.selectedCountry == "23424802":
            self.countryName = "Egypt"
        else:
            self.countryName = "Columbia"
    
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
            "title": "PeaceTech IBM GroundTruth"
        }

    @route(selectedCountry="*")
    def routeWelcome(self):
        return self._addHTMLTemplate("dashboard/main.html")