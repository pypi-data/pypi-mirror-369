from typing import Optional, Union
from typing import Annotated
from nado_protocol.utils.enum import StrEnum
from nado_protocol.utils.model import NadoBaseModel
from pydantic import conlist


class ResponseStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"


class EngineStatus(StrEnum):
    ACTIVE = "active"
    FAILED = "failed"


class MintLp(NadoBaseModel):
    product_id: int
    subaccount: str
    amount_base: str
    quote_amount_low: str
    quote_amount_high: str


class BurnLp(NadoBaseModel):
    product_id: int
    subaccount: str
    amount_lp: str


class ApplyDelta(NadoBaseModel):
    product_id: int
    subaccount: str
    amount_delta: str
    v_quote_delta: str


class MintLpTx(NadoBaseModel):
    mint_lp: MintLp


class BurnLpTx(NadoBaseModel):
    burn_lp: BurnLp


class ApplyDeltaTx(NadoBaseModel):
    apply_delta: ApplyDelta


class SubaccountHealth(NadoBaseModel):
    assets: str
    liabilities: str
    health: str


class SpotLpBalance(NadoBaseModel):
    amount: str


class SpotBalance(NadoBaseModel):
    amount: str
    last_cumulative_multiplier_x18: str


class SpotProductBalance(NadoBaseModel):
    product_id: int
    lp_balance: SpotLpBalance
    balance: SpotBalance


class PerpLpBalance(NadoBaseModel):
    amount: str
    last_cumulative_funding_x18: str


class PerpBalance(NadoBaseModel):
    amount: str
    v_quote_balance: str
    last_cumulative_funding_x18: str


class PerpProductBalance(NadoBaseModel):
    product_id: int
    lp_balance: PerpLpBalance
    balance: PerpBalance


class ProductRisk(NadoBaseModel):
    long_weight_initial_x18: str
    short_weight_initial_x18: str
    long_weight_maintenance_x18: str
    short_weight_maintenance_x18: str
    large_position_penalty_x18: str


class ProductBookInfo(NadoBaseModel):
    size_increment: str
    price_increment_x18: str
    min_size: str
    collected_fees: str
    lp_spread_x18: str


class BaseProduct(NadoBaseModel):
    product_id: int
    oracle_price_x18: str
    risk: ProductRisk
    book_info: ProductBookInfo


class BaseProductLpState(NadoBaseModel):
    supply: str


class SpotProductConfig(NadoBaseModel):
    token: str
    interest_inflection_util_x18: str
    interest_floor_x18: str
    interest_small_cap_x18: str
    interest_large_cap_x18: str


class SpotProductState(NadoBaseModel):
    cumulative_deposits_multiplier_x18: str
    cumulative_borrows_multiplier_x18: str
    total_deposits_normalized: str
    total_borrows_normalized: str


class SpotProductLpAmount(NadoBaseModel):
    amount: str
    last_cumulative_multiplier_x18: str


class SpotProductLpState(BaseProductLpState):
    quote: SpotProductLpAmount
    base: SpotProductLpAmount


class SpotProduct(BaseProduct):
    config: SpotProductConfig
    state: SpotProductState
    lp_state: SpotProductLpState


class PerpProductState(NadoBaseModel):
    cumulative_funding_long_x18: str
    cumulative_funding_short_x18: str
    available_settle: str
    open_interest: str


class PerpProductLpState(BaseProductLpState):
    last_cumulative_funding_x18: str
    cumulative_funding_per_lp_x18: str
    base: str
    quote: str


class PerpProduct(BaseProduct):
    state: PerpProductState
    lp_state: PerpProductLpState


class MaxOrderSizeDirection(StrEnum):
    LONG = "long"
    SHORT = "short"


class ProductSymbol(NadoBaseModel):
    product_id: int
    symbol: str


class SymbolData(NadoBaseModel):
    type: str
    product_id: str
    symbol: str
    price_increment_x18: str
    size_increment: str
    min_size: str
    min_depth_x18: str
    max_spread_rate_x18: str
    maker_fee_rate_x18: str
    taker_fee_rate_x18: str
    long_weight_initial_x18: str
    long_weight_maintenance_x18: str


class SubaccountPosition(NadoBaseModel):
    balance: Union[PerpProductBalance, SpotProductBalance]
    product: Union[PerpProduct, SpotProduct]


# (price, amount)
MarketLiquidity = Annotated[list, conlist(str, min_items=2, max_items=2)]


class Asset(NadoBaseModel):
    product_id: int
    ticker_id: Optional[str]
    market_type: Optional[str]
    name: str
    symbol: str
    maker_fee: Optional[float]
    taker_fee: Optional[float]
    can_withdraw: bool
    can_deposit: bool


class MarketPair(NadoBaseModel):
    ticker_id: str
    base: str
    quote: str


class SpotApr(NadoBaseModel):
    name: str
    symbol: str
    product_id: int
    deposit_apr: float
    borrow_apr: float
    tvl: float


class Orderbook(NadoBaseModel):
    ticker_id: str
    timestamp: int
    bids: list[MarketLiquidity]
    asks: list[MarketLiquidity]


class MarketType(StrEnum):
    SPOT = "spot"
    PERP = "perp"


class IsolatedPosition(NadoBaseModel):
    subaccount: str
    quote_balance: SpotProductBalance
    base_balance: PerpProductBalance
    quote_product: SpotProduct
    base_product: PerpProduct
    healths: list[SubaccountHealth]
    quote_healths: list
    base_healths: list
