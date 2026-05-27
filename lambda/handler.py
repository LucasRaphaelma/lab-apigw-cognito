import json

def lambda_handler(event, context):
    path = event.get("rawPath", "")
    claims = (
        event
        .get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )

    if path == "/public":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Rota publica funcionando",
                "auth": False
            })
        }

    if path == "/health":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "ok"
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Rota privada funcionando",
            "auth": True,
            "user": {
                "sub": claims.get("sub"),
                "email": claims.get("email"),
                "username": claims.get("username")
            }
        })
    }
