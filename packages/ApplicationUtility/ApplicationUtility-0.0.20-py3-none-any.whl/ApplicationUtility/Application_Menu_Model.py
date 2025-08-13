import cx_Oracle
from DatabaseConnectionUtility import Oracle 
from DatabaseConnectionUtility import Dremio
from DatabaseConnectionUtility import InMemory 
from DatabaseConnectionUtility import Oracle
from DatabaseConnectionUtility import MySql
from DatabaseConnectionUtility import MSSQLServer 
from DatabaseConnectionUtility import SAPHANA
from DatabaseConnectionUtility import Postgress
import json
from .UserRights import UserRights
import loggerutility as logger
from flask import request
import commonutility as common
import requests, json, traceback
from .ApplMst import ApplMst
from .Itm2Menu import Itm2Menu
from datetime import datetime

class Application_Menu_Model:

    connection           = None
    application_model    = {}
    dbDetails            = ''
    app_name             = ''
    
    def get_database_connection(self, dbDetails):
        if dbDetails['DB_VENDORE'] != None:
            klass = globals()[dbDetails['DB_VENDORE']]
            dbObject = klass()
            connection_obj = dbObject.getConnection(dbDetails)
        return connection_obj

    def commit(self):
        if self.connection:
            try:
                self.connection.commit()
                logger.log("Transaction committed successfully.")
            except cx_Oracle.Error as error:
                logger.log(f"Error during commit: {error}")
        else:
            logger.log("No active connection to commit.")

    def rollback(self):
        if self.connection:
            try:
                self.connection.rollback()
                logger.log("Transaction rolled back successfully.")
            except cx_Oracle.Error as error:
                logger.log(f"Error during rollback: {error}")
        else:
            logger.log("No active connection to rollback.")

    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                logger.log("Connection closed successfully.")
            except cx_Oracle.Error as error:
                logger.log(f"Error during close: {error}")
        else:
            logger.log("No active connection to close.")

    def custom_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  
        raise TypeError(f"Type {type(obj)} not serializable")

    def generate_menu_model(self):
        
        jsondata = request.get_data('jsonData', None)
        jsondata = json.loads(jsondata[9:])
        logger.log(f"\nJsondata inside Manage_Menu class:::\t{jsondata} \t{type(jsondata)}")

        if "app_name" in jsondata and jsondata["app_name"] is not None:
            self.app_name = jsondata["app_name"]
            logger.log(f"\nInside app_name value:::\t{self.app_name}")

        if "dbDetails" in jsondata and jsondata["dbDetails"] is not None:
            self.dbDetails = jsondata["dbDetails"]
            logger.log(f"\nInside dbDetails value:::\t{self.dbDetails}")

        self.connection = self.get_database_connection(self.dbDetails)

        if self.connection:
            try:
                menu_json = {}                
                cursor = self.connection.cursor()

                logger.log(f"app_name :: {self.app_name}")
                logger.log(f"--- Class Application_Menu_Model ---")
                cursor.execute(f"""SELECT * FROM APPL_MST WHERE TRIM(APP_NAME) = TRIM('{self.app_name}')""")
                application_row = cursor.fetchall()
                columns = [desc[0].lower() for desc in cursor.description]
                columns[columns.index('app_name')] = 'id'
                columns[columns.index('descr')] = 'description'
                columns[columns.index('appl_color')] = 'theme_color'
                columns[columns.index('appl_group')] = 'group'
                cursor.close()
                
                cursor = self.connection.cursor()
                result = [dict(zip(columns, row)) for row in application_row]
                json_data = json.dumps(result, default=self.custom_serializer, indent=4)
                menu_json['application'] = json.loads(json_data)[0]

                logger.log(f"--- Class Application_Menu_Model ---")
                cursor.execute(f"""SELECT * FROM ITM2MENU WHERE APPLICATION = '{self.app_name}' ORDER BY level_1, level_2, level_3, level_4, level_5""")
                navigation_row = cursor.fetchall()
                columns1 = [desc[0].lower() for desc in cursor.description]
                columns1[columns1.index('application')] = 'id'
                columns1[columns1.index('descr')] = 'description'
                columns1[columns1.index('icon_path')] = 'icon_image'
                columns1[columns1.index('win_name')] = 'obj_name'

                result1 = [dict(zip(columns1, row)) for row in navigation_row]
                json_data1 = json.dumps(result1, default=self.custom_serializer, indent=4)
                menu_json['navigation'] = json.loads(json_data1)
                cursor.close()

                with open('output.json', 'w') as json_file:
                    json.dump(menu_json, json_file, indent=4)

                trace = traceback.format_exc()
                descr = str("Application menu model created.")
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                return str(returnErr)

            except Exception as e:
                logger.log(f"Rollback due to error: {e}")
                self.rollback()
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                return str(returnErr)
                
            finally:
                logger.log('Closed connection successfully.')
                self.close_connection()
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Connection fail")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)


