"""Command-line entry points for the package.

This module exposes a small, testable FediCleaner class that owns configuration
and the Mastodon client. Use the module-level `main()` wrapper to run the
tool from the command line.
"""

from __future__ import annotations

import argparse
import logging
import json
from datetime import datetime, timedelta
from typing import Callable, Any, Set, Dict, Iterable, Generator
from enum import IntEnum

from mastodon import Mastodon
import asyncio
from tqdm import tqdm
import httpx

from fedi_cleaner.config import load_settings, Settings, create_example_config


class ValidState(IntEnum):
    MIGRATED = 1
    INACTIVE = 2
    DEAD = 3


class FediCleaner:
    """Encapsulates the cleaning workflow and state.

    Responsibilities:
    - create the Mastodon client from typed Settings
    - fetch and filter accounts
    - validate accounts (concurrently)
    - compute operations and perform them or write a dry-run file
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.mastodon = Mastodon(
            access_token=settings.access_token,
            api_base_url=settings.api_base_url,
            ratelimit_method="pace",
        )

    # --- fetching helpers ---
    def _fetch_accounts(
        self, api_function: Callable[[], Any], valid_date: datetime
    ) -> list[Any]:
        """Fetch accounts from API and filter by activity date."""
        accounts = api_function()
        accounts = self.mastodon.fetch_remaining(accounts)
        return [
            acc
            for acc in accounts
            if acc.get("last_status_at") is None
            or acc.get("last_status_at") < valid_date
        ]

    def _exclude_mutuals(
        self,
        accounts_dict: Dict[str, list[Any]],
        following_ids: set[int],
        followers_ids: set[int],
    ) -> None:
        """Remove mutual follows from all account lists if clean_mutuals is False."""
        if self.settings.clean_mutuals:
            return

        mutuals = following_ids & followers_ids
        if not mutuals:
            return

        logging.info(f"Excluding {len(mutuals)} mutuals")

        # Remove mutuals from simple account lists
        for account_type in ["following", "followers", "mutes"]:
            accounts_dict[account_type] = [
                acc for acc in accounts_dict[account_type] if acc["id"] not in mutuals
            ]

        # Remove mutuals from list members
        for list_data in accounts_dict["lists_members"]:
            list_data["members"] = [
                acc for acc in list_data["members"] if acc["id"] not in mutuals
            ]

    # --- async account validation ---
    @staticmethod
    async def _valid_account_async(
        client: httpx.AsyncClient, account: Any
    ) -> tuple[int, ValidState]:
        """Validate a single account by checking its ActivityPub endpoint."""
        try:
            resp = await client.get(
                account["url"], headers={"Accept": "application/activity+json"}
            )
            if resp.status_code == 200:
                try:
                    # Check if response has content and is valid JSON
                    if not resp.content.strip():
                        return account["id"], ValidState.DEAD

                    data = resp.json()
                    if data.get("movedTo"):
                        return account["id"], ValidState.MIGRATED
                    return account["id"], ValidState.INACTIVE
                except (ValueError, TypeError, json.JSONDecodeError):
                    # Invalid JSON response, treat as dead
                    return account["id"], ValidState.DEAD
            return account["id"], ValidState.DEAD
        except (httpx.RequestError, httpx.TimeoutException):
            return account["id"], ValidState.DEAD

    async def _valid_accounts_async(
        self, acc_list: list[Any]
    ) -> list[tuple[int, ValidState]]:
        """Validate multiple accounts concurrently using async HTTP requests."""
        concurrency = 16
        limits = httpx.Limits(
            max_connections=concurrency, max_keepalive_connections=concurrency
        )
        timeout = httpx.Timeout(5.0)
        results: list[tuple[int, ValidState]] = []

        async with httpx.AsyncClient(
            limits=limits, timeout=timeout, http2=True
        ) as client:
            tasks = [
                asyncio.create_task(self._valid_account_async(client, acc))
                for acc in acc_list
            ]
            with tqdm(total=len(acc_list), desc="Validating accounts") as pbar:
                for coro in asyncio.as_completed(tasks):
                    res = await coro
                    results.append(res)
                    pbar.update(1)

        return results

    def _valid_accounts(
        self, accounts: Iterable[Any]
    ) -> Generator[tuple[int, ValidState], None, None]:
        """Validate accounts and yield results. Sync wrapper around async validation."""
        acc_list = list(accounts)
        if not acc_list:
            return

        results = asyncio.run(self._valid_accounts_async(acc_list))
        yield from results

    # --- utility methods ---
    @staticmethod
    def _state_allowed(state_value: int, allowed: Set[ValidState]) -> bool:
        """Check if a validation state is in the allowed set."""
        try:
            return ValidState(state_value) in allowed
        except ValueError:
            return False

    def _apply_operations(self, operations: Dict[str, Any]) -> None:
        """Apply cleaning operations using appropriate Mastodon API calls."""
        operation_handlers = {
            "following": self.mastodon.account_unfollow,
            "followers": self.mastodon.account_remove_from_followers,
            "blocks": self.mastodon.account_unblock,
            "mutes": self.mastodon.account_unmute,
        }

        for op_type, data in operations.items():
            if not data:  # Skip empty operations
                continue

            if op_type == "lists_members":
                for list_id, member_ids in data.items():
                    if member_ids:
                        self.mastodon.list_accounts_delete(list_id, member_ids)
            elif op_type in operation_handlers:
                handler = operation_handlers[op_type]
                for acc_id in data:
                    handler(acc_id)

    def load_and_apply_operations(self, operations_file: str) -> None:
        """Load operations from a JSON file and apply them."""
        try:
            with open(operations_file, "r") as f:
                operations = json.load(f)
            logging.info(f"Loaded operations from {operations_file}")
            self._apply_operations(operations)
            logging.info("Operations applied successfully!")
        except FileNotFoundError:
            raise FileNotFoundError(f"Operations file not found: {operations_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in operations file: {e}")

    # --- main workflow ---
    def run(self) -> None:
        """Main workflow: fetch, filter, validate, and clean accounts."""
        logging.info("Starting Fedi Cleaner")

        current_user = self.mastodon.me()
        uid = current_user["id"]
        valid_date = datetime.now() - timedelta(days=self.settings.inactive_days)

        # Fetch accounts based on settings
        accounts = self._fetch_all_accounts(uid, valid_date)

        # Extract IDs for mutual exclusion
        following_ids = {acc["id"] for acc in accounts["following"]}
        followers_ids = {acc["id"] for acc in accounts["followers"]}

        # Exclude mutuals if configured
        self._exclude_mutuals(accounts, following_ids, followers_ids)

        # Build allowed states for validation
        allowed_states = self._get_allowed_states()

        # Validate and build operations
        operations = self._build_operations(accounts, allowed_states)

        # Execute or save operations
        if self.settings.dry_run:
            with open("operations.json", "w") as f:
                json.dump(operations, f, indent=4, default=str)
            logging.info("Operations saved to operations.json")
        else:
            self._apply_operations(operations)

        logging.info("Done!")

    def _fetch_all_accounts(
        self, uid: int, valid_date: datetime
    ) -> Dict[str, list[Any]]:
        """Fetch all account types based on settings."""
        accounts = {
            "following": [],
            "followers": [],
            "lists_members": [],
            "blocks": [],
            "mutes": [],
        }

        # Fetch following/followers (needed for mutual detection even if not cleaning)
        need_following = (
            self.settings.clean_following or not self.settings.clean_mutuals
        )
        need_followers = (
            self.settings.clean_followers or not self.settings.clean_mutuals
        )

        if need_following:
            logging.info("Fetching following")
            accounts["following"] = self._fetch_accounts(
                lambda: self.mastodon.account_following(uid), valid_date
            )

        if need_followers:
            logging.info("Fetching followers")
            accounts["followers"] = self._fetch_accounts(
                lambda: self.mastodon.account_followers(uid), valid_date
            )

        if self.settings.clean_lists:
            logging.info("Fetching lists")
            lists = self.mastodon.lists()
            for list_ in lists:
                list_members = self._fetch_accounts(
                    lambda: self.mastodon.list_accounts(list_["id"]), valid_date
                )
                accounts["lists_members"].append(
                    {
                        "id": list_["id"],
                        "title": list_["title"],
                        "members": list_members,
                    }
                )

        if self.settings.clean_blocks:
            logging.info("Fetching blocks")
            accounts["blocks"] = self._fetch_accounts(self.mastodon.blocks, valid_date)

        if self.settings.clean_mutes:
            logging.info("Fetching mutes")
            accounts["mutes"] = self._fetch_accounts(self.mastodon.mutes, valid_date)

        return accounts

    def _get_allowed_states(self) -> Set[ValidState]:
        """Build set of validation states that should be acted on."""
        return {
            state
            for state, enabled in [
                (ValidState.MIGRATED, self.settings.clean_migrated_accounts),
                (ValidState.INACTIVE, self.settings.clean_inactive_accounts),
                (ValidState.DEAD, self.settings.clean_dead_accounts),
            ]
            if enabled
        }

    def _build_operations(
        self, accounts: Dict[str, list[Any]], allowed_states: Set[ValidState]
    ) -> Dict[str, Any]:
        """Validate accounts and build operations for enabled account types."""
        operations = {}

        for account_type, account_list in accounts.items():
            if not self._should_clean_type(account_type) or not account_list:
                continue

            logging.info(f"Validating {account_type}")

            if account_type == "lists_members":
                operations[account_type] = {
                    list_data["id"]: [
                        acc_id
                        for acc_id, state in self._valid_accounts(list_data["members"])
                        if self._state_allowed(state, allowed_states)
                    ]
                    for list_data in account_list
                }
            else:
                operations[account_type] = [
                    acc_id
                    for acc_id, state in self._valid_accounts(account_list)
                    if self._state_allowed(state, allowed_states)
                ]

        return operations

    def _should_clean_type(self, account_type: str) -> bool:
        """Check if this account type should be cleaned based on settings."""
        return {
            "following": self.settings.clean_following,
            "followers": self.settings.clean_followers,
            "lists_members": self.settings.clean_lists,
            "blocks": self.settings.clean_blocks,
            "mutes": self.settings.clean_mutes,
        }.get(account_type, False)


def main() -> None:
    """Main entry point for the fedi-cleaner CLI."""
    parser = argparse.ArgumentParser(
        description="A tool to help you clean your Fediverse account's following/followers/lists/blocks/mutes/..."
    )
    parser.add_argument(
        "--init-config",
        "-i",
        action="store_true",
        help="Create an example configuration file",
    )
    parser.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    parser.add_argument(
        "--apply-operations",
        "-a",
        metavar="FILE",
        nargs="?",
        const="operations.json",
        help="Apply operations from a JSON file (default: operations.json)",
    )

    args = parser.parse_args()

    if args.init_config:
        create_example_config(args.config)
        return

    logging.basicConfig(level=logging.INFO)
    settings = load_settings(args.config)
    cleaner = FediCleaner(settings)

    if args.apply_operations:
        cleaner.load_and_apply_operations(args.apply_operations)
    else:
        cleaner.run()
