# -*- coding: utf-8 -*-
"""task2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TKUJeWVAoEeUZKDxh_9HIaY0IcBUJFXM
"""

from airflow import DAG
from airflow.decorators import task
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.dates import days_ago

# Default DAG arguments
default_args = {
    'owner': 'divya',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
    dag_id='elt_join_tables',
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    create_joined_table = SnowflakeOperator(
        task_id='create_session_summary',
        sql="""
            CREATE OR REPLACE TABLE analytics.session_summary AS
            SELECT
                usc.userId,
                usc.sessionId,
                usc.channel,
                st.ts
            FROM raw_data.user_session_channel usc
            JOIN raw_data.session_timestamp st
            ON usc.sessionId = st.sessionId;
        """,
        snowflake_conn_id='my_snowflake_conn',
    )

    remove_duplicates = SnowflakeOperator(
        task_id='remove_duplicates',
        sql="""
            DELETE FROM analytics.session_summary
            WHERE sessionId IN (
                SELECT sessionId
                FROM analytics.session_summary
                GROUP BY sessionId
                HAVING COUNT(*) > 1
            );
        """,
        snowflake_conn_id='my_snowflake_conn',
    )

    create_joined_table >> remove_duplicates