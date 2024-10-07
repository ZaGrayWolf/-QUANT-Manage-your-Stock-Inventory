import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def read_stocks():
    try:
        n_stocks = int(input().strip())
        stocks = {}
        for _ in range(n_stocks):
            stock_id, price = input().strip().split(',')
            stocks[stock_id] = float(price)
        return stocks
    except Exception as e:
        logging.error("Error reading stocks: %s", e)
        raise

def read_accounts():
    try:
        n_accounts = int(input().strip())
        accounts = {}
        for _ in range(n_accounts):
            account_id, account_type, parent_account = input().strip().split(',')
            accounts[account_id] = {
                'type': account_type,
                'parent': parent_account,
                'balance': 0,
                'demand': 0
            }
        return accounts
    except Exception as e:
        logging.error("Error reading accounts: %s", e)
        raise

def read_eligible_accounts(stocks):
    try:
        n_eligible_accounts = int(input().strip())
        eligible_accounts = {stock_id: [] for stock_id in stocks.keys()}
        for _ in range(n_eligible_accounts):
            stock_id, account_id = input().strip().split(',')
            eligible_accounts[stock_id].append(account_id)
        return eligible_accounts
    except Exception as e:
        logging.error("Error reading eligible accounts: %s", e)
        raise

def read_eligible_flows(stocks):
    try:
        n_flows = int(input().strip())
        eligible_flows = {stock_id: [] for stock_id in stocks.keys()}
        for _ in range(n_flows):
            stock_id, source_account_id, destination_account_id = input().strip().split(',')
            eligible_flows[stock_id].append((source_account_id, destination_account_id))
        return eligible_flows
    except Exception as e:
        logging.error("Error reading eligible flows: %s", e)
        raise

def read_balances(accounts):
    try:
        n_balances = int(input().strip())
        for _ in range(n_balances):
            stock_id, account_id, quantity = input().strip().split(',')
            quantity = int(quantity)
            if quantity > 0:
                accounts[account_id]['balance'] += quantity
            else:
                accounts[account_id]['demand'] += -quantity
    except Exception as e:
        logging.error("Error reading balances: %s", e)
        raise

def process_transactions(stocks, accounts, eligible_accounts, eligible_flows):
    transactions = []

    for stock_id in stocks.keys():
        excess_accounts = [acc for acc in eligible_accounts[stock_id] if accounts[acc]['balance'] > 0]
        demand_accounts = [acc for acc in eligible_accounts[stock_id] if accounts[acc]['demand'] > 0]

        fulfilled_demands = set()

        for demand_account in demand_accounts:
            required_quantity = accounts[demand_account]['demand']
            if demand_account in fulfilled_demands:
                continue

            for excess_account in excess_accounts:
                if required_quantity <= 0:
                    break

                if (excess_account, demand_account) in eligible_flows[stock_id]:
                    move_quantity = min(required_quantity, accounts[excess_account]['balance'])
                    if move_quantity > 0:
                        transactions.append((stock_id, excess_account, demand_account, move_quantity))
                        accounts[excess_account]['balance'] -= move_quantity
                        accounts[demand_account]['demand'] -= move_quantity
                        required_quantity -= move_quantity
                        fulfilled_demands.add(demand_account)

        for excess_account in excess_accounts:
            remaining_stock = accounts[excess_account]['balance']
            if remaining_stock > 0:
                triparty_accounts = [acc for acc in eligible_accounts[stock_id] if accounts[acc]['type'] == 'TRIPARTY']
                for triparty_account in triparty_accounts:
                    if (excess_account, triparty_account) in eligible_flows[stock_id]:
                        move_quantity = min(remaining_stock, 5)
                        transactions.append((stock_id, excess_account, triparty_account, move_quantity))
                        accounts[excess_account]['balance'] -= move_quantity
                        remaining_stock -= move_quantity
                        if remaining_stock <= 0:
                            break
                    else:
                        for intermediate_account in eligible_accounts[stock_id]:
                            if intermediate_account != excess_account and intermediate_account != triparty_account:
                                if (excess_account, intermediate_account) in eligible_flows[stock_id] and (intermediate_account, triparty_account) in eligible_flows[stock_id]:
                                    move_quantity = min(remaining_stock, 5)
                                    transactions.append((stock_id, excess_account, intermediate_account, move_quantity))
                                    accounts[excess_account]['balance'] -= move_quantity
                                    remaining_stock -= move_quantity
                                    transactions.append((stock_id, intermediate_account, triparty_account, move_quantity))
                                    if remaining_stock <= 0:
                                        break

    transactions.sort(key=lambda x: (x[0], x[1], x[2]))

    return transactions

def main():
    try:
        stocks = read_stocks()
        accounts = read_accounts()
        eligible_accounts = read_eligible_accounts(stocks)
        eligible_flows = read_eligible_flows(stocks)
        read_balances(accounts)

        transactions = process_transactions(stocks, accounts, eligible_accounts, eligible_flows)

        if transactions:
            for transaction in transactions:
                print(f"{transaction[0]},{transaction[1]},{transaction[2]},{transaction[3]}")
        else:
            print("\nNo transactions were made.")
    
    except Exception as e:
        logging.error("An error occurred in the main function: %s", e)

if __name__ == "__main__":
    main()