**Arquivo:** `Desafio_Teste.py`

Este script automatiza o processo de migração de dados de funcionários de um aplicativo legacy de Recursos Humanos (RH) e de uma API interna de onboarding de RH para o novo sistema de RH da organização - Busy Bees Resource Management.

# **Sumário**
- Dependências
- Funções
- Passo a Passo de Execução
- Configurações Adicionais

# **Dependências**
O script utiliza as seguintes bibliotecas **Python**:

`time:`Para gerenciar pausas e esperas.

`requests: `Para fazer requisições HTTP à API interna de RH.

`tkinter: `Para criar a interface gráfica de login.

`selenium: `Para automação de interações no navegador.

`bs4: `Para análise de HTML.

`legado_employee_data: `Importa os dados do aplicativo legacy.

<br>Certifique-se de que todas as bibliotecas estão instaladas. Caso contrário, instale usando pip:

```python
pip install requests tkinter selenium beautifulsoup4
```

# **Funções**
- **`initialize_driver()`**

```python
def initialize_driver(): service =
	Service('C:/Users/gabri/OneDrive/Documentos/DesafioGiGroup/chromedriver.exe')
	return webdriver.Chrome(service=service)
```

- `wait_and_click(driver, by, value)`<br>
**Inicializa o driver do Chrome para controlar o navegador.**

```python
def wait_and_click(driver, by, value):
	button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
	button.click()
```
- `wait_and_fill(driver, by, value, text)`<br>
**Espera até o elemento estar clicável e então clica nele.**

```python
def wait_and_fill(driver, by, value, text):
    field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
    field.clear()
    field.send_keys(text)
```
- `login_to_site(username, password)`<br>
**Localiza um campo e preenche-o com o texto fornecido.**

```python
def login_to_site(username, password):
    driver = initialize_driver()
    driver.get('https://pathfinder.automationanywhere.com/challenges/automationanywherelabs-employeedatamigration.html')
    time.sleep(5)

    try:
        wait_and_click(driver, By.ID, 'onetrust-accept-btn-handler')
    except:
        print("Botão de cookies não encontrado, continuando...")

    try:
        wait_and_click(driver, By.ID, 'button_modal-login-btn__iPh6x')
    except:
        print("Botão Community não encontrado")

    try:
        wait_and_fill(driver, By.ID, '43:2;a', username)
        wait_and_click(driver, By.XPATH, "//button[text()='Next']")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"][placeholder="Password"]'))
        )
        password_field.send_keys(password)
        wait_and_click(driver, By.XPATH, "//button[text()='Log in']")
        time.sleep(10)
    except Exception as e:
        print(f"Erro ao fazer login: {e}")

    return driver
```
- `get_employee_id(driver)`<br>
**Executa o processo de login no site, incluindo aceitação de cookies e entrada de credenciais.**

```python
def get_employee_id(driver):
    try:
        employee_id_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'employeeID')))
        employee_id = employee_id_input.get_attribute('value')
        print(f"ID Capturado: {employee_id}")
        return employee_id
    except Exception as e:
        print(f"Erro ao capturar o ID do funcionário: {e}")
        return None
```
- `get_legado_employee_data(employee_id)`<br>
**Captura o ID do funcionário exibido no formulário do site.**

```python
def get_legado_employee_data(employee_id):
    return legado_employee_data.get(employee_id, {})
```
- `get_api_employee_data(employee_id)`<br>
**Obtém os dados do funcionário do aplicativo legacy.**

```python
def get_api_employee_data(employee_id):
    api_url = f"https://botgames-employee-data-migration-vwsrh7tyda-uc.a.run.app/employees?id={employee_id}"
    response = requests.get(api_url)
    return response.json() if response.status_code == 200 else None
```
- `fill_employee_data(driver, combined_data)`<Br>
**Obtém os dados do funcionário da API interna de onboarding de RH.**

```python
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
            select_elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            select = Select(select_elem)
            select.select_by_visible_text(combined_data.get(key, ""))
        else:
            wait_and_fill(driver, By.CSS_SELECTOR, selector, combined_data.get(key, ""))

    wait_and_click(driver, By.XPATH, '/html/body/div[2]/div/form/div[7]/div[1]/button')
    print("Dados do funcionário preenchidos com sucesso!")
```
- `migrate_employee_data(driver)`<br>
**Preenche os campos do formulário do site com os dados combinados do aplicativo legacy e da API de onboarding.**

```python
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
```
- `run_script(username, password)`<br>
**Orquestra a migração de dados, combinando informações de ambos os sistemas e preenchendo os campos no site de destino.**

```python
def run_script(username, password):
    driver = login_to_site(username, password)
    while True:
        success = migrate_employee_data(driver)
        if not success:
            break
        time.sleep(5)
```
- `create_login_window()`<br>
**Função principal que controla o fluxo de login, captura de dados e migração contínua.**

```python
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
    window.title('Login')
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
```
**Cria a interface de login utilizando `Tkinter`.**

# **Passo a Passo de Execução**
1. Certifique-se de ter todas as dependências instaladas.

3. Crie o arquivo `legado_employee_data.py` com os dados dos funcionários do aplicativo legacy.

5. Execute o script `Desafio_Teste.py` para iniciar a automação.

7. Insira suas credenciais na janela de login que será exibida.

9. Acompanhe a automação enquanto os dados dos funcionários são capturados, combinados e inseridos no novo sistema de RH.

# Configurações Adicionais
- Caso o caminho para o `chromedriver` seja diferente, ajuste no método `initialize_driver`.

- Adapte os seletores CSS e XPath

