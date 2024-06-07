from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import time


chrome_options = Options()
chrome_options.add_argument("--headless") 

driver = webdriver.Chrome(options=chrome_options)

url = "https://pesquisaseduc.fde.sp.gov.br/localize_escola?pageNumber=1&idMunicipio=100&inicial=False"

driver.get(url)

for i in range(1, 749):

    page_content = driver.page_source

    soup = BeautifulSoup(page_content, 'html.parser')

    nav_select_page = soup.find_all('nav', class_='navSuperior')



    escolas = soup.find_all('article')[2:]

    for escola in escolas:
        nome_escola = escola.find('h4', class_='titulo_res').text.split(': ')[1]
        cep_escola = escola.find('p', class_='assunto_esc').text.split('CEP: ')[1].split('ZONA: ')[0].replace('     - ', '')

        print(nome_escola)
        print(cep_escola)
        print()

driver.quit()