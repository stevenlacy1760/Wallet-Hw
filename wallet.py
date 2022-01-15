# %%
# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
from eth_account import Account

# %%
# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")
print(mnemonic)

# %%
# Import constants.py and necessary functions from bit and web3
# YOUR CODE HERE
from web3 import Web3
from web3.middleware import geth_poa_middleware
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from bit import wif_to_key
from constants import *
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


w3.isConnected()


# %%
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --numderive={numderive} --coin={coin} --format=jsonpretty'

# YOUR CODE HERE
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)


# %%
# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {'eth':derive_wallets(mnemonic, coin=ETH, numderive=3), 'btc-test': derive_wallets(mnemonic, coin=BTCTEST, numderive=3)}


# %%
# child account selection with dictionary 
eth_key = coins['eth'][0]['privkey']
btc_key = coins['btc-test'][0]['privkey']

# %%
# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    global account
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    


# %%
eth_acc = btc_acc = priv_key_to_account(ETH, eth_key)

# %%
btc_acc = priv_key_to_account(BTCTEST, btc_key)

# %%
# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    global tx_data
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value":amount}
        )
        tx_data={
            "from": account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransaction(account.address),
        }
        return tx_data
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])
        

# %%
# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    if coin == ETH:
        tx = create_tx(coin, account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, recipient, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)



# %%
#check balances
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545/0xeb9cdd720fb80d2ab2963f5598bd756a3ea052071ef0f0b7726a0c861112790f"))
w3.eth.getBalance("0x907b31E07E8D9c5504Cc1bf28C27Ec28bF8BE111")
