import streamlit as st
import os
from helpers.database_helper import fetch_data
from helpers.helpers import format_positions_df
from helpers.settings_helper import SettingsConfiguration

st.title("📊 Portfolio", anchor=False)

if os.path.exists('trades.ddb'):
    settings = SettingsConfiguration('settings.yaml')
    balance = settings.get_settings()['balance']

    positions_df = fetch_data("SELECT * FROM positions")

    if not positions_df.empty:
        total_invested = positions_df['initial_investment'].sum()
        total_remaining = positions_df['remaining'].sum()
        total_realized = positions_df['realized_profit'].sum()
        total_unrealized = positions_df['unrealized_profit'].sum()
        total_pnl = total_realized + total_unrealized

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Balance", f"{balance:.4f} SOL")
        with col2:
            st.metric("Total Invested", f"{total_invested:.4f} SOL")
        with col3:
            st.metric("Realized P/L", f"{total_realized:.4f} SOL",
                      delta=f"{total_realized:.4f}", delta_color="normal")
        with col4:
            st.metric("Unrealized P/L", f"{total_unrealized:.4f} SOL",
                      delta=f"{total_unrealized:.4f}", delta_color="normal")

        st.divider()
        st.subheader("All Positions", anchor=False)

        open_df = positions_df[positions_df['remaining'] > 0]
        closed_df = positions_df[positions_df['remaining'] <= 0]

        tab1, tab2 = st.tabs(["Open Positions", "Closed Positions"])
        with tab1:
            if not open_df.empty:
                st.dataframe(format_positions_df(open_df), use_container_width=True)
            else:
                st.info("No open positions.")
        with tab2:
            if not closed_df.empty:
                st.dataframe(format_positions_df(closed_df), use_container_width=True)
            else:
                st.info("No closed positions yet.")
    else:
        st.info("No trading data yet. Start trading in the Trade page!")
else:
    st.warning("No database found. Please create one in Settings first.")
