import os
from typing import List

import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extensions import AsIs

from slashgpt.dbs.db_base import VectorDBBase
from slashgpt.dbs.vector_engine import VectorEngine
from slashgpt.utils.print import print_error, print_info


class DBPgVector(VectorDBBase):
    @classmethod
    def factory(cls, table_name: str, embeddings: dict, vector_engine: VectorEngine, verbose: bool):
        postgresql_config = os.getenv("POSTGRESQL_CONFIG", None)
        if postgresql_config:
            return DBPgVector(table_name, embeddings, vector_engine, verbose)
        else:
            print_error("POSTGRESQL_CONFIG environment variable is missing from .env")

    def __init__(self, table_name: str, embeddings: dict, vector_engine: VectorEngine, verbose: bool):
        super().__init__(table_name, embeddings, vector_engine, verbose)
        postgresql_config = os.getenv("POSTGRESQL_CONFIG", None)
        self.conn = psycopg2.connect(postgresql_config)
        self.table_name = table_name
        self.embeddings = embeddings
        register_vector(self.conn)

    def fetch_data(self, query_embedding: List[float]) -> List[str]:
        cur = self.conn.cursor()
        metadata = self.embeddings.get("metadata")
        storage_id = metadata.get("storage_id") if metadata else ""

        if storage_id == "":
            sql = "SELECT id, text FROM %s ORDER BY embedding <=> %s LIMIT 5"
            cur.execute(
                sql,
                (
                    AsIs(self.table_name),
                    np.array(query_embedding),
                ),
            )
        else:
            sql = "SELECT id, text FROM %s where storage_id = %s ORDER BY embedding <=> %s LIMIT 5"
            cur.execute(
                sql,
                (
                    AsIs(self.table_name),
                    storage_id,
                    np.array(query_embedding),
                ),
            )
        if self.verbose:
            print_info(sql)

        response = cur.fetchall()
        results = []
        for data in response:
            results.append(data[1])
        if self.verbose:
            print_info(results)
        return results
