output "api_endpoint" {
  value = aws_apigatewayv2_api.this.api_endpoint
}

output "user_pool_id" {
  value = aws_cognito_user_pool.this.id
}

output "app_client_id" {
  value = aws_cognito_user_pool_client.this.id
}

output "region" {
  value = var.region
}