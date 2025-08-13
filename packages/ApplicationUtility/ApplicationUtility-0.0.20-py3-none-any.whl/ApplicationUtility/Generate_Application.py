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
from copy import deepcopy
from loggerutility import deployment_log
import psycopg2

class Generate_Application:

    connection           = None
    dbDetails            = ''
    menu_model           = ''
    token_id           = ''
    
    def get_database_connection(self, dbDetails):
        try:
            if dbDetails['DB_VENDORE'] != None:
                klass = globals()[dbDetails['DB_VENDORE']]
                dbObject = klass()
                connection_obj = dbObject.getConnection(dbDetails)
            return connection_obj
        except (cx_Oracle.Error, psycopg2.Error) as error:
            logger.log(f"Error while database connection")
            deployment_log(f"Error while database connection : {error}")
            raise Exception(f"Error while database connection : {error}")

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

    def process_navigation_structure(self, input_json):
        nav_data = input_json['navigation']
        processed_nav = []
        parent_nodes = [node for node in nav_data if node['parent_id'] == '']
        app_id = input_json["application"]["id"]
        parentcounter = 0
        
        for idx, node in enumerate(parent_nodes):
            parentcounter += 1
            new_node = deepcopy(node)
            new_node['process_node'] = False
            new_node["menu_path"] = f"{app_id}.{parentcounter}"
            processed_nav.append(new_node)
        
        while True:
            unprocessed_node = None
            for node in processed_nav:
                if not node['process_node']:
                    unprocessed_node = node
                    break
            
            if not unprocessed_node:
                break
                
            unprocessed_node['process_node'] = True
            parent_menu_path = unprocessed_node['menu_path']
            children = [node for node in nav_data if node['parent_id'] == unprocessed_node['id']]
            
            for counter, child in enumerate(children, 1):
                new_child = deepcopy(child)
                new_child['process_node'] = False
                if 'order' in child:
                    menu_order = child['order'] + 1
                else:
                    menu_order = counter
                    counter += 1
                    
                new_child['menu_path'] = f"{parent_menu_path}.{menu_order}"
                processed_nav.append(new_child)
        
        new_json = {
            'application': input_json['application'],
            'navigation': processed_nav
        }
        
        return new_json

    def genearate_application_with_model(self):

        logger.log(f"\n\n {'-' * 55 }  Navigation deployment service started {'-' * 55 }  \n\n")
        deployment_log(f"\n\n {'-' * 55 }  Navigation deployment service started {'-' * 55 }  \n\n")

        jsondata = request.get_data('jsonData', None)
        jsondata = json.loads(jsondata[9:])
        logger.log(f"\nJsondata inside Manage_Menu class:::\t{jsondata} \t{type(jsondata)}")

        if "menu_model" in jsondata and jsondata["menu_model"] is not None:
            self.menu_model = jsondata["menu_model"]
            logger.log(f"\nInside menu_model value:::\t{self.menu_model}")

        if "dbDetails" in jsondata and jsondata["dbDetails"] is not None:
            self.dbDetails = jsondata["dbDetails"]
            logger.log(f"\nInside dbDetails value:::\t{self.dbDetails}")

        if "token_id" in jsondata and jsondata["token_id"] is not None:
            self.token_id = jsondata["token_id"]
            logger.log(f"\nInside token_id value:::\t{self.token_id}")

        deployment_log(f"Database details ::: {self.dbDetails}")
        self.connection = self.get_database_connection(self.dbDetails)
        deployment_log(f"Database connection created ::: {self.connection}")

        if self.connection:
            try:

                token_status = common.validate_token(self.connection, self.token_id)
                deployment_log(f"Token validation status ::: {token_status}")

                if token_status == "active":

                    deployment_log(f"Navigation processing start...")
                    appl_mst = ApplMst()
                    appl_mst.process_data(self.connection, self.menu_model, self.dbDetails['DB_VENDORE'])

                    user_rights = UserRights()
                    user_rights.process_data(self.connection, self.menu_model, self.dbDetails['DB_VENDORE'])

                    self.menu_model = self.process_navigation_structure(self.menu_model)

                    itm2menu = Itm2Menu()
                    itm2menu.process_data(self.connection, self.menu_model, self.dbDetails['DB_VENDORE'])

                    self.commit()
                    deployment_log(f"Changes commited")

                    trace = traceback.format_exc()
                    descr = str("Application and Menus Deployed Successfully.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                elif token_status == "inactive":
                    trace = traceback.format_exc()
                    descr = str("Token Id is not Active.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                else:
                    trace = traceback.format_exc()
                    descr = str("Invalid Token Id.")
                    returnErr = common.getErrorXml(descr, trace)
                    logger.log(f'\n Exception ::: {returnErr}', "0")
                    deployment_log(f"{descr}")
                    return str(returnErr)
                
            except Exception as e:
                logger.log(f"Rollback due to error: {e}")
                self.rollback()
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                deployment_log(f"Exception in Navigation deployment process ::: {descr}")
                deployment_log(f"Rollback changes")
                return str(returnErr)
                
            finally:
                logger.log('Closed connection successfully.')
                deployment_log("Closed connection successfully.")
                self.close_connection()
        else:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str("Connection fail")
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            deployment_log(f"Exception ::: {descr}")
            return str(returnErr)


