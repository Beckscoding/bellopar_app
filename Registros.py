import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Registro de vendas e pagamentos",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

col1, col2 = st.columns([1, 5])
col1.image("Logo_bellopar.png")
col2.header("Registro de vendas e pagamentos")

st.divider()


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Registros", usecols=list(range(10)), ttl=1)
existing_data = existing_data.dropna(how="all")

# Fetch clients' data from "Clientes" sheet
clients_data = conn.read(worksheet="Clientes", usecols=["Nome"], ttl=1)
clients_data = clients_data.dropna(how="all")  # Drop empty rows

# Get the list of client names
client_names = clients_data["Nome"].tolist()  # Convert to a list

# Fetch pagamentos' data from "Pagamentos" sheet
payment_data = conn.read(worksheet="Pagamentos", usecols=["Opções"], ttl=1)
payment_data = payment_data.dropna(how="all")  # Drop empty rows

# Get the list of client names
payment_options = payment_data["Opções"].tolist()  # Convert to a list

# Check if the ID column exists, and find the max ID
if "ID_reg" in existing_data.columns:
    last_id = existing_data["ID_reg"].max()  # Get the highest ID
else:
    # If no 'ID' column exists yet, initialize the ID system
    last_id = 0
    existing_data["ID_reg"] = []

name = st.selectbox(label="Nome do Cliente", options=client_names, index=None)

# Filter info on name
filtered_data_name = existing_data[existing_data["Nome"] == name]
sum_client = filtered_data_name["Valor"].sum()

# Sum the total for column Valor filtered by Venda in column Tipo
sum_venda = filtered_data_name[filtered_data_name["Tipo"] == "Venda"]["Valor"].sum()
filtered_data_name_sorted = filtered_data_name.sort_values(by="ID_reg", ascending=False)

# include an if condition in case name is not empty
if name:    
    st.dataframe(filtered_data_name_sorted[["ID_reg", "Data", "Nome", "Produto", "Valor", "Vencimento", "Tipo", "Método Pagamento", "Observações"]], hide_index=True, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric(label="Valor atual pendente de pagamento:", value=f"R${sum_client}")
    col2.metric(label="Total faturado:", value=f"R${sum_venda}")
else:
    st.markdown('<p style="color:red; font-style:italic;">Selecione um cliente.</p>', unsafe_allow_html=True)


# Create a form with with the following imputs: name, product, price, date, operation type
st.write("Registre abaixo uma nova operação de venda ou pagamento para este cliente.")
with st.form(key="my_form", clear_on_submit=True):

    today = date.today()
    data_formatada = today.strftime("%d/%m/%Y")        
    
    col1, col2 = st.columns([1, 2])
    col1.write(data_formatada)
    product = col2.text_input(label="Produto")
    price = col1.number_input(label="Valor", step=10.00)
    due_date = col2.date_input(label="Data de Vencimento/Pagamento", format="DD/MM/YYYY")
    operation_type = col1.radio(label="Tipo de operação", options=["Venda", "Pagamento"], horizontal=True)
    payment_selected = col2.selectbox(label="Método de pagamento", options=payment_options, index=None, placeholder="Escolha uma opção")
    obs = col1.text_input(label="Observações")


    # Create a button to submit the form
    submit = st.form_submit_button(label="Submit")

    if operation_type == "Pagamento":
        price = -price
    else:
        price = price

    # If the form is submitted
    if submit:
        # Increment the ID for the new row
        new_id = last_id + 1

        # Create a new row with the form data
        new_row = pd.DataFrame(
            {   "ID_reg": [new_id],
                "Data":[data_formatada],
                "Nome": [name],
                "Produto": [product],
                "Valor": [price],
                "Vencimento": [due_date],
                "Tipo": [operation_type],
                "Método Pagamento": [payment_selected],
                "Observações": [obs],
            }
        )

        # Append the new row to the existing data
        existing_data = pd.concat([existing_data, new_row], ignore_index=True)

        # Write the updated data to the Google Sheets
        conn.update(worksheet="Registros", data=existing_data)

        st.rerun()

# Deletion section
with st.sidebar:
    

    st.write("Exclua uma operação pelo ID:")
    with st.form(key="exclude-form", clear_on_submit=True):
        
        
        delete_id = st.number_input(label="ID_reg para excluir", step=1, min_value=0)

        submit_exclude = st.form_submit_button(label="Excluir")

        # Botão para deletar a linha com o ID informado
        if submit_exclude:
            if delete_id in existing_data["ID_reg"].values:
                # Filtrar a linha com o ID correspondente
                updated_data = existing_data[existing_data["ID_reg"] != delete_id]
                
                # Atualizar a planilha com os dados filtrados
                conn.update(worksheet="Registros", data=updated_data)
                
                st.success(f"Registro com ID {delete_id} excluído com sucesso!")
                st.rerun()
            else:
                st.error(f"ID {delete_id} não encontrado.")

       

        


