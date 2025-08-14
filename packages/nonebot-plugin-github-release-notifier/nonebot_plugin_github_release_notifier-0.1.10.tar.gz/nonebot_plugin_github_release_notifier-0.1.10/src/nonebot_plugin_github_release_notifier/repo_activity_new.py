from githubkit import GitHub, UnauthAuthStrategy, TokenAuthStrategy, Response
from githubkit.versions.latest.models import (Issue, PullRequest, Commit, Release,
                                              PullRequestSimple, IssueComment, PullRequestReviewComment)
from githubkit.exception import (
    RequestFailed, RequestError,
    RequestTimeout, RateLimitExceeded
)
from typing import Literal, Union, Sequence  # , TypeVar
# from githubkit.versions.v2022_11_28.types.group_0231 import CommitType
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from datetime import datetime, timezone
import os

import aiohttp
from nonebot import get_bot, get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Message

from .db_action import (
    load_group_configs,
    load_last_processed,
    save_last_processed,
    get_commit_data,
    save_commit_data,
)
from .config import config, CACHE_DIR, t
from .data import Folder, File
from .renderer import (
    issue_to_image,
    issue_commented_to_image,
    issue_opened_to_image
)
from .pic_process import html_to_pic, md_to_pic

GitHubResponse = Union[
    Response[list[Commit]],
    Response[list[Issue]],
    Response[list[PullRequestSimple]],
    Response[list[Release]]
]
IssueResponse = Union[
    Response[list[Issue]],
    Response[list[PullRequestSimple]],
    Response[list[PullRequest]]
]

superusers: set[str] = get_driver().config.superusers
max_retries: int = config.github_retries
delay: int = config.github_retry_delay
temp_disabled: dict = {}
api_cache: dict = {}
temp_commit: list = []
github = GitHub(UnauthAuthStrategy(), auto_retry=False)

config_template: dict = t
run_lock: bool = False


async def validate_github_token(retries=3, retry_delay=5) -> None:
    """
    Validate the GitHub token by making a test request,
    with retries on SSL errors.
    """
    global github
    token: str | None = config.github_token
    if not token:
        logger.warning(
            "No GitHub token provided. Proceeding without authentication."
        )
        github = GitHub(UnauthAuthStrategy(), auto_retry=False)
        return

    auth_github = GitHub(TokenAuthStrategy(token), auto_retry=False)

    @retry(stop=stop_after_attempt(retries), wait=wait_fixed(retry_delay))
    async def token_valid() -> None:
        global github
        try:
            await auth_github.rest.repos.async_get(
                owner="HTony03",
                repo="nonebot_plugin_github_release_notifier"
            )
            logger.info("GitHub token is valid.")
            github = auth_github
        except (RequestFailed, RateLimitExceeded):
            logger.error(
                "Invalid GitHub token received. "
                "Proceed without authentication."
            )
            github = GitHub(UnauthAuthStrategy(), auto_retry=False)
            return

    try:
        await token_valid()
    except RetryError as e:
        logger.error(
            "GitHub token validation failed after multiple attempts. "
            "Proceed without authentication."
        )
        logger.error(
            f"exception: {e.last_attempt.__class__}: "
            f"{e.last_attempt.exception()}"
        )
        github = GitHub(UnauthAuthStrategy(), auto_retry=False)


async def send_message(
        bot: Bot,
        target_id: int | str,
        msg: MessageSegment | Message,
        msg_type: Literal["group", "user"] = "group"
) -> None:
    """
    Send a message to the specified group or user.
    """
    if msg_type not in ["group", "user"]:
        raise ValueError(
            f"Invalid type: {msg_type}. Must be 'group' or 'user'."
        )
    try:
        target_id = int(target_id)
    except ValueError:
        logger.error(f"Invalid target_id: {target_id}. Must be an integer.")
        return
    try:
        if msg_type == "group":
            await bot.send_group_msg(group_id=target_id, message=Message(msg)
                                     if isinstance(msg, MessageSegment) else msg)
        elif msg_type == "user":
            await bot.send_private_msg(user_id=target_id, message=Message(msg)
                                       if isinstance(msg, MessageSegment) else msg)
    except Exception as e:
        logger.error(
            f"Failed to send message to {msg_type} {target_id}: "
            f"{e.__class__}: {e}"
        )


async def fetch_github_data(
        repo: str,
        endpoint: str
) -> Sequence[Commit | Issue | PullRequest | PullRequestSimple | Release] | None:
    """
    Fetch data from the GitHub API
    for a specific repo and endpoint.
    """

    cache = api_cache.get(repo, {}).get(endpoint, None)

    # Check if the data exists in the cache
    if cache is not None:
        logger.debug(f'Using cached data for {repo}/{endpoint}')
        if isinstance(cache, list) and cache and cache[0] == []:
            return []
        if isinstance(cache, list):
            return cache

    # If not in cache, fetch from the API
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(delay))
    async def get_data(
            github_client: GitHub,
            endpoint: str,
            owner: str,
            repository: str
    ) -> Sequence[Commit | Issue | PullRequestSimple | Release] | None:
        try:
            match endpoint:
                case "commits":
                    got_repo: GitHubResponse = await github_client.rest.repos.async_list_commits(
                        repo=repository, owner=owner
                    )
                case "issues":
                    got_repo: GitHubResponse = await github_client.rest.issues.async_list_for_repo(
                        repo=repository, owner=owner
                    )
                case "pulls":
                    got_repo: GitHubResponse = await github_client.rest.pulls.async_list(
                        repo=repository, owner=owner
                    )
                case "releases":
                    got_repo: GitHubResponse = await github_client.rest.repos.async_list_releases(
                        repo=repository, owner=owner
                    )
                case _:
                    raise ValueError(f"Unknown endpoint: {endpoint}")
        except (RequestFailed) as e:
            logger.error(
                f"Failed to fetch data from GitHub API: {e.__class__}: {e}"
            )
            return None

        if got_repo.is_error:
            # releases接口404时返回空列表而不是异常
            if got_repo.status_code == 404:
                return None
            raise RuntimeError("Failed to fetch data from GitHub API")
        return got_repo.parsed_data

    owner, repository = repo.split('/')

    try:
        response = await get_data(github, endpoint, owner, repository)
        if not response:
            response = []
    except RetryError as e:
        logger.error(
            "Failed to fetch data from Github API after 3 attempts:\n" +
            f"{e.last_attempt.__class__}: {e.last_attempt}"
        )
        raise RuntimeError(
            "Failed to fetch data from GitHub API after 3 retries"
        ) from e

    api_cache.setdefault(repo, {})[endpoint] = response if response else []
    return response


async def process_issues_and_prs(
        repo: str,
        owner: str,
        content_type: str,
        group_id: int,
        bot: Bot,
) -> None:
    """
    Process issues and pull requests, checking for new items and comments.
    """
    if content_type not in ["issues", "prs"]:
        raise ValueError(
            f"Invalid type: {content_type}. Must be 'issues' or 'prs'."
        )

    if content_type == "prs":
        logger.warning("Still WIP, auto exiting")
        return

    # Get last processed ID
    repo_key = f'{owner}/{repo}'
    last_id = get_commit_data(repo_key, 0, content_type)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(delay))
    async def get_issue_data(owner: str, repo: str, content_type: str) -> IssueResponse:
        # Fetch latest data
        if content_type == "issues":
            response: IssueResponse = (
                await github.rest.issues.async_list_for_repo(
                    owner=owner,
                    repo=repo,
                    state="all",
                    sort="created",
                    per_page=100
                )
            )
        else:
            response: IssueResponse = (
                await github.rest.pulls.async_list(
                    owner=owner,
                    repo=repo,
                    state="all",
                    sort="created",
                    per_page=100,
                    direction='desc'
                )
            )
        return response

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(delay))
    async def get_comment_data(owner: str, repo: str, num: int) -> Response[list[IssueComment]]:
        # Fetch latest data
        response: Response[list[IssueComment]] = await github.rest.issues.async_list_comments(
            owner=owner,
            repo=repo,
            issue_number=num
        )
        return response

    try:
        response: list[Issue] | list[PullRequestSimple] | list[PullRequest] = (
            await get_issue_data(owner, repo, content_type)
            ).parsed_data
    except RetryError as e:
        logger.error(
            "Failed to fetch data from Github API after 3 attempts:\n" +
            f"{e.last_attempt.__class__}: {e.last_attempt}"
        )
        raise RuntimeError(
            "Failed to fetch data from GitHub API after 3 retries"
        ) from e

    # Check for new issues/PRs
    latest_item = response[0]
    if not last_id or latest_item.id != int(last_id):
        # New issue/PR found
        if isinstance(latest_item, Issue):
            image_data = await issue_opened_to_image(
                repo=latest_item.repository,
                issue=latest_item
            )
        else:
            # TODO: Implement PR opened image rendering
            # image_data = await issue_opened_to_image(
            #     repo=latest_item.repository,
            #     issue=latest_item
            # )
            return
        await send_message(
            bot,
            group_id,
            MessageSegment.image(image_data)
        )
        # await send_message(
        #     bot,
        #     group_id,
        #     MessageSegment.image(await issue_to_image(latest_item))
        # )
        temp_commit.append({
            "key": repo_key,
            "hash": str(latest_item.id),
            "id": 0,
            "content_type": content_type
        })
        # Update last processed ID

    # Check for new comments on existing issues/PRs
    for item in response:
        stored_comment_id = get_commit_data(repo_key, item.id, content_type)

        # Fetch comments for this issue/PR
        try:
            comments_response: Response[list[IssueComment]] = await get_comment_data(
                owner, repo, item.number
            )
            comments = comments_response.parsed_data
        except RetryError as e:
            logger.error(f"Failed to fetch Comments for issue/pull request id {item.number}: "
                         f"{e.last_attempt.__class__}:{e.last_attempt}")
            continue

        if comments:
            latest_comment = comments[-1]
            if not stored_comment_id or latest_comment.id != int(stored_comment_id):
                # New comment found
                if isinstance(item, Issue):
                    image_data = await issue_commented_to_image(
                        repo=item.repository,
                        issue=item,
                        comment=latest_comment
                    )
                else:
                    # TODO: Implement PR comment image rendering
                    # image_data = await issue_commented_to_image(
                    #     repo=item.repository,
                    #     issue=item,
                    #     comment=latest_comment
                    # )
                    return

                await send_message(
                    bot,
                    group_id,
                    MessageSegment.image(image_data)
                )

                # Save the latest comment ID
                temp_commit.append({
                    "key": repo_key,
                    "hash": str(latest_comment.id),
                    "id": item.id,
                    "content_type": content_type
                })

    # # Save updated last processed data
    # save_last_processed(last_data)


async def send_release_files(
        bot: Bot,
        group_id: int,
        release_item: Release,
        debugging=False
) -> None:
    """Send release assets to group if enabled."""
    group_config = load_group_configs().get(str(group_id), {})

    if not group_config.get('send_release', False) and not debugging:
        return

    # Check if the file folder exists
    folders = await bot.call_api("get_group_root_files", group_id=group_id)
    upload_folder = group_config.get('release_folder', False)

    if upload_folder:
        if (not folders.get('folders') or
                upload_folder not in folders.get('folders')):
            # Create folder if it doesn't exist
            await bot.call_api(
                'create_group_file_folder',
                group_id=group_id,
                name=upload_folder,
                parent_id='/'
            )
            call2 = await bot.call_api("get_group_root_files", group_id=group_id)
            if upload_folder not in call2.get('folders', []):
                logger.error(
                    f"Failed to create upload folder {upload_folder} "
                    f"in group {group_id}."
                )
                logger.error('Auto upload to Root folder.')
                upload_folder = None

    # Remove older versions if enabled
    if config.github_upload_remove_older_ver:
        try:
            folder = await bot.call_api("get_group_root_files", group_id=group_id)
            folders_list = [Folder(**f) for f in folder.get("folders", [])]

            folder_id = None
            for f in folders_list:
                if f.folder_name == upload_folder:
                    folder_id = f.folder_id
                    break

            if folder_id:
                files_in_folder = (await bot.call_api(
                    'get_group_files_by_folder',
                    group_id=group_id,
                    folder_id=folder_id,
                )).get("files", [])
            else:
                files_in_folder = folder.get("files", [])

            # Remove old files with same names
            asset_names = [asset.name for asset in release_item.assets]
            files = [
                File(**f) for f in files_in_folder
                if f.get("name") in asset_names
            ]

            for file in files:
                try:
                    await bot.call_api(
                        "delete_group_file",
                        group_id=group_id,
                        file_id=file.file_id,
                        busid=file.busid,
                    )
                    logger.info(f"Removed old release file: {file.file_name}")
                except Exception as e:
                    logger.error(
                        f"Failed to remove old release file "
                        f"{file.file_name}: {e}"
                    )
        except Exception as e:
            logger.error(f"Error managing old release files: {e}")

    # Upload new release assets
    for asset in release_item.assets:
        download_url = asset.browser_download_url
        filename = asset.name
        file_route = os.path.join(CACHE_DIR, filename)

        if not download_url or not filename:
            continue

        try:
            # Download the file
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as resp:
                    resp.raise_for_status()
                    file_bytes = await resp.read()
                    with open(file_route, "wb") as f:
                        f.write(file_bytes)
                    logger.info(f"{file_route} downloaded successfully.")

            # Upload file
            await bot.call_api(
                "upload_group_file",
                group_id=group_id,
                file=file_route,
                name=filename,
                folder=upload_folder if upload_folder else None,
            )
            logger.info(f"Uploaded release file: {filename}")
        except Exception as e:
            logger.error(f"Failed to send release file {filename}: {e}")


def format_message(
        item: dict,
        data_type: str,
        only_first_line: bool = True
) -> str:
    """Format the notification message based on the data type."""
    if data_type == "commit":
        message = item.get("message", "")
        if only_first_line:
            item["message"] = message.split("\n")[0]

    elif data_type not in ["issue", "pull_req", "release"]:
        return "Unknown data type."

    return config_template.get(data_type,
                               "<unknown format, please report to the developer (with the language config)>"
                               ).format(**item)


async def notify(
        bot: Bot,
        group_id: int,
        repo: str,
        data: list[Commit | Issue | PullRequest | PullRequestSimple | Release],
        data_type: str,
        last_processed: dict,
) -> None:
    """Send notifications for new data (commits, issues, PRs, releases)."""
    latest_data: list[Commit | Issue | PullRequest | PullRequestSimple | Release] = data[:5]\
        if isinstance(data, list) else [data]

    for item in latest_data:
        if isinstance(item, Commit):
            item_time = item.commit.author.date if item.commit.author else None
        elif isinstance(item, (Issue, PullRequest, PullRequestSimple)):
            item_time = item.created_at
        elif isinstance(item, Release):
            item_time = item.published_at if item.published_at else None
        else:
            continue
        if not item_time:
            logger.warning(f"Failed to fetch param time for item {repr(item)}, skipping")
            continue

        last_time: str | None = (
            load_last_processed().get(repo, {}).get(data_type)
        )

        if (not last_time or
                item_time > datetime.fromisoformat(
                    last_time.replace("Z", "+00:00")
                )):

            if isinstance(item, Commit):
                datas = {
                    "repo": repo,
                    "message": item.commit.message.split("\n")[0],
                    "author": item.commit.author.name if item.commit.author else None,
                    "url": item.html_url,
                    "time": item.commit.author.date if item.commit.author else None,
                }
            elif isinstance(item, Issue):
                datas = {
                    "repo": repo,
                    "title": item.title,
                    "author": item.user.login if item.user else None,
                    "url": item.html_url,
                    "time": item.created_at,
                }
            elif isinstance(item, (PullRequest, PullRequestSimple)):
                datas = {
                    "repo": repo,
                    "title": item.title,
                    "author": item.user.login if item.user else None,
                    "url": item.html_url,
                    "time": item.created_at,
                }
            elif isinstance(item, Release):
                datas = {
                    "repo": repo,
                    "name": item.name or "New Release",
                    "version": item.tag_name or "Unknown Version",
                    "details": item.body or "No description provided.",
                    "url": item.html_url,
                    "time": item.published_at,
                }
            else:
                continue

            message = format_message(datas, data_type)

            if data_type == 'issue' and 'pull' in message:
                # ignore issues from pulls
                continue

            if config.github_send_in_markdown:
                pic: bytes = await md_to_pic(message)
                await send_message(
                    bot, group_id, MessageSegment.image(pic)
                )
            else:
                if (config.github_send_detail_in_markdown and
                        data_type in ('release',)):
                    markdown_text: str = datas.get(
                        'details', 'No details provided.'
                    )
                    splited: list[str] = message.split(markdown_text)
                    pic = await md_to_pic(markdown_text)
                    msg_all = (
                        MessageSegment.text(splited[0]) +
                        MessageSegment.image(pic) +
                        MessageSegment.text(splited[1])
                    )
                else:
                    msg_all = MessageSegment.text(message)

                await send_message(
                    bot, group_id, msg_all
                )

                if isinstance(item, Release) and load_group_configs().get(group_id, {}).get("send_release", False):
                    await send_release_files(bot, group_id, item)

    if latest_data:
        # Ensure the value is always a datetime object before calling isoformat
        def get_datetime(item) -> datetime:
            if isinstance(item, Commit):
                if item.commit.author and item.commit.author.date:
                    return item.commit.author.date
                else:
                    return datetime.now(timezone.utc)
            elif isinstance(item, (Issue, PullRequest, PullRequestSimple)):
                if getattr(item, "created_at", None):
                    return item.created_at
                else:
                    return datetime.now(timezone.utc)
            elif isinstance(item, Release):
                if getattr(item, "published_at", None):
                    return item.published_at  # type: ignore
                else:
                    return datetime.now(timezone.utc)
            else:
                return datetime.now(timezone.utc)

        last_processed.setdefault(repo, {})[data_type] = get_datetime(latest_data[0]).isoformat()


def reset_temp_disabled_configs() -> None:
    """Reset configs to True if a new hour has started."""
    current_hour = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    )
    to_reset = []
    for key, hour in temp_disabled.items():
        if hour < current_hour:
            to_reset.append(key)
    # Remove reset entries
    for key in to_reset:
        del temp_disabled[key]


async def check_repo_updates() -> None:
    """Check for new commits, issues, PRs, and releases for all repos and notify groups."""
    api_cache.clear()
    try:
        global run_lock
        if run_lock:
            logger.warning("Execution of job \"check_repo_updates\" skipped: "
                           "maximum number of running instances reached (1)")
            return
        run_lock = True
        try:
            bot: Bot = get_bot()  # type: ignore
            last_processed = load_last_processed()
            group_repo_dict: dict[int, list[dict[str, str]]] = load_group_configs(False)
        except Exception:
            run_lock = False
            return

        # Reset disables at the start of each hour
        reset_temp_disabled_configs()

        for group_id, repo_configs in group_repo_dict.items():
            group_id = int(group_id)
            for repo_config in repo_configs:
                repo = repo_config.get("repo")
                if not repo:
                    continue

                # Process different data types
                for data_type, endpoint in [
                    ("commit", "commits"),
                    ("issue", "issues"),
                    ("pull_req", "pulls"),
                    ("release", "releases")
                ]:
                    if (repo_config.get(data_type, False) and
                            not temp_disabled.get((group_id, repo, data_type))):
                        try:
                            # Skip if comments are not enabled for issues/PRs
                            if (data_type == 'issue' and
                                    not repo_config.get("send_issue_comment", False)):
                                pass
                            elif (data_type == 'pull_req' and
                                  not repo_config.get("send_pr_comment", False)):
                                pass
                            elif (data_type == 'issue' and
                                    repo_config.get("send_issue_comment", False)):
                                await process_issues_and_prs(repo.split('/')[1], repo.split('/')[0], "issues",
                                                             group_id, bot)
                                continue
                            elif (data_type == 'pull_req' and
                                  repo_config.get("send_pr_comment", False)):
                                await process_issues_and_prs(repo.split('/')[1], repo.split('/')[0], "prs",
                                                             group_id, bot)
                                continue
                            # # For issues and PRs, use enhanced processing
                            # if data_type in ['issue', 'pull_req']:
                            #     owner, repository = repo.split('/')
                            #     content_type = 'issues' if data_type == 'issue' else 'prs'
                            #     await process_issues_and_prs(
                            #         repository, owner, content_type, group_id, bot, last_processed
                            #     )
                            # else:
                            # For commits and releases, use traditional method
                            data = await fetch_github_data(repo, endpoint)
                            if data:
                                await notify(
                                    bot=bot,
                                    group_id=group_id,
                                    repo=repo,
                                    data=data,
                                    data_type=data_type,
                                    last_processed=last_processed,
                                )
                        except RuntimeError as e:
                            html = (
                                f"<p>GitHub API Error:</p>"
                                f"<p style='white-space=pre-wrap'>"
                                f"{e.__cause__.last_attempt.__class__}: "  # pylint: disable=no-member  # type: ignore
                                f"{e.__cause__.last_attempt.exception()}"  # pylint: disable=no-member  # type: ignore
                                ).replace('\n', '</br>')
                            # Handle GitHub API errors
                            if config.github_send_faliure_group:
                                pic = await html_to_pic(html)
                                await send_message(
                                    bot, group_id, MessageSegment.image(pic)
                                )

                            if config.github_send_faliure_superuser:
                                for user_id in superusers:
                                    pic = await html_to_pic(html)
                                    await send_message(
                                        bot, user_id, MessageSegment.image(pic), "user"
                                    )

                            # Disable configuration if needed
                            if config.github_disable_when_fail:
                                ...
                            current_hour = datetime.now(timezone.utc).replace(
                                minute=0, second=0, microsecond=0
                            )
                            temp_disabled[(group_id, repo, data_type)] = current_hour

        save_last_processed(last_processed)
        for x in temp_commit:
            save_commit_data(
                        x.get("key"),
                        x.get("hash"),
                        x.get("id"),
                        x.get("content_type")
                    )
    finally:
        run_lock = False
