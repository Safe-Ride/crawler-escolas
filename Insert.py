from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mysql.connector
import csv
import os  
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


con = mysql.connector.connect(
    host='localhost',
    database='saferide',
    user='safeuser',
    password='eunaosei',
    charset='utf8mb4',
    collation='utf8mb4_general_ci'
)


def insert_escolas(nome_escola: str, endereco_id: int):
    mySql_insert = "INSERT INTO escola (nome, endereco_id) VALUES (%s, %s)"
    cursor = con.cursor()
    cursor.execute(mySql_insert, (nome_escola, endereco_id))
    con.commit()
    cursor.close()

def endereco(cep: str):
    mySql_insert = "INSERT INTO endereco (cep, usuario_id) VALUES (%s, 100)"
    cursor = con.cursor()
    cursor.execute(mySql_insert, (cep,))
    con.commit()
    cursor.close()

def select_endereco(cep: str):
    mySql_select = "SELECT id FROM endereco WHERE cep = %s LIMIT 1"
    cursor = con.cursor()
    cursor.execute(mySql_select, (cep,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado[0] if resultado else None

try:
    os.remove("enderecos.csv")
except:
    pass

try:
    os.remove("escolas.csv")
except:
    pass
chrome_options = Options()
chrome_options.add_argument("--headless") 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


dados_escolas_csv = []
dados_enderecos_csv = []


cabecalho_escolas = ["nome", "endereco_id"]
cabecalho_enderecos = ["cep", "usuario_id"]


for i in range(1, 749):
    url = f'https://pesquisaseduc.fde.sp.gov.br/localize_escola?pageNumber={i}&idMunicipio=100&inicial=False'
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#conteudo > div > article:nth-child(5)')))
    except Exception as e:
        print(f"Erro: {e}")
        break
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    escolas = soup.find_all('article')[2:]

    for escola in escolas:
        nome_escola = escola.find('h4', class_='titulo_res').text.split(': ')[1]
        cep_escola = escola.find('p', class_='assunto_esc').text.split('CEP: ')[1].split('ZONA: ')[0].replace('     - ', '').strip()

        id_endereco = select_endereco(cep_escola)

        if id_endereco is None:
            endereco(cep_escola)
            id_endereco = select_endereco(cep_escola)
        print(f"Página: {i}")
        print(f"CEP: {cep_escola}")


        if id_endereco:
            print(f"ID Endereço: {id_endereco}")
            insert_escolas(nome_escola, id_endereco)

            dados_escolas_csv.append([nome_escola, id_endereco])
            dados_enderecos_csv.append([cep_escola, 100])  

        else:
            print(f"Endereço não encontrado para CEP: {cep_escola}")


    if len(dados_escolas_csv) >= 200:
        if not os.path.exists('escolas.csv'):
            with open('escolas.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(cabecalho_escolas)  
        with open('escolas.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerows(dados_escolas_csv)
        dados_escolas_csv.clear()  

    if len(dados_enderecos_csv) >= 200:

        if not os.path.exists('enderecos.csv'):
            with open('enderecos.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(cabecalho_enderecos)
        with open('enderecos.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerows(dados_enderecos_csv)
        dados_enderecos_csv.clear()  

if dados_escolas_csv:
    with open('escolas.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerows(dados_escolas_csv)

if dados_enderecos_csv:
    with open('enderecos.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerows(dados_enderecos_csv)


driver.quit()
con.close()
