import os
import pathlib

from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH

chia_root = pathlib.Path(
    os.path.expanduser(os.environ.get("CHIA_ROOT", DEFAULT_ROOT_PATH))
)
chia_config = load_config(chia_root, "config.yaml")
self_hostname = chia_config["self_hostname"]
wallet_rpc_port = chia_config["wallet"]["rpc_port"]
selected_network = chia_config["selected_network"]
address_prefix = chia_config["network_overrides"]["config"][selected_network][
    "address_prefix"
]


dexie_mainnet = "https://dexie.space"
dexie_testnet = "https://testnet.dexie.space"
dexie_local = "http://localhost:3000"

dexie_url = os.environ.get(
    "DEXIE_URL", dexie_mainnet if selected_network == "mainnet" else dexie_testnet
)

dexie_api_mainnet = "https://api.dexie.space/v1"
dexie_api_testnet = "https://api-testnet.dexie.space/v1"
dexie_api_local = "http://localhost:3001/v1"

dexie_api_url = os.environ.get(
    "DEXIE_API_URL",
    dexie_api_mainnet if selected_network == "mainnet" else dexie_api_testnet,
)

dexie_db_path = os.environ.get("DEXIE_DB_PATH", ".")

dexie_blue = "#4655FF"
