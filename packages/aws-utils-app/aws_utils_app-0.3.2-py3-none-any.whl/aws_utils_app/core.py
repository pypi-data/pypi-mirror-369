class AWSAuth:
    """
    Classe de autenticação com a AWS.
    Attributes:
        aws_access_key_id(str) : ID de autenticação da API da AWS para utilização com boto3.
        aws_secret_access_key(str) : Chave de autenticação da API da AWS para utilização com boto3.
        region_name(str) Optional : Região para utilização da API da AWS.
    Methods:
        __init__ : Sessão autenticada do boto3 para utilização de API da AWS.
        get_client : Sessão do boto3.client.
        get_resource : Sessão do boto3.resource.
    """
    def __init__(self, aws_access_key_id:str, aws_secret_access_key:str, region_name:str="sa-east-1"):
        import boto3
        self.session = boto3.Session(
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = aws_secret_access_key,
            region_name = region_name
        )

    def get_client(self, service_name):
        return self.session.client(service_name)

    def get_resource(self, service_name):
        return self.session.resource(service_name)
        

class SNS:
    """
    Realiza publicação em tópicos SNS.
    Attributes:
        auth (required): Autenticação da AWS pela classe AWSAuth.
    Methods:
        publish_message : Realiza publicação de uma mensagem em um tópico SNS.
    """
    def __init__(self, auth: AWSAuth):
        self.sns_client = auth.get_client("sns")

    def publish_message(self, topic_arn:str, message:dict, attributes:dict=None):
        import json
        self.sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message if isinstance(message, dict) else json.loads(message)),
            MessageAttributes=attributes
        )


class SQS:
    """
    Realiza envio de mensagens para filas SQS.
    Attributes:
        auth (required): Autenticação da AWS pela classe AWSAuth.
    Methods:
        send_message : Envia uma mensagem para uma fila SQS.
    """
    def __init__(self, auth:AWSAuth):
        self.sqs_client = auth.get_client("sqs")

    def send_message(self, queue_url:str, message_body:dict, delay_seconds:int=0, attributes:dict=None):
        import json
        payload = {
            "QueueUrl": queue_url,
            "MessageBody": json.dumps(message_body),
            "DelaySeconds": delay_seconds
        }
        if attributes:
            payload["MessageAttributes"] = attributes

        return self.sqs_client.send_message(**payload)


class Lambda:
    """
    Realiza a invocação de funções Lambda.
    Attributes:
        auth (required): Autenticação da AWS pela classe AWSAuth.
    Methods:
        invoke_lambda : Realiza a invocação de determinada lambda.
    """
    def __init__(self, auth: AWSAuth):
        self.lambda_client = auth.get_client("lambda")

    def invoke_lambda(self, function_name:str, payload:dict, invocation_type:str="Event"):
        import json
        response = self.lambda_client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload).encode()
        )
        return response["Payload"].read().decode("utf-8")


class DynamoDB:
    """
    Realiza operações de dados no DynamoDB.
    Attributes:
        auth (required): Autenticação da AWS pela classe AWSAuth.
    Methods:
        put_item : Insere dados em uma determinada tabela no DynamoDB.
        get_item : Extrai dados de uma tabela a partir de determinada chave primária.
        update_items :  Atualiza um item do DynamoDB.
        
    """
    def __init__(self, auth: AWSAuth):
        self.dynamo_resource = auth.get_resource("dynamodb")

    def ajust_return_data(self, item):
        from boto3.dynamodb.types import TypeDeserializer
        from decimal import Decimal
        
        deserializer = TypeDeserializer()

        if isinstance(item, dict) and len(item) == 1 and list(item.keys())[0] in (
            "S", "N", "BOOL", "L", "M", "NULL", "SS", "NS", "BS"
        ):
            value = deserializer.deserialize(item)
            if isinstance(value, Decimal):
                return int(value) if value % 1 == 0 else float(value)
            return value

        elif isinstance(item, dict):
            return {k: self.ajust_return_data(v) for k, v in item.items()}

        elif isinstance(item, list):
            return [self.ajust_return_data(i) for i in item]

        elif isinstance(item, Decimal):
            return int(item) if item % 1 == 0 else float(item)

        else:
            return item

    def convert_data(self, obj):
        from decimal import Decimal
        if isinstance(obj, dict):
            return {k: self.convert_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_data(elem) for elem in obj]
        elif isinstance(obj, float):
            return Decimal(str(obj))
        else:
            return obj

    def put_item(self, table_name:str, item:dict):
        table = self.dynamo_resource.Table(table_name)
        response = table.put_item(Item=self.convert_data(item))
        return response

    def get_item(self, table_name:str, key:dict):
        table = self.dynamo_resource.Table(table_name)
        response = table.get_item(Key=key)
        item = response.get("Item")
        return self.ajust_return_data(item)

    def update_items(
        self,
        table_name: str,
        key: dict,
        updates: dict,
        list_attrs: list = None,
        ttl: int = None
    ):
        import time
        table = self.dynamo_resource.Table(table_name)
        list_attrs = list_attrs or []

        update_expressions = []
        expression_values = {}

        for attr, value in updates.items():
            if attr in list_attrs:
                update_expressions.append(
                    f"{attr} = list_append(if_not_exists({attr}, :empty_{attr}), :val_{attr})"
                )
                expression_values[f":empty_{attr}"] = []
                expression_values[f":val_{attr}"] = value if isinstance(value, list) else [value]
            else:
                update_expressions.append(f"{attr} = :val_{attr}")
                expression_values[f":val_{attr}"] = value

        if ttl is not None:
            update_expressions.append("created_at = if_not_exists(created_at, :created_at)")
            expression_values[":created_at"] = int(time.time()) + ttl

        update_expression = "SET " + ", ".join(update_expressions)

        return table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

    def delete_item(self, table_name: str, key: dict):
        table = self.dynamo_resource.Table(table_name)
        return table.delete_item(Key=key)


    def query_items(self, table_name:str, partition_key_value:any, partition_key_name:str="phone_id"):
        from boto3.dynamodb.conditions import Key
        table = self.dynamo_resource.Table(table_name)
        params = {
            "KeyConditionExpression": Key(partition_key_name).eq(partition_key_value),
        }
        query_return = table.query(**params)
        return [item for item in self.ajust_return_data(query_return.get("Items"))]


    def clear_attributes(self, table_name: str, key: dict, attributes: dict):
        """
        Limpa atributos de um item no DynamoDB, definindo como lista vazia, removendo, ou atribuindo valores fixos.
        """
        table = self.dynamo_resource.Table(table_name)
        set_exprs = []
        remove_exprs = []
        expr_values = {}

        for attr, val in attributes.items():
            if val == "REMOVE":
                remove_exprs.append(attr)
            elif val == []:
                set_exprs.append(f"{attr} = :empty_{attr}")
                expr_values[f":empty_{attr}"] = []
            else:
                set_exprs.append(f"{attr} = :val_{attr}")
                expr_values[f":val_{attr}"] = self.convert_data(val)

        expressions = []
        if set_exprs:
            expressions.append("SET " + ", ".join(set_exprs))
        if remove_exprs:
            expressions.append("REMOVE " + ", ".join(remove_exprs))

        update_expression = " ".join(expressions)

        return table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_values if expr_values else None
        )

    
class RDS:
    """
    Realiza operações com bancos RDS usando SQLAlchemy.
    Attributes:
        auth (required): Autenticação da AWS pela classe AWSAuth.
    Methods:
        insert_db : Insere dados em uma determinada tabela no RDS.
    """
    def __init__(self, connection_string: str):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine(
            connection_string,
            pool_size=20,
            max_overflow=2,
            pool_recycle=300,
            pool_pre_ping=True,
            pool_use_lifo=True,
            connect_args={"connect_timeout": 30},
            echo=False
        )
        self.Session = sessionmaker(bind=self.engine)

    def insert_db(self, data):
        with self.Session() as session:
            session.add_all(data)
            session.commit()


class S3:
    """
    Classe para manipulação de arquivos no Amazon S3.
    Attributes:
        auth (required): Autenticação da AWS pela classe AWSAuth.
    Methods:
        upload_file : Realiza o upload de um arquivo local para o S3.
        read_file_content : Lê o conteúdo de um arquivo armazenado no S3 (modo texto).
    """
    def __init__(self, auth: AWSAuth):
        self.s3_client = auth.get_client("s3")
        self.s3_resource = auth.get_resource("s3")

    def upload_file(self, local_path:str, s3_key:str, bucket_name:str="dados-bi-appmax"):
        self.s3_client.upload_file(local_path, bucket_name, s3_key)

    def read_file_content(self, s3_key: str, bucket_name:str="dados-bi-appmax"):
        obj = self.s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        return obj["Body"].read().decode("utf-8")