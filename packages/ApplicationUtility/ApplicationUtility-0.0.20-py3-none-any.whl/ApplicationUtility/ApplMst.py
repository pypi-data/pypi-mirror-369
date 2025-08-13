import cx_Oracle
from datetime import datetime
import loggerutility as logger
from loggerutility import deployment_log

class ApplMst:
    sql_models = []

    def insert_or_update_applmst(self, application, connection, con_type):
        if not connection:
            deployment_log(f"Database connection not found!")
            return

        required_keys = ['id']
        missing_keys = [key for key in required_keys if key not in application]

        if missing_keys:
            deployment_log(f"Missing required keys for APPL_MST table: {', '.join(missing_keys)}")
            raise KeyError(f"Missing required keys for APPL_MST table: {', '.join(missing_keys)}")
        else:
            app_name = application.get('id', '').strip() or None
            logger.log(f"application name :: {app_name}")
            logger.log(f"application length :: {len(app_name)}")
            app_name = app_name.upper()
            logger.log(f"app_name ::: {app_name}")
            descr = application.get('description', '') or None
            chg_date = datetime.now().strftime('%d-%m-%y')
            chg_user = application.get('chg_user', '').strip() or 'System'
            chg_term = application.get('chg_term', '').strip() or 'System'
            appl_group = application.get('group', '') or None
            appl_color = application.get('theme_color', '') or None
            appl_order = application.get('appl_order', '') or None
            conn_option = application.get('conn_option', '') or None
            appl_type = application.get('appl_type', '') or ''
            search_domain = application.get('search_domain', '') or None
            appl_grp_descr = application.get('appl_grp_descr', '') or None
            appl_group_color = application.get('appl_group_color', '') or None
            title = application.get('title', '') or None
            logger.log(f"app_name :: {app_name}")
            deployment_log(f"Application name ::: {app_name}")

            cursor = connection.cursor()
            queryy = f"""
                SELECT COUNT(*) FROM APPL_MST 
                WHERE APP_NAME = '{app_name}'
            """
            logger.log(f"\n--- Class ApplMst ---\n")
            logger.log(f"{queryy}")
            deployment_log(f"APPL_MST table select query ::: {queryy}")
            cursor.execute(queryy)
            row_exists = cursor.fetchone()[0]
            logger.log(f"row_exists :: {row_exists}")
            deployment_log(f"APPL_MST table select query result::: {row_exists}")
            cursor.close()

            if row_exists:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    update_query = """
                        UPDATE APPL_MST SET
                            DESCR = :descr,
                            CHG_DATE = TO_DATE(:chg_date, 'DD-MM-YY'),  
                            CHG_USER = :chg_user,
                            CHG_TERM = :chg_term,
                            APPL_GROUP = :appl_group,
                            APPL_COLOR = :appl_color,
                            APPL_ORDER = :appl_order,
                            CONN_OPTION = :conn_option,
                            APPL_TYPE = :appl_type,
                            SEARCH_DOMAIN = :search_domain,
                            APPL_GRP_DESCR = :appl_grp_descr,
                            APPL_GROUP_COLOR = :appl_group_color,
                            TITLE = :title
                        WHERE TRIM(APP_NAME) = TRIM(:app_name)
                    """
                    values = {
                        'descr': descr,
                        'chg_date': chg_date, 
                        'chg_user': chg_user,
                        'chg_term': chg_term,
                        'appl_group': appl_group,
                        'appl_color': appl_color,
                        'appl_order': appl_order,
                        'conn_option': conn_option,
                        'appl_type': appl_type,
                        'search_domain': search_domain,
                        'appl_grp_descr': appl_grp_descr,
                        'appl_group_color': appl_group_color,
                        'title': title,
                        'app_name': app_name
                    }
                    logger.log(f"\n--- Class ApplMst ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"APPL_MST table update query for Oracle database ::: {update_query}")
                    deployment_log(f"APPL_MST table update query values for Oracle database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in APPL_MST table for Oracle database.")
                else:
                    update_query = """
                        UPDATE APPL_MST SET
                            DESCR = %s,
                            CHG_DATE = TO_DATE(%s, 'DD-MM-YY'),  
                            CHG_USER = %s,
                            CHG_TERM = %s,
                            APPL_GROUP = %s,
                            APPL_COLOR = %s,
                            APPL_ORDER = %s,
                            CONN_OPTION = %s,
                            APPL_TYPE = %s,
                            SEARCH_DOMAIN = %s,
                            APPL_GRP_DESCR = %s,
                            APPL_GROUP_COLOR = %s,
                            TITLE = %s
                        WHERE TRIM(APP_NAME) = TRIM(%s)
                    """
                    values = (
                        descr, chg_date, chg_user, chg_term, appl_group, appl_color, appl_order,
                        conn_option, appl_type, search_domain, appl_grp_descr, appl_group_color,
                        title, app_name
                    )
                    logger.log(f"\n--- Class ApplMst ---\n")
                    logger.log(f"update_query values :: {values}")
                    deployment_log(f"APPL_MST table update query for Other database ::: {update_query}")
                    deployment_log(f"APPL_MST table update query values for Other database ::: {values}")
                    cursor.execute(update_query, values)
                    logger.log(f"Successfully updated row.")
                    deployment_log(f"Data updated successfully in APPL_MST table for Other database.")
                cursor.close()
            else:
                cursor = connection.cursor()
                if con_type == 'Oracle':
                    insert_query = """
                        INSERT INTO APPL_MST (
                            APP_NAME, DESCR, CHG_DATE, CHG_USER, CHG_TERM,
                            APPL_GROUP, APPL_COLOR, APPL_ORDER, CONN_OPTION,
                            APPL_TYPE, SEARCH_DOMAIN, APPL_GRP_DESCR, APPL_GROUP_COLOR, TITLE
                        ) VALUES (
                            :app_name, :descr, TO_DATE(:chg_date, 'DD-MM-YY'), :chg_user, :chg_term,
                            :appl_group, :appl_color, :appl_order, :conn_option,
                            :appl_type, :search_domain, :appl_grp_descr, :appl_group_color, :title
                        )
                        """
                    values = {'app_name':app_name,
                        'descr':descr,
                        'chg_date':chg_date,
                        'chg_user':chg_user,
                        'chg_term':chg_term,
                        'appl_group':appl_group,
                        'appl_color':appl_color,
                        'appl_order':appl_order,
                        'conn_option':conn_option,
                        'appl_type':appl_type,
                        'search_domain':search_domain,
                        'appl_grp_descr':appl_grp_descr,
                        'appl_group_color':appl_group_color,
                        'title':title
                        }
                    logger.log(f"\n--- Class ApplMst ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"APPL_MST table insert query for Oracle database ::: {insert_query}")
                    deployment_log(f"APPL_MST table insert query values for Oracle database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in APPL_MST table for Oracle database.")
                else:
                    insert_query = """
                        INSERT INTO APPL_MST (
                            APP_NAME, DESCR, CHG_DATE, CHG_USER, CHG_TERM,
                            APPL_GROUP, APPL_COLOR, APPL_ORDER, CONN_OPTION,
                            APPL_TYPE, SEARCH_DOMAIN, APPL_GRP_DESCR, APPL_GROUP_COLOR, TITLE
                        ) VALUES (
                            %s, %s, TO_DATE(%s, 'DD-MM-YY'), %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s
                        )
                    """
                    values = (
                        app_name, descr, chg_date, chg_user, chg_term,
                        appl_group, appl_color, appl_order, conn_option,
                        appl_type, search_domain, appl_grp_descr, appl_group_color, title
                    )
                    logger.log(f"\n--- Class ApplMst ---\n")
                    logger.log(f"insert_query values :: {values}")
                    deployment_log(f"APPL_MST table insert query for Other database ::: {insert_query}")
                    deployment_log(f"APPL_MST table insert query values for Other database ::: {values}")
                    cursor.execute(insert_query, values)
                    logger.log(f"Successfully inserted row.")
                    deployment_log(f"Data inserted successfully in APPL_MST table for Other database.")
                cursor.close()
        
    def process_data(self, conn, menu_model, db_vendore):
        logger.log(f"Start of ApplMst Class")
        deployment_log(f"\n--------------------------------- Start of ApplMst Class -------------------------------------\n")
        if "application" in menu_model:
            application = menu_model["application"]
            self.insert_or_update_applmst(application, conn, db_vendore)
        logger.log(f"End of ApplMst Class")
        deployment_log(f"End of ApplMst Class")
            
        
