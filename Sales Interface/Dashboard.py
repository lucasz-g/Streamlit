import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go


def formatar_valor(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

def app():
    st.set_page_config(layout='wide')
    st.title('Dashboard de Vendas')

    url = 'https://labdados.com/produtos'
    
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        st.error(f'Erro ao carregar os dados: {e}')

    df = pd.DataFrame.from_dict(data)
    
    ## Tabelas
    df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format='%d/%m/%Y')
    
    ### Tabelas de Receita
    receita_estados = df.groupby('Local da compra')[['Preço']].sum()
    receita_estados = df.drop_duplicates(subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

    receita_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))[['Preço']].sum().reset_index()
    receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()
    receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year

    receita_categoria = df.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)
    receita_categoria = receita_categoria.reset_index()

    ### Tabelas de Quantidade de Vendas
    vendas_estado = df.groupby('Local da compra')[['Preço']].count()
    vendas_estado = df.drop_duplicates(subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(vendas_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)
    vendas_estado = vendas_estado.rename(columns={'Preço': 'Vendas'})

    vendas_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))[['Preço']].count().reset_index()
    vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()
    vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
    vendas_mensal = vendas_mensal.rename(columns={'Preço': 'Vendas'})
    
    vendas_mensal_agrupado = vendas_mensal.groupby(['Mês'])[['Vendas']].sum().reset_index()
    vendas_mensal_agrupado = vendas_mensal_agrupado.sort_values('Vendas', ascending=False)

    vendas_categoria = df.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)
    vendas_categoria = vendas_categoria.reset_index()
    vendas_categoria = vendas_categoria.rename(columns={'Preço': 'Vendas'})

    ### Tabelas de Vendedores
    vendedores = pd.DataFrame(df.groupby('Vendedor')['Preço'].agg({'sum', 'count'}))

    ## Gráficos 
    fig_mapa_receita = px.scatter_geo(receita_estados, 
                                      lat='lat', 
                                      lon='lon', 
                                      size='Preço', 
                                      scope='south america',
                                      template='seaborn',
                                      hover_name='Local da compra',
                                      hover_data={'lat': False, 'lon': False}, 
                                      projection='natural earth',
                                      title='Receita por estado')
    
    fig_barra_receita_estados = px.bar(receita_estados.head(10), 
                               x='Local da compra', 
                               y='Preço', 
                               title='Receita por estado', 
                               color='Preço',
                               color_continuous_scale='Teal')
    fig_barra_receita_estados.update_layout(xaxis_title='Estado', yaxis_title='Receita (R$)')

    fig_barra_receita_produto = px.bar(receita_categoria,
                                       x='Categoria do Produto',
                                        y='Preço',
                                        title='Receita por categoria',
                                        color='Preço',
                                        color_continuous_scale='Teal')
    fig_barra_receita_produto.update_layout(xaxis_title='Categoria', yaxis_title='Receita (R$)')

    fig_receita_mensal = px.line(receita_mensal,
                                 x='Mês',
                                 y='Preço',
                                markers=True,
                                range_y=(0, receita_mensal.max()),
                                color='Ano',
                                line_dash='Ano',
                                title='Receita mensal')
    fig_receita_mensal.update_layout(yaxis_title='Receita (R$)',)

    fig_mapa_vendas_estado = px.scatter_geo(vendas_estado,
                                           lat='lat',
                                           lon='lon',
                                           size='Vendas',
                                           scope='south america',
                                           template='seaborn',
                                           hover_name='Local da compra',
                                           hover_data={'lat': False, 'lon': False},
                                           projection='natural earth',
                                           title='Quantidade de Vendas por estado')
    
    fig_vendas_mensal = px.line(vendas_mensal,
                                x='Mês',
                                y='Vendas',
                                markers=True,
                                range_y=(0, vendas_mensal.max()),
                                color='Ano',
                                line_dash='Ano',
                                title='Quantidades de Vendas por mês')
    fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

    
    fig_barra_vendas_mensal = px.bar(vendas_mensal_agrupado,
                                     x='Mês',
                                     y='Vendas',
                                     title='Quantidade de vendas por mês',
                                     color='Vendas',
                                     color_continuous_scale='Teal')
    fig_barra_vendas_mensal.update_layout(xaxis_title='Mês', yaxis_title='Quantidade de vendas')


    fig_barra_vendas_produto = px.bar(vendas_categoria,
                                    x='Categoria do Produto',
                                    y='Vendas',
                                    title='Quantidade de vendas por categoria',
                                    color='Vendas',
                                    color_continuous_scale='Teal')
    fig_barra_vendas_produto.update_layout(xaxis_title='Categoria', yaxis_title='Quantidade de vendas')

    ## Visualização
    aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

    with aba1:
        preco = df['Preço'].sum()
        quantidade = df.shape[0]

        col1, col2 = st.columns(2)

        with col1:
            st.metric('Receita total', formatar_valor(preco, 'R$'))
            st.plotly_chart(fig_mapa_receita, use_container_width=True)
            st.plotly_chart(fig_barra_receita_estados, use_container_width=True)

        with col2:
            st.metric('Quantidade de compras', formatar_valor(quantidade))
            st.plotly_chart(fig_receita_mensal, use_container_width=True)
            st.plotly_chart(fig_barra_receita_produto, use_container_width=True)

    with aba2:
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Receita total', formatar_valor(preco, 'R$'))
            st.plotly_chart(fig_mapa_vendas_estado, use_container_width=True)
            st.plotly_chart(fig_barra_vendas_mensal, use_container_width=True)

        with col2:
            st.metric('Quantidade de compras', formatar_valor(quantidade))
            st.plotly_chart(fig_vendas_mensal, use_container_width=True)
            st.plotly_chart(fig_barra_vendas_produto, use_container_width=True)

    with aba3:
        qtd_vendedores = st.number_input('Quantidade de vendedores', min_value=2, max_value=10, value=5)
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Receita total', formatar_valor(preco, 'R$'))
            fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                            x=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                            y='sum',
                                            title=f'Top {qtd_vendedores} vendedores por receita',
                                            color='sum',
                                            color_continuous_scale='Teal')
            fig_receita_vendedores.update_layout(xaxis_title='Vendedor', yaxis_title='Receita (R$)')
            st.plotly_chart(fig_receita_vendedores, use_container_width=True)
        with col2:
            st.metric('Quantidade de compras', formatar_valor(quantidade))
            fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                            x=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                            y='count',
                                            title=f'Top {qtd_vendedores} vendedores por quantidade de vendas',
                                            color='count',
                                            color_continuous_scale='Teal')
            fig_vendas_vendedores.update_layout(xaxis_title='Vendedor', yaxis_title='Quantidade de vendas')
            st.plotly_chart(fig_vendas_vendedores, use_container_width=True)

if __name__ == '__main__':
    app()