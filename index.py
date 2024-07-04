import sqlite3
import pandas as pd
import requests
import matplotlib.pyplot as plt
import click

# Função para carregar os dados do banco de dados SQLite
def load_from_db(db_path, id_territory):
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM territorios WHERE id = {id_territory}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Função para carregar os dados do CSV (não utilizada atualmente)
def load_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    return df

# Função para buscar dados na API do IBGE
def fetch_from_ibge_api(id_territory):
    url = f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{id_territory}/metadados"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Função para obter a dimensão do território
def get_dimensao(db_path, csv_path, id_territory):
    df = load_from_db(db_path, id_territory)
    if not df.empty:
        return df.iloc[0]
    else:
        data = fetch_from_ibge_api(id_territory)
        if data:
            # Adapte conforme necessário para a estrutura dos dados da API
            return {
                'nome': data['nome'],
                'dimensao': data['dimensao']
            }
        else:
            return None

@click.group()
def cli():
    pass

@click.command()
@click.argument('id')
@click.argument('output')
def dimensao(id, output):
    db_path = 'database.db'
    csv_path = 'dict.csv'  # Não utilizado atualmente
    
    territory_data = get_dimensao(db_path, csv_path, id)
    if territory_data is not None:
        territory_name = territory_data['nome']
        dimensao = territory_data['dimensao']
        
        # Gerar o gráfico
        plt.bar(territory_name, dimensao)
        plt.xlabel('Território')
        plt.ylabel('Dimensão (km²)')
        plt.title(f'Dimensão do Território: {territory_name}')
        plt.savefig(output)
        plt.close()
        
        click.echo(f'Nome: {territory_name} | Dimensão: {dimensao}km² | Gráfico: {output}')
    else:
        click.echo('Território não encontrado.')

@click.command()
@click.argument('id1')
@click.argument('id2')
@click.argument('output')
def comparar(id1, id2, output):
    db_path = 'database.db'
    csv_path = 'dict.csv'  # Não utilizado atualmente
    
    territory_data1 = get_dimensao(db_path, csv_path, id1)
    territory_data2 = get_dimensao(db_path, csv_path, id2)
    
    if territory_data1 is not None and territory_data2 is not None:
        territory_name1 = territory_data1['nome']
        dimensao1 = territory_data1['dimensao']
        territory_name2 = territory_data2['nome']
        dimensao2 = territory_data2['dimensao']
        
        difference = abs(dimensao1 - dimensao2)
        
        # Gerar o gráfico comparativo
        plt.bar([territory_name1, territory_name2], [dimensao1, dimensao2])
        plt.xlabel('Território')
        plt.ylabel('Dimensão (km²)')
        plt.title('Comparação de Dimensões de Territórios')
        plt.savefig(output)
        plt.close()
        
        click.echo(f'{territory_name1}: {dimensao1}km² | {territory_name2}: {dimensao2}km² | Diferença: {difference}km² | Gráfico: {output}')
    else:
        click.echo('Um ou ambos os territórios não foram encontrados.')

cli.add_command(dimensao)
cli.add_command(comparar)

if __name__ == '__main__':
    cli()