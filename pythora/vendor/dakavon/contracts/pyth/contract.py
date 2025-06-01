"""This module contains the scaffold contract definition."""

# ruff: noqa: PLR0904
from aea.common import JSONLike
from aea.crypto.base import LedgerApi
from aea.contracts.base import Contract
from aea.configurations.base import PublicId


class Pyth(Contract):
    """The scaffold contract class for a smart contract."""

    contract_id = PublicId.from_str("open_aea/scaffold:0.1.0")

    @classmethod
    def get_ema_price_no_older_than(cls, ledger_api: LedgerApi, contract_address: str, id: str, age: int) -> JSONLike:
        """Handler method for the 'get_ema_price_no_older_than' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.getEmaPriceNoOlderThan(id=id, age=age).call()
        return {"price": result}

    @classmethod
    def get_ema_price_unsafe(cls, ledger_api: LedgerApi, contract_address: str, id: str) -> JSONLike:
        """Handler method for the 'get_ema_price_unsafe' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.getEmaPriceUnsafe(id=id).call()
        return {"price": result}

    @classmethod
    def get_price_no_older_than(cls, ledger_api: LedgerApi, contract_address: str, id: str, age: int) -> JSONLike:
        """Handler method for the 'get_price_no_older_than' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.getPriceNoOlderThan(id=id, age=age).call()
        return {"price": result}

    @classmethod
    def get_price_unsafe(cls, ledger_api: LedgerApi, contract_address: str, id: str) -> JSONLike:
        """Handler method for the 'get_price_unsafe' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.getPriceUnsafe(id=id).call()
        return {"price": result}

    @classmethod
    def get_twap_update_fee(cls, ledger_api: LedgerApi, contract_address: str, update_data: list[str]) -> JSONLike:
        """Handler method for the 'get_twap_update_fee' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.getTwapUpdateFee(updateData=update_data).call()
        return {"feeAmount": result}

    @classmethod
    def get_update_fee(cls, ledger_api: LedgerApi, contract_address: str, update_data: list[str]) -> JSONLike:
        """Handler method for the 'get_update_fee' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.getUpdateFee(updateData=update_data).call()
        return {"feeAmount": result}

    @classmethod
    def parse_price_feed_updates(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        update_data: list[str],
        price_ids: list[str],
        min_publish_time: int,
        max_publish_time: int,
    ) -> JSONLike:
        """Handler method for the 'parse_price_feed_updates' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.parsePriceFeedUpdates(
            updateData=update_data, priceIds=price_ids, minPublishTime=min_publish_time, maxPublishTime=max_publish_time
        )

    @classmethod
    def parse_price_feed_updates_unique(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        update_data: list[str],
        price_ids: list[str],
        min_publish_time: int,
        max_publish_time: int,
    ) -> JSONLike:
        """Handler method for the 'parse_price_feed_updates_unique' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.parsePriceFeedUpdatesUnique(
            updateData=update_data, priceIds=price_ids, minPublishTime=min_publish_time, maxPublishTime=max_publish_time
        )

    @classmethod
    def parse_price_feed_updates_with_slots_strict(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        update_data: list[str],
        price_ids: list[str],
        min_publish_time: int,
        max_publish_time: int,
    ) -> JSONLike:
        """Handler method for the 'parse_price_feed_updates_with_slots_strict' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.parsePriceFeedUpdatesWithSlotsStrict(
            updateData=update_data, priceIds=price_ids, minPublishTime=min_publish_time, maxPublishTime=max_publish_time
        )

    @classmethod
    def parse_twap_price_feed_updates(
        cls, ledger_api: LedgerApi, contract_address: str, update_data: list[str], price_ids: list[str]
    ) -> JSONLike:
        """Handler method for the 'parse_twap_price_feed_updates' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.parseTwapPriceFeedUpdates(updateData=update_data, priceIds=price_ids)

    @classmethod
    def update_price_feeds(cls, ledger_api: LedgerApi, contract_address: str, update_data: list[str]) -> JSONLike:
        """Handler method for the 'update_price_feeds' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.updatePriceFeeds(updateData=update_data)

    @classmethod
    def update_price_feeds_if_necessary(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        update_data: list[str],
        price_ids: list[str],
        publish_times: list[int],
    ) -> JSONLike:
        """Handler method for the 'update_price_feeds_if_necessary' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.updatePriceFeedsIfNecessary(
            updateData=update_data, priceIds=price_ids, publishTimes=publish_times
        )

    @classmethod
    def get_price_feed_update_events(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        id: str | None = None,
        publish_time: int | None = None,
        price: int | None = None,
        conf: int | None = None,
        look_back: int = 1000,
        to_block: str = "latest",
        from_block: int | None = None,
    ) -> JSONLike:
        """Handler method for the 'PriceFeedUpdate' events ."""

        instance = cls.get_instance(ledger_api, contract_address)
        arg_filters = {
            key: value
            for key, value in (("id", id), ("publishTime", publish_time), ("price", price), ("conf", conf))
            if value is not None
        }
        to_block = to_block or "latest"
        if to_block == "latest":
            to_block = ledger_api.api.eth.block_number
        from_block = from_block or (to_block - look_back)
        result = instance.events.PriceFeedUpdate().get_logs(
            fromBlock=from_block, toBlock=to_block, argument_filters=arg_filters
        )
        return {
            "events": result,
            "from_block": from_block,
            "to_block": to_block,
        }

    @classmethod
    def get_twap_price_feed_update_events(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        twap_price: int | None = None,
        twap_conf: int | None = None,
        down_slots_ratio: int | None = None,
        look_back: int = 1000,
        to_block: str = "latest",
        from_block: int | None = None,
    ) -> JSONLike:
        """Handler method for the 'TwapPriceFeedUpdate' events ."""

        instance = cls.get_instance(ledger_api, contract_address)
        arg_filters = {
            key: value
            for key, value in (
                ("id", id),
                ("startTime", start_time),
                ("endTime", end_time),
                ("twapPrice", twap_price),
                ("twapConf", twap_conf),
                ("downSlotsRatio", down_slots_ratio),
            )
            if value is not None
        }
        to_block = to_block or "latest"
        if to_block == "latest":
            to_block = ledger_api.api.eth.block_number
        from_block = from_block or (to_block - look_back)
        result = instance.events.TwapPriceFeedUpdate().get_logs(
            fromBlock=from_block, toBlock=to_block, argument_filters=arg_filters
        )
        return {
            "events": result,
            "from_block": from_block,
            "to_block": to_block,
        }
