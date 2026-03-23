import streamlit as st
import os
from helpers.settings_helper import SettingsConfiguration
from helpers.database_helper import create_db, delete_db

st.title("⚙️ Settings", anchor=False)

settings = SettingsConfiguration('settings.yaml')
settings_data = settings.get_settings()

with st.container(border=True):
    st.subheader("Trading Configuration", anchor=False)
    new_balance = st.number_input("Starting Balance (SOL)", value=float(settings_data['balance']), min_value=0.0, step=0.1)
    new_priority_buy = st.number_input("Priority Buy Fee (SOL)", value=float(settings_data['priority_buy_fee']), min_value=0.0, step=0.001, format="%.3f")
    new_priority_sell = st.number_input("Priority Sell Fee (SOL)", value=float(settings_data['priority_sell_fee']), min_value=0.0, step=0.001, format="%.3f")

    if st.button("Save Trading Settings", use_container_width=True):
        settings.update_settings('balance', new_balance, rerun=False)
        settings.update_settings('priority_buy_fee', new_priority_buy, rerun=False)
        settings.update_settings('priority_sell_fee', new_priority_sell, rerun=False)
        st.toast("Settings saved!", icon='✅')
        st.rerun()

with st.container(border=True):
    st.subheader("API Configuration", anchor=False)
    st.markdown("Get your API key from [BitQuery](https://account.bitquery.io/)")
    new_api_key = st.text_input("BitQuery API Key", value=settings_data.get('api_key', ''), type="password")
    if st.button("Save API Key", use_container_width=True):
        settings.update_settings('api_key', new_api_key, rerun=False)
        st.toast("API key saved!", icon='✅')
        st.rerun()

with st.container(border=True):
    st.subheader("Database Management", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Database", use_container_width=True):
            create_db()
            st.toast("Database created!", icon='✅')
            st.rerun()
    with col2:
        if st.button("Delete Database", use_container_width=True, type="primary"):
            delete_db()
            st.toast("Database deleted!", icon='🗑️')
            st.rerun()

    if os.path.exists('trades.ddb'):
        st.success("Database: Connected")
    else:
        st.error("Database: Not found")
