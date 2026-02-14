from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


EPSILON = 1e-9


def normalize_rate(rate: float) -> float:
    """Accepts 0~1 or 0~100 inputs and returns 0~1."""
    if rate is None:
        return 0.0
    return rate / 100.0 if rate > 1 else rate


def compute_bundle_size(discount_rate: float) -> float:
    return 1 + normalize_rate(discount_rate) * 2


def compute_avg_order_price(list_price: float, discount_rate: float) -> float:
    return list_price * compute_bundle_size(discount_rate) * (1 - normalize_rate(discount_rate))


def compute_churn_rate(base_churn_rate: float, branding: float) -> float:
    return base_churn_rate / (100 + branding)


def compute_conversion_rate(
    base_conversion_rate: float,
    industry_index: float,
    product_index: float,
    competition_index: float,
) -> float:
    return normalize_rate(base_conversion_rate) * industry_index * product_index * competition_index


def compute_customer_acquisition_cost(
    base_customer_acquisition_cost: float,
    marketing_efficiency: float,
) -> float:
    return base_customer_acquisition_cost * 100 / (100 + marketing_efficiency)


def compute_orders(customers: float, conversion_rate: float, inventory: float) -> float:
    return min(customers * conversion_rate, inventory)


def compute_revenue(avg_order_price: float, orders: float) -> float:
    return avg_order_price * orders


def compute_fees(revenue: float, fee_rate: float) -> float:
    return revenue * normalize_rate(fee_rate)


def compute_variable_logistics_cost(weight: float, logistics_cost_per_weight: float) -> float:
    return weight * logistics_cost_per_weight


def compute_logistics_cost(
    base_logistics_cost: float,
    variable_logistics_cost: float,
    orders: float,
) -> float:
    return (base_logistics_cost + variable_logistics_cost) * orders


def compute_cost_of_goods_sold(orders: float, product_cost: float) -> float:
    return orders * product_cost


def compute_variable_cost(
    fees: float,
    logistics_cost: float,
    marketing_spend: float,
    cost_of_goods_sold: float,
) -> float:
    return fees + logistics_cost + marketing_spend + cost_of_goods_sold


def compute_interest_cost(loan: float, interest_rate: float) -> float:
    return loan * normalize_rate(interest_rate) / 365


def compute_fixed_cost(labor_cost: float, rent: float, interest_cost: float) -> float:
    return labor_cost + rent + interest_cost


def compute_expenses(variable_cost: float, fixed_cost: float) -> float:
    return variable_cost + fixed_cost


def compute_purchase_cost(purchase_quantity: float, unit_cost: float) -> float:
    return purchase_quantity * unit_cost


def compute_cash_flow_next(
    cash_flow: float,
    loan: float,
    revenue: float,
    expenses: float,
    purchase_cost: float,
) -> float:
    return cash_flow + loan + revenue - expenses - purchase_cost


def compute_inventory_next(
    inventory: float,
    orders: float,
    bundle_size: float,
    purchase_quantity: float,
) -> float:
    return inventory - orders * bundle_size + purchase_quantity


def enforce_moq(purchase_quantity: float, minimum_order_quantity: float) -> None:
    if purchase_quantity > EPSILON and purchase_quantity < minimum_order_quantity:
        raise ValueError("매입수량은 MOQ 이상이어야 합니다.")


def evaluate_product_unlock(
    metric_score: float,
    decision_score: float,
    threshold: float = 0.5,
) -> bool:
    weighted_score = 0.3 * metric_score + 0.7 * decision_score
    return weighted_score >= threshold


def add_tech(tech_owned: List[str], tech_name: str) -> List[str]:
    if tech_name in tech_owned:
        raise ValueError("이미 보유한 기술입니다.")
    return [*tech_owned, tech_name]


def add_staff(staff_roster: List[str], staff_name: str, staff_capacity: int) -> List[str]:
    if staff_name in staff_roster:
        raise ValueError("이미 고용된 직원입니다.")
    if len(staff_roster) + 1 > staff_capacity:
        raise ValueError("사무실 수용 인원을 초과했습니다.")
    return [*staff_roster, staff_name]


def remove_staff(staff_roster: List[str], staff_name: str) -> List[str]:
    if staff_name not in staff_roster:
        raise ValueError("해당 직원이 없습니다.")
    return [name for name in staff_roster if name != staff_name]


@dataclass
class Product:
    name: str
    list_price: float
    discount_rate: float
    product_cost: float
    weight: float
    minimum_order_quantity: float
    is_product_unlocked: bool

    def bundle_size(self) -> float:
        return compute_bundle_size(self.discount_rate)

    def avg_order_price(self) -> float:
        return compute_avg_order_price(self.list_price, self.discount_rate)


@dataclass
class OperatorSettings:
    base_churn_rate: float
    base_conversion_rate: float
    industry_index: float
    product_index: float
    competition_index: float
    base_customer_acquisition_cost: float
    base_logistics_cost: float
    logistics_cost_per_weight: float
    interest_rate: float


@dataclass
class UserDecisions:
    office_lease_enabled: bool
    hire_staff_enabled: bool
    tech_development_enabled: bool
    promotion_enabled: bool
    purchase_quantity: float
    marketing_efficiency: float
    branding: float
    tech_owned: List[str] = field(default_factory=list)
    staff_roster: List[str] = field(default_factory=list)
    staff_capacity: int = 0


@dataclass
class DayInputs:
    marketing_spend: float
    fee_rate: float
    annual_labor_cost: float
    annual_rent: float
    loan: float
    cash_flow: float
    total_revenue: float
    existing_customers: float
    inventory: float


@dataclass
class DayResult:
    orders: float
    revenue: float
    expenses: float
    cash_flow_next: float
    total_revenue_next: float
    inventory_next: float
    churn_rate: float
    conversion_rate: float
    customer_acquisition_cost: float


def simulate_day(
    product: Product,
    operator: OperatorSettings,
    decisions: UserDecisions,
    inputs: DayInputs,
) -> DayResult:
    enforce_moq(decisions.purchase_quantity, product.minimum_order_quantity)

    churn_rate = compute_churn_rate(operator.base_churn_rate, decisions.branding)
    conversion_rate = compute_conversion_rate(
        operator.base_conversion_rate,
        operator.industry_index,
        operator.product_index,
        operator.competition_index,
    )
    customer_acquisition_cost = compute_customer_acquisition_cost(
        operator.base_customer_acquisition_cost,
        decisions.marketing_efficiency,
    )

    new_customers = inputs.marketing_spend / customer_acquisition_cost if customer_acquisition_cost > EPSILON else 0.0
    existing_customers = inputs.existing_customers * (1 - churn_rate)
    customers = new_customers + existing_customers

    avg_order_price = product.avg_order_price()
    orders = compute_orders(customers, conversion_rate, inputs.inventory)
    revenue = compute_revenue(avg_order_price, orders)

    fees = compute_fees(revenue, inputs.fee_rate)
    variable_logistics_cost = compute_variable_logistics_cost(product.weight, operator.logistics_cost_per_weight)
    logistics_cost = compute_logistics_cost(operator.base_logistics_cost, variable_logistics_cost, orders)
    cost_of_goods_sold = compute_cost_of_goods_sold(orders, product.product_cost)
    variable_cost = compute_variable_cost(fees, logistics_cost, inputs.marketing_spend, cost_of_goods_sold)

    labor_cost = inputs.annual_labor_cost / 365
    rent = inputs.annual_rent / 365
    interest_cost = compute_interest_cost(inputs.loan, operator.interest_rate)
    fixed_cost = compute_fixed_cost(labor_cost, rent, interest_cost)
    expenses = compute_expenses(variable_cost, fixed_cost)

    purchase_cost = compute_purchase_cost(decisions.purchase_quantity, product.product_cost)
    cash_flow_next = compute_cash_flow_next(
        inputs.cash_flow,
        inputs.loan,
        revenue,
        expenses,
        purchase_cost,
    )
    total_revenue_next = inputs.total_revenue + revenue
    inventory_next = compute_inventory_next(
        inputs.inventory,
        orders,
        product.bundle_size(),
        decisions.purchase_quantity,
    )

    return DayResult(
        orders=orders,
        revenue=revenue,
        expenses=expenses,
        cash_flow_next=cash_flow_next,
        total_revenue_next=total_revenue_next,
        inventory_next=inventory_next,
        churn_rate=churn_rate,
        conversion_rate=conversion_rate,
        customer_acquisition_cost=customer_acquisition_cost,
    )
