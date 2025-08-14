from fastmcp import Client
from fastmcp.resources import Resource
from fastmcp.tools.tool import Tool
from fastmcp.prompts.prompt import Prompt
from mcp.types import CallToolResult, GetPromptResult, TextResourceContents, BlobResourceContents

from ...Application.Abstractions.base_mcp_client import BaseMCPClient


class MCPClient(BaseMCPClient):
    def __init__(self):
        self.__client:Client = None
        self.__tools:list[Tool] = []
        self.__prompts:list[Prompt] = []
        self.__resources:list[Resource] = []
    
    @classmethod
    async def create(cls:'MCPClient', host:str='127.0.0.1', port:int=5000, path:str='/mcp'):
        new_instance:'MCPClient' = cls()
        new_instance.__client = Client(f"http://{host}:{port}/{path}")
        
        await new_instance.check_avaible()

        return new_instance

    async def check_avaible(self):
        return True if await self.__client.ping() else False
    
    async def load_env(self)->bool:
        try:
            if self.check_avaible():
                self.__tools = await self.__client.list_tools()
                self.__prompts = await self.__client.list_prompts()
                self.__resources = await self.__client.list_resources()
                
                return True
            
            return False
        except Exception as ex:
            print(f"ERROR:{ex}")
            return False

    async def call_tool(self, name_fn:str, param:dict)->CallToolResult:
        result = await self.__client.call_tool(name_fn, param)

        return result
    
    async def read_resource(self, uri:str)->list[TextResourceContents | BlobResourceContents]:
        result = await self.__client.read_resource(uri)

        return result

    async def get_prompt(self, name:str, param:dict)->GetPromptResult:
        result = await self.__client.get_prompt(name, arguments=param)

        return result
