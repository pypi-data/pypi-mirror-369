import cx_Oracle
import json
from DatabaseConnectionUtility import Oracle 
import loggerutility as logger
from loggerutility import deployment_log

class UserRights:

    menu_model = {}

    def check_user_rights(self, application, connection):
        if not connection:
            deployment_log(f"Database connection not found!")
            return False
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM USER_RIGHTS WHERE APPLICATION = '{application}'")
            deployment_log(f"USER_RIGHTS table select query ::: SELECT COUNT(*) FROM USER_RIGHTS WHERE APPLICATION = '{application}'")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except cx_Oracle.Error as error:
            logger.log(f"Error: {error}")
            deployment_log(f"Error in check_user_rights function: {error}")
            return False
        
    def process_data(self, conn, app_model, con_type):
        logger.log(f"Start of UserRights Class")
        deployment_log(f"\n--------------------------------- Start of UserRights Class -------------------------------------\n")
        self.menu_model = app_model
        application_name = self.menu_model['application']['id']
        logger.log(f"application_name ::: {application_name}")
        deployment_log(f"Application Name ::: {application_name}")
        exsist = self.check_user_rights(application_name, conn)
        logger.log(f"exsist ::: {exsist}")
        deployment_log(f"Result of check_user_rights function ::: {exsist}")
        if exsist:
            cursor = conn.cursor()
            model_obj_name_list = [i['obj_name'].lower() for i in self.menu_model['navigation']]
            logger.log(f"model_obj_name_list:: {model_obj_name_list}")

            deployment_log(f"USER_RIGHTS table select query ::: SELECT obj_name FROM USER_RIGHTS WHERE TRIM(APPLICATION) = TRIM('{application_name}')")
            cursor.execute(f"""SELECT obj_name FROM USER_RIGHTS WHERE TRIM(APPLICATION) = TRIM('{application_name}')""")
            data_obj_name_list = cursor.fetchall()
            logger.log(f"data_obj_name_list:: {data_obj_name_list}")
            for obj_name_list in data_obj_name_list:
                obj_name = obj_name_list[0]
                if obj_name not in model_obj_name_list:
                    deployment_log(f"Data for APPLICATION: {application_name} having no user rights.")
                    raise KeyError(f"Data for APPLICATION: {application_name} having no user rights.")          
            cursor.close()
            for navigation in self.menu_model['navigation']:
                logger.log(f"navigation::; {navigation}")
                logger.log(f"application_name ::: {application_name}")
                logger.log(f"obj_name ::: {navigation['obj_name'].lower()}")
                cursor = conn.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE USER_RIGHTS SET
                        MENU_ROW = :menu_row, MENU_COL = :menu_col, MENU_SUBCOL = :menu_subcol, LEVEL_4 = :level_4, LEVEL_5 = :level_5
                        WHERE TRIM(APPLICATION) = TRIM(:application) AND TRIM(OBJ_NAME) = TRIM(:obj_name)
                    """
                    values = {
                        'menu_row': navigation['menu_row'],
                        'menu_col': navigation['menu_col'],
                        'menu_subcol': navigation['menu_subcol'],
                        'level_4': navigation['level_4'],
                        'level_5': navigation['level_5'],
                        'application': application_name,
                        'obj_name': navigation['obj_name'].lower()
                    }
                    logger.log(f"\n--- Class UserRights ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"USER_RIGHTS table update query for Oracle database ::: {update_query}")
                    deployment_log(f"USER_RIGHTS table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in USER_RIGHTS table for Oracle database.")
                else:
                    update_query = """
                        UPDATE USER_RIGHTS SET
                            MENU_ROW = %s,
                            MENU_COL = %s,
                            MENU_SUBCOL = %s,
                            LEVEL_4 = %s,
                            LEVEL_5 = %s
                        WHERE TRIM(APPLICATION) = TRIM(%s) 
                        AND TRIM(OBJ_NAME) = TRIM(LOWER(%s))
                    """
                    values = (
                        navigation['menu_row'],
                        navigation['menu_col'],
                        navigation['menu_subcol'],
                        navigation['level_4'],
                        navigation['level_5'],
                        application_name,
                        navigation['obj_name']
                    )
                    logger.log(f"\n--- Class UserRights ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"USER_RIGHTS table update query for Other database ::: {update_query}")
                    deployment_log(f"USER_RIGHTS table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in USER_RIGHTS table for Other database.")
                cursor.close()

        logger.log(f"End of UserRights Class")
        deployment_log(f"End of UserRights Class")