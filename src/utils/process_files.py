import pandas as pd
import os



class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df_users = None
        self.df_transactions = None
        self.df_mapped_users_transaction = None

    def read_files(self):
        user_path = os.path.join(self.file_path, "users_data.csv")
        transaction_path = os.path.join(self.file_path, "transactions_data.csv")

        self.df_users = pd.read_csv(user_path)
        self.df_transactions = pd.read_csv(transaction_path)
        self.df_mapped_users_transaction = self.df_users.merge(
            self.df_transactions, how='inner', left_on='id', right_on='client_id'
        )
        return self.df_users, self.df_transactions, self.df_mapped_users_transaction



class DataPreprocessor:
    @staticmethod
    def preprocess(df_users, df_transactions, df_mapped):
        df_transactions['amount'] = df_transactions['amount'].str.replace('$', '').astype(float)
        df_transactions['date'] = pd.to_datetime(df_transactions['date'])
        df_transactions['quarter'] = df_transactions['date'].dt.to_period('Q')
        df_transactions["spending_category"] = pd.qcut(df_transactions["amount"], q=3, labels=['Low', 'Medium', 'High'])


        for col in ["per_capita_income", "yearly_income", "amount", "total_debt"]:
            df_mapped[col] = df_mapped[col].str.replace('$', '').astype(float)
        

        return df_users, df_transactions, df_mapped




class UserInsights:
    def __init__(self, df_users, df_transactions, df_mapped_users_transaction, client_id):
        self.df_users = df_users
        self.df_transactions = df_transactions
        self.df_mapped_users_transaction = df_mapped_users_transaction
        self.client_id = client_id
        self.user_transactions = self._filter_user_transactions()


    def get_top_n_transactions_by_quarter(df, n=3):
        """
        Returns the top N transactions for each quarter.
        """
        top_n_by_quarter = {}
        for quarter in ["2019Q1", "2019Q2", "2019Q3", "2019Q4"]:
            top_n = df[df["quarter"] == quarter].nlargest(n, "count_trnsxn")
            top_n_by_quarter[quarter] = top_n
        combined_df = pd.concat(top_n_by_quarter.values(), keys=top_n_by_quarter.keys())
        combined_df.reset_index(level=0, inplace=True)
        del combined_df["level_0"]

        return combined_df
    

    def _filter_user_transactions(self):
        """
        filter users based on input client id
        """
        return self.df_transactions[self.df_transactions["client_id"] == self.client_id]


    def get_aggregate_metrics(self):
        """
        get general aggregate metrics for given client
        """
        sum_amount = self.user_transactions['amount'].sum()
        count_amount_num = self.user_transactions['amount'].count()
        avg_amount = self.user_transactions['amount'].mean()

        return sum_amount, count_amount_num, avg_amount

    def get_spending_by_payment_mode(self):
        """
        get the payment mode distribution for given client
        """
        mode_spent = self.user_transactions.groupby("use_chip")["amount"].sum().reset_index(name="amount_spent")
        mode_count = self.user_transactions.groupby("use_chip")["use_chip"].count().reset_index(name="Num_of_transaction")
        return mode_spent, mode_count

    def get_top_5_merchants(self):
        """
        get to N merchants for given client
        """
        return self.user_transactions.groupby("merchant_category")["amount"].sum().nlargest(3).reset_index()

    def get_quarterly_spending(self):
        """
        get quarter wise total spending for given client
        """
        return self.user_transactions.groupby("quarter")["amount"].sum().reset_index(name="Amount_Spent")


    def get_top_3_transactions_by_quarter(self):
        """
        get top N transactions of user for every quarter
        """
        trnx_qtr_merchant = self.user_transactions.groupby(["quarter", "merchant_category"]).size().reset_index(name="count_trnsxn")
        return trnx_qtr_merchant.groupby("quarter").apply(lambda x: x.nlargest(3, "count_trnsxn")).reset_index(drop=True)

    def get_top_5_store_visits(self):
        """
        get top N specific merchant visits for given client
        """
        store_visits = self.user_transactions.groupby("merchant_category")["merchant_id"].count().reset_index(name="count_visits")
        return store_visits.nlargest(3, "count_visits")

    def get_spending_summary_by_category(self):
        """
        get spending category for given client, i.e High-Low-Medium spending capacity
        """
        spending_category = self.user_transactions.groupby(["spending_category", "merchant_category"]).size().reset_index(name="num_trnsxns")
        return spending_category.groupby("spending_category")["num_trnsxns"].sum().reset_index(name="count_trxn")

    def generate_insights(self):
        """
        Aggregate all above methods to get the outputs 
        """
        sum_amount_spent, count_amount_spent, avg_amount_spent = self.get_aggregate_metrics()
        mode_spent, mode_count = self.get_spending_by_payment_mode()
        top_5_merchants = self.get_top_5_merchants()
        quarterly_spent = self.get_quarterly_spending()
        top_3_trnxn_qtr = self.get_top_3_transactions_by_quarter()
        top_5_store_visits = self.get_top_5_store_visits()
        spending_summary = self.get_spending_summary_by_category()

        sum_amount_spent = str(sum_amount_spent)
        count_amount_spent = str(count_amount_spent)
        avg_amount_spent = str(avg_amount_spent)
        mode_spent = mode_spent.to_dict(orient="records")
        mode_count = mode_count.to_dict(orient="records")
        top_5_merchants = top_5_merchants.to_dict(orient="records")

        quarterly_spent["quarter"] = quarterly_spent["quarter"].astype(str)
        quarterly_spent = quarterly_spent.to_dict(orient="records")

        top_3_trnxn_qtr["quarter"] = top_3_trnxn_qtr["quarter"].astype(str)
        top_3_trnxn_qtr = top_3_trnxn_qtr.to_dict(orient="records")

        top_5_store_visits = top_5_store_visits.to_dict(orient="records")
        spending_summary = spending_summary.to_dict(orient="records")
        
        
        return ({
            "sum_amount_spent": sum_amount_spent,
            "count_amount_spent": count_amount_spent,
            "avg_amount_spent": avg_amount_spent,
            "mode_spent": mode_spent,
            "mode_count":mode_count,
            "top_5_merchants": top_5_merchants,
            "quarterly_spent": quarterly_spent,
            "top_3_trnxn_qtr": top_3_trnxn_qtr,
            "top_5_store_visits":top_5_store_visits,
            "spending_summary": spending_summary
        })
