from .Database import Database
from datetime import datetime, time


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_history():
        sql = "SELECT * from History"
        return Database.get_rows(sql)

    @staticmethod
    def read_temp():
        sql = "SELECT Value FROM History where	`Component id` = 2;"
        return Database.get_rows(sql)

    @staticmethod
    def read_temp_hist():
        sql = "SELECT Value, Timestamp FROM History where `Component id` = 2 order by Timestamp desc limit 25;"
        return Database.get_rows(sql)

    @staticmethod
    def read_rain_hist():
        sql = "SELECT Value, Timestamp FROM History where `Component id` = 4 order by Timestamp desc limit 25;"
        return Database.get_rows(sql)

    @staticmethod
    def update_history(component_id, actie_id, value):
        date = datetime.now()
        sql = "INSERT into History VALUES (0,%s,%s,%s,%s)"
        params = [component_id, actie_id, date, value]
        return Database.execute_sql(sql, params)

    @staticmethod
    def project_on():
        sql = "UPDATE Components SET `Status` = 1 WHERE `Status` = 0;"
        return Database.execute_sql(sql)

    @staticmethod
    def component_off(id):
        sql = "UPDATE Components SET `Status` = 0 WHERE id = %s;"
        params = [id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def component_on(id):
        sql = "UPDATE Components SET `Status` = 1 WHERE id = %s;"
        params = [id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def project_off():
        sql = "UPDATE Components SET `Status` = 0 WHERE `Status` = 1"
        return Database.execute_sql(sql)
