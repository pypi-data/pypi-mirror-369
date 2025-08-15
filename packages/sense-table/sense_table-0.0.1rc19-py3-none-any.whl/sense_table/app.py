import logging
import os
from typing import Optional

import boto3
import duckdb
from botocore.client import BaseClient
from flask import Flask, Response, jsonify
from pydantic import ConfigDict, validate_call

from sense_table.handlers.fs import fs_bp
from sense_table.handlers.pages import pages_bp
from sense_table.handlers.query import query_bp
from sense_table.handlers.s3 import s3_bp
from sense_table.settings import FolderShortcut, SenseTableSettings
from sense_table.utils.duckdb_connections import DuckdbConnectionMaker, duckdb_connection_using_s3

PWD = os.path.dirname(os.path.abspath(__file__))


logger = logging.getLogger(__name__)


class SenseTableApp:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        *,
        settings: Optional[SenseTableSettings] = None,
        url_prefix: str = "",
        s3_client: Optional[BaseClient] = None,
        duckdb_connection_maker: Optional[DuckdbConnectionMaker] = None,
    ):
        self.settings = settings if settings is not None else SenseTableSettings()  # type: ignore
        self.s3_client = s3_client if s3_client is not None else boto3.client("s3")
        self.duckdb_connection_maker = (
            duckdb_connection_maker
            if duckdb_connection_maker is not None
            else lambda: duckdb.connect()
        )
        if url_prefix:
            assert url_prefix.startswith("/"), "url_prefix must start with /"
            assert not url_prefix.endswith("/"), "url_prefix must not end with /"
        self.url_prefix = url_prefix

    def create_app(self) -> Flask:
        app = Flask(__name__, static_folder="statics", static_url_path=f"{self.url_prefix}")

        # Store the s3_client in app config so blueprints can access it
        app.config["S3_CLIENT"] = self.s3_client
        app.config["URL_PREFIX"] = self.url_prefix
        app.config["DUCKDB_CONNECTION_MAKER"] = self.duckdb_connection_maker

        # Register blueprints with url_prefix
        app.register_blueprint(query_bp, url_prefix=f"{self.url_prefix}/api")
        app.register_blueprint(fs_bp, url_prefix=f"{self.url_prefix}/api")
        app.register_blueprint(pages_bp, url_prefix=self.url_prefix)
        app.register_blueprint(s3_bp, url_prefix=f"{self.url_prefix}/api")

        @app.route(f"{self.url_prefix}/api/settings")
        def get_settings() -> Response:
            return jsonify(self.settings.model_dump())

        return app

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        self.create_app().run(host=host, port=port)


if __name__ == "__main__":
    session = boto3.Session(profile_name="readonly")
    s3_client = session.client("s3")
    SenseTableApp(
        s3_client=s3_client,
        duckdb_connection_maker=duckdb_connection_using_s3(s3_client=s3_client),
        settings=SenseTableSettings(  # type: ignore
            enableDebugging=True,
            s3PrefixToSaveShareableLink="s3://sense-table-demo/internal/persisted-state/",
            folderShortcuts=[
                FolderShortcut(name="Home", path="~"),
                FolderShortcut(name="S3 datasets", path="s3://sense-table-demo/datasets"),
                FolderShortcut(
                    name="NYCTaxi", path="~/Work/sense-table-demo-data/datasets/NYCTaxi"
                ),
            ],
        ),
    ).run()
