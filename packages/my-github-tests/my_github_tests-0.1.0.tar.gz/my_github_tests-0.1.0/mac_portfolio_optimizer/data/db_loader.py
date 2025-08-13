"""
1. create data from local excel and publish to postgres
2. fetch data from postgres and return instantiated MacUniverse dataclass
"""

import urllib.parse
from enum import Enum
from typing import Dict, List, Literal, NamedTuple, Optional, Union

import jsonpickle
import jsonpickle.ext.pandas as jsonpickle_pandas
import pandas as pd
import qis as qis
import requests
from qis.file_utils import INDEX_COLUMN
from ramen.pydantic_model.setting.maestro_config import (
    MaestroConfig,
)
from mac_portfolio_optimizer.data.excel_loader import (
    load_mac_portfolio_universe,
)
from mac_portfolio_optimizer.data.mac_universe import (
    MacUniverseData,
    SaaPortfolio,
    TaaPortfolio,
)
from ramen.quant_model_mvp.mac_portfolio_optimizer.local_path import LOCAL_PATH
from sqlalchemy import URL, Engine, create_engine, text

jsonpickle_pandas.register_handlers()

# data tables fetched from db
DB_TABLES = [
    "saa_prices",
    "saa_universe_df",
    "taa_prices",
    "taa_universe_df",
    "asset_class_ranges",
    "benchmarks",
    "risk_factor_prices",
    "asset_loadings",
    "sub_asset_class_ranges",
    "model_params",
    "model_params",
]

DB_SCHEMA = "db"


def load_mac_universe_data_from_excel() -> MacUniverseData:
    mac_universe_data = load_mac_portfolio_universe(
        local_path=LOCAL_PATH,
        saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
        taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
        sub_asset_class_ranges_sheet_name="sub_asset_class_constraints1",
    )
    return mac_universe_data


def create_db_engine(maestro_config: MaestroConfig) -> Engine:
    config = dict(
        drivername="postgresql+psycopg2",
        username=maestro_config.postgresql_db_user,
        password=maestro_config.postgresql_db_password,
        host=maestro_config.postgresql_db_host,
        port=maestro_config.postgresql_db_port,
        database=maestro_config.postgresql_db_database,
        query={},
    )
    url = URL(**config)
    return create_engine(url)


def save_mac_universe_data_to_db(
    maestro_config: MaestroConfig, mac_universe_data: MacUniverseData
) -> None:
    datasets = mac_universe_data.to_dict()
    if maestro_config.postgresql_db_user == "LGT_QDEV":
        save_df_dict_to_sql(
            engine=create_db_engine(maestro_config),
            table_name="mac",
            dfs=datasets,
            schema="mac_portfolio_optimizer",
            if_exists="replace",
        )
    else:
        save_df_dict_to_sql(
            engine=create_db_engine(maestro_config),
            table_name="mac",
            dfs=datasets,
            schema="mac_portfolio_optimizer",
            if_exists="truncate-append",
        )


def save_df_dict_to_sql(
    engine: Engine,
    table_name: str,
    dfs: Dict[Union[str, Enum, NamedTuple], pd.DataFrame],
    schema: Optional[str] = None,
    index_col: Optional[str] = INDEX_COLUMN,
    if_exists: Literal["fail", "replace", "append"]
    | Literal["truncate-append"] = "fail",
) -> None:
    """
    save pandas dict to sql engine
    """
    for key, df in dfs.items():
        if df is not None and isinstance(df, pd.DataFrame):
            if index_col is not None:
                df = df.reset_index(names=index_col)
            if if_exists == "truncate-append":
                schema_str = f"{schema}." if schema else ""
                with engine.connect() as con:
                    statement = text(f"TRUNCATE TABLE {schema_str}{table_name}_{key}")
                    con.execute(statement)
                    con.commit()
                df.to_sql(
                    f"{table_name}_{key}",
                    engine,
                    schema=schema,
                    if_exists="append",
                    method="multi",
                    chunksize=1000,
                )
            else:
                df.to_sql(
                    f"{table_name}_{key}", engine, schema=schema, if_exists=if_exists
                )


def load_mac_universe_data_from_db(maestro_config: MaestroConfig) -> MacUniverseData:
    datasets = load_df_dict_from_sql(
        engine=create_db_engine(maestro_config),
        table_name="mac",
        dataset_keys=[
            "asset_class_ranges",
            "asset_loadings",
            "benchmarks",
            "model_params",
            "risk_factor_prices",
            "saa_prices",
            "saa_universe_df",
            "sub_asset_class_ranges",
            "taa_prices",
            "taa_universe_df",
        ],
        schema="mac_portfolio_optimizer",
    )
    return MacUniverseData(**datasets)


# To be replaced by qis.load_df_dict_from_sql once it is updated
def load_df_dict_from_sql(
    engine: Engine,
    table_name: str,
    dataset_keys: List[Union[str, Enum, NamedTuple]],
    schema: Optional[str] = None,
    index_col: Optional[str] = INDEX_COLUMN,
    columns: Optional[List[str]] = None,
    drop_sql_index: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    pandas dict from csv files
    """
    pandas_dict = {}
    for key in dataset_keys:
        # df will have index set by index_col with added column 'index' from sql
        df = pd.read_sql_table(
            table_name=f"{table_name}_{key}",
            con=engine,
            schema=schema,
            index_col=index_col,
            columns=columns,
        )
        if drop_sql_index:
            df = df.drop("index", axis=1)
            #  df[index_col] = pd.to_datetime(df[index_col])
            #  df = df.set_index(index_col, drop=True)
        pandas_dict[key] = df
    return pandas_dict


def publish_excel_data_to_csv():
    mac_universe_data = load_mac_universe_data_from_excel()
    datasets = mac_universe_data.to_dict()
    qis.save_df_dict_to_csv(
        datasets=datasets, file_name=DB_SCHEMA, local_path=LOCAL_PATH
    )


def load_mac_universe_data_from_csv() -> MacUniverseData:
    datasets = qis.load_df_dict_from_csv(
        dataset_keys=DB_TABLES, file_name=DB_SCHEMA, local_path=LOCAL_PATH
    )
    return MacUniverseData(**datasets)


def load_mac_universe_data_from_api() -> MacUniverseData:
    maestro_config = MaestroConfig()
    path = urllib.parse.urljoin(
        maestro_config.api_public_base_url,
        "/mvp/mac_portfolio_optimizer/mac_universe_data",
    )
    rsp = requests.get(path, verify=False)
    rsp_json = rsp.json()
    un_pickler = jsonpickle.Unpickler()
    mac_universe_dict = un_pickler.restore(rsp_json)
    mac_universe_data = MacUniverseData(**mac_universe_dict)
    return mac_universe_data


def publish_mac_universe_data_to_api(mac_universe_data: MacUniverseData) -> None:
    maestro_config = MaestroConfig()
    mac_universe_dict = mac_universe_data.to_dict()

    pickler = jsonpickle.Pickler()
    req_json = pickler.flatten(mac_universe_dict)

    path = urllib.parse.urljoin(
        maestro_config.api_public_base_url,
        "/mvp/mac_portfolio_optimizer/mac_universe_data",
    )
    rsp = requests.post(url=path, json=req_json, verify=False)

    print(rsp)


class LocalTests(Enum):
    PUBLISH_MAC_UNIVERSE_TO_API = 1
    LOAD_MAC_UNIVERSE_FROM_API = 2
    PUBLISH_EXCEL_TO_CSV = 3


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """

    if local_test == LocalTests.PUBLISH_MAC_UNIVERSE_TO_API:
        mac_universe_data = load_mac_universe_data_from_excel()
        publish_mac_universe_data_to_api(mac_universe_data)

    elif local_test == LocalTests.LOAD_MAC_UNIVERSE_FROM_API:
        mac_universe_data = load_mac_universe_data_from_api()
        print(mac_universe_data)

    elif local_test == LocalTests.PUBLISH_EXCEL_TO_CSV:
        publish_excel_data_to_csv()


if __name__ == "__main__":

    run_local_test(local_test=LocalTests.PUBLISH_EXCEL_TO_CSV)
