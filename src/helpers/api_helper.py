import requests

  class QueryAPI:
      def __init__(self, api_key):
          """
          Initialize the QueryAPI with an API key.

          Parameters:
          - api_key (str): The API key for BitQuery authentication.
          """
          self.api_key = api_key

      def get_sol_price(self):
          """
          Get the current price of SOL in USD via CoinGecko.

          Returns:
          - dict or str: Price data or error message.
          """
          url = 'https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd'
          response = requests.get(url)
          if response.status_code == 200:
              return response.json()
          else:
              if response.status_code == 429:
                  return f'Too many requests to CoinGecko API! (Status Code: {response.status_code})'
              return f'Error! (Status Code: {response.status_code})'

      def token_data(self, contract_address):
          """
          Get token data for a specific Solana contract address via BitQuery.

          Parameters:
          - contract_address (str): The mint address of the token.

          Returns:
          - dict or str: Token details or error message.
          """
          url = "https://streaming.bitquery.io/eap"

          query = """
          query GetDEXTradeAndTokenSupply($mintAddress: String!) {
          Solana {
              DEXTrades(
              limit: { count: 1 }
              orderBy: { descending: Block_Time }
              where: {
                  Trade: {
                  Buy: { Currency: { MintAddress: { is: $mintAddress } } }
                  }
                  Transaction: { Result: { Success: true } }
              }
              ) {
              Trade {
                  Buy {
                  PriceInUSD
                  Currency {
                      Name
                      Symbol
                      MintAddress
                  }
                  }
              }
              }
              TokenSupplyUpdates(
              limit: { count: 1 }
              orderBy: { descending: Block_Time }
              where: { Currency: { MintAddress: { is: $mintAddress } } }
              ) {
              Currency {
                  MintAddress
                  Name
                  Symbol
                  Decimals
              }
              PostBalanceInUSD
              }
          }
          }
          """

          headers = {
              "Content-Type": "application/json",
              "Authorization": f"Bearer {self.api_key}"
          }

          variables = {"mintAddress": contract_address}
          response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

          if response.status_code == 200:
              data = response.json()
              try:
                  dex_trades = data['data']['Solana']['DEXTrades']
                  token_supply = data['data']['Solana']['TokenSupplyUpdates']

                  if not dex_trades:
                      return 'No trading activity found for this token!'

                  trade = dex_trades[0]['Trade']['Buy']
                  token_price = trade['PriceInUSD']
                  name = trade['Currency']['Name']
                  symbol = trade['Currency']['Symbol']

                  market_cap = 0
                  if token_supply:
                      market_cap = token_supply[0]['PostBalanceInUSD']

                  return {
                      'name': name,
                      'symbol': symbol,
                      'token_price': token_price,
                      'market_cap': market_cap
                  }
              except (KeyError, IndexError) as e:
                  return f'Error parsing token data: {str(e)}'
          else:
              return f'BitQuery API error! (Status Code: {response.status_code})'

      def get_multiple_token_data(self, contract_addresses):
          """
          Get token data for multiple contract addresses.

          Parameters:
          - contract_addresses (list): List of mint addresses.

          Returns:
          - dict: Dictionary mapping contract address to token details.
          """
          result = {}
          for ca in contract_addresses:
              data = self.token_data(ca)
              result[ca] = data
          return result
  