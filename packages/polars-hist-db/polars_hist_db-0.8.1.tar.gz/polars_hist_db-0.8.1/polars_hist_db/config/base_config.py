from functools import reduce
import os
from typing import Any, Iterable, Mapping, Optional
import yaml

from .dataset import DatasetsConfig
from .engine import DbEngineConfig
from .table import TableConfigs


class BaseConfig:
    def __init__(
        self,
        cfg_dict: Mapping[str, Any],
        table_configs_path: Iterable[str],
        datasets_path: Iterable[str],
        db_config_path: Iterable[str],
        config_file_path: Optional[str] = None,
    ):
        self.config_file_path = config_file_path
        dataset_params = BaseConfig.get_nested_key(cfg_dict, datasets_path)
        db_params = BaseConfig.get_nested_key(cfg_dict, db_config_path)
        table_params = BaseConfig.get_nested_key(cfg_dict, table_configs_path)

        self.tables = TableConfigs(items=table_params)

        if db_params:
            self.db_config = DbEngineConfig(**db_params)

        if dataset_params:
            self.datasets = DatasetsConfig(
                datasets=dataset_params, config_file_path=config_file_path
            )

    @staticmethod
    def get_nested_key(my_dict: Mapping[str, Any], keys: Iterable[str]):
        try:
            return reduce(lambda d, key: d[key], keys, my_dict)
        except (KeyError, TypeError):
            return None

    @classmethod
    def yaml_to_dict(cls, filename: str) -> Any:
        def _expand_env_vars(value: Any) -> Any:
            if isinstance(value, str):
                return os.path.expandvars(value)
            elif isinstance(value, dict):
                return {k: _expand_env_vars(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_expand_env_vars(v) for v in value]
            else:
                return value

        print(f"loading Config from: {filename}")
        with open(filename, "r") as file:
            yaml_dict = yaml.safe_load(file)
            yaml_dict = _expand_env_vars(yaml_dict)

        return yaml_dict

    @classmethod
    def from_yaml(
        cls,
        filename: str,
        table_configs_path: str = "table_configs",
        datasets_path: str = "datasets",
        db_config_path: str = "db",
    ) -> "BaseConfig":
        yaml_dict: Mapping[str, Any] = cls.yaml_to_dict(filename)
        config = BaseConfig(
            yaml_dict,
            db_config_path=db_config_path.split("."),
            table_configs_path=table_configs_path.split("."),
            datasets_path=datasets_path.split("."),
            config_file_path=filename,
        )

        return config
