import logging
import time
from typing import Callable

from amazon_paapi import AmazonApi
from amazon_paapi.errors import ItemsNotFound, TooManyRequests
from amazon_paapi.models import Country


class Paapi:
    def __init__(
            self,
            amazon_key: str,
            amazon_secret: str,
            amazon_tag: str,
            logger=None,
            throttling: float = 5.0,
            max_retries: int = 5,
    ):
        self.api = AmazonApi(
            key=amazon_key,
            secret=amazon_secret,
            tag=amazon_tag,
            country=Country.US,
            throttling=throttling,
        )
        self.throttling = throttling
        self.max_retries = max(max_retries, 0)
        self.logger = logging.getLogger(__name__) if logger is None else logger

    def get_browse_nodes(self, browse_node_ids: list) -> dict:
        result = {x: None for x in browse_node_ids}
        node_list = self.api.get_browse_nodes(browse_node_ids)
        for node in node_list:
            result[node.id] = node.to_dict()
        return result

    def get_items(self, asin_list: list) -> dict | None:
        item_list = None
        wait = self.throttling
        for _ in range(self.max_retries):
            try:
                item_list = self.api.get_items(asin_list)
            except ItemsNotFound:
                item_list = []
            except TooManyRequests:
                self.logger.warning(f"TooManyRequests - wait {wait} seconds")
                time.sleep(wait)
                wait *= 2

            if item_list is not None:
                break

        if item_list is None:
            return None

        result = {x: None for x in asin_list}
        for item in item_list:
            result[item.asin] = item.to_dict()
        return result

    def search_items(
            self, node_id: str, page: int = 1, sort_by: str = "NewestArrivals"
    ) -> list:
        result = self._fetch_list(
            self.api.search_items,
            browse_node_id=str(node_id),
            item_page=page,
            sort_by=sort_by,
            search_index="Music",
        )
        items = getattr(result, "items", None) or []
        return [x.to_dict() for x in items]

    def _fetch_list(self, func: Callable, **kwargs):
        wait = self.throttling
        retry = 0
        while retry <= self.max_retries:
            try:
                return func(**kwargs)
            except ItemsNotFound:
                return None
            except TooManyRequests:
                if retry < self.max_retries:
                    self.logger.warning(f"TooManyRequests - wait for {wait} seconds")
                    time.sleep(wait)
                    wait *= 2
                else:
                    raise
        else:
            raise RuntimeError("Failed too many items")
