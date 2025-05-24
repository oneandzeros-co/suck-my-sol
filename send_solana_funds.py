from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import transfer_checked, create_associated_token_account, TransferCheckedParams
from solana.rpc.types import TokenAccountOpts, TxOpts
import base58
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('solana_transfers.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Interval (in seconds) between balance scans. Override with SCAN_INTERVAL env var.
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "5"))

def get_token_balance(client, token_address, wallet_address):
    try:
        # Define filter options for the specified mint
        opts = TokenAccountOpts(mint=token_address)

        # Fetch token accounts owned by the wallet corresponding to the mint
        token_accounts = client.get_token_accounts_by_owner(wallet_address, opts)

        # If no token accounts found, return zero balance
        if not token_accounts.value:
            return 0

        # Fetch balance of first token account
        balance_resp = client.get_token_account_balance(token_accounts.value[0].pubkey)
        return int(balance_resp.value.amount)
    except Exception as e:
        logging.error(f"Error getting token balance: {str(e)}")
        return 0

def send_all_funds():
    # Initialize Solana client (using public RPC endpoint)
    client = Client("https://api.mainnet-beta.solana.com")
    
    # Load your private key from environment variable
    private_key = os.getenv('SOLANA_PRIVATE_KEY')
    if not private_key:
        raise ValueError("Please set your SOLANA_PRIVATE_KEY in .env file")
    
    # Convert private key to bytes and create keypair
    private_key_bytes = base58.b58decode(private_key)
    sender_keypair = Keypair.from_bytes(private_key_bytes)
    
    # Destination address you want to safley send
    destination_address = Pubkey.from_string("7R28vXEVvp3qrKV5Ba7Ba9UbKsjBkrxNc5qDz33E8b51")
    
    # SPL Token address you created
    spl_token_address = Pubkey.from_string("CwbpyHPZJ133hgWQvd1hZA4ZxjQu3mL7WRxEhmqQYkCB")
    
    try:
        # Get SOL balance
        sol_balance = client.get_balance(sender_keypair.pubkey())
        logging.info(f"Current SOL balance: {sol_balance.value / 1e9} SOL")
        
        # Calculate minimum SOL to keep for gas (0.000005 SOL per transaction)
        min_sol_keep = 0.000005 * 1e9  # Convert to lamports
        
        # Send SOL if available
        if sol_balance.value > min_sol_keep:
            transfer_amount = sol_balance.value - min_sol_keep
            
            # Get recent blockhash
            recent_blockhash = client.get_latest_blockhash()
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=sender_keypair.pubkey(),
                    to_pubkey=destination_address,
                    lamports=int(transfer_amount)  # Ensure lamports is an integer
                )
            )
            
            # Build transaction
            transaction = Transaction(
                fee_payer=sender_keypair.pubkey(),
                recent_blockhash=recent_blockhash.value.blockhash
            )
            transaction.add(transfer_ix)
            
            # Send transaction
            result = client.send_transaction(
                transaction,
                sender_keypair,
                opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed)
            )
            
            logging.info(f"SOL transfer sent! Amount: {transfer_amount / 1e9} SOL")
            logging.info(f"Transaction signature: {result.value}")
        
        # Send SPL tokens if available
        if get_token_balance(client, spl_token_address, sender_keypair.pubkey()) > 0:
            # Get token accounts
            source_token_accounts = client.get_token_accounts_by_owner(
                sender_keypair.pubkey(),
                TokenAccountOpts(mint=spl_token_address)
            )
            
            if not source_token_accounts.value:
                logging.error("No source token account found")
                return
                
            dest_token_accounts = client.get_token_accounts_by_owner(
                destination_address,
                TokenAccountOpts(mint=spl_token_address)
            )
            
            if not dest_token_accounts.value:
                # Create associated token account for destination
                create_ata_ix = create_associated_token_account(
                    payer=sender_keypair.pubkey(),
                    owner=destination_address,
                    mint=spl_token_address
                )
                
                # Get recent blockhash for ATA creation
                recent_blockhash = client.get_latest_blockhash()
                
                # Build transaction for ATA creation
                transaction = Transaction(
                    fee_payer=sender_keypair.pubkey(),
                    recent_blockhash=recent_blockhash.value.blockhash
                )
                transaction.add(create_ata_ix)
                transaction.sign(sender_keypair)
                
                # Send ATA creation transaction
                result = client.send_transaction(
                    transaction,
                    sender_keypair,
                    opts=TxOpts(skip_confirmation=True, preflight_commitment=Confirmed)
                )
                
                # Get the newly created token account
                dest_token_accounts = client.get_token_accounts_by_owner(
                    destination_address,
                    TokenAccountOpts(mint=spl_token_address)
                )
            
            # Amount to transfer
            spl_balance = get_token_balance(client, spl_token_address, sender_keypair.pubkey())

            # Create transfer instruction
            transfer_ix = transfer_checked(
                TransferCheckedParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=source_token_accounts.value[0].pubkey,
                    mint=spl_token_address,
                    dest=dest_token_accounts.value[0].pubkey,
                    owner=sender_keypair.pubkey(),
                    amount=spl_balance,
                    decimals=9,
                    signers=[]
                )
            )
            
            # Get recent blockhash for transfer
            recent_blockhash = client.get_latest_blockhash()
            
            # Build transaction
            transaction = Transaction(
                fee_payer=sender_keypair.pubkey(),
                recent_blockhash=recent_blockhash.value.blockhash
            )
            transaction.add(transfer_ix)
            transaction.sign(sender_keypair)
            
            # Send transfer transaction
            result = client.send_transaction(
                transaction,
                sender_keypair,
                opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed)
            )
            
            logging.info(f"SPL token transfer sent! Amount: {spl_balance}")
            logging.info(f"Transaction signature: {result.value}")
        
        logging.info("All transfers completed successfully")
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

def main():
    logging.info("Starting Solana auto-sweeper … (scan interval: %s s)", SCAN_INTERVAL)
    while True:
        try:
            send_all_funds()
        except Exception as loop_err:
            logging.error("Unhandled error in sweeper loop: %s", loop_err)
        # Wait before next scan
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main() 