from pyspark.sql import DataFrame

def write_to_bigquery(spark_df, table_name, project_id="pcb-prod-pds",
                      dataset="PCMC_PORTFOLIO", mode="overwrite"):
    """
    Writes a Spark DataFrame to a BigQuery table.

    :param spark_df: The Spark DataFrame to write.
    :type spark_df: pyspark.sql.DataFrame
    :param table_name: The name of the BigQuery table.
    :type table_name: str
    :param project_id: The Google Cloud project ID.
    :type project_id: str
    :param dataset: The BigQuery dataset name.
    :type dataset: str
    :param mode: Write mode ('overwrite' or 'append').
    :type mode: str
    """
    
    full_table_id = "{}.{}.{}".format(project_id, dataset, table_name)

    (spark_df.write
        .format("bigquery")
        .mode(mode)
        .option("table", full_table_id)
        .option("temporaryGcsBucket", "sas-pcbpds-in")
        .option("writeDisposition", "WRITE_TRUNCATE" if mode == "overwrite" else "WRITE_APPEND")
        .save())

    print("{}d {} in BigQuery table {}".format(mode.capitalize(), table_name, full_table_id))