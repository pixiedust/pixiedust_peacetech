from pixiedust.display.app import *
from pixiedust import Logger
from pixiedust_peacetech import *
from pixiedust_peacetech.watsonTrainNLCApp import NLCTrainer
from .storedAlerts import StoredAlerts
from threading import Thread
from IPython.display import display as ipythonDisplay, HTML, Javascript
import pandas
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
            #ar = [t for t in s['classes'] if t['class_name'] == s['top_class']]
            #if len(ar) > 0:
            #    self.enrichedAlerts.append(
            #        (url, ar[0]['class_name'], ar[0]['confidence'])
            #    )
            results = [(t['class_name'], t['confidence']) for t in s['classes'] if t['class_name'] == s['top_class']]
            return list(results[0]) if len(results) > 0 else ["N/A", 0.0]
            #return "".join(['{} ({})'.format(t['class_name'], t['confidence']) for t in s['classes'] if t['class_name'] == s['top_class']])
        except Exception as e:
            self.exception(e)
            return [str(e), 0.0]

    def onCountrySelected(self):
        message = self.initNLC()
        if message is not None:
            return message
        self.alerts=self.getAlerts(self.selectedCountry)
        self.storedAlerts = StoredAlerts(self.selectedCountry)
        
    #@route(selectedCountry="*", listAlerts="*")
    #def showListAlerts(self):
    #    self._addHTMLTemplate("enrichment/showListAlerts.html")
        
    #@route(selectedCountry="*")
    #def showAlerts(self):
    #    self._addHTMLTemplate("enrichment/showAlerts.html")

    @route(selectedCountry="*")
    def startEnrichment(self):
        return """
<div style="text-align:center;font-size:xx-large">
59 Alerts found. Click start enrichment to proceed
</div>

<div style="text-align:center;margin-top:30px">
<button type="submit" class="btn btn-primary" style="width:80%;height:75px;margin-bottom:20px;">
    <pd_script>self.doEnrichment=True</pd_script>
    Start Enrichment
</button>
</div>
"""

    @route(doEnrichment=True)
    def _doEnrichment(self):
        def processAlerts():
            self.enrichedAlerts = pandas.DataFrame(
                columns=self.alerts.columns.values.tolist() + ['class', 'confidence']
            )
            self.enrichedTweets = None
            for index, row in self.alerts.iterrows():
                if not self.doEnrichment:
                    break;
                self.enrichedAlerts.loc[len(self.enrichedAlerts.index)] = row.values.tolist() + ["Not Yet Computed", 0.0]
                ipythonDisplay(Javascript("""
                    var n = $("#enrichmentProgress{0}");
                    n.attr("value", parseInt( n.attr("value")) + 1);
                """.format(self.prefix)))
                
                tweetsPDF = self.getAlert(row['key'])
                self.tweetsPDF = tweetsPDF
                if self.enrichedTweets is None:
                    self.enrichedTweets = pandas.DataFrame(
                        columns = ['alertKey'] + tweetsPDF.columns.values.tolist() + ["class", "confidence"]
                    )
                
                for index2, row2 in tweetsPDF.iterrows():
                    if not self.doEnrichment:
                        break;
                    ipythonDisplay(Javascript("""
                        $("#enrichmentStatus{0}").text("Processing alert with key: {1} and Tweet {2}");
                """.format(self.prefix, row['key'], row2['key'])))
                    self.enrichedTweets.loc[ len(self.enrichedTweets.index)] = [row['key']] + row2.values.tolist() \
                        + self.classify(row2['url'] )
                
            self.doEnrichment = False
            viewResultsFragment = """
                <button type="submit" class="btn btn-primary" style="width:80%;height:50px;margin-bottom:20px;">
                    <pd_script>self.viewResults=True</pd_script>
                    View Results
                </button>
            """.strip().replace("\n", "")
            ipythonDisplay(Javascript("""
                    $("#results{0}").html('{1}');
                """.format(self.prefix, viewResultsFragment)))
        t = Thread(target=processAlerts)
        t.daemon = True
        t.start()      
        return """
        <div style="text-align:center" id="enrichmentStatus{{prefix}}"></div>
        <progress id="enrichmentProgress{{prefix}}" max="{{this.alerts|length - 1}}" value="0" style="height:0.3em;width:100%">
        </progress>
        
        <div style="text-align:center" id="results{{prefix}}">
            <button type="submit" class="btn btn-primary" pd_norefresh style="width:80%;height:50px;margin-bottom:20px;">
                <pd_script>self.doEnrichment=False</pd_script>
                Cancel
            </button>
        </div>
        """

    @route(viewResults=True)
    def _viewResults(self):
        return """
<div class="row">
    <div class="form-group col-sm-2" style="padding-right:10px;">    
        <p>
        <button type="submit" class="btn btn-primary" pd_target="results{{prefix}}" 
            pd_options="handlerId=barChart;keyFields=class;valueFields=confidence;aggregation=COUNT;rowCount=500;rendererId=bokeh"
            pd_entity="enrichedTweets"> Tweets By Classes
        </button>
        </p>
        <p>
        <button type="submit" class="btn btn-primary" pd_target="results{{prefix}}">
            <pd_script>self.saveToDash()</pd_script>
            Save to DashDB
        </button>
        </p>
    </div>
    <div class="form-group col-sm-10">
        <div id="results{{prefix}}"></div>
    </div>
</div>
"""