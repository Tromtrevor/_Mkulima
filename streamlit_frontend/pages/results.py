import streamlit as st

st.set_page_config(page_title='Prediction Result')
st.write('''## Top recommendation''')

col1, col2 = st.columns(2)

with col1:
	if 'best_crop' in st.session_state:
		crop = st.session_state['best_crop']
		yield_estimate = st.session_state.get('total_yield', 0)
		profit_margin = st.session_state.get('profit_margin', 0)
		st.write(f'''
			## {crop.capitalize()}
			Estimated Yield: {yield_estimate:.2f} tonnes\n
			Criteria: Highest Profit Potential
			''')

		if st.button('View Details'):
			st.switch_page('pages/details.py')

	else:
		st.warning("No prediction found. Please run a crop recommendation first.")
		if st.button("🔙 Go Back"):
			st.switch_page("pages/crop_recommendation.py")

with col2:
	st.write(f'''
		\n### Profitability Analysis
		''')
	st.metric(
		label= 'Estimated Revenue:',
		 value= f'Ksh. {st.session_state.get("total_revenue", 0):.2f}')

	st.metric(
		label= 'Estimated Cultivation Cost:',
		value= f'Ksh. {st.session_state.get("total_cost", 0):.2f}')

	st.metric(
		label= 'Net Profit:',
		value= f'Ksh. {st.session_state.get("profit", 0):.2f}',
		delta= f'{st.session_state.get("profit_margin", 0):.2f}%')
	

st.write('''## Other recommendations''')

# Display other crop options
if 'all_profits' in st.session_state:
	for crop_name, profit_data in st.session_state['all_profits'].items():
		if crop_name != st.session_state.get('best_crop'):
			col_crop = st.columns(1)[0]
			with col_crop:
				st.subheader(f"{crop_name.capitalize()}")
				col_a, col_b, col_c = st.columns(3)
				with col_a:
					st.metric("Yield", f"{profit_data.get('prediction', 0):.2f} tonnes")
				with col_b:
					st.metric("Revenue", f"Ksh. {profit_data.get('profit', {}).get('total_revenue', 0):.2f}")
				with col_c:
					st.metric("Profit", f"Ksh. {profit_data.get('profit', {}).get('total_profit', 0):.2f}")

