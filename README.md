# Lab API Gateway + Cognito + Lambda

Este projeto e um lab de uma HTTP API no Amazon API Gateway integrada com uma AWS Lambda e protegida por Cognito JWT Authorizer.

## Arquitetura

O Terraform cria:

- Cognito User Pool
- Cognito User Pool Client sem client secret
- Lambda em Python
- API Gateway HTTP API
- JWT Authorizer no API Gateway
- Rotas publicas e privada
- Permissao para o API Gateway invocar a Lambda

Fluxo visual:

![Fluxo API Gateway Cognito](api-gateway-fluxo.png)

## Estrutura

```text
.
├── api-gateway-fluxo.png
├── lambda
│   └── handler.py
└── terraform
    ├── main.tf
    ├── outputs.tf
    └── variables.tf
```

## Rotas

| Metodo | Rota | Autenticacao | Descricao |
| --- | --- | --- | --- |
| GET | `/health` | Nao | Health check da API |
| GET | `/public` | Nao | Rota publica |
| GET | `/private` | Sim | Rota protegida por JWT do Cognito |

## Pre-requisitos

- Terraform `>= 1.5`
- AWS CLI configurado
- Credenciais AWS com permissao para criar API Gateway, Lambda, IAM e Cognito
- `curl`
- `jq` para extrair o token nos exemplos de teste

Verifique sua identidade AWS antes de aplicar:

```sh
aws sts get-caller-identity
```

## Deploy

Entre na pasta do Terraform:

```sh
cd terraform
```

Inicialize os providers:

```sh
terraform init
```

Revise o plano:

```sh
terraform plan
```

Aplique a infraestrutura:

```sh
terraform apply
```

## Outputs

Depois do `apply`, exporte os valores usados nos testes:

```sh
API_URL=$(terraform output -raw api_endpoint)
USER_POOL_ID=$(terraform output -raw user_pool_id)
CLIENT_ID=$(terraform output -raw app_client_id)
REGION=$(terraform output -raw region)
```

Essas variaveis ficam apenas na sessao atual do terminal.

## Testando as rotas publicas

Health check:

```sh
curl "$API_URL/health"
```

Resposta esperada:

```json
{"status": "ok"}
```

Rota publica:

```sh
curl "$API_URL/public"
```

Resposta esperada:

```json
{"message": "Rota publica funcionando", "auth": false}
```

## Testando a rota privada

Primeiro, defina um email e uma senha para o usuario de teste:

```sh
EMAIL="lucas.lab@example.com"
read -s PASSWORD
```

Crie o usuario no Cognito:

```sh
aws cognito-idp sign-up \
  --client-id "$CLIENT_ID" \
  --username "$EMAIL" \
  --password "$PASSWORD" \
  --user-attributes Name=email,Value="$EMAIL" \
  --region "$REGION"
```

Confirme o usuario pelo admin da AWS:

```sh
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id "$USER_POOL_ID" \
  --username "$EMAIL" \
  --region "$REGION"
```

Gere um token JWT:

```sh
TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$CLIENT_ID" \
  --auth-parameters USERNAME="$EMAIL",PASSWORD="$PASSWORD" \
  --region "$REGION" \
  | jq -r '.AuthenticationResult.IdToken')
```

Chame a rota privada com o token:

```sh
curl "$API_URL/private" \
  -H "Authorization: Bearer $TOKEN"
```

Resposta esperada:

```json
{
  "message": "Rota privada funcionando",
  "auth": true,
  "user": {
    "sub": "...",
    "email": "lucas.lab@example.com",
    "username": "..."
  }
}
```

Sem token, a rota privada deve retornar erro de autorizacao:

```sh
curl -i "$API_URL/private"
```

## Alterando a Lambda

O Terraform gera o `lambda.zip` a partir de `lambda/handler.py` usando o provider `archive`.

Depois de alterar o handler, rode:

```sh
cd terraform
terraform apply
```

## Limpando o ambiente

Para remover os recursos criados na AWS:

```sh
cd terraform
terraform destroy
```

## Cuidados antes de commitar

Nao commite arquivos de estado ou artefatos locais:

- `terraform.tfstate`
- `terraform.tfstate.backup`
- `.terraform/`
- `lambda.zip`
- `__pycache__/`
- arquivos `.env` ou `.tfvars` com valores sensiveis

Esses arquivos ja estao cobertos pelo `.gitignore` deste projeto.
