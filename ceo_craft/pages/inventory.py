import streamlit as st

from ceo_model import (
	DayInputs,
	OperatorSettings,
	Product,
	UserDecisions,
	simulate_day,
)

st.set_page_config(page_title="CEO Craft - 재고", layout="wide")

company_name = st.session_state.get("company_name", "회사")

st.markdown(f"## {company_name}")
st.title("재고")

st.markdown("재고 변동 시뮬레이션 입력값을 설정하세요.")

with st.form("inventory_simulation_form"):
	st.subheader("상품 설정")
	product_name = st.text_input("상품명", value="기본 상품")
	list_price = st.number_input("정가", min_value=0.0, value=10000.0, step=100.0)
	discount_rate = st.number_input("할인율(0~1 또는 0~100)", min_value=0.0, value=10.0, step=1.0)
	product_cost = st.number_input("상품원가", min_value=0.0, value=6000.0, step=100.0)
	weight = st.number_input("무게", min_value=0.0, value=1.0, step=0.1)
	minimum_order_quantity = st.number_input("MOQ", min_value=0.0, value=100.0, step=10.0)
	is_product_unlocked = st.checkbox("상품 해금 여부", value=True)

	st.subheader("운영자 설정")
	base_churn_rate = st.number_input("기본이탈율(%)", min_value=0.0, value=5.0, step=0.1)
	base_conversion_rate = st.number_input("기준전환율(%)", min_value=0.0, value=3.0, step=0.1)
	industry_index = st.number_input("산업지수", min_value=0.0, value=1.0, step=0.1)
	product_index = st.number_input("상품지수", min_value=0.0, value=1.0, step=0.1)
	competition_index = st.number_input("경쟁지수", min_value=0.0, value=1.0, step=0.1)
	base_customer_acquisition_cost = st.number_input(
		"기본고객획득비용",
		min_value=0.0,
		value=20000.0,
		step=100.0,
	)
	base_logistics_cost = st.number_input("기본물류비", min_value=0.0, value=3000.0, step=100.0)
	logistics_cost_per_weight = st.number_input("단위물류비", min_value=0.0, value=100.0, step=10.0)
	interest_rate = st.number_input("이자율(%)", min_value=0.0, value=5.0, step=0.1)

	st.subheader("유저 결정")
	office_lease_enabled = st.checkbox("사무실임대", value=False)
	hire_staff_enabled = st.checkbox("인력충원", value=False)
	tech_development_enabled = st.checkbox("기술개발", value=False)
	promotion_enabled = st.checkbox("프로모션", value=False)
	purchase_quantity = st.number_input("매입수량", min_value=0.0, value=100.0, step=10.0)
	marketing_efficiency = st.number_input("마케팅효율", min_value=0.0, value=0.0, step=1.0)
	branding = st.number_input("브랜딩", min_value=0.0, value=0.0, step=10.0)

	st.subheader("일 단위 입력")
	marketing_spend = st.number_input("마케팅비", min_value=0.0, value=500000.0, step=10000.0)
	fee_rate = st.number_input("수수료율(%)", min_value=0.0, value=3.0, step=0.1)
	annual_labor_cost = st.number_input("직원연봉 합계", min_value=0.0, value=0.0, step=100000.0)
	annual_rent = st.number_input("연간 임대료", min_value=0.0, value=0.0, step=100000.0)
	loan = st.number_input("대출", min_value=0.0, value=0.0, step=100000.0)
	cash_flow = st.number_input("현금흐름(현재)", value=0.0, step=100000.0)
	total_revenue = st.number_input("매출실적(누적)", value=0.0, step=100000.0)
	existing_customers = st.number_input("기존고객 수", min_value=0.0, value=0.0, step=10.0)
	inventory = st.number_input("재고량", min_value=0.0, value=1000.0, step=10.0)

	submitted = st.form_submit_button("재고 시뮬레이션")

if submitted:
	if not is_product_unlocked:
		st.warning("상품이 잠겨 있어 시뮬레이션 결과가 의미 없을 수 있습니다.")

	product = Product(
		name=product_name,
		list_price=list_price,
		discount_rate=discount_rate,
		product_cost=product_cost,
		weight=weight,
		minimum_order_quantity=minimum_order_quantity,
		is_product_unlocked=is_product_unlocked,
	)

	operator = OperatorSettings(
		base_churn_rate=base_churn_rate,
		base_conversion_rate=base_conversion_rate,
		industry_index=industry_index,
		product_index=product_index,
		competition_index=competition_index,
		base_customer_acquisition_cost=base_customer_acquisition_cost,
		base_logistics_cost=base_logistics_cost,
		logistics_cost_per_weight=logistics_cost_per_weight,
		interest_rate=interest_rate,
	)

	decisions = UserDecisions(
		office_lease_enabled=office_lease_enabled,
		hire_staff_enabled=hire_staff_enabled,
		tech_development_enabled=tech_development_enabled,
		promotion_enabled=promotion_enabled,
		purchase_quantity=purchase_quantity,
		marketing_efficiency=marketing_efficiency,
		branding=branding,
		staff_capacity=0,
	)

	inputs = DayInputs(
		marketing_spend=marketing_spend,
		fee_rate=fee_rate,
		annual_labor_cost=annual_labor_cost,
		annual_rent=annual_rent,
		loan=loan,
		cash_flow=cash_flow,
		total_revenue=total_revenue,
		existing_customers=existing_customers,
		inventory=inventory,
	)

	try:
		result = simulate_day(product, operator, decisions, inputs)
	except ValueError as exc:
		st.error(str(exc))
	else:
		st.subheader("재고 결과")
		col1, col2 = st.columns(2)
		col1.metric("재고량(현재)", f"{inventory:,.2f}")
		col1.metric("재고량(다음)", f"{result.inventory_next:,.2f}")
		col2.metric("주문건", f"{result.orders:,.2f}")
		col2.metric("매입수량", f"{purchase_quantity:,.2f}")

		st.markdown("---")
		st.write("매출", f"{result.revenue:,.0f}")
		st.write("현금흐름(다음)", f"{result.cash_flow_next:,.0f}")
		st.write("고객획득비용", f"{result.customer_acquisition_cost:,.2f}")
