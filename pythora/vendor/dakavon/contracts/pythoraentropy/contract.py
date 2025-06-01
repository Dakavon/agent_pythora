"""This module contains the scaffold contract definition."""

# ruff: noqa: PLR0904
from aea.common import JSONLike
from aea.crypto.base import Address, LedgerApi
from aea.contracts.base import Contract
from aea.configurations.base import PublicId


class Pythoraentropy(Contract):
    """The scaffold contract class for a smart contract."""

    contract_id = PublicId.from_str("open_aea/scaffold:0.1.0")

    @classmethod
    def last_sequence_number(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
    ) -> JSONLike:
        """Handler method for the 'last_sequence_number' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.lastSequenceNumber().call()
        return {"int": result}

    @classmethod
    def random_numbers_by_sequence_number(cls, ledger_api: LedgerApi, contract_address: str, var_0: int) -> JSONLike:
        """Handler method for the 'random_numbers_by_sequence_number' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.randomNumbersBySequenceNumber(var_0).call()
        return {"str": result}

    @classmethod
    def sequence_numbers_by_user_random_number(
        cls, ledger_api: LedgerApi, contract_address: str, var_0: str
    ) -> JSONLike:
        """Handler method for the 'sequence_numbers_by_user_random_number' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.sequenceNumbersByUserRandomNumber(var_0).call()
        return {"int": result}

    @classmethod
    def entropy_callback(
        cls, ledger_api: LedgerApi, contract_address: str, sequence: int, provider: Address, random_number: str
    ) -> JSONLike:
        """Handler method for the 'entropy_callback' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions._entropyCallback(sequence=sequence, provider=provider, randomNumber=random_number)

    @classmethod
    def request_random_number(cls, ledger_api: LedgerApi, contract_address: str, user_random_number: str) -> JSONLike:
        """Handler method for the 'request_random_number' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        return instance.functions.requestRandomNumber(userRandomNumber=user_random_number)

    @classmethod
    def get_pythora_entropy_callback_events(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        sequence_number: int | None = None,
        provider: Address = None,
        random_number: str | None = None,
        look_back: int = 1000,
        to_block: str = "latest",
        from_block: int | None = None,
    ) -> JSONLike:
        """Handler method for the 'PythoraEntropyCallback' events ."""

        instance = cls.get_instance(ledger_api, contract_address)
        arg_filters = {
            key: value
            for key, value in (
                ("sequenceNumber", sequence_number),
                ("provider", provider),
                ("randomNumber", random_number),
            )
            if value is not None
        }
        to_block = to_block or "latest"
        if to_block == "latest":
            to_block = ledger_api.api.eth.block_number
        from_block = from_block or (to_block - look_back)
        result = instance.events.PythoraEntropyCallback().get_logs(
            fromBlock=from_block, toBlock=to_block, argument_filters=arg_filters
        )
        return {
            "events": result,
            "from_block": from_block,
            "to_block": to_block,
        }

    @classmethod
    def get_random_number_requested_events(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        sequence_number: int | None = None,
        provider: Address = None,
        user_random_number: str | None = None,
        look_back: int = 1000,
        to_block: str = "latest",
        from_block: int | None = None,
    ) -> JSONLike:
        """Handler method for the 'RandomNumberRequested' events ."""

        instance = cls.get_instance(ledger_api, contract_address)
        arg_filters = {
            key: value
            for key, value in (
                ("sequenceNumber", sequence_number),
                ("provider", provider),
                ("userRandomNumber", user_random_number),
            )
            if value is not None
        }
        to_block = to_block or "latest"
        if to_block == "latest":
            to_block = ledger_api.api.eth.block_number
        from_block = from_block or (to_block - look_back)
        result = instance.events.RandomNumberRequested().get_logs(
            fromBlock=from_block, toBlock=to_block, argument_filters=arg_filters
        )
        return {
            "events": result,
            "from_block": from_block,
            "to_block": to_block,
        }
