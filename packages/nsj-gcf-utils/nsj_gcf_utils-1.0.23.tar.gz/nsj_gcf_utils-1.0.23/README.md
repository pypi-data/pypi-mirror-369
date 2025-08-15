# nsj_gcf_utils
Utilitários para construção de Google Cloud Functions.

## Features disponíveis

Segue breve descrição das features disponiveis, identificando os respectivos módulos:

* ```nsj_gcf_utils.app_logger```: Configuração padrão de logger para aplicações GCF.
* ```nsj_gcf_utils.authentication_service```: Validação de chaves recebidas no cabeçalho X-API-Key.
* ```nsj_gcf_utils.db_adapter```: Adapter de comunicação com o banco.
* ```nsj_gcf_utils.http_util```: Realiza requisições HTTP, com suporte a tentativas seguidas em caso de falha.
* ```nsj_gcf_utils.iban```: Utilitário para manipulação de International Bank Account Number (IBAN)
* ```nsj_gcf_utils.json_util```: Serialização e desserialização em JSON, com manipulação nativa de datas no formato "yyyy-mm-ddThh:mm:ss". Decimal é traduzido para string ao serializar para JSON.
* ```nsj_gcf_utils.keycloak_service```: Autenticação para aplicação enquanto cliente Oauth.
* ```nsj_gcf_utils.nsj_authentication_service```: Validação de access_token recebido no cabeçalho Authorization (Bearer token), por meio do padrão Token Instrospection (RFC 7662).
* ```nsj_gcf_utils.router```: Utilitário para controler de rotas por meio decorators, fazendo com que uma fucntion-framework se comporte de modo similar a outros frameworks web como Spring ou Symfony.

## Testes Automatizados

Sempre rode o comando abaixo, antes de dar push neste repositório:

> make tests
