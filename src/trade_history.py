import streamlit as st
import os
import pandas as pd
from helpers.database_helper import fetch_data

st.title("🗓️ Trade History", anchor=False)

if os.path.exists('trades.ddb'):
    transactions_df = fetch_data("SELECT * FROM transactions ORDER BY date DESC, time DESC")

    if not transactions_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            total_buys = len(transactions_df[transactions_df['action'] == 'buy'])
            st.metric("Total Buys", total_buys)
        with col2:
            total_sells = len(transactions_df[transactions_df['action'] == 'sell'])
            st.metric("Total Sells", total_sells)
        with col3:
            total_volume = transactions_df['total'].sum()
            st.metric("Total Volume", f"{total_volume:.4f} SOL")

        st.divider()

        action_filter = st.selectbox("Filter by action", ["All", "buy", "sell"])
        if action_filter != "All":
            display_df = transactions_df[transactions_df['action'] == action_filter]
        else:
            display_df = transactions_df

        st.dataframe(display_df, use_container_width=True)

        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Export to CSV",
            data=csv,
            file_name="solsim_trade_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No trade history yet. Start trading in the Trade page!")
else:
    st.warning("No database found. Please create one in Settings first.")
