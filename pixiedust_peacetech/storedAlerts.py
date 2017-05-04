
from pixiedust.utils.shellAccess import ShellAccess
from py4j.protocol import Py4JError
import numpy
from pyspark.sql.types import *

class StoredAlerts(object):    
    def __init__(self, selectedCountry):
        if ShellAccess.dashDbCredentials is None:
            raise Exception("No DashDb credentials specified. Please create a variable named dashDbCredentials")
        self.props = { 'user' : ShellAccess.dashDbCredentials['username'], 'password' : ShellAccess.dashDbCredentials['password'] }
        self.jdbcurl= ShellAccess.dashDbCredentials['jdbcurl']
        self.alertsTableName = "{}.ALERTS_{}".format(ShellAccess.dashDbCredentials['username'].upper(), selectedCountry)
        self.tweetsTableName = "{}.TWEETS_{}".format(ShellAccess.dashDbCredentials['username'].upper(), selectedCountry)
        self.patchDB2Dialect()
        try:
            self.alertsRDD = ShellAccess.sqlContext.read.jdbc(self.jdbcurl,self.alertsTableName,properties=self.props)
            self.tweetsRDD = ShellAccess.sqlContext.read.jdbc(self.jdbcurl,self.tweetsTableName,properties=self.props)
        except Py4JError as e:
            if hasattr(e.java_exception, "getErrorCode") and e.java_exception.getErrorCode() == -204:
                self.alertsRDD = ShellAccess.sc.emptyRDD()
            else:
                raise

    def patchDB2Dialect(self):
        scalaCode = """
import org.apache.spark.sql.jdbc._
import org.apache.spark.sql.types.{StringType, DataType}

def unregisterDialect(dialect: String){
    val dialectClass = JdbcDialects.getClass
    val method1 = dialectClass.getDeclaredMethod("get", classOf[String])
    method1.setAccessible(true)
    val dialectObj = method1.invoke(JdbcDialects, dialect).asInstanceOf[JdbcDialect] 
    println(dialectObj)
    JdbcDialects.unregisterDialect(dialectObj)
}

object MyDialect extends JdbcDialect {
  override def canHandle(url: String): Boolean = url.startsWith("jdbc:db2")
  override def getJDBCType(dt: DataType): Option[JdbcType] = dt match {
    case StringType => Option(JdbcType("VARCHAR(1000)", java.sql.Types.VARCHAR))
    case _ => None
  }
}

unregisterDialect("jdbc:db2")
JdbcDialects.registerDialect(MyDialect)
        """
        get_ipython().run_cell_magic('scala','cl=dialect',scalaCode)
        
    def saveToDash(self, enrichedAlerts, enrichedTweets):
        self.saveRDD( self.createRDD(enrichedAlerts), self.alertsTableName )
        self.saveRDD( self.createRDD(enrichedTweets), self.tweetsTableName )

    def createRDD(self, pdf):
        structTypes = []
        for col in pdf.columns.values.tolist():
            structTypes.append( StructField(col, FloatType() if pdf[col].dtype == numpy.float64 else StringType(), True))

        return ShellAccess.sqlContext.createDataFrame(pdf, StructType( structTypes ))

    def saveRDD(self, rdd, tblName):
        rdd.write.mode("append").jdbc(self.jdbcurl, tblName ,properties=self.props)

