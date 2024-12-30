import time
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from legado_employee_data import legado_employee_data


# Função para inicializar o driver do Chrome
def initialize_driver():
    service = Service('C:/Users/gabri/OneDrive/Documentos/DesafioGiGroup/chromedriver.exe')
    return webdriver.Chrome(service=service)


# Função para esperar e clicar em elementos
def wait_and_click(driver, by, value):
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    )
    button.click()


# Função para localizar e preencher campos
def wait_and_fill(driver, by, value, text):
    field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((by, value))
    )
    field.clear()
    field.send_keys(text)


# Função para fazer login no site
def login_to_site(username, password):
    driver = initialize_driver()
    driver.get('https://pathfinder.automationanywhere.com/challenges/automationanywherelabs-employeedatamigration.html')
    time.sleep(5)

    try:
        # Aceitar cookies
        wait_and_click(driver, By.ID, 'onetrust-accept-btn-handler')
    except:
        print("Botão de cookies não encontrado, continuando...")

    try:
        # Escolher a opção do desafio, "Community"
        wait_and_click(driver, By.ID, 'button_modal-login-btn__iPh6x')
    except:
        print("Botão Community não encontrado")

    try:
        # Digitar username e clicar em "Next"
        wait_and_fill(driver, By.ID, '43:2;a', username)
        wait_and_click(driver, By.XPATH, "//button[text()='Next']")

        # Digitar senha
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"][placeholder="Password"]'))
        )
        password_field.send_keys(password)

        # Clicar no botão "Log in"
        wait_and_click(driver, By.XPATH, "//button[text()='Log in']")
        time.sleep(10)
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
    
    return driver


# Função para pegar IDs de forma automática
def get_employee_id(driver):
    try:
        employee_id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'employeeID'))
        )
        employee_id = employee_id_input.get_attribute('value')
        print(f"ID Capturado: {employee_id}")
        return employee_id
    except Exception as e:
        print(f"Erro ao capturar o ID do funcionário: {e}")
        return None


# Função para pegar dados do aplicativo Legacy
def get_legado_employee_data(employee_id):
    return legado_employee_data.get(employee_id, {})


# Função para pegar dados da API
def get_api_employee_data(employee_id):
    api_url = f"https://botgames-employee-data-migration-vwsrh7tyda-uc.a.run.app/employees?id={employee_id}"
    response = requests.get(api_url)
    return response.json() if response.status_code == 200 else None


# Função para preencher os dados no site
def fill_employee_data(driver, combined_data):
    fields = {
        "First Name": 'input[id="firstName"]',
        "Last Name": 'input[id="lastName"]',
        "phoneNumber": 'input[id="phone"]',
        "Email": 'input[id="email"]',
        "City": 'input[id="city"]',
        "State": 'select[id="state"]',
        "Zip": 'input[id="zip"]',
        "Job Title": 'input[id="title"]',
        "Department": 'select[id="department"]',
        "startDate": 'input[id="startDate"]',
        "Manager": 'input[id="manager"]'
    }

    for key, selector in fields.items():
        if "select" in selector:
            select_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            select = Select(select_elem)
            select.select_by_visible_text(combined_data.get(key, ""))
        else:
            wait_and_fill(driver, By.CSS_SELECTOR, selector, combined_data.get(key, ""))

    wait_and_click(driver, By.XPATH, '/html/body/div[2]/div/form/div[7]/div[1]/button')
    print("Dados do funcionário preenchidos com sucesso!")


# Função principal para orquestrar a migração dos dados
def migrate_employee_data(driver):
    employee_id = get_employee_id(driver)
    if employee_id:
        legacy_data = get_legado_employee_data(employee_id)
        api_data = get_api_employee_data(employee_id)
        if legacy_data and api_data:
            combined_data = {**legacy_data, **api_data}
            fill_employee_data(driver, combined_data)
            return True
        else:
            print(f"Dados não encontrados para o ID {employee_id}")
            return False
    return False


# Função para iniciar a execução do script
def run_script(username, password):
    driver = login_to_site(username, password)
    while True:
        success = migrate_employee_data(driver)
        if not success:
            break
        time.sleep(5)


# Interface de Login com Tkinter
def create_login_window():
    def on_submit():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            window.destroy()
            run_script(username, password)
        else:
            messagebox.showwarning("Erro", "Por favor, preencha ambos os campos de login e senha.")
    
    window = tk.Tk()
    window.title('Desafio - GiGroup')
    window.geometry('300x150')
    window.resizable(False, False)

    style = ttk.Style(window)
    style.configure("TLabel", font=('Helvetica', 10))
    style.configure("TButton", font=('Helvetica', 10))
    style.configure("TEntry", font=('Helvetica', 10))

    ttk.Label(window, text="E-mail:", padding=10).grid(row=0, column=0, sticky='W')
    ttk.Label(window, text="Senha:", padding=10).grid(row=1, column=0, sticky='W')
    
    username_entry = ttk.Entry(window)
    password_entry = ttk.Entry(window, show="*")
    
    username_entry.grid(row=0, column=1, pady=5)
    password_entry.grid(row=1, column=1, pady=5)
    
    ttk.Button(window, text='Entrar', command=on_submit).grid(row=2, column=1, pady=10)
    
    window.mainloop()


if __name__ == "__main__":
    create_login_window()