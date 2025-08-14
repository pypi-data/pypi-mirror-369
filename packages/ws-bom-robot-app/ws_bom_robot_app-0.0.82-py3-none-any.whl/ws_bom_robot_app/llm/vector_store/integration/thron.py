import asyncio, logging, aiohttp
from ws_bom_robot_app.llm.vector_store.integration.base import IntegrationStrategy
from langchain_core.documents import Document
from ws_bom_robot_app.llm.vector_store.loader.base import Loader
from typing import List, Union, Optional
from pydantic import BaseModel, Field, AliasChoices
import json
import os

class ThronParams(BaseModel):
  """
  ThronParams is a model that defines the parameters required for Thron integration.

  Attributes:
    app_id (str): The application ID for Thron.
    client_id (str): The client ID for Thron.
    client_secret (str): The client secret for Thron.
  """
  organization_name: str = Field(validation_alias=AliasChoices("organizationName","organization_name"))
  attribute_fields: Optional[List[str]] = Field(default=None, validation_alias=AliasChoices("attributeFields","attribute_fields"))
  client_id: str = Field(validation_alias=AliasChoices("clientId","client_id"))
  client_secret: str = Field(validation_alias=AliasChoices("clientSecret","client_secret"))

class Thron(IntegrationStrategy):
  def __init__(self, knowledgebase_path: str, data: dict[str, Union[str,int,list]]):
    super().__init__(knowledgebase_path, data)
    self.__data = ThronParams.model_validate(self.data)

  def working_subdirectory(self) -> str:
    return 'thron'

  async def run(self) -> None:
    _data = await self.__get_data()
    transformed_data = self.__transform_data(_data)
    json_file_path = os.path.join(self.working_directory, 'thron_data.json')
    with open(json_file_path, 'w', encoding='utf-8') as f:
      json.dump(transformed_data, f, indent=2, ensure_ascii=False)

  async def load(self) -> list[Document]:
    await self.run()
    await asyncio.sleep(1)
    return await Loader(self.working_directory).load()

  async def __get_auth_token(self) -> str:
    try:
      async with aiohttp.ClientSession() as session:
        auth_data = {
          "grant_type": "client_credentials",
          "client_id": self.__data.client_id,
          "client_secret": self.__data.client_secret
        }
        headers = {
          "accept": "application/json",
          "Content-Type": "application/x-www-form-urlencoded"
        }
        async with session.post(f"https://{self.__data.organization_name}.thron.com/api/v1/authentication/oauth2/token", data=auth_data, headers=headers) as response:
          result = await response.json()
          return result.get("access_token", "")
    except Exception as e:
      logging.error(f"Error fetching Thron auth token: {e}")
      return None

  async def __get_data(self) -> dict:
    try:
      token = await self.__get_auth_token()
      if not token:
        logging.error("Failed to obtain Thron authentication token.")
        return {}
      attribute_fields = ",".join(self.__data.attribute_fields) if self.__data.attribute_fields else ""
      async with aiohttp.ClientSession() as session:
        headers = {
          "accept": "application/json",
          "Authorization": f"Bearer {token}"
        }
        async with session.get(f"https://{self.__data.organization_name}.thron.com/api/v1/product-data/products?attributeFields=product_id,{attribute_fields}", headers=headers) as response:
          result = await response.json()
          return result.get("items", {})
    except Exception as e:
      logging.error(f"Error fetching Thron product data: {e}")
      return {}
    return []



  def __transform_data(self, data: dict) -> dict:
    _data = []
    for item in data:
      if item.get("hierarchyLevel") == "MASTER":
        # Iterate through variants to find the product_id
        for item_variant in data:
          if item_variant.get("hierarchyLevel") == "VARIANT":
            for attr in item.get("attributes", []):
              if attr.get("code") == "product_id" and attr.get("identifier") == item_variant.get("variation").get("master").split(":")[-1]:
                # Initialize variants list if it doesn't exist
                if "variants" not in item:
                  item["variants"] = []
                item["variants"].append(item_variant)
                _data.append(item)
                break
      elif item.get("hierarchyLevel") == "SIMPLE":
        _data.append(item)
    return _data
