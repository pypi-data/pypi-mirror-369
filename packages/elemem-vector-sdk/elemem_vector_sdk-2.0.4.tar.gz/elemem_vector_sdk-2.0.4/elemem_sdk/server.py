# Python 3  
from http.server import HTTPServer, SimpleHTTPRequestHandler  
  
# 设置主机名和端口号  
hostName = "0.0.0.0"  
serverPort = 8008 
  
# 创建HTTP服务器实例  
server = HTTPServer((hostName, serverPort), SimpleHTTPRequestHandler)  
  
# 启动服务器  
print(f"服务器启动成功 http://{hostName}:{serverPort}")  
server.serve_forever()
