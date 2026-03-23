from datetime import datetime
import streamlit as st
from helpers.settings_helper import SettingsConfiguration
from helpers.api_helper import QueryAPI
from helpers.database_helper import insert_to_db, fetch_data, delete_position

def get_open_token_contract():
    df = fetch_data("SELECT * FROM positions WHERE remaining > 0")
    token_contract_tuple = tuple(f"{token} - {contract}" for token, contract in zip(df['token'], df['contract_address']))
    return token_contract_tuple

class SubmitOrder:
    def __init__(self):
        self.settings = SettingsConfiguration('settings.yaml')
        self.settings_data = self.settings.get_settings()
        self.api_key = self.settings_data['api_key']
        self.balance = self.settings_data['balance']
        self.priority_buy_fee = self.settings_data['priority_buy_fee']
        self.priority_sell_fee = self.settings_data['priority_sell_fee']
        self.query_api = QueryAPI(self.api_key)

    def calculate_token_amt(self, total, token_price, sol_price):
        return (sol_price * total) / token_price

    def calculate_avg_mc(self, contract_address):
        df = fetch_data(f"SELECT * FROM transactions WHERE contract_address = '{contract_address}' AND action = 'buy'")
        total_tokens = df['token_amt'].sum()
        weighted_mcs = sum(row['token_amt'] * row['market_cap'] for _, row in df.iterrows())
        return weighted_mcs / total_tokens

    def calculate_changes(self, mc, amc, initial_not_sold):
        percentage_change = (mc - amc) / amc
        return initial_not_sold * percentage_change

    def calculate_roi(self, initial_investment, remaining, sold):
        return (((remaining + sold) - initial_investment) / initial_investment) * 100

    def add_to_trade_history(self, contract_address, amt, action, token_amt=None):
        token_details = self.query_api.token_data(contract_address)
        if isinstance(token_details, str):
            return token_details
        sol_price = self.query_api.get_sol_price()
        if isinstance(sol_price, str):
            return sol_price

        date = datetime.now().strftime("%Y-%m-%d")
        time_val = datetime.now().strftime("%H:%M:%S")
        symbol = token_details['symbol']
        name = token_details['name']
        mc = token_details['market_cap']
        token_price = token_details['token_price']

        if token_price <= 0:
            return 'Token price is 0! Try again later!'

        if token_amt is None:
            token_amt = self.calculate_token_amt(amt, token_price, sol_price['solana']['usd'])

        data = [[date, time_val, symbol, name, contract_address, action, mc, token_price, token_amt, amt]]
        insert_to_db('transactions', data)
        return data

    def refresh_token(self):
        df = fetch_data("SELECT * FROM positions WHERE remaining > 0")
        if df.empty:
            return "No open positions to refresh!"

        ca_to_refresh = list(df['contract_address'])
        all_token_details = self.query_api.get_multiple_token_data(ca_to_refresh)

        to_insert = []
        for _, row in df.iterrows():
            ca = row['contract_address']
            mc = all_token_details[ca]['market_cap']
            initial_not_sold = row['initial_investment'] - row['sold']
            unrealized_profit = self.calculate_changes(mc, row['average_market_cap'], initial_not_sold)
            remaining = initial_not_sold + unrealized_profit
            roi = self.calculate_roi(row['initial_investment'], remaining, row['sold'])
            data = [row['date'], row['time'], row['symbol'], row['token'], row['contract_address'],
                    mc, row['average_market_cap'], row['initial_investment'], remaining, row['sold'],
                    unrealized_profit, row['realized_profit'], roi, row['total_token_amt'], row['remaining_token_amt']]
            to_insert.append(data)

        delete_position(ca_to_refresh)
        insert_to_db('positions', to_insert)

    def buy_coin(self, contract_address, buy_amt):
        if not contract_address:
            return 'No contract address entered!'
        if buy_amt <= 0:
            return 'Buy amount must be more than 0 SOL!'
        if self.balance - buy_amt < 0:
            return 'Insufficient balance!'
        actual_buy_amt = buy_amt - self.priority_buy_fee
        if actual_buy_amt <= 0:
            return 'Insufficient balance to pay priority fee!'

        data = self.add_to_trade_history(contract_address, actual_buy_amt, 'buy')
        if isinstance(data, str):
            return data

        df = fetch_data(f"SELECT * FROM positions WHERE contract_address = '{contract_address}'")

        if not df.empty:
            date, time_val = data[0][0], data[0][1]
            mc = data[0][6]
            token_amt = data[0][8]
            avg_mc = float(self.calculate_avg_mc(contract_address))
            initial_investment = float(df['initial_investment']) + actual_buy_amt
            total_sold = float(df['sold'].iloc[0])
            initial_not_sold = initial_investment - total_sold
            unrealized_profit = self.calculate_changes(mc, avg_mc, initial_not_sold)
            remaining = initial_not_sold + unrealized_profit
            roi = self.calculate_roi(initial_investment, remaining, total_sold)
            total_token_amt = float(df['total_token_amt']) + token_amt
            remaining_token_amt = float(df['remaining_token_amt']) + token_amt
            realized_profit = float(df['realized_profit'].iloc[0])
            new_data = [(date, time_val, df['symbol'].iloc[0], df['token'].iloc[0], df['contract_address'].iloc[0],
                         mc, avg_mc, initial_investment, remaining, total_sold, unrealized_profit, realized_profit,
                         roi, total_token_amt, remaining_token_amt)]
            delete_position(contract_address)
            insert_to_db('positions', new_data)
        else:
            date, time_val = data[0][0], data[0][1]
            symbol, token = data[0][2], data[0][3]
            mc = data[0][6]
            token_amt = data[0][8]
            initial_investment = remaining = data[0][9]
            new_data = [[date, time_val, symbol, token, contract_address, mc, mc, initial_investment,
                         remaining, 0, 0.0, 0.0, 0.0, token_amt, token_amt]]
            insert_to_db('positions', new_data)

        self.settings.update_settings('balance', self.balance - buy_amt, rerun=False)

    def sell_coin(self, contract_address, sell_percentage):
        if not isinstance(sell_percentage, float):
            sell_percentage = float(str(sell_percentage).strip('%'))
        if sell_percentage <= 0:
            return 'Sell percentage not entered!'
        if contract_address is None:
            return 'Please select a token to sell!'

        contract_address = contract_address.split(' - ')[1]
        df = fetch_data(f"SELECT * FROM positions WHERE contract_address = '{contract_address}' AND remaining > 0")

        current_token_amt = float(df['remaining_token_amt'].iloc[0])
        tokens_to_sell = current_token_amt * (sell_percentage / 100)

        token_details = self.query_api.token_data(contract_address)
        if isinstance(token_details, str):
            return token_details
        sol_price = self.query_api.get_sol_price()
        if isinstance(sol_price, str):
            return sol_price

        token_price = token_details['token_price']
        sol_price_usd = sol_price['solana']['usd']

        sell_amt = (tokens_to_sell * token_price) / sol_price_usd
        actual_sell_amt = sell_amt - self.priority_sell_fee

        if actual_sell_amt <= 0:
            return 'Insufficient balance to pay priority fee!'

        proportion_sold = tokens_to_sell / float(df['total_token_amt'].iloc[0])
        cost_basis = float(df['initial_investment'].iloc[0]) * proportion_sold
        realized_profit_from_sale = actual_sell_amt - cost_basis

        if sell_percentage == 100:
            remaining_token_amt = 0
            remaining = 0
        else:
            remaining_token_amt = current_token_amt - tokens_to_sell
            remaining = float(df['remaining'].iloc[0]) - sell_amt

        data = self.add_to_trade_history(contract_address, actual_sell_amt, 'sell', tokens_to_sell)
        if isinstance(data, str):
            return data

        date, time_val = data[0][0], data[0][1]
        symbol, token = data[0][2], data[0][3]
        mc = token_details['market_cap']
        avg_mc = float(df['average_market_cap'].iloc[0])
        initial_investment = float(df['initial_investment'].iloc[0])
        total_sold = float(df['sold'].iloc[0]) + actual_sell_amt
        total_token_amt = float(df['total_token_amt'].iloc[0])
        total_realized_profit = float(df['realized_profit'].iloc[0]) + realized_profit_from_sale

        if sell_percentage == 100:
            unrealized_profit = 0
            remaining = 0
            remaining_token_amt = 0
        else:
            initial_not_sold = initial_investment - total_sold
            unrealized_profit = self.calculate_changes(mc, avg_mc, initial_not_sold)
            remaining = initial_not_sold + unrealized_profit

        roi = self.calculate_roi(initial_investment, remaining, total_sold)

        new_data = [(date, time_val, symbol, token, contract_address, mc, avg_mc,
                     initial_investment, remaining, total_sold, unrealized_profit,
                     total_realized_profit, roi, total_token_amt, remaining_token_amt)]

        delete_position(contract_address)
        insert_to_db('positions', new_data)
        self.settings.update_settings('balance', self.balance + actual_sell_amt, rerun=False)
