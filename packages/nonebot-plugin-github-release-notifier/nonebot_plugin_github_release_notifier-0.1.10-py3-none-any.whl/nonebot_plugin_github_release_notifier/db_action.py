import sqlite3
from nonebot.log import logger
from .config import DATA_DIR

DB_FILE = DATA_DIR / "github_release_notifier.db"
group_data = {}


# Initialize the database
def init_database() -> None:
    """Initialize the SQLite database and create
    the necessary table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_processed (
            repo TEXT PRIMARY KEY,
            commits TEXT,
            issues TEXT,
            prs TEXT,
            releases TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_config (
            group_id TEXT,
            repo TEXT,
            commits BOOLEAN,
            issues BOOLEAN,
            prs BOOLEAN,
            releases BOOLEAN,
            release_folder TEXT,
            send_release BOOLEAN DEFAULT FALSE,
            send_issue_comment BOOLEAN DEFAULT FALSE,
            send_pr_comment BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (group_id, repo)
        )
    """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS prs (
                repo TEXT,
                id INT,
                latest_commit_hash TEXT,
                PRIMARY KEY (id, repo)
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                repo TEXT,
                id INT,
                latest_commit_hash TEXT,
                PRIMARY KEY (id, repo)
            )
        """)
    cursor.execute("PRAGMA table_info(group_config)")
    columns = [row[1] for row in cursor.fetchall()]
    if "release_folder" not in columns:
        cursor.execute("ALTER TABLE group_config ADD COLUMN release_folder TEXT")
    if "send_release" not in columns:
        cursor.execute("ALTER TABLE group_config ADD COLUMN send_release BOOLEAN")
    if "send_issue_comment" not in columns:
        cursor.execute("ALTER TABLE group_config ADD COLUMN send_issue_comment BOOLEAN")
    if "send_pr_comment" not in columns:
        cursor.execute("ALTER TABLE group_config ADD COLUMN send_pr_comment BOOLEAN")
    if "groupid" in columns:
        cursor.execute('ALTER TABLE group_config RENAME COLUMN groupid TO group_id;')
    conn.commit()
    conn.close()


def load_last_processed() -> dict:
    """Load the last processed timestamps from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM last_processed")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a dictionary
    last_processed = {}
    for row in rows:
        repo, commits, issues, prs, releases = row
        last_processed[repo] = {
            "commit": commits,
            "issue": issues,
            "pull_req": prs,
            "release": releases,
        }
    return last_processed


def save_last_processed(data: dict) -> None:
    """Save the last processed timestamps to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for repo, timestamps in data.items():
        cursor.execute("""
            INSERT INTO last_processed (repo, commits, issues, prs, releases)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(repo) DO UPDATE SET
                commits=excluded.commits,
                issues=excluded.issues,
                prs=excluded.prs,
                releases=excluded.releases
        """, (
            repo,
            timestamps.get("commit"),
            timestamps.get("issue"),
            timestamps.get("pull_req"),
            timestamps.get("release"),
        ))

    conn.commit()
    conn.close()


def load_group_configs(fast=True) -> dict:
    """Load the group configurations from the SQLite database."""
    global group_data
    if fast:
        return group_data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_config")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a dictionary
    group_data = {}
    for row in rows:
        (
            group_id,
            repo,
            commits,
            prs,
            issues,
            releases,
            send_folder,
            send_release,
            send_issue_comment,
            send_pr_comment
        ) = row
        if group_id not in group_data:
            data = []
        else:
            data: list = group_data[group_id]
        data.append({
            "repo": repo,
            "commit": commits if commits else False,
            "issue": issues if issues else False,
            "pull_req": prs if prs else False,
            "release": releases if releases else False,
            "send_release": send_release if send_release else False,
            "release_folder": send_folder if send_folder else None,
            "send_issue_comment": send_issue_comment if send_issue_comment else False,
            "send_pr_comment": send_pr_comment if send_pr_comment else False,
        })
        group_data[group_id] = data
    return group_data


def add_group_repo_data(
        group_id: int | str,
        repo: str,
        commits: bool = False,
        issues: bool = False,
        prs: bool = False,
        releases: bool = False,
        release_folder: str | None = None,
        send_release: bool = False,
        send_issue_comment: bool = False,
        send_pr_comment: bool = False,
) -> None:
    """Add or update a group's repository
    configuration in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    cursor.execute("""
        INSERT INTO group_config (group_id, repo, commits,
issues, prs, releases, release_folder, send_release, send_issue_comment, send_pr_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(group_id, repo) DO UPDATE SET
            commits=excluded.commits,
            issues=excluded.issues,
            prs=excluded.prs,
            releases=excluded.releases,
            release_folder=excluded.release_folder,
            send_release=excluded.send_release,
            send_issue_comment=excluded.send_issue_comment,
            send_pr_comment=excluded.send_pr_comment
    """, (group_id, repo, commits, issues, prs, releases,
          release_folder, send_release, send_issue_comment, send_pr_comment))

    conn.commit()
    conn.close()


def change_group_repo_cfg(group_id: int | str, repo: str,
                          config_type: str, value: bool | str) -> None:
    """Change a group's repository configuration in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    # Map type to database column
    column_mapping = {
        "commit": "commits",
        "issue": "issues",
        "pull_req": "prs",
        "release": "releases",
        "commits": "commits",
        "issues": "issues",
        "prs": "prs",
        "releases": "releases",
        "release_folder": "release_folder",
        "send_release": "send_release",
        "send_issue_comment": "send_issue_comment",
        "send_pr_comment": "send_pr_comment",
    }
    if config_type not in column_mapping:
        logger.error(
            f"Error: Invalid type format '{config_type}'. "
            f"Must be one of {list(column_mapping.keys())}."
        )
        conn.close()
        raise ValueError(
            f"Invalid type format '{config_type}'. "
            f"Must be one of {list(column_mapping.keys())}."
        )

    # Get the correct column name
    column = column_mapping[config_type]

    cursor.execute(f"""
        UPDATE group_config
        SET {column}=?
        WHERE group_id=? AND repo=?
    """, (value, group_id, repo))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def remove_group_repo_data(group_id: int | str, repo: str) -> None:
    """Remove a group's repository configuration from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)
    cursor.execute("""
        DELETE FROM group_config
        WHERE group_id=? AND repo=?
    """, (group_id, repo))

    conn.commit()
    conn.close()


def save_commit_data(repo: str, commit_hash: str, id_: int, type_: str) -> None:
    """Save commit data to the database."""
    if type_ not in ["issues", "prs"]:
        raise ValueError(f"Invalid type '{type_}'. Must be 'issues' or 'prs'.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {type_} (repo, id, latest_commit_hash)
        VALUES (?, ?, ?)
        ON CONFLICT(repo, id) DO UPDATE SET
            latest_commit_hash=excluded.latest_commit_hash
    """, (repo, id_, commit_hash))
    conn.commit()
    conn.close()


def get_commit_data(repo: str, id_: int, type_: str) -> str | None:
    """Get the latest commit hash for a specific issue or pull request."""
    if type_ not in ["issues", "prs"]:
        raise ValueError(f"Invalid type '{type_}'. Must be 'issues' or 'prs'.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT latest_commit_hash FROM {type_}
        WHERE repo=? AND id=?
    """, (repo, id_))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
