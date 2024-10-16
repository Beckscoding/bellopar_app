import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Relatórios gerenciais",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

col1, col2 = st.columns([1, 5])
col1.image("Logo_bellopar.png")
col2.header("Relatórios gerenciais")

st.divider()


# bd["data_emissao_pedido"] = pd.to_datetime(bd["data_emissao_pedido"])
# bd = bd.sort_values("data_emissao_pedido")
# bd["Mes"] = bd["data_emissao_pedido"].apply(lambda x: str(x.year) + "-" + str(x.month))

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Registros", usecols=list(range(9)), ttl=1)
existing_data = existing_data.dropna(how="all")

# Show a bar chart with the selling evolution by month
filtered_data_venda = existing_data[existing_data["Tipo"] == "Venda"]
filtered_data_venda["Data"] = pd.to_datetime(filtered_data_venda["Data"], dayfirst=True).dt.strftime("%m/%Y") 
filtered_data_venda = filtered_data_venda.sort_values("Data")


spend_mom = filtered_data_venda.groupby('Data')[['Valor']].sum().reset_index()

client_spend = filtered_data_venda.groupby('Nome')[['Valor']].sum().reset_index()
client_spend = client_spend.sort_values("Valor")

client_delta = existing_data.groupby('Nome')[['Valor']].sum().reset_index()
client_delta = client_delta.sort_values("Valor", ascending=False)


# Cria o gráfico de barras com rótulos
fig = px.bar(spend_mom, x="Data", y="Valor", text="Valor", 
             title="Evolução das Vendas por Mês")

# Adiciona a exibição dos rótulos nas barras
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

# Personaliza o layout (opcional)
fig.update_layout(
    xaxis_title="Data",
    yaxis_title="Valor (R$)",
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

# Exibe o gráfico no Streamlit
st.plotly_chart(fig)

col1, col2 = st.columns(2)


# Cria o gráfico de barras horizontais com rótulos
fig1 = px.bar(client_spend, x="Valor", y="Nome", text="Valor", orientation="h",
             title="Clientes com maior valor de compra")


# Adiciona a exibição dos rótulos nas barras
fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')

col1.plotly_chart(fig1)

# Cria o gráfico de barras horizontais com rótulos
fig2 = px.bar(client_delta, x="Valor", y="Nome", text="Valor", orientation="h",
             title="Clientes com as maiores pendências de pagamento")
fig2.update_layout(yaxis={'categoryorder':'total ascending'})

# Adiciona a exibição dos rótulos nas barras
fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')

col2.plotly_chart(fig2)

st.write("Lista de cliente com pendências de pagamento:")
st.dataframe(client_delta, hide_index=True, use_container_width=True)