# dealership-api

<br>
```Essa api tem como objetivo realizar a venda de veiculos a clientes em uma concessionaria. Cada concessionaria tem seus respectivos vendedosres e veiculos.```

- #### Features

  - Autenticação
    <br>
    ```Foram implementados as funcionalidades de login e verificação de credenciais baseado em claims```
  - Usuarios
    <br>
    `Existem dois tipos de usuarios, vendedor responsavel pelo cadastro, listagem de clientes, assim como a venda de veiculos e listagem de carros disponiveis para a venda. E o usuario dono da consessionaria, responsavel pela compara de veiculos para a propria.`
  - Cliente
    <br>
    `Somente o cadastro e listagem de clientes foram implementados, sendo resposabilidade do vendador realizar essas operações`
  - Veiculo
    <br>
    `A venda de veiculos para clientes é de responsabilidade do vendedor, sendo limitado a posse de até 3 veiculos por cliente, caso o cliente tenha 3 veiuclos a venda será bloqueada. A compra de veiuclos fica vedado ao escopo da concessionaria, assim na hora da venda a troca de donos será realizada.`

- #### Como executar o projeto?

  - Utilizando docker compose
    <br>
    `docker-compose --env-file .env up`
  - Utilizando python
    <br>
    ```
        python -m virtualenv .venv -p python3.10
        source .venv/bin/activate
        pip install -r requirements.txt
        python -m gunicorn -w 4 -b 127.0.0.1:8080 main:app
    ```

- #### Postman Collaction
  - https://www.postman.com/dealership-api/workspace/dealership-api/overview
