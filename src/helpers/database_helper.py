import duckdb
  import os
  import streamlit as st

  def create_db(db_name='trades.ddb'):
      """
      Create the SolSim database and tables if they do not exist.
      """
      with duckdb.connect(db_name) as con:
          con.execute('''
              CREATE TABLE IF NOT EXISTS transactions (
                  date DATE,
                  time TIME,
                  symbol TEXT,
                  token TEXT,
                  contract_address TEXT,
                  action TEXT,
                  market_cap REAL,
                  token_price REAL,
                  token_amt REAL,
                  total REAL
              );
          ''')

          con.execute('''
              CREATE TABLE IF NOT EXISTS positions (
                  date DATE,
                  time TIME,
                  symbol TEXT,
                  token TEXT,
                  contract_address TEXT,
                  market_cap REAL,
                  average_market_cap REAL,
                  initial_investment REAL,
                  remaining REAL,
                  sold REAL,
                  unrealized_profit REAL,
                  realized_profit REAL,
                  roi REAL,
                  total_token_amt REAL,
                  remaining_token_amt REAL
              );
          ''')

  def delete_db(db_name='trades.ddb'):
      """Delete the database file."""
      if os.path.exists(db_name):
          os.remove(db_name)

  def insert_to_db(table, data, db_name='trades.ddb'):
      """
      Insert data into the specified table.

      Parameters:
      - table (str): The table to insert data into.
      - data (list): The data to insert.
      """
      with duckdb.connect(db_name) as con:
          if table == 'transactions':
              query = f'''
                  INSERT INTO {table} (date, time, symbol, token, contract_address, action, market_cap, token_price, token_amt, total)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              '''
          elif table == 'positions':
              query = f'''
                  INSERT INTO {table} (date, time, symbol, token, contract_address, market_cap, average_market_cap, initial_investment, remaining, sold, unrealized_profit, realized_profit, roi, total_token_amt, remaining_token_amt)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              '''
          con.executemany(query, data)

  def fetch_data(query, db_name='trades.ddb'):
      """
      Fetch data from the database using a SQL query.

      Parameters:
      - query (str): SQL query to execute.

      Returns:
      - pd.DataFrame: Query result as a DataFrame.
      """
      with duckdb.connect(db_name) as con:
          return con.execute(query).df()

  def delete_position(contract_address, db_name='trades.ddb'):
      """
      Delete a position from the positions table.

      Parameters:
      - contract_address (str or list): Contract address(es) to delete.
      """
      with duckdb.connect(db_name) as con:
          if isinstance(contract_address, list):
              for ca in contract_address:
                  con.execute(f"DELETE FROM positions WHERE contract_address = '{ca}'")
          else:
              con.execute(f"DELETE FROM positions WHERE contract_address = '{contract_address}'")
  