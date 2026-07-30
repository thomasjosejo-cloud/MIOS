from fyers_apiv3 import fyersModel

client_id = "IMWRJ91YE9-100"

secret_key = "0MOAPI9EKD"

redirect_uri = "http://127.0.0.1:3000"


auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJJTVdSSjkxWUU5IiwidXVpZCI6IjhjNTczYWZkMjFjOTQ5YmZhOWI0Y2ZlNTlhN2VhYTFlIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IkRUMDA0OTEiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJmMzcxNzhkMDRhOGE0MWIwODY4ZDYwYzFlZmQwZGM0ZWVkNzhmNDhmZmNlOWMxNjk2ZjBhZjE1OSIsImlzRGRwaUVuYWJsZWQiOiJZIiwiaXNNdGZFbmFibGVkIjoiWSIsImF1ZCI6IltcIng6MFwiXSIsImV4cCI6MTc4NTQ2NDM5NiwiaWF0IjoxNzg1NDM0Mzk2LCJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJuYmYiOjE3ODU0MzQzOTYsInN1YiI6ImF1dGhfY29kZSJ9._ZMplDf5NSB8DM0xFlhEFiQ7VQA8_WmM38ekAl2k45k"


session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type="code",
    grant_type="authorization_code",
)


session.set_token(auth_code)


response = session.generate_token()


print(response)
