"""
This module initializes the GitHub Release Notifier plugin for NoneBot.

It sets up the plugin metadata, initializes the database, configures
group-to-repo mappings, and schedules periodic tasks to check for updates
in GitHub repositories. The plugin notifies group members of new commits,
issues, pull requests, and releases in the configured repositories.
"""

from nonebot import require, get_driver
from nonebot.internal.driver.abstract import Driver
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from .repo_activity_new import check_repo_updates
from .setup import pre_plugin_setup, post_plugin_setup
from .db_action import (
    load_group_configs
)
from .commands import repo_group
from .config import Config, config
from .debugs import debugs

__version__ = "0.1.10"
DEBUG: bool = config.github_dbg

__plugin_meta__ = PluginMetadata(
    name="github_release_notifier",
    description=(
        "A plugin for nonebot & onebot to notify "
        "group members of new commits, "
        "issues, and PRs in GitHub repos."
    ),
    type='application',
    usage="github repo events auto forward | 自动转发github repo事件",
    homepage=(
        "https://github.com/HTony03/nonebot_plugin_github_release_notifier"
    ),
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={},
)

logger.info(
    f"Initializing nonebot_plugin_github_release_notifier version: {__version__}"
)

if DEBUG:
    logger.info("Debug mode is enabled. ")

# Scheduler for periodic tasks
scheduler = require("nonebot_plugin_apscheduler").scheduler

pre_plugin_setup()

group_repo_dict = load_group_configs(False)
if DEBUG:
    logger.debug(f"Read from db: {group_repo_dict}")


# TODO: Reformat database


def refresh_data_from_db() -> None:
    """Refresh the group-to-repo mapping from the database."""
    group_repo_dict = load_group_configs(False)


# Register the initialization function to run when the bot starts
driver: Driver = get_driver()
driver.on_startup(post_plugin_setup)


@scheduler.scheduled_job("cron", minute="*/5")
async def _() -> None:
    """Check for all repos and notify groups."""
    load_group_configs(False)
    await check_repo_updates()
