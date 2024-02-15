import abc
from typing import Dict
import boto3
from app.domain import model
from botocore import exceptions as boto3_exceptions


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def get_by_id(self, id_: str, table_name: str) -> Dict: ...

    @abc.abstractmethod
    def put(self, entity: model.Entity) -> None: ...


class DynamoRepository(AbstractRepository):
    def __init__(self, region_name: str) -> None:
        self._dn_client = boto3.resource("dynamodb", region_name=region_name)

    def put(self, entity: model.Entity) -> None:
        table = self._dn_client.Table(entity.table_name)
        table.put_item(Item=entity.model_dump())

    def get_by_id(self, id_: str, table_name: str) -> Dict:
        table = self._dn_client.Table(table_name)
        try:
            response = table.get_item(Key={"chat_id": id_})
        except boto3_exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return {}
            else:
                raise e
        return response.get("Item", {})
