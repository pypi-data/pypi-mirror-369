from itertools import islice
import cx_Oracle
from datetime import datetime
import loggerutility as logger
from loggerutility import deployment_log

class Itm2Menu:

    data = {}
    
    def delete_and_insert_itm2menu(self, navigation, application_id, conn, con_type):
        if not conn:
            deployment_log(f"Database connection not found!")
            raise Exception("Oracle connection is not established.")
        
        cursor = conn.cursor()
        application = application_id.strip().upper()
        queryy = f"""
            SELECT COUNT(*) FROM ITM2MENU 
            WHERE APPLICATION = '{application}'
        """
        deployment_log(f"ITM2MENU table select query ::: SELECT COUNT(*) FROM ITM2MENU WHERE APPLICATION = '{application}'")
        cursor.execute(queryy)
        row_exists = cursor.fetchone()[0]
        cursor.close()
        logger.log(f"row_exists :: {row_exists}")
        deployment_log(f"ITM2MENU table select query result::: {row_exists}")

        if row_exists:
            cursor = conn.cursor()
            delete_query = f"""
                DELETE FROM ITM2MENU 
                WHERE TRIM(APPLICATION) = TRIM('{application}')
            """
            deployment_log(f"ITM2MENU table delete query ::: DELETE FROM ITM2MENU WHERE TRIM(APPLICATION) = TRIM('{application}')")
            logger.log(f"\n--- Class Itm2Menu ---\n")
            logger.log(f"{delete_query}")
            cursor.execute(delete_query)
            cursor.close()
            logger.log("Data deleted") 
            deployment_log(f"Data deleted from ITM2MENU table for application name ::: {application}") 

        for navigations in navigation:
            required_keys = ['id']
            missing_keys = [key for key in required_keys if key not in navigations]

            if missing_keys:
                deployment_log(f"Missing required keys for ITM2MENU table: {', '.join(missing_keys)}")
                raise KeyError(f"Missing required keys for ITM2MENU table: {', '.join(missing_keys)}")
            else:
                application = application_id.strip().upper()
                logger.log(f"application name :: {application}")
                deployment_log(f"Application name :: {application}")
                id_val = navigations.get('id', '') or None
                menu_path_val = navigations.get('menu_path', '') or None

                # id_parts = ''
                # if id_val == menu_path_val:
                #     id_parts = menu_path_val
                # else:
                #     if menu_path_val.startswith(id_val):
                #         id_parts = menu_path_val[len(id_val)+1:]
                #     else:
                #         id_parts = menu_path_val

                id_parts = menu_path_val

                logger.log(f"menu_path_val:;  {menu_path_val}")
                logger.log(f"id_parts:;  {id_parts}")
                id_parts = id_parts.split('.')
                logger.log(f"id_parts:;  {id_parts}")
                level_1 = int(id_parts[1]) if len(id_parts) > 1 else 0
                level_2 = int(id_parts[2]) if len(id_parts) > 2 else 0
                level_3 = int(id_parts[3]) if len(id_parts) > 3 else 0
                level_4 = int(id_parts[4]) if len(id_parts) > 4 else 0
                level_5 = int(id_parts[5]) if len(id_parts) > 5 else 0
                descr = navigations.get('title', '') or None
                comments = navigations.get('description', '') or None
                menu_path = application + "." + str(level_1) + "." + str(level_2) + "." + str(level_3) + "." + str(level_4) + "." + str(level_5)
                icon_path = navigations.get('icon_image', '') or None
                close_icon = icon_path
                open_icon = navigations.get('open_icon', '') or None
                obj_type = navigations.get('obj_type', '') or None
                if obj_type == '' or obj_type == '-' or obj_type == 'NULL':
                    win_name = '-'
                else:
                    win_name = "w_"+navigations.get('obj_name', '').lower()
                chg_date = datetime.now().strftime('%d-%m-%y')
                chg_term = navigations.get('chg_term', '').strip() or 'System'
                chg_user = navigations.get('chg_user', '').strip() or 'System'
                mob_deploy = navigations.get('mob_deploy', '').strip() or None
                default_state = navigations.get('default_state', '') or None
                def_action = navigations.get('def_action', '') or None
                mob_deply = navigations.get('mob_deply', '') or None
                ent_types = navigations.get('ent_types', '').strip() or 0

                cursor = conn.cursor()
                if con_type == 'Oracle':
                    insert_query = """INSERT INTO ITM2MENU (APPLICATION, LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, WIN_NAME, DESCR, COMMENTS, 
                        MENU_PATH, ICON_PATH, CLOSE_ICON, OPEN_ICON, OBJ_TYPE, CHG_DATE, CHG_TERM, CHG_USER, 
                        MOB_DEPLOY, DEFAULT_STATE, DEF_ACTION, MOB_DEPLY, ENT_TYPES) 
                        VALUES (:APPLICATION, :LEVEL_1, :LEVEL_2, :LEVEL_3, :LEVEL_4, :LEVEL_5, :WIN_NAME, :DESCR, 
                        :COMMENTS, :MENU_PATH, :ICON_PATH, :CLOSE_ICON, :OPEN_ICON, :OBJ_TYPE, 
                        TO_DATE(:CHG_DATE, 'DD-MM-YY'), :CHG_TERM, :CHG_USER, :MOB_DEPLOY, :DEFAULT_STATE, 
                        :DEF_ACTION, :MOB_DEPLY, :ENT_TYPES)"""                    
                    values = {
                        'application': application,
                        'level_1': level_1,
                        'level_2': level_2,
                        'level_3': level_3,
                        'level_4': level_4,
                        'level_5': level_5,
                        'win_name': win_name,
                        'descr': descr,
                        'comments': comments,
                        'menu_path': menu_path,
                        'icon_path': icon_path,
                        'close_icon': close_icon,
                        'open_icon': open_icon,
                        'obj_type': obj_type,
                        'chg_date': chg_date,
                        'chg_term': chg_term,
                        'chg_user': chg_user,
                        'mob_deploy': mob_deploy,
                        'default_state': default_state,
                        'def_action': def_action,
                        'mob_deply': mob_deply,
                        'ent_types': ent_types
                    }
                    logger.log(f"\n--- Class Itm2Menu ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"ITM2MENU table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"ITM2MENU table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in ITM2MENU table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO ITM2MENU (
                            APPLICATION, LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, WIN_NAME, DESCR, COMMENTS, 
                            MENU_PATH, ICON_PATH, CLOSE_ICON, OPEN_ICON, OBJ_TYPE, CHG_DATE, CHG_TERM, CHG_USER, 
                            MOB_DEPLOY, DEFAULT_STATE, DEF_ACTION, MOB_DEPLY, ENT_TYPES
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, TO_DATE(%s, 'DD-MM-YY'), %s, %s, 
                            %s, %s, %s, %s, %s
                        )
                    """               
                    values = (
                        application, level_1, level_2, level_3, level_4, level_5, win_name, descr, comments,
                        menu_path, icon_path, close_icon, open_icon, obj_type, chg_date, chg_term, chg_user,
                        mob_deploy, default_state, def_action, mob_deply, ent_types
                    )
                    logger.log(f"\n--- Class Itm2Menu ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"ITM2MENU table insert query for Other database ::: {insert_query}")
                    deployment_log(f"ITM2MENU table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in ITM2MENU table for Other database.")
                cursor.close()


    def process_data(self, conn, menu_model, db_vendore):
        logger.log(f"Start of ITM2MENU Class")
        deployment_log(f"\n--------------------------------- Start of ITM2MENU Class -------------------------------------\n")
        if "navigation" in menu_model:
            navigation = menu_model["navigation"]
            application = menu_model["application"]["id"]
            self.delete_and_insert_itm2menu(navigation, application, conn, db_vendore)
        logger.log(f"End of ITM2MENU Class")
        deployment_log(f"End of ITM2MENU Class")
            

