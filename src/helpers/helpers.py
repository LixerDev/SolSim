import yaml
import pandas as pd
import streamlit as st

def write_yaml(path, data):
    with open(path, 'w') as file:
        yaml.dump(data, file)

def format_positions_df(df):
    if df.empty:
        return df
    display_df = df.copy()
    numeric_cols = ['market_cap', 'average_market_cap', 'initial_investment',
                    'remaining', 'sold', 'unrealized_profit', 'realized_profit', 'roi']
    for col in numeric_cols:
        if col in display_df.columns:
            if col == 'roi':
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")
            elif col in ['market_cap', 'average_market_cap']:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.4f} SOL")
    return display_df
