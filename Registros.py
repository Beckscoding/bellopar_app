import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime

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

# From filtered_data_name  get the highest date from the column "Vencimento"
filtered_data_name_sorted["Venc_Numb"] = filtered_data_name_sorted['Vencimento'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%Y%m%d"))
due_date_max = filtered_data_name_sorted["Venc_Numb"].max()


date_today = date.today()
date_today = date_today.strftime("%Y%m%d")


# include an if condition in case name is not empty
if name:    
    st.dataframe(filtered_data_name_sorted[["ID_reg", "Data", "Nome", "Produto", "Valor", "Vencimento", "Tipo", "Método Pagamento", "Observações"]], hide_index=True, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Valor atual pendente de pagamento:", value=f"R${sum_client:.2f}")
    
    if sum_client > 0:
        if due_date_max < date_today:
            col2.image("red_light.png")
            
        else:
            col2.image("yellow_light.png")
            
    else:
        col2.image("green_light.png")
        
    col3.metric(label="Total já vendido para este cliente:", value=f"R${sum_venda:.2f}")
else:
    st.markdown('<p style="color:red; font-style:italic;">Selecione um cliente.</p>', unsafe_allow_html=True)

today = date.today()
data_formatada = today.strftime("%d/%m/%Y")    

operation_type = st.radio(label="Escolha o tipo de operação que deseja registrar!", options=["Venda", "Pagamento"], horizontal=True, index=None)

# If operation type equals "Venda" create a form
if operation_type == "Venda":
    st.write("Registre abaixo uma nova operação de venda para este cliente.")
    with st.form(key="my_form", clear_on_submit=True):
            
        product = st.text_input(label="Produtos vendidos")
        col1, col2, col3, col4 = st.columns(4)
        parcela1 = col1.number_input(label="Parcela 1", step=10.00)
        parcela2 = col1.number_input(label="Parcela 2", step=10.00)
        parcela3 = col1.number_input(label="Parcela 3", step=10.00)
        parcela4 = col3.number_input(label="Parcela 4", step=10.00)
        parcela5 = col3.number_input(label="Parcela 5", step=10.00)
        parcela6 = col3.number_input(label="Parcela 6", step=10.00)
        due_date1 = col2.date_input(label="Data de Vencimento 1", format="DD/MM/YYYY", value=None)
        due_date2 = col2.date_input(label="Data de Vencimento 2", format="DD/MM/YYYY", value=None)
        due_date3 = col2.date_input(label="Data de Vencimento 3", format="DD/MM/YYYY", value=None)
        due_date4 = col4.date_input(label="Data de Vencimento 4", format="DD/MM/YYYY", value=None)
        due_date5 = col4.date_input(label="Data de Vencimento 5", format="DD/MM/YYYY", value=None)
        due_date6 = col4.date_input(label="Data de Vencimento 6", format="DD/MM/YYYY", value=None)
        obs = st.text_input(label="Observações")

        # Create a button to submit the form
        submit_venda = st.form_submit_button(label="Submit")
        if submit_venda:
        # Increment the ID for the new row
            new_id = last_id + 1

                # Create a new row with the form data
            if parcela1 > 0:
                new_row1 = pd.DataFrame(
                    {   "ID_reg": [new_id],
                        "Data":[data_formatada],
                        "Nome": [name],
                        "Produto": [product],
                        "Valor": [parcela1],
                        "Vencimento": [due_date1],
                        "Tipo": [operation_type],
                        "Observações": [obs],
                    }
                )
            if parcela2 > 0:
                new_row2 = pd.DataFrame(
                    {   "ID_reg": [new_id],
                        "Data":[data_formatada],
                        "Nome": [name],
                        "Produto": [product],
                        "Valor": [parcela2],
                        "Vencimento": [due_date2],
                        "Tipo": [operation_type],
                        "Observações": [obs],
                    }
                )
            if parcela3 > 0:
                new_row3 = pd.DataFrame(
                   {   "ID_reg": [new_id],
                        "Data":[data_formatada],
                        "Nome": [name],
                        "Produto": [product],
                        "Valor": [parcela3],
                        "Vencimento": [due_date3],
                        "Tipo": [operation_type],
                        "Observações": [obs],
                    }
                )

            if parcela4 > 0:
                new_row4 = pd.DataFrame(
                   {   "ID_reg": [new_id],
                        "Data":[data_formatada],
                        "Nome": [name],
                        "Produto": [product],
                        "Valor": [parcela3],
                        "Vencimento": [due_date4],
                        "Tipo": [operation_type],
                        "Observações": [obs],
                    }
                )

            if parcela5 > 0:
                new_row5 = pd.DataFrame(
                   {   "ID_reg": [new_id],
                        "Data":[data_formatada],
                        "Nome": [name],
                        "Produto": [product],
                        "Valor": [parcela3],
                        "Vencimento": [due_date5],
                        "Tipo": [operation_type],
                        "Observações": [obs],
                    }
                )

            if parcela6 > 0:
                new_row6 = pd.DataFrame(
                   {   "ID_reg": [new_id],
                        "Data":[data_formatada],
                        "Nome": [name],
                        "Produto": [product],
                        "Valor": [parcela3],
                        "Vencimento": [due_date6],
                        "Tipo": [operation_type],
                        "Observações": [obs],
                    }
                )

            # Append the new row to the existing data
            if parcela6 > 0:
                existing_data = pd.concat([existing_data, new_row1, new_row2, new_row3, new_row4, new_row5, new_row6], ignore_index=True)
            elif parcela5 > 0:
                existing_data = pd.concat([existing_data, new_row1, new_row2, new_row3, new_row4, new_row5], ignore_index=True)
            elif parcela4 > 0:
                existing_data = pd.concat([existing_data, new_row1, new_row2, new_row3, new_row4], ignore_index=True)
            elif parcela3 > 0:
                existing_data = pd.concat([existing_data, new_row1, new_row2, new_row3], ignore_index=True)
            elif parcela2 > 0:
                existing_data = pd.concat([existing_data, new_row1, new_row2], ignore_index=True)
            else:
                existing_data = pd.concat([existing_data, new_row1], ignore_index=True)

            # Write the updated data to the Google Sheets
            conn.update(worksheet="Registros", data=existing_data)
            st.rerun()
            

        # Append the new row to the existing data
elif operation_type == "Pagamento":
    st.write("Registre abaixo uma nova operação de pagamento para este cliente.")
    with st.form(key="my_form", clear_on_submit=True):
        
        col1, col2 = st.columns([1, 2])
        value_paid = col1.number_input(label="Valor Pago", step=10.00)
        date_paid = col2.date_input(label="Data do Pagamento", format="DD/MM/YYYY", value=None)
        payment_selected = col2.selectbox(label="Como foi realizado o pagamento?", options=payment_options, index=None, placeholder="Escolha uma opção")
        obs = col1.text_input(label="Observações")

         # Create a button to submit the form
        submit_pagamento = st.form_submit_button(label="Submit")
        if submit_pagamento:
            # Increment the ID for the new row
            new_id = last_id + 1
            value_paid = -1 * value_paid

                # Create a new row with the form data
            new_row = pd.DataFrame(
                {   "ID_reg": [new_id],
                    "Data":[data_formatada],
                    "Nome": [name],
                    "Produto": "Pagamento",
                    "Valor": [value_paid],
                    "Vencimento": [date_paid],
                    "Tipo": [operation_type],
                    "Método Pagamento": [payment_selected],
                    "Observações": [obs],
                }
            )
            
            existing_data = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Registros", data=existing_data)
            st.rerun()


else:
    st.write("Selecione um tipo de operação.")

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

       

        


