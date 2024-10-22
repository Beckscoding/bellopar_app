import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(
    page_title="Cadastro de Clientes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

col1, col2 = st.columns([1, 5])
col1.image("Logo_bellopar.png")
col2.header("Cadastro de clientes")

st.divider()

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Clientes", usecols=list(range(9)), ttl=1)
existing_data = existing_data.dropna(how="all")

# Check if the ID column exists, and find the max ID
if "ID_Cliente" in existing_data.columns:
    last_id = existing_data["ID_Cliente"].max()  # Get the highest ID
else:
    # If no 'ID' column exists yet, initialize the ID system
    last_id = 0
    existing_data["ID_Cliente"] = []

# Create a form, using st.forms to include new clientes data do the google sheets file
with st.form(key="my_form", clear_on_submit=True):

    name = st.text_input(label="Nome")
    col1, col2 = st.columns(2)
    address = col1.text_input(label="Endereço")
    district = col2.text_input(label="Bairro")
    city = col1.text_input(label="Cidade")
    phone = col1.text_input(label="Telefone")
    email = col2.text_input(label="E-mail")
    numero_pe = col2.text_input(label="Número Calçado")
    doc = col1.text_input(label="CPF")
    obs = st.text_area(label="Observações")
    # Create a button to submit the form
    submit = st.form_submit_button(label="Submit")

    # If the form is submitted
    if submit:
        # Increment the ID for the new row
        new_id = last_id + 1

        # Create a new row with the form data
        new_row = pd.DataFrame(
            {   "ID_Cliente": [new_id],
                "Nome": [name],
                "CPF": [doc],
                "Endereço": [address],
                "Bairro": [district],
                "Cidade": [city],
                "Telefone": [phone],
                "E-mail": [email],
                "Nr. Calçado": [numero_pe],
                "Observações": [obs],
            }
        )

        # Append the new row to the existing data
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)

        # Update the Google Sheets file with the updated data
        conn.update(worksheet="Clientes", data=updated_data)

        st.success("Cliente adicionado com sucesso!")

# Get the list of client names
client_names = existing_data["Nome"].tolist()  # Convert to a list

name = st.selectbox(label="Consultar Cliente", options=client_names, index=None)

filtered_data_name = existing_data[existing_data["Nome"] == name]

# include an if condition in case name is not empty
if name:    
    st.dataframe(filtered_data_name[["ID_Cliente", "Nome", "CPF", "Endereço", "Bairro", "Cidade", "Telefone", "E-mail", "Nr. Calçado", "Observações"]], hide_index=True)
    
else:
    st.markdown('<p style="color:red; font-style:italic;">Selecione um cliente.</p>', unsafe_allow_html=True)


# Widget para exclusão de um cadastro de cliente.  
with st.sidebar:
    

    st.write("Exclua uma operação pelo ID:")
    with st.form(key="exclude-form", clear_on_submit=True):
        
        
        delete_name = st.selectbox(label="Consultar Cliente", options=client_names, index=None)

        submit_exclude = st.form_submit_button(label="Excluir")

        # Botão para deletar a linha com o ID informado
        if submit_exclude:
            if delete_name in existing_data["Nome"].values:
                # Filtrar a linha com o ID correspondente
                updated_data_name = existing_data[existing_data["Nome"] != delete_name]
                
                # Atualizar a planilha com os dados filtrados
                conn.update(worksheet="Clientes", data=updated_data_name)
                
                st.success(f"O cliente {delete_name} foi excluído com sucesso!")
                st.rerun()
            else:
                st.error(f"O cliente {delete_name} não foi encontrado.")