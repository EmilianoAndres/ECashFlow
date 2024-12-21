# ECashFlow
Repositorio para proyecto de Tesis; carrera Analista de Sistemas; promoción 2024; IRESM


Este proyecto es una aplicación web desarrollada con Django. 
A continuación, se detallan los pasos para configurar el entorno de 
desarrollo en Windows, instalar las dependencias y ejecutar la aplicación.

## Requisitos Previos

- Python 3.12.0 (algunas librerías dan problemas con otras versiones de python 3)
- pip (el administrador de paquetes de Python)

## Configuración del Entorno de Desarrollo

### 1. Crear un Entorno Virtual

Es recomendable utilizar un entorno virtual para aislar las dependencias 
del proyecto. Para crear un entorno virtual con `venv` :

```cmd
python -m venv venv
```
### 2. Activar el entorno virtual

Luego de crear el entorno virtual, nos posicionamos sobre su carpeta, 
y ejecutamos:

```cmd
.\venv\Scripts\activate
```

Una vez seleccionado y activado el entorno virtual, ejecutamos el packet manager de python para
actualizar las dependencias del projecto, que se encuentra en la carpeta root.

### 3. Instalar las Dependencias

```cmd
pip install -r requirements.txt
```

### 4. Migraciones

Si es la primera vez que se ejecuta el proyecto, se debe correr el siguiente comando para
aplicar las migraciones en la sqlite:

```cmd
py manage.py migrate
```

### 5. Desactivar el ambiente virtual

Al finalizar la ejecución de la aplicación, de ser necesario, en la consola que esté corriendo
el ambiente virtual, ejecutar el siguiente comando:

```cmd
deactivate
```

## Docker

El proyecto está preparado para correr en una instancia de docker, utilizando docker compose para integrar Traefic, el cual también está configurado para funcionar de Load Balancer y Reverse Proxy.

para utilizarlo, basta con clonar el proyecto y, asumendo que docker y compose están instalados en el sistema, ejecutar desde la carpeta root del proyecto:

```cmd
docker compose up --build
```

dirigirse al archivo Dockerfile y docker-compose.yml para modificar los parámetros necesarios, como por ejemplo el puerto por el cual se expone la aplicación, el proxy que realiza traefic, y el manejo del dns.
