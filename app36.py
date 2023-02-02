import streamlit as st
import pandas as pd
import transformers
from simple_salesforce import Salesforce

sf = None

@st.cache
def login():
    global sf
    username = st.text_input("Username:")
    password = st.text_input("Password:", type='password')
    security_token = st.text_input("Security Token:")
    sf = Salesforce(username=username, password=password, security_token=security_token)
    if sf:
        st.success("Login successful")
    else:
        st.error("Login failed")

def leads():
    if sf:
        query = "SELECT Name, Company, Email, Phone FROM Lead"
        results = sf.query(query)
        leads_df = pd.DataFrame(results['records'])
        st.dataframe(leads_df)
        
        def load_data():
            data = leads_df
            # Preprocessing steps (cleaning, handling missing values, formatting for BERT input)
            return data

        df = load_data()

        # Load BERT Model
        model = transformers.BertModel.from_pretrained('bert-base-uncased')
        tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased')

        # Tokenize Data
        input_ids = df['text'].apply(lambda x: tokenizer.encode(x, return_tensors='pt')).tolist()

        # Pass Tokenized Data Through BERT Model
        with torch.no_grad():
            last_hidden_states = [model(input_ids[i])[0] for i in range(len(input_ids))]

        # Train Classifier on Embeddings
        clf = LogisticRegression()
        clf.fit(last_hidden_states, df['label'])

        # Rank Leads Based on Likelihood to Close
        df['prediction'] = clf.predict_proba(last_hidden_states)[:,1]
        df = df.sort_values(by='prediction', ascending=False)

        # Display Graph
        st.bar_chart(df, x='lead_id', y='prediction')
    else:
        st.warning("Please log in to Salesforce")

def accounts():
    if sf:
        query = "SELECT Name, Industry, Phone, Type FROM Account"
        results = sf.query(query)
        accounts_df = pd.DataFrame(results['records'])
        st.dataframe(accounts_df)
    else:
        st.warning("Please log in to Salesforce")

def contacts():
    if sf:
        query = "SELECT FirstName, LastName, Email, Phone FROM Contact"
        results = sf.query(query)
        contacts_df = pd.DataFrame(results['records'])
        st.dataframe(contacts_df)
    else:
        st.warning("Please log in to Salesforce")

def opportunities():
    if sf:
        query = "SELECT Name, StageName, Amount, CloseDate FROM Opportunity"
        results = sf.query(query)
        opportunities_df = pd.DataFrame(results['records'])

        st.write("Opportunities Data")
        st.dataframe(opportunities_df)

        # Add a bar chart of the Opportunity amounts
        st.write("Opportunities Amounts")
        st.bar_chart(opportunities_df["Amount"])
    else:
        st.warning("Please log in to Salesforce")

def quotes():
    if sf:
        query = "SELECT Name, ExpirationDate, TotalAmount FROM Quote"
        results = sf.query(query)
        quotes_df = pd.DataFrame(results['records'])
        st.dataframe(quotes_df)
    else:
        st.warning("Please log in to Salesforce")

def quote_editor():
    if sf:
        opportunity_id = st.text_input("Opportunity ID:")
        query = f"SELECT Name, ProductCode, Description FROM OpportunityLineItem WHERE OpportunityId='{opportunity_id}'"
        results = sf.query(query)
        quote_items_df = pd.DataFrame(results['records'])
        st.write("Quote Editor")
        st.dataframe(quote_items_df)
        product_code = st.text_input("Product Code")
        description = st.text_input("Description")
        price = st.text_input("Price")
        quantity = st.text_input("Quantity")
        item = {
            "OpportunityId": opportunity_id,
            "PricebookEntryId": product_code,
            "Quantity": quantity,
            "UnitPrice": price
        }
        sf.OpportunityLineItem.create(item)
        st.success("Quote item added")
    else:
        st.warning("Please log in to Salesforce")

def products():
    if sf:
        query = "SELECT Name, ProductCode, Description, IsActive FROM Product2"
        results = sf.query(query)
        products_df = pd.DataFrame(results['records'])
        st.dataframe(products_df)
    else:
        st.warning("Please log in to Salesforce")

def dashboards():
    if sf:
        st.write("Dashboards information")
    else:
        st.warning("Please log in to Salesforce")

def reports():
    if sf:
        st.write("Reports information")
    else:
        st.warning("Please log in to Salesforce")

def quote_templates():
    st.write("Quote Templates")
    templates = sf.query("SELECT Id, Name FROM QuoteTemplate")
    templates_df = pd.DataFrame(templates["records"])
    st.write("List of Quote Templates")
    st.write(templates_df)

def more():
    st.write("More")
    st.write("You can add more pages here")

def home():
    option = st.sidebar.selectbox("Select a Tab", ["Leads", "Accounts", "Contacts", "Opportunities", "Quotes", "Quote Editor", "Products", "Dashboards", "Reports", "Quote Templates", "More"])
    if option == "Leads":
        leads()
    elif option == "Accounts":
        accounts()
    elif option == "Contacts":
        contacts()
    elif option == "Opportunities":
        opportunities()
    elif option == "Quotes":
        quotes()
    elif option == "Quote Editor":
        quote_editor()
    elif option == "Products":
        products()
    elif option == "Dashboards":
        dashboards()
    elif option == "Reports":
        reports()
    elif option == "Quote Templates":
        quote_templates()
    elif option == "More":
        more()

def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    security_token = st.text_input("Security Token")
    if username and password and security_token:
        global sf
        sf = Salesforce(username=username, password=password, security_token=security_token)
        st.success("Login Successful")
        home()

if __name__ == "__main__":
    st.title("Salesforce Login")
    login()