from pixiedust.display.app import *
from .baseWelcome import BaseWelcome
from pixiedust.utils import Logger
import requests

@PixieApp
@Logger()
class PeaceTechTraining(BaseWelcome):
    def getDialogOptions(self):
        return {
            "title": "Training Data Generation"
        }
    def onCountrySelected(self):
        self.alerts=self.getAlerts(self.selectedCountry)
        self.alertIterator = enumerate(self.alerts['key'].values.tolist())
        self.tweetUrlIterator = None
        
    def getNextTweetUrl(self):
        item = next(self.tweetUrlIterator, None) if self.tweetUrlIterator is not None else None
        if item is None:
            self.tweetUrlIterator = None
            self.curKeyAlert = next(self.alertIterator, None)
            if self.curKeyAlert is None:
                return None
            self.curAlert = self.getAlert(self.curKeyAlert[1])
            if len(self.curAlert.index)>0:
                self.tweetUrlIterator = enumerate( self.curAlert['url'].values.tolist())
            return self.getNextTweetUrl()
        return item
    
    @route(selectedCountry="*")
    def genTrainingData(self):
        item = self.getNextTweetUrl()
        if item is None:
            return "<div>No more data to train</div>"
        
        total = len(self.curAlert.index)
        self.index = item[0]
        url = item[1]
        
        oembed = "https://publish.twitter.com/oembed?url={}".format(url)
        try:
            html=requests.get(oembed).json()['html']
        except Exception as e:
            html = "OOPS got exception {} for url {}".format(e, url)
            
        if self.options.get("targetDivId", None) is not None:
            return html
        fragment = """
<div class="well" style="text-align:center;font-weight: bold;font-size: x-large;">
    Processing alert "<span class="no_loading_msg" id="alert{{prefix}}">{{this.curKeyAlert[1]}}</span>" 
    <span id="badge{{prefix}}" class="badge no_loading_msg" style="font-size: x-large">{{index + 1}}/{{total}}</span>
</div>
<div style="height: calc(100% - 120px);overflow: auto;text-align: center" id="tweet{{prefix}}" pd_loading_msg="Loading Next Tweet...">
    {{html}}
</div>

<div style="text-align:center">
{%for indicator in indicators%}
    <button type="submit" class="btn btn-primary">{{indicator}}
        <target pd_target="tweet{{prefix}}"/>
        <target pd_target="alert{{prefix}}" pd_script="print(self.curKeyAlert[1])"/>
        <target pd_target="badge{{prefix}}">
            <pd_script>
                print( '{}/{}'.format(self.index+1, len(self.curAlert.index)) )
            </pd_script>
        </target>
    </button>
{%endfor%}
</div>
<div style="text-align:center;margin-top:5px">
    <button type="submit" class="btn btn-primary">Skip
        <target pd_target="tweet{{prefix}}"/>
        <target pd_target="alert{{prefix}}" pd_script="print(self.curKeyAlert[1])"/>
        <target pd_target="badge{{prefix}}">
            <pd_script>
                print( '{}/{}'.format(self.index+1, len(self.curAlert.index)) )
            </pd_script>
        </target>
    </button>
</div>
        """
        self._addHTMLTemplateString(fragment, indicators = BaseWelcome.indicators, index=self.index, total=total, url=url, html=html)