import rich_click as click

from dexie_rewards import __version__
from .rewards.main import rewards_cmd


@click.group("dexie")
@click.version_option(__version__)
def dexie_cmd() -> None:
    pass


dexie_cmd.add_command(rewards_cmd)
