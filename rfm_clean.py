# import necessary packages
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# read dataset
df = pd.read_csv('~./data.csv')
df.head(10)

# removing na values and duplicates
df = df.dropna()
df = df.drop_duplicates()

# converting InvoiceDate column to pandas datetime format
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# sorting records by InvoiceDate in ascending order
df = df.sort_values(by='InvoiceDate')

# removing trailing '.0' from CustomerID
df['CustomerID'] = df['CustomerID'].apply(lambda x: str(x)[:-2])

# add column Amount = quantity * unit_price
df['Amount'] = round(df['Quantity']*df['UnitPrice'],2)

# taking only necessary columns and aggregating by 'CustomerID'
df = df[['CustomerID','InvoiceDate','Amount']]

rfm_df = df.groupby('CustomerID').agg(list).reset_index()
rfm_df.head(5)

# find last dates for every customer
rfm_df['last_dates'] = rfm_df['InvoiceDate'].apply(lambda x: x[-1])

# find latest date of purchase
latest_date = df['InvoiceDate'].max()

# find recency by subtracting last_dates from maximum date
rfm_df['recency'] = rfm_df['last_dates'].apply(lambda x: (latest_date- x).days)

# find frequency by counting no. of transactions per customer
rfm_df['frequency'] = rfm_df['Amount'].apply(len)

# find monetary value by summing up transaction amounts per customer
rfm_df['monetary_value'] = rfm_df['Amount'].apply(sum)\

# take only necessary columns
rfm_df=rfm_df[['CustomerID','recency','frequency','monetary_value']]

# binning recency col
rfm_df['r'] = pd.qcut(rfm_df['recency'].rank(method='first'),5,labels=[5,4,3,2,1]).tolist()

# binning frequency col
rfm_df['f'] = pd.qcut(rfm_df['frequency'].rank(method='first'),5,labels=[1,2,3,4,5]).tolist()

# binning monetary_value col
rfm_df['m'] = pd.qcut(rfm_df['monetary_value'].rank(method='first'),5,labels=[1,2,3,4,5]).tolist()

# concatenating r,f,m scores together
rfm_df['rfm_score'] = rfm_df['r'].apply(str) + rfm_df['f'].apply(str) + rfm_df['m'].apply(str)

# function to find customer segments
def find_segments(df, customer_id):
    classes = []
    for row in df.iterrows():
        if (row[1]['r'] in [4,5]) & (row[1]['f'] in [4,5]) & (row[1]['m'] in [4,5]):
            classes.append({row[1][customer_id]:'Champions'})
        elif (row[1]['r'] in [4,5]) & (row[1]['f'] in [1,2]) & (row[1]['m'] in [3,4,5]):
            classes.append({row[1][customer_id]:'Promising'})
        elif (row[1]['r'] in [3,4,5]) & (row[1]['f'] in [3,4,5]) & (row[1]['m'] in [3,4,5]):
            classes.append({row[1][customer_id]:'Loyal Accounts'})
        elif (row[1]['r'] in [3,4,5]) & (row[1]['f'] in [2,3]) & (row[1]['m'] in [2,3,4]):
            classes.append({row[1][customer_id]:'Potential Loyalist'})
        elif (row[1]['r'] in [3,4,5]) & (row[1]['f'] in [1,2,3,4,5]) & (row[1]['m'] in [1,2]):
            classes.append({row[1][customer_id]:'Low Spenders'})
        elif (row[1]['r'] in [2,3]) & (row[1]['f'] in [1,2]) & (row[1]['m'] in [4,5]):
            classes.append({row[1][customer_id]:'Need Attention'})
        elif (row[1]['r'] in [2,3]) & (row[1]['f'] in [1,2]) & (row[1]['m'] in [1,2,3]):
            classes.append({row[1][customer_id]:"About to Sleep"})
        elif (row[1]['r'] in [1,2]) & (row[1]['f'] in [1,2,3,4,5]) & (row[1]['m'] in [3,4,5]):
            classes.append({row[1][customer_id]:'At Risk'})
        elif (row[1]['r'] in [1,2]) & (row[1]['f'] in [1,2,3,4,5]) & (row[1]['m'] in [1,2]):
            classes.append({row[1][customer_id]:"Lost"})
        else:
            classes.append({0:[row[1]['r'],row[1]['f'],row[1]['m']]})
    accs = [list(i.keys())[0] for i in classes]
    segments = [list(i.values())[0] for i in classes]
    df['segment'] = df[customer_id].map(dict(zip(accs,segments)))
    return df

# find segments
rfm_df = find_segments(rfm_df, 'CustomerID')
rfm_df.head(10)
