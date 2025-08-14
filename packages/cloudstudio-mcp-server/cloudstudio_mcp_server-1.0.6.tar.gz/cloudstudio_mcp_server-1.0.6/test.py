from src.mcp_deploy.mcp_handlers import createLiteapp, uploadfile
from src.mcp_deploy.models import File

# result = createLiteapp(api_token="eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjM2NzI5NCwiaWF0IjoxNzU0OTc4OTQwLCJleHAiOjE3NjI3MDQwMDAsImp0aSI6IjA3MzcwZThjLWRkMjctNGQ0Yi1iOTU1LWYzYjg1OTUxM2Y3YyJ9.OYHgEX3njwKVSsSsr7DBoFL2dCE0kiMEoe0IXe8_dcQ",title="1234")
# print(result)

upload = uploadfile(
    api_token="eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjM2NzI5NCwiaWF0IjoxNzU0OTc4OTQwLCJleHAiOjE3NjI3MDQwMDAsImp0aSI6IjA3MzcwZThjLWRkMjctNGQ0Yi1iOTU1LWYzYjg1OTUxM2Y3YyJ9.OYHgEX3njwKVSsSsr7DBoFL2dCE0kiMEoe0IXe8_dcQ",
    space_key="8d4c99e0dfe6421b97e5cd4c03b6bade",
    region="ap-shanghai",
    files=[
        File(
            save_path="/workspace/index.html",
            local_path="/Users/yechenglong/CodeBuddy/feixingqi/index.html"
        )
    ]
)
print(upload)