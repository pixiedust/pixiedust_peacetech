from pixiedust.display.app import *
from pixiedust.utils import Logger, cache
from pixiedust.utils.shellAccess import ShellAccess
import requests
from pandas.io.json import json_normalize
import pandas
import json

baseUrl = "https://j26ovra6z7.execute-api.us-east-1.amazonaws.com/prod/"
indicators = ["Economy", "Energy", "Law & Order", "Environment", "Labor"]

@PixieApp
@Logger()
class BaseWelcome():
    indicators = ["Economy", "Energy", "Law & Order", "Environment", "Labor"]
    
    @cache(fieldName="_alerts")
    def getAlerts(self, startDate, endDate=None, location=None):
        if location is not None and endDate is not None:
            restUrl = "{0}alerts/search?startDate={1}&endDate={2}&location={3}".format(baseUrl, startDate, endDate, location)
            return self.normalize(requests.get(restUrl, headers=ShellAccess.headers).json())
        else:
            return self.normalize(requests.get(baseUrl+"alerts?eventDate="+eventDate, headers=headers).json())

    def normalize(self, jsonPayload):
        if len(jsonPayload) > 0:
            return json_normalize(jsonPayload)
        return pandas.DataFrame()
    
    def getAlert(self, alertKey):
        resp = requests.get(baseUrl+"alerts/"+alertKey, headers=ShellAccess.headers).json()
        return self.normalize(resp)
    
    #subclass can override
    def onCountrySelected(self):
        pass
    
    @route()
    def baseWelcome(self):
        if ShellAccess.headers is None:
            return "<div>Error, you must define the GroudTruth DataHub credentials in a variable called headers</div>"
        return """
<div>
  <div class="form-horizontal">
    <div class="form-group">
      <label for="country{{prefix}}" class="control-label col-sm-2">Select a country:</label>
      <div class="col-sm-5">
        <select class="form-control" id="country{{prefix}}">
          <option value="23424802">Egypt</option>
          <option value="23424787">Columbia</option>
        </select>
      </div>
      <div class="col-sm-1">
        <button type="submit" class="btn btn-primary">
          Go
          <pd_script>
self.selectedCountry=$val(country{{prefix}})
self.onCountrySelected()
          </pd_script>
        </button>
      </div>
    </div>
  </div>
</div>
"""