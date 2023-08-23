import time
import random
from datetime import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
from airflow.decorators import dag, task
from airflow.providers.http.operators.http import HttpSensor
from sqlalchemy import create_engine
from plugins.models.custom_sqlalchemy_models import ProductTableDefinition


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 19),
    'retries': 1,
}

dag = DAG(
    'leroy_data_collection',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    tags=['leroy']
)


driver = webdriver.Chrome(ChromeDriverManager().install())


def insert_or_update_data(**kwargs):
 
    connection_str = f"mssql+pyodbc://{kwargs['username']}:{kwargs['password']}@{kwargs['server']}/{kwargs['database']}?driver=SQL+Server"
    engine = create_engine(connection_str, echo=True)
    
    with engine.connect() as conn:
        new_product = ProductTableDefinition(
            nome=kwargs['nome'],
            concorrente="LeroyMerlin",
            preco_concorrente=kwargs['precos'],
            jsonatributos=kwargs['atributos'] ,
            json_imagem_atributos=kwargs['imagens'] ,
            pagina=kwargs['url'],
            jsoncategorias=kwargs['categorias'] ,
            descricao=kwargs['descricao'],
            preco_detalhes=kwargs['detalhesprecos'],
            categoria = kwargs['categoria'],
            subcategoria = kwargs['subcategoria']
        )
        conn.execute(new_product)



@task
def random_delay() -> float:
    return random.uniform(0.5, 3.0)

@task
def random_sleep() -> int:
    return random.randint(4, 15)

@task
def scroll(driver) -> None:
    driver.implicitly_wait(7)
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while not match:
        lastCount = lenOfPage
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True

@task
def make_request(driver, url: str) -> None:
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(user_agents)})
    time.sleep(random_delay())
    driver.get(url)
    time.sleep(random_delay())
    scroll(driver)




def extract_product_info(driver, url: str):
    product_dict = {}

    make_request(driver, url)
    product_dict['url'] = url

    try:
        nome = driver.find_elements(
            By.XPATH, "/html/body/div[10]/div/div[1]/div[1]/div/div[1]/h1")[0].text
        product_dict["nome"] = nome.strip()
    except:
        pass
    
    try:
        precos = driver.find_elements(
            By.XPATH, "/html/body/div[10]/div/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/span[1]")[0].text
        preco = precos.strip()
        product_dict["precos"] = round(float(preco.replace("R$","").replace(",",".").strip()),2)
    except:
        pass
    
    try:
        preco_detalhes = driver.find_elements(
            By.XPATH, "/html/body/div[10]/div/div[1]/div[2]/div[2]/div/div[1]/div/div[3]/div/strong")[0].text
        product_dict["detalhespreco"] = preco_detalhes
    except:
        pass
    
    try:
        descricao = driver.find_elements(
            By.XPATH, "/html/body/div[10]/div/div[1]/div[2]/div[1]/div[2]/div/div[2]/div/div/div/p")[0].text
        product_dict["descricao"] = descricao
    except:
        pass

    try:
        imagens_dict = {}
        imagens = driver.find_elements(
            By.XPATH, "//div[@class='css-17kvx2v-wrapper__image-wrapper ejgu7z2']//img")
        for cont, imagem in enumerate(imagens):
            imagens_dict["imagem" + str(cont)] = imagem.get_attribute("src").replace("140x140.jpg", "600x600.jpg").replace("140x140.jpeg", "600x600.jpeg")
    except Exception as e:
        print(e)
    
    atributos_dict = {}
    referencias = driver.find_elements(By.XPATH, "/html/body/div[10]/div/div[4]/div[2]/table/tbody/tr/th")
    atributos = driver.find_elements(By.XPATH, "/html/body/div[10]/div/div[4]/div[2]/table/tbody/tr/td")
    for cont, atributo in enumerate(referencias):
        atributos_dict[str(atributo.text).strip()] = str(atributos[cont].text).strip()
    
    categorias_dict = {}
    categoria_nomes = driver.find_elements(By.XPATH, '/html/body/div[7]/div/ul[1]/li/a/span')
    url_categorias = driver.find_elements(By.XPATH, '/html/body/div[7]/div/ul[1]/li/a')
    for cont, categorias in enumerate(categoria_nomes):
        categorias_dict[categorias.text] = url_categorias[cont].get_attribute("href")
    
    try:
        categoria_produto = list(categorias_dict.keys())
    except:
        pass

    try:
        insert_or_update_data(
            nome=str(product_dict.get("nome")).strip(),
            descricao=str(product_dict.get("descricao")).strip(),
            precos=float(product_dict.get("precos")),
            detalhesprecos=str(product_dict.get("detalhespreco")).strip(),
            url=str(product_dict.get("url")).strip(),
            categorias=json.dumps(categorias_dict, indent=4),
            atributos=json.dumps(atributos_dict, indent=4),
            imagens=json.dumps(imagens_dict, indent=4),
            categoria=categoria_produto[1],
            subcategoria=categoria_produto[2]
        )
    except:
        pass



wait_for_leroy_url_collect = HttpSensor(
    task_id='wait_for_leroy_url_collect',
    http_conn_id='http_default',
    endpoint='/api/v1/dags/Leroy_url_collect/dagRuns',
    request_params={'state': 'success'},
    response_check=lambda response: len(response.json()) > 0,
    poke_interval=60,
    timeout=600,
    dag=dag
)


urlanuncios = Variable.get("urlanuncios", deserialize_json=True)
extract_product_infos = []
for urlanuncio in urlanuncios:
    extract_product_info_task = PythonOperator(
        task_id=f'extract_product_info_{urlanuncio}',
        python_callable=extract_product_info,
        op_args=[driver, urlanuncio.get("urlanuncio")],
        provide_context=True,
        dag=dag,
    )
    extract_product_infos.append(extract_product_info_task)


def close_selenium_driver(driver):
    driver.quit()

close_selenium_task = PythonOperator(
    task_id='close_selenium_driver',
    python_callable=close_selenium_driver,
    op_args=[driver],
    provide_context=True,
    dag=dag
)


wait_for_leroy_url_collect >> extract_product_infos >> close_selenium_task



