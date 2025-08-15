from typing import Any
from fastmcp import Client
from mcp.types import CallToolResult, GetPromptResult, TextResourceContents, BlobResourceContents
from ...Application.Abstractions.base_mcp_client import BaseMCPClient

class MCPClient(BaseMCPClient):
    def __init__(self, host:str='127.0.0.1', port:int=5000, path:str='mcp'):
        self.__client:Client = Client(f"http://{host}:{port}/{path}")

    async def check_avaible(self):
        
        async with self.__client:
            return True if await self.__client.ping() else False
        
        return False
    
    async def load_env(self)->bool:
        try:
            if await self.check_avaible():
                async with self.__client:
                    self.tools = await self.__client.list_tools()
                    self.prompts = await self.__client.list_prompts()
                    self.resources = await self.__client.list_resources()
                
                return True
            
            return False
        except Exception as ex:
            print(f"ERROR:{ex}")
            return False

    async def call_tool(self, name_fn:str, param:dict[str, Any]={})->CallToolResult:
        if await self.check_avaible():
            async with self.__client:
                result = await self.__client.call_tool(name_fn, param)

        return result

    async def read_resource(self, uri:str)->list[TextResourceContents | BlobResourceContents]:
        if await self.check_avaible():
            async with self.__client:
                result = await self.__client.read_resource(uri)

        return result

    async def get_prompt(self, name:str, param:dict[str, Any]={})->GetPromptResult:
        if await self.check_avaible():
            async with self.__client:
                result = await self.__client.get_prompt(name, arguments=param)

        return result