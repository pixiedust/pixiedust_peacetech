from pixiedust.display.app import *
from pixiedust.utils import Logger

@PixieApp
@Logger()
class BaseWelcome():
    
    #subclass can override
    def onCountrySelected(self):
        pass
    
    @route()
    def baseWelcome(self):
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