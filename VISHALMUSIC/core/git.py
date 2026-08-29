# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram 
#   Module : Git Update & Repository Manager
# ═══════════════════════════════════════════════════════════

import asyncio
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config

from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO
    try:
        repo = Repo()
        LOGGER(__name__).info(f"Git Client Found [VPS DEPLOYER]")
        # Ensure origin remote points to correct URL
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
            if list(origin.urls)[0] != UPSTREAM_REPO:
                origin.set_url(UPSTREAM_REPO)
        else:
            repo.create_remote("origin", UPSTREAM_REPO)
    except GitCommandError:
        LOGGER(__name__).info(f"Invalid Git Command")
    except InvalidGitRepositoryError:
        # Deployed from a ZIP (no .git directory): do NOT clone/checkout the
        # upstream repo here — that would silently REPLACE the deployed code
        # with the upstream repository on every restart. Keep current code intact.
        LOGGER(__name__).info(
            "No git repository found (ZIP deploy). Skipping upstream sync to keep current code intact."
        )
        return

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
