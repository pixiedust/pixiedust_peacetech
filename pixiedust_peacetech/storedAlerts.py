
from pixiedust.utils.shellAccess import ShellAccess
from py4j.protocol import Py4JError

class StoredAlerts(object):    
    def __init__(self, selectedCountry):
        if ShellAccess.dashDbCredentials is None:
            raise Exception("No DashDb credentials specified. Please create a variable named dashDbCredentials")
        props = { 'user' : ShellAccess.dashDbCredentials['username'], 'password' : ShellAccess.dashDbCredentials['password'] }
        jdbcurl= ShellAccess.dashDbCredentials['jdbcurl']
        tableName = "{}.ALERTS_{}".format(ShellAccess.dashDbCredentials['username'].upper(), selectedCountry)
        try:
            self.alertsRDD = ShellAccess.sqlContext.read.jdbc(jdbcurl,tableName,properties=props)
        except Py4JError as e:
            if hasattr(e.java_exception, "getErrorCode") and e.java_exception.getErrorCode() == -204:
                self.alertsRDD = ShellAccess.sc.emptyRDD()
            else:
                raise