from typing import Any, Optional, Sequence

from autonity import Autonity
from autonity.constants import AUTONITY_CONTRACT_ADDRESS
from autonity.contracts.autonity import ABI
from click import argument, group
from web3 import Web3

from ..options import rpc_endpoint_option
from ..utils import autonity_from_endpoint_arg, to_json, web3_from_endpoint_arg


@group(name="protocol")
def protocol_group() -> None:
    """
    Commands related to Autonity-specific protocol operations.

    See the Autonity contract reference for details.
    """


def _show_sequence(value: Sequence[Any]) -> str:
    return "\n".join([str(v) for v in value])


def _show_json(value: Any) -> str:
    return to_json(value, pretty=True)


@protocol_group.command()
@rpc_endpoint_option
def config(rpc_endpoint: Optional[str]) -> None:
    """
    The Autonity contract configuration.
    """

    print(_show_json(autonity_from_endpoint_arg(rpc_endpoint).get_config()))


@protocol_group.command()
@rpc_endpoint_option
def client_config(rpc_endpoint: Optional[str]) -> None:
    """
    The current client-aware configuration.
    """

    print(_show_json(autonity_from_endpoint_arg(rpc_endpoint).get_client_config()))


@protocol_group.command()
@rpc_endpoint_option
def epoch_id(rpc_endpoint: Optional[str]) -> None:
    """
    ID of the current epoch.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_epoch_id())


@protocol_group.command()
@rpc_endpoint_option
def last_epoch_time(rpc_endpoint: Optional[str]) -> None:
    """
    Timestamp of the last epoch.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_last_epoch_time())


@protocol_group.command()
@rpc_endpoint_option
def epoch_total_bonded_stake(rpc_endpoint: Optional[str]) -> None:
    """
    Total stake bonded this epoch.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_epoch_total_bonded_stake())


@protocol_group.command()
@rpc_endpoint_option
def inflation_reserve(rpc_endpoint: Optional[str]) -> None:
    """
    The inflation reserve.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_inflation_reserve())


@protocol_group.command()
@rpc_endpoint_option
def current_epoch_period(rpc_endpoint: Optional[str]) -> None:
    """
    The current epoch period in blocks.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_current_epoch_period())


@protocol_group.command()
@rpc_endpoint_option
def epoch_period(rpc_endpoint: Optional[str]) -> None:
    """
    The current epoch period in blocks. If there is an update at epoch end,
    the new epoch period is returned.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_epoch_period())


@protocol_group.command()
@rpc_endpoint_option
def block_period(rpc_endpoint: Optional[str]) -> None:
    """
    Block period in seconds.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_block_period())


@protocol_group.command()
@rpc_endpoint_option
def unbonding_period(rpc_endpoint: Optional[str]) -> None:
    """
    Unbonding period in blocks.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_unbonding_period())


@protocol_group.command()
@rpc_endpoint_option
def last_epoch_block(rpc_endpoint: Optional[str]) -> None:
    """
    Block number of the last epoch.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_last_epoch_block())


@protocol_group.command()
@rpc_endpoint_option
def version(rpc_endpoint: Optional[str]) -> None:
    """
    Contract version.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_version())


@protocol_group.command()
@rpc_endpoint_option
def epoch_info(rpc_endpoint: Optional[str]):
    """
    Information about the current epoch.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(_show_json(aut.get_epoch_info()))


@protocol_group.command()
@rpc_endpoint_option
def committee(rpc_endpoint: Optional[str]) -> None:
    """
    The current committee.
    """

    print(_show_json(autonity_from_endpoint_arg(rpc_endpoint).get_committee()))


@protocol_group.command()
@rpc_endpoint_option
def validators(rpc_endpoint: Optional[str]) -> None:
    """
    The current validators.
    """

    print(_show_sequence(autonity_from_endpoint_arg(rpc_endpoint).get_validators()))


@protocol_group.command()
@rpc_endpoint_option
def treasury_account(rpc_endpoint: Optional[str]) -> None:
    """
    Treasury account address.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_treasury_account())


@protocol_group.command()
@rpc_endpoint_option
def treasury_fee(rpc_endpoint: Optional[str]) -> None:
    """
    Treasury fee.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_treasury_fee())


@protocol_group.command()
@rpc_endpoint_option
def current_committee_size(rpc_endpoint: Optional[str]) -> None:
    """
    Current committee size.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_current_committee_size())


@protocol_group.command()
@rpc_endpoint_option
def max_committee_size(rpc_endpoint: Optional[str]) -> None:
    """
    Maximum committee size.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_max_committee_size())


@protocol_group.command()
@rpc_endpoint_option
def committee_enodes(rpc_endpoint: Optional[str]) -> None:
    """
    Enodes in current committee.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_committee_enodes())


@protocol_group.command()
@rpc_endpoint_option
def minimum_base_fee(rpc_endpoint: Optional[str]) -> None:
    """
    Minimum base fee.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_minimum_base_fee())


@protocol_group.command()
@rpc_endpoint_option
def max_schedule_duration(rpc_endpoint: Optional[str]) -> None:
    """
    The maximum allowed duration of any schedule or contract.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_max_schedule_duration())


@protocol_group.command()
@rpc_endpoint_option
def operator(rpc_endpoint: Optional[str]) -> None:
    """
    The governance operator.
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_operator())


@protocol_group.command()
@rpc_endpoint_option
@argument("block-height", type=int)
def epoch_by_height(rpc_endpoint: Optional[str], block_height: int):
    """
    Information about the epoch at the given block height.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(_show_json(aut.get_epoch_by_height(block_height)))


@protocol_group.command()
@rpc_endpoint_option
@argument("block", type=int)
def epoch_from_block(rpc_endpoint: Optional[str], block: int) -> None:
    """
    The ID of the epoch of the given block.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_epoch_from_block(block))


@protocol_group.command()
@rpc_endpoint_option
@argument("unbonding-id", type=int)
def is_unbonding_released(rpc_endpoint: Optional[str], unbonding_id: int):
    """
    Checks if unbonding with the given ID is released or not.

    Prints 1 if the unbonding is released and 0 otherwise.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(int(aut.is_unbonding_released(unbonding_id)))


@protocol_group.command()
@rpc_endpoint_option
@argument("unbonding-id", type=int)
def unbonding_share(rpc_endpoint: Optional[str], unbonding_id: int):
    """
    The share for unbonding with the given ID.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_unbonding_share(unbonding_id))


@protocol_group.command()
@rpc_endpoint_option
@argument("vault-address-str", metavar="VAULT-ADDRESS")
@argument("index", type=int)
def schedule(rpc_endpoint: Optional[str], vault_address_str: str, index: int):
    """
    The schedule for the given vault at the given index.
    """

    vault_address = Web3.to_checksum_address(vault_address_str)
    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(_show_json(aut.get_schedule(vault_address, index)))


@protocol_group.command()
@rpc_endpoint_option
@argument("vault-address-str", metavar="VAULT-ADDRESS")
def total_schedules(rpc_endpoint: Optional[str], vault_address_str: str):
    """
    The total number of schedules for the given vault.
    """

    vault_address = Web3.to_checksum_address(vault_address_str)
    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_total_schedules(vault_address))


@protocol_group.command()
@rpc_endpoint_option
@argument("id", type=int)
def bonding_request(rpc_endpoint: Optional[str], id: int):
    """
    The bonding request corresponding to the given bonding ID.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    bonding_request = aut.get_bonding_request_by_id(id)
    if bonding_request:
        print(_show_json(bonding_request))


@protocol_group.command()
@rpc_endpoint_option
@argument("id", type=int)
def unbonding_request(rpc_endpoint: Optional[str], id: int):
    """
    The unbonding request corresponding to the given unbonding ID.
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    unbonding_request = aut.get_unbonding_request_by_id(id)
    if unbonding_request:
        print(_show_json(unbonding_request))


@protocol_group.command()
def contract_address() -> None:
    """
    Address of the Autonity Contract.
    """

    print(AUTONITY_CONTRACT_ADDRESS)


@protocol_group.command()
def contract_abi() -> None:
    """
    ABI of the Autonity Contract.
    """

    print(_show_json(ABI))
