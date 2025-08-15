from typing import Optional
from pydantic import AnyUrl, Field
from nado_protocol.utils.enum import StrEnum

from nado_protocol.utils.model import NadoBaseModel


class NadoNetwork(StrEnum):
    """
    Enumeration representing various network environments for the Nado protocol.
    """

    # dev
    HARDHAT = "localhost"
    TESTING = "test"


class NadoAbiName(StrEnum):
    """
    Enumeration representing various contract names for which the ABI can be loaded in the Nado protocol.
    """

    ENDPOINT = "Endpoint"
    FQUERIER = "FQuerier"
    ICLEARINGHOUSE = "IClearinghouse"
    IENDPOINT = "IEndpoint"
    IOFFCHAIN_BOOK = "IOffchainBook"
    IPERP_ENGINE = "IPerpEngine"
    ISPOT_ENGINE = "ISpotEngine"
    MOCK_ERC20 = "MockERC20"
    ISTAKING = "IStaking"
    IVRTX_AIRDROP = "IVrtxAirdrop"
    IFOUNDATION_REWARDS_AIRDROP = "IFoundationRewardsAirdrop"


class NadoDeployment(NadoBaseModel):
    """
    Class representing deployment data for Nado protocol contracts.

    Attributes:
        node_url (AnyUrl): The URL of the node.

        quote_addr (str): The address of the quote contract.

        querier_addr (str): The address of the querier contract.

        clearinghouse_addr (str): The address of the clearinghouse contract.

        endpoint_addr (str): The address of the endpoint contract.

        spot_engine_addr (str): The address of the spot engine contract.

        perp_engine_addr (str): The address of the perpetual engine contract.

        vrtx_airdrop_addr (str): The address of the VRTX airdrop contract.

        vrtx_staking_addr (str): The address of the VRTX staking contract.

        foundation_rewards_airdrop_addr (str): The address of Foundation Rewards airdrop contract for the corresponding chain (e.g: Arb airdrop for Arbitrum).
    """

    node_url: AnyUrl = Field(alias="publicNodeUrl")
    quote_addr: str = Field(alias="quote")
    querier_addr: str = Field(alias="querier")
    clearinghouse_addr: str = Field(alias="clearinghouse")
    endpoint_addr: str = Field(alias="endpoint")
    spot_engine_addr: str = Field(alias="spotEngine")
    perp_engine_addr: str = Field(alias="perpEngine")
    vrtx_airdrop_addr: str = Field(alias="vrtxAirdrop")
    vrtx_staking_addr: str = Field(alias="vrtxStaking")
    foundation_rewards_airdrop_addr: str = Field(alias="foundationRewardsAirdrop")


class DepositCollateralParams(NadoBaseModel):
    """
    Class representing parameters for depositing collateral in the Nado protocol.

    Attributes:
        subaccount_name (str): The name of the subaccount.

        product_id (int): The ID of the spot product to deposit collateral for.

        amount (int): The amount of collateral to be deposited.

        referral_code (Optional[str]): Use this to indicate you were referred by existing member.
    """

    subaccount_name: str
    product_id: int
    amount: int
    referral_code: Optional[str]


class ClaimVrtxParams(NadoBaseModel):
    epoch: int
    amount: Optional[int]
    claim_all: Optional[bool]


class ClaimVrtxContractParams(NadoBaseModel):
    epoch: int
    amount_to_claim: int
    total_claimable_amount: int
    merkle_proof: list[str]


class ClaimFoundationRewardsProofStruct(NadoBaseModel):
    totalAmount: int
    week: int
    proof: list[str]


class ClaimFoundationRewardsContractParams(NadoBaseModel):
    claim_proofs: list[ClaimFoundationRewardsProofStruct]


class NadoExecuteType(StrEnum):
    """
    Enumeration of possible actions to execute in Nado.
    """

    PLACE_ORDER = "place_order"
    PLACE_ISOLATED_ORDER = "place_isolated_order"
    CANCEL_ORDERS = "cancel_orders"
    CANCEL_PRODUCT_ORDERS = "cancel_product_orders"
    CANCEL_AND_PLACE = "cancel_and_place"
    WITHDRAW_COLLATERAL = "withdraw_collateral"
    LIQUIDATE_SUBACCOUNT = "liquidate_subaccount"
    MINT_LP = "mint_lp"
    BURN_LP = "burn_lp"
    LINK_SIGNER = "link_signer"


NadoTxType = StrEnum(
    "NadoTxType",
    {
        **{name: member.value for name, member in NadoExecuteType.__members__.items()},
        **{"AUTHENTICATE_STREAM": "authenticate"},
        **{"LIST_TRIGGER_ORDERS": "list_trigger_orders"},
    },
)  # type: ignore
