from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mysql.connector
import time

# Conectar ao banco de dados
con = mysql.connector.connect(
    host='localhost',
    database='saferide',
    user='safeuser',
    password='eunaosei'
)

def insert_escolas(nome_escola: str, endereco_id: int):
    mySql_insert = "INSERT INTO escola (nome, endereco_id) VALUES (%s, %s)"
    cursor = con.cursor()
    cursor.execute(mySql_insert, (nome_escola, endereco_id))
    con.commit()
    cursor.close()

def endereco(cep: str):
    mySql_insert = "INSERT INTO endereco (cep, usuario_id) VALUES (%s, 32)"
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

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

for i in range(1, 749):
    url = f'https://pesquisaseduc.fde.sp.gov.br/localize_escola?pageNumber={i}&idMunicipio=100&inicial=False'
    driver.get(url)
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    escolas = soup.find_all('article')[2:]

    for escola in escolas:
        nome_escola = escola.find('h4', class_='titulo_res').text.split(': ')[1]
        cep_escola = escola.find('p', class_='assunto_esc').text.split('CEP: ')[1].split('ZONA: ')[0].replace('     - ', '').strip()

        endereco(cep_escola)
        print(f"CEP: {cep_escola}")
        id_endereco = select_endereco(cep_escola)

        if id_endereco:
            print(f"ID Endereço: {id_endereco}")
            insert_escolas(nome_escola, id_endereco)
        else:
            print(f"Endereço não encontrado para CEP: {cep_escola}")

driver.quit()
con.close()
