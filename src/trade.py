import streamlit as st
import os
import time
from helpers.database_helper import fetch_data
from helpers.trades_helper import SubmitOrder, get_open_token_contract
from helpers.settings_helper import SettingsConfiguration
from helpers.helpers import format_positions_df
from streamlit_extras.stylable_container import stylable_container

st.title("📈 Trade", anchor=False)

settings = SettingsConfiguration('settings.yaml')
priority_buy_fee = settings.get_settings()['priority_buy_fee']
priority_sell_fee = settings.get_settings()['priority_sell_fee']

if os.path.exists('trades.ddb'):
    order = SubmitOrder()

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(border=True):
            st.header("Buy", anchor=False, divider='green')
            ca_input_buy = st.text_input("Contract Address (CA)")
            buy_sol_amt = st.number_input("Buy Amount (SOL)", min_value=0.0)
            submit_buy = st.button("BUY", use_container_width=True)
            if submit_buy:
                error = order.buy_coin(ca_input_buy, buy_sol_amt)
                if error is not None:
                    st.toast(f"{error}", icon='🚨')
                else:
                    st.toast(f"Buy order submitted! Priority fee: {priority_buy_fee} SOL", icon='✅')
                    time.sleep(1)
                    st.rerun()

    with col2:
        options = get_open_token_contract()
        with st.container(border=True):
            st.header("Sell", anchor=False, divider='red')
            ca_input_sell = st.selectbox("Select token", options)
            sell_percentage_radio = st.radio(
                "Sell percentage",
                [None, "25%", "50%", "75%", "100%"],
                horizontal=True
            )
            if sell_percentage_radio is None:
                st.session_state['disable_number_input'] = False
            else:
                st.session_state['disable_number_input'] = True
            sell_percentage_input = st.number_input(
                "Sell percentage (manual)",
                min_value=0.0,
                max_value=100.0,
                disabled=st.session_state.get('disable_number_input', False)
            )
            submit_sell = st.button("SELL", use_container_width=True)
            if submit_sell:
                sell_pct = sell_percentage_radio if sell_percentage_radio else sell_percentage_input
                error = order.sell_coin(ca_input_sell, sell_pct)
                if error is not None:
                    st.toast(f"{error}", icon='🚨')
                else:
                    st.toast(f"Sell order submitted! Priority fee: {priority_sell_fee} SOL", icon='✅')
                    time.sleep(1)
                    st.rerun()

    st.divider()
    st.subheader("Open Positions", anchor=False)
    col_refresh, _ = st.columns([1, 5])
    with col_refresh:
        if st.button("Refresh Prices", use_container_width=True):
            msg = order.refresh_token()
            if msg:
                st.toast(msg, icon='⚠️')
            else:
                st.toast("Positions refreshed!", icon='✅')
            time.sleep(0.5)
            st.rerun()

    positions_df = fetch_data("SELECT * FROM positions WHERE remaining > 0")
    if not positions_df.empty:
        st.dataframe(format_positions_df(positions_df), use_container_width=True)
    else:
        st.info("No open positions. Start trading above!")
else:
    st.warning("No database found. Please create one in Settings first.")
