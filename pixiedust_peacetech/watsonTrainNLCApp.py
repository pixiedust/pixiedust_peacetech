from pixiedust.display.app import *
from pixiedust.apps.connectionWidget import *
import json
from watson_developer_cloud import NaturalLanguageClassifierV1
from pyspark.sql.functions import length
from pixiedust.utils.shellAccess import ShellAccess
from six import iteritems
from pyspark.sql.functions import lit

@PixieApp
class NLCTrainer(ConnectionWidget):
    @route(trainNLC='true', selectedConnection=None)
    def _selectCloudantConnection(self):
        self.trainNLC='true'
        return """<div pd_widget="DataSourcesList"/>"""
    
    @route(trainNLC='true', cloudantDF="*")
    def preTrain(self):
        return """
<div style="text-align:center, font-size:x-large">Training Database contains {{this.cloudantDF.count()}} documents</div>

<div class="row" pixiedust="{{pd_controls|htmlAttribute}}">
    <div class="form-group col-sm-2" style="padding-right:10px;">    
        <p>
            <button type="submit" class="btn btn-primary" pd_target="trainingResults{{prefix}}" pd_entity="cloudantDF"
                pd_options="handlerId=barChart;keyFields=class;valueFields=count;aggregation=COUNT;rowCount=100;rendererId=matplotlib">
                View Training Data Distribution
            </button>
        </p>    
        <p>
            <button pd_options="doTraining=true" pd_target="training{{prefix}}" type="submit" class="btn btn-primary">
                Proceed with Training
            </button>
        </p>
    </div>
    <div class="form-group col-sm-10">
        <div id="trainingResults{{prefix}}" style="min-height:400px"></div>
    </div>
</div>
"""
    @route(trainNLC='true', cloudantDF="*", doTraining="true")
    def _doTraining(self):
        classes = self.cloudantDF.groupBy("class").count()
        groupCount = classes.count()
        maxPerGroup = int(15000/groupCount)
        groups = {}
        for cl in classes.collect():
            className = cl["class"]
            groups[className] = self.cloudantDF.filter(self.cloudantDF["class"] == className).limit(maxPerGroup)

        with open("/Users/dtaieb/temp/train/egyptNLCTrain.csv", "w") as f:
            for className,group in iteritems(groups):
                rows = group.take(5)
                for row in rows:
                    f.write("{},{}\n".format(row["input"].encode("utf-8","ignore"), row["class"]))
                    
        self.natural_language_classifier.create(open("/Users/dtaieb/temp/train/egyptNLCTrain.csv","r"), language="ar")
        return """<div>Success submitted request, Training in Progress</div>"""
    
    @route(trainNLC='true')
    def _trainNLC(self):
        return """
<div class="well">
    Training using cloudant connection {{this.selectedConnection}}
</div>
<div id="training{{prefix}}">
    <button type="submit" pd_refresh pd_target="training{{prefix}}" class="btn btn-primary">
        <pd_script>self.loadCloudantDF()</pd_script>
        Load Training Data...
    </button>
</div>
"""
    
    def loadCloudantDF(self):
        self.cloudantDF = ShellAccess.sqlContext.read.format("com.cloudant.spark")\
                .option("cloudant.host", "127.0.0.1:5984")\
                .option("cloudant.username","dtaieb")\
                .option("cloudant.password","password")\
                .option("cloudant.protocol", "http")\
                .option("schemaSampleSize", "-1")\
                .load("egypt_training")
        
        self.cloudantDF = self.cloudantDF.filter(self.cloudantDF['class'] != "NaN")\
            .filter(length(self.cloudantDF['input']) < 1024)
        self.cloudantDF=self.cloudantDF.withColumn('count', lit(1))
        self.cloudantDF.cache()

    def removeClassifier(self, classifierId):
        self.natural_language_classifier.remove(classifierId)

    def initNLC(self):
        credentials = self.getPixieAppEntity()
        if credentials is None:
            return "<div>You must provide credentials to your Watson NLC Service</div>"
        
        self.natural_language_classifier = NaturalLanguageClassifierV1(
            username=credentials['username'],
            password=credentials['password'] )

    @route()
    def startScreen(self):
        message = self.initNLC();
        if message is not None:
            return message
        
        nlcList = self.natural_language_classifier.list()
        self._addHTMLTemplate("watsonTrainNLC/classifierList.html", classifiers = nlcList['classifiers'])