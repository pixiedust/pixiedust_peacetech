from pixiedust.display.app import *
from pixiedust import Logger
from pixiedust_peacetech import *
from pixiedust_peacetech.watsonTrainNLCApp import NLCTrainer
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
        self.alerts=self.getAlerts("20170223", "20170406", self.selectedCountry)
        
    @route(selectedCountry="*", listAlerts="*")
    def showListAlerts(self):
        return """
<table class="table table-condensed">
    <thead>
        <tr>
            {%for col in this.listAlerts.columns%}
            <th>{{col}}</th>
            {%endfor%}
            <th>Predicted Indicator</th>
        </tr>
    </thead>
    <tbody>
        {%for row in this.listAlerts.iterrows()%}
        {%set rowIndex = loop.index%}
        <tr>
            {%for col in this.listAlerts.columns%}
            <th class="{{col}}{{prefix}}">{{row[1][col]}}</th>
            {%endfor%}
            <th id="predictedIndicator{{rowIndex}}{{prefix}}" class="predictedIndicator{{prefix}}" url="{{row[1]['url']}}">
                {%if loop.index < 20%}
                {{this.classify(row[1]['url'])}}
                {%endif%}
            </th>
        </tr>
        {%endfor%}
    </tbody>
</table>
<script>
/*$(".predictedIndicator{{prefix}}").each(function(){
    debugger;
    pixiedust.executeDisplay({{pd_controls}}, {
        "targetDivId": this.getAttribute("id")
    });
    $(this).text( this.getAttribute("url"));
})*/
</script>
"""
        
    @route(selectedCountry="*")
    def showAlerts(self):
        return """
<div class="row" style="max-height:{{'100%' if this.runInDialog else '500px'}};overflow:auto">
    <div class="form-group col-sm-3" style="padding-right:10px;">
        <ul class="nav nav-pills nav-stacked">
            {%for key in this.alerts['key'].values.tolist()%}
            <li class="{{'active' if loop.first else ''}}" pd_target="target{{prefix}}"
                pd_refresh
                pd_script="self.listAlerts = self.getAlert('{{key}}')">
                <a href="#">{{key}}</a>
            </li>
            {%endfor%}
        </ul>
        
    </div>
    <div class="form-group col-sm-9">
        <div id="target{{prefix}}"></div>
    </div>
</div>
"""  