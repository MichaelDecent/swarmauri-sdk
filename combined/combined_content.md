```swarmauri/README.md

# swarmaURI sdk

This repository includes core interfaces, standard ABCs, and standard concrete references of the SwarmaURI Framework.


## Core
- ABCs
- Utilities

## Standard
- Concrete Classes

## Community
- Concrete Classes that utilize third party plug-ins

## Experimental
- Tools in development



```

```swarmauri/__init__.py

__version__ = "0.1.25"
__long_desc__ = """
# swarmaURI sdk

This repository includes core interfaces, standard ABCs, and standard concrete references of the SwarmaURI Framework.


## Core
- ABCs
- Utilities

## Standard
- Concrete Classes

## Community
- Concrete Classes that utilize third party plug-ins

## Experimental
- Tools in development

"""

```

```swarmauri/community/__init__.py



```

```swarmauri/community/tools/__init__.py



```

```swarmauri/community/tools/base/__init__.py



```

```swarmauri/community/tools/concrete/__init__.py



```

```swarmauri/community/tools/concrete/EntityRecognitionTool.py

import json
from transformers import pipeline, logging as hf_logging
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

hf_logging.set_verbosity_error()

class EntityRecognitionTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter("text","string","The text for entity recognition",True)
        ]
        super().__init__(name="EntityRecognitionTool", 
                         description="Extracts named entities from text", 
                         parameters=parameters)
        

    def __call__(self, text: str) -> dict:
        try:
            self.nlp = pipeline("ner")
            entities = self.nlp(text)
            organized_entities = {}
            for entity in entities:
                if entity['entity'] not in organized_entities:
                    organized_entities[entity['entity']] = []
                organized_entities[entity['entity']].append(entity['word'])
            return json.dumps(organized_entities)
        except Exception as e:
            raise e
        finally:
            del self.nlp

```

```swarmauri/community/tools/concrete/GmailSendTool.py

import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class GmailSendTool(ToolBase):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, credentials_path: str, sender_email: str):
        """
        Initializes the GmailSendTool with a path to the credentials JSON file and the sender email.

        Parameters:
        credentials_path (str): The path to the Gmail service JSON file.
        sender_email (str): The email address being used to send emails.
        """
        
        parameters = [
            Parameter(
                name="recipients",
                type="string",
                description="The email addresses of the recipients, separated by commas",
                required=True
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True
            ),
            Parameter(
                name="htmlMsg",
                type="string",
                description="The HTML message to be sent as the email body",
                required=True
            )
        ]
        
        super().__init__(name="GmailSendTool", 
                         description="Sends an email using the Gmail API.",
                         parameters=parameters)
        self.credentials_path = credentials_path
        self.sender_email = sender_email
        

    def authenticate(self):
        """
        Authenticates the user and creates a Gmail API service for sending emails.
        """
        credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
        
        delegated_credentials = credentials.with_subject(self.sender_email)
        self.service = build('gmail', 'v1', credentials=delegated_credentials)

    def create_message(self, to: str, subject: str, message_text: str):
        """
        Create a MIMEText message for sending an email.

        Parameters:
        sender (str): The email address of the sender.
        to (str): The email address of the recipient.
        subject (str): The subject of the email.
        message_text (str): The HTML body of the email.

        Returns:
        The created MIMEText message.
        """
        message = MIMEMultipart('alternative')
        message['from'] = self.sender_email
        message['to'] = to
        message['subject'] = subject
        mime_text = MIMEText(message_text, 'html')
        message.attach(mime_text)
        raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}

    def __call__(self, recipients, subject, htmlMsg):
        """
        Sends an email to the specified recipients with the given subject and HTML message.
        
        Parameters:
        sender (str): The email address of the sender.
        recipients (str): The email address of the recipients, separated by commas.
        subject (str): The subject of the email.
        htmlMsg (str): The HTML content of the email body.

        Returns:
        The result of sending the email or an error message if the operation fails.
        """
        self.authenticate()
        try:
            message = self.create_message(recipients, subject, htmlMsg)
            sent_message = (self.service.users().messages().send(userId='me', body=message).execute())
            return f"Email sent successfully to {recipients}"

        except Exception as e:
            return f"An error occurred in sending the email: {e}"
        finally:
            del self.service

```

```swarmauri/community/tools/concrete/GmailReadTool.py

import os
import base64
import json
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

class GmailReadTool(ToolBase):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, credentials_path: str, sender_email: str):
        """
        Initializes the GmailReadTool with a path to the credentials JSON file.

        Parameters:
        credentials_path (str): The path to the Gmail service JSON file.
        """
        
        parameters = [
            Parameter(
                name="query",
                type="string",
                description='''The query to filter emails. For example, "is:unread" or "from:example@gmail.com" or "from:sender@company.com"''',
                required=True
            ),
            Parameter(
                name="max_results",
                type="integer",
                description='''The number of emails to return. Defaults to 10.'''
            )
        ]
        
        
        super().__init__(name="GmailReadTool", 
                         description="Read emails from a Gmail account.", 
                         parameters = parameters)
        self.credentials_path = credentials_path
        self.sender_email = sender_email
        

    def authenticate(self):
        """
        Authenticates the user and creates a Gmail API service.
        """
        credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
        
        delegated_credentials = credentials.with_subject(self.sender_email)
        self.service = discovery.build('gmail', 'v1', credentials=delegated_credentials)



    def __call__(self, query='', max_results=10):
        """
        Fetches emails from the authenticated Gmail account based on the given query.

        Parameters:
        query (str): The query to filter emails. For example, "is:unread".
        max_results (int): The maximum number of email messages to fetch.

        Returns:
        list: A list of email messages.
        """
        self.authenticate()
        try:
            # Call the Gmail API
            
            gmail_messages = self.service.users().messages()
            results = gmail_messages.list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            message_data = ""
            for message in messages:
                
                msg = gmail_messages.get(userId='me', id=message['threadId'], format="full").execute()
                headers = msg['payload']['headers']
                
                sender = next(header['value'] for header in headers if header['name'] == 'From')
                subject = next(header['value'] for header in headers if header['name'] == 'Subject')
                reply_to = next((header['value'] for header in headers if header['name'] == 'Reply-To'), subject)
                date_time = next(header['value'] for header in headers if header['name'] == 'Date')
                
                #part = msg['payload']['parts'][0]
                #data = part['body']['data']
                #decoded_data = base64.urlsafe_b64decode(data.encode('ASCII'))

                formatted_msg = f"\nsender:{sender} reply-to:{reply_to} subject: {subject} date_time:{date_time}"
                
                message_data += formatted_msg
                
            
            return message_data
        
        
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        
        finally:
            del self.service
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

```

```swarmauri/community/tools/concrete/SentimentAnalysisTool.py

from transformers import pipeline
from transformers import logging as hf_logging

from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

hf_logging.set_verbosity_error()

class SentimentAnalysisTool(ToolBase):
    def __init__(self):
        super().__init__("SentimentAnalysisTool", 
                         "Analyzes the sentiment of the given text.", 
                         parameters=[
                             Parameter("text", "string", "The text for sentiment analysis", True)
                         ])
        

    def __call__(self, text: str) -> str:
        try:
            self.analyzer = pipeline("sentiment-analysis")
            result = self.analyzer(text)
            return result[0]['label']
        except:
            raise
        finally:
            del self.analyzer

```

```swarmauri/community/tools/concrete/WebScrapingTool.py

import requests
from bs4 import BeautifulSoup
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter

class WebScrapingTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="URL of the link, website, webpage, etc... to scrape",
                required=True
            ),
            Parameter(
                name="selector",
                type="string",
                description="CSS selector to target specific elements",
                required=True
            )
        ]
        
        super().__init__(name="WebScrapingTool", 
                         description="This is a web scraping tool that you can utilize to scrape links, websites, webpages, etc... This tool uses python's requests and BeautifulSoup libraries to parse a URL using a CSS to target specific elements.", 
                         parameters=parameters)

    def __call__(self, url: str, selector: str) -> str:
        """
        Fetches content from the specified URL and extracts elements based on the provided CSS selector.
        
        Args:
            url (str): The URL of the webpage to scrape.
            selector (str): CSS selector to target specific elements in the webpage.

        Returns:
            str: Extracted text from the selector or an error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad requests (4xx or 5xx)

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            elements = soup.select(selector)
            extracted_text = '\n'.join([element.text for element in elements])
            return extracted_text
        except requests.RequestException as e:
            return f"Request Exception: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

```

```swarmauri/community/tools/concrete/DownloadPdfTool.py

import requests
from typing import Dict
from pathlib import Path
from ...standard.tools.base.ToolBase import ToolBase
from ...standard.tools.concrete.Parameter import Parameter

class DownloadPDFTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the PDF file to download",
                required=True
            ),
            Parameter(
                name="destination",
                type="string",
                description="The path where the PDF file will be saved",
                required=True
            )
        ]
        
        super().__init__(name="DownloadPDFTool",
                         description="Downloads a PDF from a specified URL and saves it to a specified path.",
                         parameters=parameters)

    def __call__(self, url: str, destination: str) -> Dict[str, str]:
        """
        Download the PDF from the specified URL and saves it to the given destination path.

        Parameters:
        - url (str): The URL from where to download the PDF.
        - destination (str): The local file path where the PDF should be saved.
        
        Returns:
        - Dict[str, str]: A dictionary containing the result message and the destination path.
        """
        try:
            # Send a GET request to the specified URL
            response = requests.get(url, stream=True)

            # Raise an HTTPError if the status code is not 200 (OK)
            response.raise_for_status()

            # Ensure destination directory exists
            Path(destination).parent.mkdir(parents=True, exist_ok=True)

            # Open a file at the specified destination path and write the content of the response to it
            with open(Path(destination), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            return {
                "message": "PDF downloaded successfully.",
                "destination": destination
            }

        except requests.exceptions.RequestException as e:
            # Handle requests-related errors
            return {"error": f"Failed to download PDF: {e}"}
        except IOError as e:
            # Handle file I/O errors
            return {"error": f"Failed to save PDF: {e}"}

```

```swarmauri/community/tools/concrete/PaCMAP.py

from ....core.tools.ITool import ITool
from ....standard.tools.concrete.Parameter import Parameter  # Update import path as necessary
import numpy as np
import pacmap  # Ensure pacmap is installed

class PaCMAPTool(ITool):
    """
    A tool for applying the PaCMAP method for dimensionality reduction.
    """

    def __init__(self):
        parameters = [
            Parameter(
                name="X",
                type="object",
                description="X (np.ndarray): The high-dimensional data points to reduce.",
                required=True
            ),
            Parameter(
                name="n_neighbors",
                type="integer",
                description="The size of local neighborhood (in terms of number of neighboring data points) used for manifold approximation.",
                required=False
            ),
            Parameter(
                name="n_components",
                type="integer",
                description="The dimension of the space into which to embed the data.",
                required=True
            ),
            Parameter(
                name="n_iterations",
                type="integer",
                description="The number of iterations used for optimization.",
                required=False
            )
        ]
        
        super().__init__(name="PaCMAPTool", 
                         description="Applies PaCMAP for dimensionality reduction.", 
                         parameters=parameters)

    def __call__(self, **kwargs) -> np.ndarray:
        """
        Applies the PaCMAP algorithm on the provided dataset.

        Parameters:
        - kwargs: Additional keyword arguments for the PaCMAP algorithm.

        Returns:
        - np.ndarray: The reduced dimension data points.
        """
        # Set default values for any unspecified parameters
        X = kwargs.get('X')
        n_neighbors = kwargs.get('n_neighbors', 30)
        n_components = kwargs.get('n_components', 2)
        n_iterations = kwargs.get('n_iterations', 500)
        
        # Instantiate the PaCMAP instance with specified parameters
        embedder = pacmap.PaCMAP(n_neighbors=n_neighbors, n_components=n_components, 
                                 n_iters=n_iterations, **kwargs)
                                 
        # Fit the model and transform the data
        X_reduced = embedder.fit_transform(X)

        return X_reduced

```

```swarmauri/community/tools/concrete/ZapierHookTool.py

import json
import requests
from typing import Dict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class ZapierHookTool(ToolBase):
    def __init__(self, auth_token, zap_id):
        parameters = [
            Parameter(
                name="payload",
                type="string",
                description="A Payload to send when triggering the Zapier webhook",
                required=True
            )
        ]
        super().__init__(name="ZapierTool", 
                         description="Tool to authenticate with Zapier and execute zaps.", 
                        parameters=parameters)
        self._auth_token = auth_token
        self._zap_id = zap_id

    def authenticate(self):
        """Set up the necessary headers for authentication."""
        self.headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json"
        }

    def execute_zap(self, payload: str):
        """Execute a zap with given payload.

        Args:
            zap_id (str): The unique identifier for the Zap to trigger.
            payload (dict): The data payload to send to the Zap.

        Returns:
            dict: The response from Zapier API.
        """
        self.authenticate()
        response = requests.post(f'https://hooks.zapier.com/hooks/catch/{self._zap_id}/',
                                     headers=self.headers, json={"data":payload})
        # Checking the HTTP response status for success or failure
        if response.status_code == 200:
            return json.dumps(response.json())
        else:
            response.raise_for_status()  # This will raise an error for non-200 responses

    def __call__(self, payload: str):
        """Enable the tool to be called with zap_id and payload directly."""
        return self.execute_zap(payload)

```

```swarmauri/community/retrievers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/community/retrievers/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/community/retrievers/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/community/retrievers/concrete/RedisDocumentRetriever.py

from typing import List
from redisearch import Client, Query
from ....core.documents.IDocument import IDocument
from ....standard.document_stores.concrete.ConcreteDocument import ConcreteDocument
from ....standard.retrievers.base.DocumentRetrieverBase import DocumentRetrieverBase

class RedisDocumentRetriever(DocumentRetrieverBase):
    """
    A document retriever that fetches documents from a Redis store.
    """
    
    def __init__(self, redis_idx_name, redis_host, redis_port):
        """
        Initializes a new instance of RedisDocumentRetriever.

        Args:
            redis_client (Redis): An instance of the Redis client.
        """
        self._redis_client = None
        self._redis_idx_name = redis_idx_name
        self._redis_host = redis_host
        self._redis_port = redis_port

    @property
    def redis_client(self):
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            self._redis_client = Client(self.redis_idx_name, host=self.redis_host, port=self.redis_port)
        return self._redis_client
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int, optional): The number of top relevant documents to retrieve. Defaults to 5.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        query_result = self.redis_client.search(Query(query).paging(0, top_k))
        
        documents = [
            ConcreteDocument(
                doc_id=doc.id,
                content=doc.text,  # Note: Adjust 'text' based on actual Redis document schema
                metadata=doc.__dict__  # Including full document fields and values in metadata
            )
            for doc in query_result.docs
        ]

        return documents


```

```swarmauri/community/document_stores/__init__.py



```

```swarmauri/community/document_stores/base/__init__.py



```

```swarmauri/community/document_stores/concrete/__init__.py



```

```swarmauri/community/document_stores/concrete/RedisDocumentStore.py

from typing import List, Optional
from ....standard.document_stores.base.DocumentStoreBase import DocumentStoreBase
from ....core.documents.IDocument import IDocument
import redis
import json
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


class RedisDocumentStore(DocumentStoreBase):
    def __init__(self, host, password, port, db):
        """Store connection details without initializing the Redis client."""
        self._host = host
        self._password = password
        self._port = port
        self._db = db
        self._redis_client = None  # Delayed initialization

    @property
    def redis_client(self):
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            print('here')
            self._redis_client = redis.Redis(host=self._host, 
                                             password=self._password, 
                                             port=self._port, 
                                             db=self._db)
            print('there')
        return self._redis_client

    def add_document(self, document: IDocument) -> None:
        
        data = document.as_dict()
        doc_id = data['id'] 
        del data['id']
        self.redis_client.json().set(doc_id, '$', json.dumps(data))

    def add_documents(self, documents: List[IDocument]) -> None:
        with self.redis_client.pipeline() as pipe:
            for document in documents:
                pipe.set(document.doc_id, document)
            pipe.execute()

    def get_document(self, doc_id: str) -> Optional[IDocument]:
        result = self.redis_client.json().get(doc_id)
        if result:
            return json.loads(result)
        return None

    def get_all_documents(self) -> List[IDocument]:
        keys = self.redis_client.keys('*')
        documents = []
        for key in keys:
            document_data = self.redis_client.get(key)
            if document_data:
                documents.append(json.loads(document_data))
        return documents

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        self.add_document(updated_document)

    def delete_document(self, doc_id: str) -> None:
        self.redis_client.delete(doc_id)
    
    def __getstate__(self):
        """Return the object state for serialization, excluding the Redis client."""
        state = self.__dict__.copy()
        state['_redis_client'] = None  # Exclude Redis client from serialization
        return state

    def __setstate__(self, state):
        """Restore the object state after serialization, reinitializing the Redis client."""
        self.__dict__.update(state)

```

```swarmauri/core/README.md

# Core Library

The Core Library provides the foundational interfaces and abstract base classes necessary for developing scalable and flexible machine learning agents, models, and tools. It is designed to offer a standardized approach to implementing various components of machine learning systems, such as models, parsers, conversations, and vector stores.

## Features

- **Models Interface**: Define and interact with predictive models.
- **Agents Interface**: Build and manage intelligent agents for varied tasks.
- **Tools Interface**: Develop tools with standardized execution and configuration.
- **Parsers and Conversations**: Handle and parse text data, manage conversations states.
- **Vector Stores**: Interface for vector storage and similarity searches.
- **Document Stores**: Manage the storage and retrieval of documents.
- **Retrievers and Chunkers**: Efficiently retrieve relevant documents and chunk large text data.

## Getting Started

To start developing with the Core Library, include it as a module in your Python project. Ensure you have Python 3.6 or later installed.

```python
# Example of using an abstract model interface from the Core Library
from swarmauri.core.models.IModel import IModel

class MyModel(IModel):
    # Implement the abstract methods here
    pass
```

## Documentation

For more detailed documentation on each interface and available abstract classes, refer to the [Docs](/docs) directory within the library.

## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, please submit a pull request.

## License

See `LICENSE` for more information.


```

```swarmauri/core/__init__.py



```

```swarmauri/core/models/__init__.py



```

```swarmauri/core/models/IPredict.py

from abc import ABC, abstractmethod

class IPredict(ABC):
    """
    Interface for making predictions with models.
    """

    @abstractmethod
    def predict(self, input_data) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

```

```swarmauri/core/models/IFit.py

from abc import ABC, abstractmethod

class IFit(ABC):
    """
    Interface for training models.
    """

    @abstractmethod
    def fit(self, X_train, y_train, epochs: int, batch_size: int) -> None:
        """
        Train the model on the provided dataset.
        """
        pass

```

```swarmauri/core/models/IModel.py

from abc import ABC, abstractmethod

class IModel(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the model.
        """
        pass

    @model_name.setter
    @abstractmethod
    def model_name(self, value: str) -> None:
        """
        Set the name of the model.
        """
        pass

```

```swarmauri/core/agent_apis/__init__.py

from .IAgentCommands import IAgentCommands
from .IAgentRouterCRUD import IAgentRouterCRUD

__all__ = ['IAgentCommands', 'IAgentRouterCRUD']

```

```swarmauri/core/agent_apis/IAgentCommands.py

from abc import ABC, abstractmethod
from typing import Callable, Any, List

class IAgentCommands(ABC):
    """
    Interface for the API object that enables a SwarmAgent to host various API routes.
    """


    @abstractmethod
    def invoke(self, request: Any) -> Any:
        """
        Handles invocation requests synchronously.
        
        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: The response payload.
        """
        pass

    @abstractmethod
    async def ainvoke(self, request: Any) -> Any:
        """
        Handles invocation requests asynchronously.
        
        Parameters:
            request (Any): The incoming request payload.

        Returns:
            Any: The response payload.
        """
        pass

    @abstractmethod
    def batch(self, requests: List[Any]) -> List[Any]:
        """
        Handles batched invocation requests synchronously.
        
        Parameters:
            requests (List[Any]): A list of incoming request payloads.

        Returns:
            List[Any]: A list of responses.
        """
        pass

    @abstractmethod
    async def abatch(self, requests: List[Any]) -> List[Any]:
        """
        Handles batched invocation requests asynchronously.
        
        Parameters:
            requests (List[Any]): A list of incoming request payloads.

        Returns:
            List[Any]: A list of responses.
        """
        pass

    @abstractmethod
    def stream(self, request: Any) -> Any:
        """
        Handles streaming requests.
        
        Parameters:
            request (Any): The incoming request payload.
        
        Returns:
            Any: A streaming response.
        """
        pass

    @abstractmethod
    def get_schema_config(self) -> dict:
        """
        Retrieves the schema configuration for the API.

        Returns:
            dict: The schema configuration.
        """
        pass

```

```swarmauri/core/agent_apis/IAgentRouterCRUD.py

from abc import ABC, abstractmethod
from typing import Callable, Any, Dict

class IAgentRouterCRUD(ABC):
    """
    Interface for managing API routes within a SwarmAgent.
    """
    
    @abstractmethod
    def create_route(self, path: str, method: str, handler: Callable[[Any], Any]) -> None:
        """
        Create a new route for the API.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method (e.g., 'GET', 'POST').
        - handler (Callable[[Any], Any]): The function that handles requests to this route.
        """
        pass
    
    @abstractmethod
    def read_route(self, path: str, method: str) -> Dict:
        """
        Retrieve information about a specific route.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        
        Returns:
        - Dict: Information about the route, including path, method, and handler.
        """
        pass
    
    @abstractmethod
    def update_route(self, path: str, method: str, new_handler: Callable[[Any], Any]) -> None:
        """
        Update the handler function for an existing route.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        - new_handler (Callable[[Any], Any]): The new function that handles requests to this route.
        """
        pass
    
    @abstractmethod
    def delete_route(self, path: str, method: str) -> None:
        """
        Delete a specific route from the API.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        """
        pass

```

```swarmauri/core/conversations/__init__.py



```

```swarmauri/core/conversations/IMaxSize.py

from abc import ABC, abstractmethod

class IMaxSize(ABC):

    @property
    @abstractmethod
    def max_size(self) -> int:
        """
        """
        pass

    @max_size.setter
    @abstractmethod
    def max_size(self, new_max_size: int) -> None:
        """ 
        """
        pass

```

```swarmauri/core/conversations/IConversation.py

from abc import ABC, abstractmethod
from typing import List, Optional
from ..messages.IMessage import IMessage

class IConversation(ABC):
    """
    Interface for managing conversations, defining abstract methods for
    adding messages, retrieving the latest message, getting all messages, and clearing history.
    """

    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history.
        """
        pass

    @abstractmethod
    def get_last(self) -> Optional[IMessage]:
        """
        Retrieves the latest message from the conversation history.
        """
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """
        Clears the conversation history.
        """
        pass

    @abstractmethod
    def as_dict(self) -> List[dict]:
        """
        Returns all messages from the conversation history as a list of dictionaries.
        """
        pass

```

```swarmauri/core/conversations/ISystemContext.py

from abc import ABC, abstractmethod
from typing import Optional
from ..messages.IMessage import IMessage

class ISystemContext(ABC):

    @property
    @abstractmethod
    def system_context(self) -> Optional[IMessage]:
        """
        An abstract property to get the system context message.
        Subclasses must provide an implementation for storing and retrieving system context.
        """
        pass

    @system_context.setter
    @abstractmethod
    def system_context(self, new_system_message: Optional[IMessage]) -> None:
        """
        An abstract property setter to update the system context.
        Subclasses must provide an implementation for how the system context is updated.
        This might be a direct string, which is converted to an IMessage instance, or directly an IMessage instance.
        """
        pass

```

```swarmauri/core/documents/__init__.py



```

```swarmauri/core/documents/IDocument.py

from abc import ABC, abstractmethod
from typing import Dict

class IDocument(ABC):
    @abstractmethod
    def __init__(self, doc_id, content, metadata: Dict):
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Get the document's ID.
        """
        pass

    @id.setter
    @abstractmethod
    def id(self, value: str) -> None:
        """
        Set the document's ID.
        """
        pass

    @property
    @abstractmethod
    def content(self) -> str:
        """
        Get the document's content.
        """
        pass

    @content.setter
    @abstractmethod
    def content(self, value: str) -> None:
        """
        Set the document's content.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict:
        """
        Get the document's metadata.
        """
        pass

    @metadata.setter
    @abstractmethod
    def metadata(self, value: Dict) -> None:
        """
        Set the document's metadata.
        """
        pass

    # Including the abstract methods __str__ and __repr__ definitions for completeness.
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass
    
    def __setitem__(self, key, value):
        """Allow setting items like a dict for metadata."""
        self.metadata[key] = value

    def __getitem__(self, key):
        """Allow getting items like a dict for metadata."""
        return self.metadata.get(key)

```

```swarmauri/core/documents/IEmbed.py

from abc import ABC, abstractmethod
from typing import Dict
from swarmauri.core.vectors.IVector import IVector

class IEmbed(ABC):
    @property
    @abstractmethod
    def embedding(self) -> IVector:
        """
        Get the document's embedding.
        """
        pass

    @embedding.setter
    @abstractmethod
    def embedding(self, value: IVector) -> None:
        """
        Set the document's embedding.
        """
        pass



```

```swarmauri/core/messages/IMessage.py

from abc import ABC, abstractmethod

class IMessage(ABC):
    """
    An abstract interface representing a general message structure.

    This interface defines the basic attributes that all
    messages should have, including type, name, and content, 
    and requires subclasses to implement representation and formatting methods.
    """
    @property
    @abstractmethod
    def role(self) -> str:
        pass
    
    @property
    @abstractmethod
    def content(self) -> str:
        pass

    @abstractmethod
    def as_dict(self) -> dict:
        """
        An abstract method that subclasses must implement to return a dictionary representation of the object.
        """
        pass

```

```swarmauri/core/messages/__init__.py

from .IMessage import IMessage

```

```swarmauri/core/parsers/__init__.py



```

```swarmauri/core/parsers/IParser.py

from abc import ABC, abstractmethod
from typing import List, Union, Any
from ..documents.IDocument import IDocument

class IParser(ABC):
    """
    Abstract base class for parsers. It defines a public method to parse input data (str or Message) into documents,
    and relies on subclasses to implement the specific parsing logic through protected and private methods.
    """

    @abstractmethod
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.
        
        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass



```

```swarmauri/core/prompts/__init__.py



```

```swarmauri/core/prompts/IPrompt.py

from abc import ABC, abstractmethod
from typing import Optional, Any

class IPrompt(ABC):
    """
    A base abstract class representing a prompt system.

    Methods:
        __call__: Abstract method that subclasses must implement to enable the instance to be called directly.
    """

    @abstractmethod
    def __call__(self, prompt: Optional[Any]) -> str:
        """
        Abstract method that subclasses must implement to define the behavior of the prompt when called.

        """
        pass


```

```swarmauri/core/agents/__init__.py



```

```swarmauri/core/agents/IAgentToolkit.py

from abc import ABC, abstractmethod
from swarmauri.core.toolkits.IToolkit import IToolkit


class IAgentToolkit(ABC):


    @property
    @abstractmethod
    def toolkit(self) -> IToolkit:
        pass
    
    @toolkit.setter
    @abstractmethod
    def toolkit(self) -> IToolkit:
        pass
    


```

```swarmauri/core/agents/IAgentConversation.py

from abc import ABC, abstractmethod
from swarmauri.core.conversations.IConversation import IConversation

class IAgentConversation(ABC):
    
    @property
    @abstractmethod
    def conversation(self) -> IConversation:
        """
        The conversation property encapsulates the agent's ongoing dialogue or interaction context.
        """
        pass

    @conversation.setter
    @abstractmethod
    def conversation(self) -> IConversation:
        pass

```

```swarmauri/core/agents/IAgentRetriever.py

from abc import ABC, abstractmethod
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve

class IAgentRetriever(ABC):
    
    @property
    @abstractmethod
    def retriever(self) -> IDocumentRetrieve:
        pass

    @retriever.setter
    @abstractmethod
    def retriever(self) -> IDocumentRetrieve:
        pass

```

```swarmauri/core/agents/IAgentParser.py

from abc import ABC, abstractmethod
from swarmauri.core.parsers.IParser import IParser 

class IAgentParser(ABC):
    
    @property
    @abstractmethod
    def parser(self) -> IParser:
        pass

    @parser.setter
    @abstractmethod
    def parser(self) -> IParser:
        pass

```

```swarmauri/core/agents/IAgentName.py

from abc import ABC, abstractmethod

class IAgentName(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The conversation property encapsulates the agent's ongoing dialogue or interaction context.
        """
        pass

    @name.setter
    @abstractmethod
    def name(self) -> str:
        pass

```

```swarmauri/core/agents/IAgent.py

from abc import ABC, abstractmethod
from typing import Any, Optional
from swarmauri.core.models.IModel import IModel

class IAgent(ABC):

    @abstractmethod
    def exec(self, input_data: Optional[Any]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass
    
    @property
    @abstractmethod
    def model(self) -> IModel:
        """
        The model property describes the computational model used by the agent.
        """
        pass
    
    @model.setter
    @abstractmethod
    def model(self) -> IModel:

        pass


```

```swarmauri/core/agents/IAgentDocument.py

from abc import ABC, abstractmethod
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class IAgentDocumentStore(ABC):
    
    @property
    @abstractmethod
    def document_store(self) -> IDocumentStore:
        pass

    @document_store.setter
    @abstractmethod
    def document_store(self) -> IDocumentStore:
        pass

```

```swarmauri/core/swarms/__init__.py



```

```swarmauri/core/swarms/ISwarm.py

from abc import ABC, abstractmethod
from typing import Any, List, Dict
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.chains.ICallableChain import ICallableChain

class ISwarm(ABC):
    """
    Interface for a Swarm, representing a collective of agents capable of performing tasks, executing callable chains, and adaptable configurations.
    """

    @abstractmethod
    def add_agent(self, agent: IAgent) -> None:
        """
        Adds an agent to the swarm.

        Args:
            agent (IAgent): The agent to be added.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Removes an agent from the swarm by ID.

        Args:
            agent_id (str): The unique identifier for the agent.
            
        Returns:
            bool: True if the agent was successfully removed; False otherwise.
        """
        pass

    @abstractmethod
    def execute_callable_chain(self, chain: ICallableChain, context: Dict[str, Any] = {}) -> Any:
        """
        Executes a callable chain within the swarm, optionally in a specific execution context.

        Args:
            chain (ICallableChain): The callable chain to be executed.
            context (Dict[str, Any]): Optional context and metadata for executing the chain.
        
        Returns:
            Any: The result of the chain execution.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> IAgent:
        """
        Retrieves an agent by its ID from the swarm.

        Args:
            agent_id (str): The unique identifier for the agent.

        Returns:
            IAgent: The agent associated with the given id.
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[IAgent]:
        """
        Lists all agents currently in the swarm.

        Returns:
            List[IAgent]: A list of agents in the swarm.
        """
        pass

    @abstractmethod
    def update_swarm_configuration(self, configuration: Dict[str, Any]) -> None:
        """
        Updates the swarm's configuration.

        Args:
            configuration (Dict[str, Any]): The new configuration settings for the swarm.
        """
        pass

    @abstractmethod
    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Retrieves the current status and health information of the swarm, including the number of agents, active tasks, etc.

        Returns:
            Dict[str, Any]: The current status of the swarm.
        """
        pass

```

```swarmauri/core/swarms/ISwarmComponent.py

from abc import ABC, abstractmethod

class ISwarmComponent(ABC):
    """
    Interface for defining a general component within a swarm system.
    """

    @abstractmethod
    def __init__(self, key: str, name: str):
        """
        Initializes a swarm component with a unique key and name.
        """
        pass

```

```swarmauri/core/swarms/ISwarmConfigurationExporter.py

from abc import ABC, abstractmethod
from typing import Dict
class ISwarmConfigurationExporter(ABC):

    @abstractmethod
    def to_dict(self) -> Dict:
        """
        Serializes the swarm configuration to a dictionary.

        Returns:
            Dict: The serialized configuration as a dictionary.
        """
        pass

    @abstractmethod
    def to_json(self) -> str:
        """
        Serializes the swarm configuration to a JSON string.

        Returns:
            str: The serialized configuration as a JSON string.
        """
        pass

    @abstractmethod
    def to_pickle(self) -> bytes:
        """
        Serializes the swarm configuration to a Pickle byte stream.

        Returns:
            bytes: The serialized configuration as a Pickle byte stream.
        """
        pass

```

```swarmauri/core/swarms/ISwarmFactory.py

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Type, Union
from swarmauri.core.swarms.ISwarm import ISwarm
from swarmauri.core.chains.ICallableChain import ICallableChain 
from swarmauri.core.agents.IAgent import IAgent 

class Step(NamedTuple):
    description: str
    callable: Callable  # Reference to the function to execute
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None

class CallableChainItem(NamedTuple):
    key: str  # Unique identifier for the item within the chain
    execution_context: Dict[str, Any]  # Execution context and metadata
    steps: List[Step]

class AgentDefinition(NamedTuple):
    type: str
    configuration: Dict[str, Any]
    capabilities: List[str]
    dependencies: List[str]
    execution_context: Dict[str, Any]

class FunctionParameter(NamedTuple):
    name: str
    type: Type
    default: Optional[Any] = None
    required: bool = True

class FunctionDefinition(NamedTuple):
    identifier: str
    parameters: List[FunctionParameter]
    return_type: Type
    execution_context: Dict[str, Any]
    callable_source: Callable
    
class ISwarmFactory(ABC):

    @abstractmethod
    def create_swarm(self, *args, **kwargs) -> ISwarm:
        """
        Creates and returns a new swarm instance configured with the provided arguments.
        """
        pass

    @abstractmethod
    def create_agent(self, agent_definition: AgentDefinition) -> IAgent:
        """
        Creates a new agent based on the provided enhanced agent definition.
        
        Args:
            agent_definition: An instance of AgentDefinition detailing the agent's setup.
        
        Returns:
            An instance or identifier of the newly created agent.
        """
        pass
    
    @abstractmethod
    def create_callable_chain(self, chain_definition: List[CallableChainItem]) -> ICallableChain:
        """
        Creates a new callable chain based on the provided definition.

        Args:
            chain_definition: Details required to build the chain, such as sequence of functions and arguments.

        Returns:
            ICallableChain: The constructed callable chain instance.
        """
        pass
    
    @abstractmethod
    def register_function(self, function_definition: FunctionDefinition) -> None:
        """
        Registers a function within the factory ecosystem, making it available for callable chains and agents.

        Args:
            function_definition: An instance of FunctionDefinition detailing the function's specification.
        """
        pass

    @abstractmethod
    def export_callable_chains(self, format_type: str = 'json') -> Union[dict, str, bytes]:
        """
        Exports configurations of all callable chains in the specified format.
        Supported formats: 'json', 'pickle'.

        Args:
            format_type (str): The format for exporting the configurations.

        Returns:
            Union[dict, str, bytes]: The callable chain configurations in the specified format.
        """
        pass

    @abstractmethod
    def load_callable_chains(self, chains_data, format_type: str = 'json'):
        """
        Loads callable chain configurations from given data.

        Args:
            chains_data (Union[dict, str, bytes]): Data containing callable chain configurations.
            format_type (str): The format of the provided chains data.
        """
        pass

    @abstractmethod
    def export_configuration(self, format_type: str = 'json') -> Union[dict, str, bytes]:
        """
        Exports the swarm's and agents' configurations in the specified format.
        Supported formats: 'json', 'pickle'. Default is 'json'.

        Args:
            format_type (str): The format for exporting the configurations.

        Returns:
            Union[dict, str, bytes]: The configurations in the specified format.
        """
        pass


```

```swarmauri/core/swarms/ISwarmAgentRegistration.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from swarmauri.core.agents.IAgent import IAgent

class IAgentRegistration(ABC):
    """
    Interface for registering agents with the swarm, designed to support CRUD operations on IAgent instances.
    """

    @abstractmethod
    def register_agent(self, agent: IAgent) -> bool:
        """
        Register a new agent with the swarm.

        Parameters:
            agent (IAgent): An instance of IAgent representing the agent to register.

        Returns:
            bool: True if the registration succeeded; False otherwise.
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, updated_agent: IAgent) -> bool:
        """
        Update the details of an existing agent. This could include changing the agent's configuration,
        task assignment, or any other mutable attribute.

        Parameters:
            agent_id (str): The unique identifier for the agent.
            updated_agent (IAgent): An updated IAgent instance to replace the existing one.

        Returns:
            bool: True if the update was successful; False otherwise.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm based on its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent to be removed.

        Returns:
            bool: True if the removal was successful; False otherwise.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[IAgent]:
        """
        Retrieve an agent's instance from its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent of interest.

        Returns:
            Optional[IAgent]: The IAgent instance if found; None otherwise.
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[IAgent]:
        """
        List all registered agents.

        Returns:
            List[IAgent]: A list containing instances of all registered IAgents.
        """
        pass

```

```swarmauri/core/toolkits/__init__.py



```

```swarmauri/core/toolkits/IToolkit.py

from typing import Dict
from abc import ABC, abstractmethod
from ..tools.ITool import ITool  # Ensure Tool is correctly imported from your tools package

class IToolkit(ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @property
    @abstractmethod
    def tools(self) -> Dict[str, ITool]:
        """
        An abstract property that should be implemented by subclasses to return the tools dictionary
        """
        pass

    @abstractmethod
    def add_tools(self, tools: Dict[str, ITool]):
        """
        An abstract method that should be implemented by subclasses to add multiple tools to the toolkit.
        """
        pass

    @abstractmethod
    def add_tool(self, tool: ITool):
        """
        An abstract method that should be implemented by subclasses to add a single tool to the toolkit.
        """
        pass

    @abstractmethod
    def remove_tool(self, tool_name: str):
        """
        An abstract method that should be implemented by subclasses to remove a tool from the toolkit by name.
        """
        pass

    @abstractmethod
    def get_tool_by_name(self, tool_name: str) -> ITool:
        """
        An abstract method that should be implemented by subclasses to retrieve a tool from the toolkit by name.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        An abstract method that should be implemented by subclasses to return the number of tools in the toolkit.
        """
        pass

```

```swarmauri/core/tools/__init__.py



```

```swarmauri/core/tools/ITool.py

from abc import ABC, abstractmethod

class ITool(ABC):
    
    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    @abstractmethod
    def description(self):
        pass
    
    @property
    @abstractmethod
    def parameters(self):
        pass
    
    @abstractmethod
    def as_dict(self):
        pass

    @abstractmethod
    def to_json(obj):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass







```

```swarmauri/core/tools/IParameter.py

from abc import ABC, abstractmethod
from typing import Optional, List, Any

class IParameter(ABC):
    """
    An abstract class to represent a parameter for a tool.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Abstract property for getting the name of the parameter.
        """
        pass

    @name.setter
    @abstractmethod
    def name(self, value: str):
        """
        Abstract setter for setting the name of the parameter.
        """
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """
        Abstract property for getting the type of the parameter.
        """
        pass

    @type.setter
    @abstractmethod
    def type(self, value: str):
        """
        Abstract setter for setting the type of the parameter.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Abstract property for getting the description of the parameter.
        """
        pass

    @description.setter
    @abstractmethod
    def description(self, value: str):
        """
        Abstract setter for setting the description of the parameter.
        """
        pass

    @property
    @abstractmethod
    def required(self) -> bool:
        """
        Abstract property for getting the required status of the parameter.
        """
        pass

    @required.setter
    @abstractmethod
    def required(self, value: bool):
        """
        Abstract setter for setting the required status of the parameter.
        """
        pass

    @property
    @abstractmethod
    def enum(self) -> Optional[List[Any]]:
        """
        Abstract property for getting the enum list of the parameter.
        """
        pass

    @enum.setter
    @abstractmethod
    def enum(self, value: Optional[List[Any]]):
        """
        Abstract setter for setting the enum list of the parameter.
        """
        pass

```

```swarmauri/core/utils/__init__.py



```

```swarmauri/core/utils/ITransactional.py

from abc import ABC, abstractmethod

class ITransactional(ABC):

    @abstractmethod
    def begin_transaction(self):
        """
        Initiates a transaction for a series of vector store operations.
        """
        pass
    
    @abstractmethod
    def commit_transaction(self):
        """
        Commits the current transaction, making all operations within the transaction permanent.
        """
        pass
    
    @abstractmethod
    def abort_transaction(self):
        """
        Aborts the current transaction, reverting all operations performed within the transaction.
        """
        pass

```

```swarmauri/core/vector_stores/ISimiliarityQuery.py

from abc import ABC, abstractmethod
from typing import List, Dict

class ISimilarityQuery(ABC):
    
    @abstractmethod
    def search_by_similarity_threshold(self, query_vector: List[float], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (List[float]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        pass

```

```swarmauri/core/vector_stores/IGradient.py

from abc import ABC, abstractmethod
from typing import List, Callable

class IGradient(ABC):
    """
    Interface for calculating the gradient of a scalar field.
    """

    @abstractmethod
    def calculate_gradient(self, scalar_field: Callable[[List[float]], float], point: List[float]) -> List[float]:
        """
        Calculate the gradient of a scalar field at a specific point.

        Parameters:
        - scalar_field (Callable[[List[float]], float]): The scalar field represented as a function
                                                         that takes a point and returns a scalar value.
        - point (List[float]): The point at which the gradient is to be calculated.

        Returns:
        - List[float]: The gradient vector at the specified point.
        """
        pass

```

```swarmauri/core/vector_stores/IAngleBetweenVectors.py

from abc import ABC, abstractmethod
from typing import List

class IAngleBetweenVectors(ABC):
    """
    Interface for calculating the angle between two vectors.
    """

    @abstractmethod
    def angle_between(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Method to calculate and return the angle in radians between two vectors.

        Parameters:
        - vector_a (List[float]): The first vector as a list of floats.
        - vector_b (List[float]): The second vector as a list of floats.

        Returns:
        - float: The angle between vector_a and vector_b in radians.

        Note: Implementations should handle the vectors' dimensionality and throw appropriate exceptions for incompatible vectors.
        """
        pass

```

```swarmauri/core/vector_stores/IDecompose.py

from abc import ABC, abstractmethod
from typing import Tuple, List
from swarmauri.core.vectors.IVector import IVector  # Assuming there's a base IVector interface for vector representations

class IDecompose(ABC):
    """
    Interface for decomposing a vector into components along specified basis vectors.
    This operation is essential in expressing a vector in different coordinate systems or reference frames.
    """

    @abstractmethod
    def decompose(self, vector: IVector, basis_vectors: List[IVector]) -> List[IVector]:
        """
        Decompose the given vector into components along the specified basis vectors.

        Parameters:
        - vector (IVector): The vector to be decomposed.
        - basis_vectors (List[IVector]): A list of basis vectors along which to decompose the given vector.

        Returns:
        - List[IVector]: A list of vectors, each representing the component of the decomposed vector along 
                         the corresponding basis vector in the `basis_vectors` list.
        """
        pass

```

```swarmauri/core/vector_stores/IDivergence.py

from abc import ABC, abstractmethod
from typing import List

class IDivergence(ABC):
    """
    Interface for calculating the divergence of a vector field.
    """

    @abstractmethod
    def calculate_divergence(self, vector_field: List[List[float]], point: List[float]) -> float:
        """
        Calculate the divergence of a vector field at a specific point.

        Parameters:
        - vector_field (List[List[float]]): A representation of the vector field as a list of vectors.
        - point (List[float]): The point at which the divergence is to be calculated.

        Returns:
        - float: The divergence value at the specified point.
        """
        pass

```

```swarmauri/core/vector_stores/IOrthogonalProject.py

from abc import ABC, abstractmethod
from typing import List

class IOrthogonalProject(ABC):
    """
    Interface for calculating the orthogonal projection of one vector onto another.
    """

    @abstractmethod
    def orthogonal_project(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Calculates the orthogonal projection of vector_a onto vector_b.
        
        Args:
            vector_a (List[float]): The vector to be projected.
            vector_b (List[float]): The vector onto which vector_a is orthogonally projected.
        
        Returns:
            List[float]: The orthogonal projection of vector_a onto vector_b.
        """
        pass

```

```swarmauri/core/vector_stores/IProject.py

from abc import ABC, abstractmethod
from typing import List

class IProject(ABC):
    """
    Interface for projecting one vector onto another.
    """

    @abstractmethod
    def project(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Projects vector_a onto vector_b.
        
        Args:
            vector_a (List[float]): The vector to be projected.
            vector_b (List[float]): The vector onto which vector_a is projected.
        
        Returns:
            List[float]: The projection of vector_a onto vector_b.
        """
        pass



```

```swarmauri/core/vector_stores/IReflect.py

from abc import ABC, abstractmethod
from typing import List

class IReflect(ABC):
    """
    Interface for reflecting a vector across a specified plane or axis.
    """

    @abstractmethod
    def reflect_vector(self, vector: List[float], normal: List[float]) -> List[float]:
        """
        Reflects a vector across a plane or axis defined by a normal vector.

        Parameters:
        - vector (List[float]): The vector to be reflected.
        - normal (List[float]): The normal vector of the plane across which the vector will be reflected.

        Returns:
        - List[float]: The reflected vector.
        """
        pass

```

```swarmauri/core/vector_stores/ISimilarity.py

from abc import ABC, abstractmethod
from typing import List, Tuple
from swarmauri.core.vectors.IVector import IVector

class ISimilarity(ABC):
    """
    Interface to define operations for computing similarity and distance between vectors.
    This interface is crucial for systems that need to perform similarity searches, clustering,
    or any operations where vector similarity plays a key role.
    """

    @abstractmethod
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors. The definition of similarity (e.g., cosine similarity)
        should be implemented in concrete classes.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        pass



```

```swarmauri/core/vector_stores/IVectorSpan.py

from abc import ABC, abstractmethod
from typing import List, Any

class IVectorSpan(ABC):
    """
    Interface for determining if a vector is within the span of a set of vectors.
    """

    @abstractmethod
    def in_span(self, vector: Any, basis_vectors: List[Any]) -> bool:
        """
        Checks if the given vector is in the span of the provided basis vectors.

        Parameters:
        - vector (Any): The vector to check.
        - basis_vectors (List[Any]): A list of vectors that might span the vector.

        Returns:
        - bool: True if the vector is in the span of the basis_vectors, False otherwise.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorArithmetic.py

from abc import ABC, abstractmethod
from typing import List

class IVectorArithmetic(ABC):
    @abstractmethod
    def add(self, vector1: List[float], vector2: List[float]) -> List[float]:
        """
        Vector addition of 'vector1' and 'vector2'.
        """
        pass
        
    @abstractmethod
    def subtract(self, vector1: List[float], vector2: List[float]) -> List[float]:
        """
        Vector subtraction of 'vector1' - 'vector2'.
        """
        pass
   
    @abstractmethod
    def multiply(self, vector: List[float], scalar: float) -> List[float]:
        """
        Scalar multiplication of 'vector' by 'scalar'.
        """
        pass
        
    @abstractmethod
    def divide(self, vector: List[float], scalar: float) -> List[float]:
        """
        Scalar division of 'vector' by 'scalar'.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorLinearCombination.py

from abc import ABC, abstractmethod
from typing import List, Any

class ILinearCombination(ABC):
    """
    Interface for creating a vector as a linear combination of a set of vectors.
    """

    @abstractmethod
    def linear_combination(self, coefficients: List[float], vectors: List[Any]) -> Any:
        """
        Computes the linear combination of the given vectors with the specified coefficients.

        Parameters:
        - coefficients (List[float]): A list of coefficients for the linear combination.
        - vectors (List[Any]): A list of vectors to be combined.

        Returns:
        - Any: The resulting vector from the linear combination.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorNorm.py

# core/vectors/IVectorNorm.py

from abc import ABC, abstractmethod
from typing import List, Union

class IVectorNorm(ABC):
    """
    Interface for calculating vector norms.
    Supports L1 norm, L2 norm, and Max norm calculations.
    """

    @abstractmethod
    def l1_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the L1 norm (Manhattan norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the L1 norm.

        Returns:
        - float: The L1 norm of the vector.
        """
        pass

    @abstractmethod
    def l2_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the L2 norm (Euclidean norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the L2 norm.

        Returns:
        - float: The L2 norm of the vector.
        """
        pass

    @abstractmethod
    def max_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the Max norm (infinity norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the Max norm.

        Returns:
        - float: The Max norm of the vector.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorRotate.py

from abc import ABC, abstractmethod
from typing import List

class IRotate(ABC):
    """
    Interface for rotating a vector.
    """
    
    @abstractmethod
    def rotate(self, vector: List[float], angle: float, axis: List[float] = None) -> List[float]:
        """
        Rotate the given vector by a specified angle around an axis (for 3D) or in a plane (for 2D).

        For 2D vectors, the axis parameter can be omitted.

        Args:
            vector (List[float]): The vector to rotate.
            angle (float): The angle of rotation in degrees.
            axis (List[float], optional): The axis of rotation (applicable in 3D).

        Returns:
            List[float]: The rotated vector.
        """
        pass


```

```swarmauri/core/vector_stores/IVectorBasisCheck.py

from abc import ABC, abstractmethod
from typing import List, Any

class IVectorBasisCheck(ABC):
    """
    Interface for checking if a given set of vectors forms a basis of the vector space.
    """

    @abstractmethod
    def is_basis(self, vectors: List[Any]) -> bool:
        """
        Determines whether the given set of vectors forms a basis for their vector space.

        Parameters:
        - vectors (List[Any]): A list of vectors to be checked.

        Returns:
        - bool: True if the vectors form a basis, False otherwise.
        """
        pass

```

```swarmauri/core/vector_stores/IVectorStore.py

from abc import ABC, abstractmethod
from typing import List, Dict, Union
from ..vectors.IVector import IVector

class IVectorStore(ABC):
    """
    Interface for a vector store that allows the storage, retrieval,
    and management of high-dimensional vector data used in search and machine learning applications.
    """

    @abstractmethod
    def add_vector(self, vector_id: str, vector: IVector, metadata: Dict = None) -> None:
        """
        Store a vector along with its identifier and optional metadata.

        Args:
            vector_id (str): Unique identifier for the vector.
            vector (List[float]): The high-dimensional vector to be stored.
            metadata (Dict, optional): Optional metadata related to the vector.
        """
        pass

    @abstractmethod
    def get_vector(self, vector_id: str) -> Union[List[float], None]:
        """
        Retrieve a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector.

        Returns:
            Union[List[float], None]: The vector associated with the given ID, or None if not found.
        """
        pass

    @abstractmethod
    def delete_vector(self, vector_id: str) -> None:
        """
        Delete a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector to be deleted.
        """
        pass

    @abstractmethod
    def update_vector(self, vector_id: str, new_vector: IVector, new_metadata: Dict = None) -> None:
        """
        Update the vector and metadata for a given vector ID.

        Args:
            vector_id (str): The unique identifier for the vector to update.
            new_vector (List[float]): The new vector data to store.
            new_metadata (Dict, optional): Optional new metadata related to the vector.
        """
        pass

```

```swarmauri/core/vector_stores/__init__.py



```

```swarmauri/core/document_stores/IDocumentStore.py

from abc import ABC, abstractmethod
from typing import List, Union
from ..documents.IDocument import IDocument

class IDocumentStore(ABC):
    """
    Interface for a Document Store responsible for storing, indexing, and retrieving documents.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Stores a single document in the document store.

        Parameters:
        - document (IDocument): The document to store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Stores multiple documents in the document store.

        Parameters:
        - documents (List[IDocument]): The list of documents to store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        """
        Retrieves a document by its ID.

        Parameters:
        - doc_id (str): The unique identifier for the document.

        Returns:
        - Union[IDocument, None]: The requested document, or None if not found.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieves all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Deletes a document from the document store by its ID.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass


    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Updates a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier for the document to update.
        - updated_document (IDocument): The updated document object.

        Note: It's assumed that the updated_document will retain the same doc_id but may have different content or metadata.
        """
        pass

    @abstractmethod
    def document_count(self) -> int:
        pass

```

```swarmauri/core/document_stores/__init__.py



```

```swarmauri/core/document_stores/IDocumentRetrieve.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.documents.IDocument import IDocument

class IDocumentRetrieve(ABC):
    """
    Abstract base class for document retrieval operations.
    
    This class defines the interface for retrieving documents based on a query or other criteria.
    Implementations may use various indexing or search technologies to fulfill these retrievals.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Parameters:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
            
        Returns:
            List[Document]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/core/chunkers/__init__.py

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 20:35:27 2024

@author: bigman
"""



```

```swarmauri/core/chunkers/IChunker.py

from abc import ABC, abstractmethod
from typing import List, Union, Any

class IChunker(ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """

    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[Any]:
        pass

```

```swarmauri/core/vectors/IVectorMeta.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class IVectorMeta(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Unique identifier for the vector. This ID can be used to reference the vector
        in a database or a vector store.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Optional metadata associated with the vector. Metadata can include additional information
        useful for retrieval, categorization, or description of the vector data.
        """
        pass



```

```swarmauri/core/vectors/IVectorTransform.py

from abc import ABC, abstractmethod
from .IVector import IVector

class IVectorTransform(ABC):
    """
    Interface for performing various transformations on vectors.
    """

    @abstractmethod
    def translate(self, translation_vector: IVector) -> IVector:
        """
        Translate a vector by a given translation vector.
        """
        pass

    @abstractmethod
    def rotate(self, angle: float, axis: IVector) -> IVector:
        """
        Rotate a vector around a given axis by a certain angle.
        """
        pass

    @abstractmethod
    def reflect(self, plane_normal: IVector) -> IVector:
        """
        Reflect a vector across a plane defined by its normal vector.
        """
        pass

    @abstractmethod
    def scale(self, scale_factor: float) -> IVector:
        """
        Scale a vector by a given scale factor.
        """
        pass

    @abstractmethod
    def shear(self, shear_factor: float, direction: IVector) -> IVector:
        """
        Shear a vector along a given direction by a shear factor.
        """
        pass

    @abstractmethod
    def project(self, plane_normal: IVector) -> IVector:
        """
        Project a vector onto a plane defined by its normal vector.
        """
        pass

```

```swarmauri/core/vectors/IVector.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class IVector(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    @property
    @abstractmethod
    def data(self) -> List[float]:
        """
        The high-dimensional data that the vector represents. It is typically a list of float values.
        """
        pass



```

```swarmauri/core/vectors/__init__.py



```

```swarmauri/core/vectors/IVectorProduct.py

from abc import ABC, abstractmethod
from typing import List, Tuple

class IVectorProduct(ABC):
    """
    Interface for various vector products including dot product, cross product,
    and triple products (vector and scalar).
    """

    @abstractmethod
    def dot_product(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate the dot product of two vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.

        Returns:
        - float: The dot product of the two vectors.
        """
        pass

    @abstractmethod
    def cross_product(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Calculate the cross product of two vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.

        Returns:
        - List[float]: The cross product as a new vector.
        """
        pass

    @abstractmethod
    def vector_triple_product(self, vector_a: List[float], vector_b: List[float], vector_c: List[float]) -> List[float]:
        """
        Calculate the vector triple product of three vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.
        - vector_c (List[float]): The third vector.

        Returns:
        - List[float]: The result of the vector triple product as a new vector.
        """
        pass

    @abstractmethod
    def scalar_triple_product(self, vector_a: List[float], vector_b: List[float], vector_c: List[float]) -> float:
        """
        Calculate the scalar triple product of three vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.
        - vector_c (List[float]): The third vector.

        Returns:
        - float: The scalar value result of the scalar triple product.
        """
        pass

```

```swarmauri/core/swarm_apis/__init__.py



```

```swarmauri/core/swarm_apis/ISwarmAPI.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISwarmAPI(ABC):
    """
    Interface for managing the swarm's API endpoints.
    """
    
    @abstractmethod
    def dispatch_request(self, request_data: Dict[str, Any]) -> Any:
        """
        Dispatches an incoming user request to one or more suitable agents based on their capabilities.

        Parameters:
        - request_data (Dict[str, Any]): Data related to the incoming request.

        Returns:
        - Any: Response from processing the request.
        """
        pass

    @abstractmethod
    def broadcast_request(self, request_data: Dict[str, Any]) -> Any:
        pass

```

```swarmauri/core/swarm_apis/IAgentRegistrationAPI.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from swarmauri.core.agents.IAgent import IAgent

class IAgentRegistrationAPI(ABC):
    """
    Interface for registering agents with the swarm, designed to support CRUD operations on IAgent instances.
    """

    @abstractmethod
    def register_agent(self, agent: IAgent) -> bool:
        """
        Register a new agent with the swarm.

        Parameters:
            agent (IAgent): An instance of IAgent representing the agent to register.

        Returns:
            bool: True if the registration succeeded; False otherwise.
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, updated_agent: IAgent) -> bool:
        """
        Update the details of an existing agent. This could include changing the agent's configuration,
        task assignment, or any other mutable attribute.

        Parameters:
            agent_id (str): The unique identifier for the agent.
            updated_agent (IAgent): An updated IAgent instance to replace the existing one.

        Returns:
            bool: True if the update was successful; False otherwise.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm based on its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent to be removed.

        Returns:
            bool: True if the removal was successful; False otherwise.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[IAgent]:
        """
        Retrieve an agent's instance from its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent of interest.

        Returns:
            Optional[IAgent]: The IAgent instance if found; None otherwise.
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[IAgent]:
        """
        List all registered agents.

        Returns:
            List[IAgent]: A list containing instances of all registered IAgents.
        """
        pass

```

```swarmauri/core/vectorizers/__init__.py

#

```

```swarmauri/core/vectorizers/IVectorize.py

from abc import ABC, abstractmethod
from typing import List, Union, Any
from swarmauri.core.vectors.IVector import IVector

class IVectorize(ABC):
    """
    Interface for converting text to vectors. 
    Implementations of this interface transform input text into numerical 
    vectors that can be used in machine learning models, similarity calculations, 
    and other vector-based operations.
    """
    @abstractmethod
    def fit(self, data: Union[str, Any]) -> List[IVector]:
        pass
    
    @abstractmethod
    def transform(self, data: Union[str, Any]) -> List[IVector]:
        pass

    @abstractmethod
    def fit_transform(self, data: Union[str, Any]) -> List[IVector]:
        pass

    @abstractmethod
    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> IVector:
        pass

```

```swarmauri/core/vectorizers/IFeature.py

from abc import ABC, abstractmethod
from typing import List, Any

class IFeature(ABC):

    @abstractmethod
    def extract_features(self) -> List[Any]:
        pass
    


```

```swarmauri/core/tracing/__init__.py



```

```swarmauri/core/tracing/ITraceContext.py

from abc import ABC, abstractmethod
from typing import Any

class ITraceContext(ABC):
    """
    Interface for a trace context, representing a single trace instance.
    This context carries the state and metadata of the trace across different system components.
    """

    @abstractmethod
    def get_trace_id(self) -> str:
        """
        Retrieves the unique identifier for this trace.

        Returns:
            str: The unique trace identifier.
        """
        pass

    @abstractmethod
    def add_attribute(self, key: str, value: Any):
        """
        Adds or updates an attribute associated with this trace.

        Args:
            key (str): The attribute key or name.
            value (Any): The value of the attribute.
        """
        pass

```

```swarmauri/core/tracing/ITracer.py

from swarmauri.core.tracing.ITraceContext import ITraceContext
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ITracer(ABC):
    """
    Interface for implementing distributed tracing across different components of the system.
    """

    @abstractmethod
    def start_trace(self, name: str, initial_attributes: Optional[Dict[str, Any]] = None) -> ITraceContext:
        """
        Starts a new trace with a given name and optional initial attributes.

        Args:
            name (str): Name of the trace, usually represents the operation being traced.
            initial_attributes (Optional[Dict[str, Any]]): Key-value pairs to be attached to the trace initially.

        Returns:
            ITraceContext: A context object representing this particular trace instance.
        """
        pass

    @abstractmethod
    def end_trace(self, trace_context: ITraceContext):
        """
        Marks the end of a trace, completing its lifecycle and recording its details.

        Args:
            trace_context (ITraceContext): The trace context to be ended.
        """
        pass

    @abstractmethod
    def annotate_trace(self, trace_context: ITraceContext, key: str, value: Any):
        """
        Adds an annotation to an existing trace, enriching it with more detailed information.

        Args:
            trace_context (ITraceContext): The trace context to annotate.
            key (str): The key or name of the annotation.
            value (Any): The value of the annotation.
        """
        pass

```

```swarmauri/core/tracing/IChainTracer.py

from abc import ABC, abstractmethod
from typing import Callable, List, Tuple, Dict, Any

class IChainTracer(ABC):
    """
    Interface for a tracer supporting method chaining through a list of tuples.
    Each tuple in the list contains: trace context, function, args, and kwargs.
    """

    @abstractmethod
    def process_chain(self, chain: List[Tuple[Any, Callable[..., Any], List[Any], Dict[str, Any]]]) -> "IChainTracer":
        """
        Processes a sequence of operations defined in a chain.

        Args:
            chain (List[Tuple[Any, Callable[..., Any], List[Any], Dict[str, Any]]]): A list where each tuple contains:
                - The trace context or reference required by the function.
                - The function (method of IChainTracer) to execute.
                - A list of positional arguments for the function.
                - A dictionary of keyword arguments for the function.

        Returns:
            IChainTracer: Returns self to allow further method chaining.
        """
        pass

```

```swarmauri/core/chains/ICallableChain.py

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple

CallableDefinition = Tuple[Callable, List[Any], dict]

class ICallableChain(ABC):
    @abstractmethod
    def __call__(self, *initial_args: Any, **initial_kwargs: Any) -> Any:
        """Executes the chain of callables."""
        pass

    @abstractmethod
    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: dict = None) -> None:
        """Adds a new callable to the chain."""
        pass

```

```swarmauri/core/chains/__init__.py

from swarmauri.core.chains.ICallableChain import ICallableChain

```

```swarmauri/core/chains/IChain.py

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from swarmauri.core.chains.IChainStep import IChainStep

class IChain(ABC):
    """
    Defines the interface for a Chain within a system, facilitating the organized
    execution of a sequence of tasks or operations. This interface is at the core of
    orchestrating operations that require coordination between multiple steps, potentially
    involving decision-making, branching, and conditional execution based on the outcomes
    of previous steps or external data.

    A chain can be thought of as a workflow or pipeline, where each step in the chain can
    perform an operation, transform data, or make decisions that influence the flow of
    execution.

    Implementors of this interface are responsible for managing the execution order,
    data flow between steps, and any dynamic adjustments to the execution based on
    runtime conditions.

    Methods:
        add_step: Adds a step to the chain.
        remove_step: Removes a step from the chain.
        execute: Executes the chain, potentially returning a result.
    """

    @abstractmethod
    def __init__(self, steps: List[IChainStep] = None, **configs):
        pass

    @abstractmethod
    def add_step(self, step: IChainStep, **kwargs) -> None:
        """
        Adds a new step to the chain. Steps are executed in the order they are added.
        Each step is represented by a Callable, which can be a function or method, with
        optional keyword arguments that specify execution aspects or data needed by the step.

        Parameters:
            step (IChainStep): The Callable representing the step to add to the chain.
            **kwargs: Optional keyword arguments that provide additional data or configuration
                      for the step when it is executed.
        """
        pass

    @abstractmethod
    def remove_step(self, step: IChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (IChainStep): The Callable representing the step to remove from the chain.
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Initiates the execution of the chain. This involves invoking each step in the order
        they have been added to the chain, passing control from one step to the next, and optionally
        aggregating or transforming results along the way.

        The execution process can incorporate branching, looping, or conditional logic based on the
        implementation, allowing for complex workflows to be represented and managed within the chain.

        Parameters:
            *args: Positional arguments passed to the first step in the chain. These can be data inputs
                   or other values required for the chain's execution.
            **kwargs: Keyword arguments that provide additional context, data inputs, or configuration
                      for the chain's execution. These can be passed to individual steps or influence
                      the execution flow of the chain.

        Returns:
            Any: The outcome of executing the chain. This could be a value produced by the final
                 step, a collection of outputs from multiple steps, or any other result type as
                 determined by the specific chain implementation.
        """
        pass

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass

```

```swarmauri/core/chains/IChainFactory.py

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep

class IChainFactory(ABC):
    """
    Interface for creating and managing execution chains within the system.
    """

    @abstractmethod
    def __init__(self, **configs):
        pass

    @abstractmethod
    def create_chain(self, steps: List[IChainStep] = None) -> IChain:
        pass
    
    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_chain_info(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_chain(self) -> IChain:
        pass
    
    @abstractmethod
    def set_chain(self, chain: IChain):
        pass
    
    @abstractmethod
    def reset_chain(self):
        pass
    
    @abstractmethod
    def get_chain_steps(self) -> List[IChainStep]:
        pass
    
    @abstractmethod
    def set_chain_steps(self, steps: List[IChainStep]):
        pass
    
    @abstractmethod
    def add_chain_step(self, step: IChainStep):
        pass
    
    @abstractmethod
    def remove_chain_step(self, key: str):
        pass
    
    
    @abstractmethod
    def get_configs(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def set_configs(self, **configs):
        pass
    
    @abstractmethod
    
    def get_config(self, key: str) -> Any:
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any):
        pass
    
    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_chain_info(self) -> Dict[str, Any]:
        pass    
    


```

```swarmauri/core/chains/IChainStep.py

from typing import List, Dict, Any, Callable

class IChainStep:
    """
    Represents a single step within an execution chain.
    """
    def __init__(self, 
        key: str, 
        method: Callable, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None, 
        ref: str = None):
        """
        Initialize a chain step.

        Args:
            key (str): Unique key or identifier for the step.
            method (Callable): The callable object (function or method) to execute in this step.
            args (List[Any], optional): Positional arguments for the callable.
            kwargs (Dict[str, Any], optional): Keyword arguments for the callable.
            ref (str, optional): Reference to another component or context variable, if applicable.
        """
        self.key = key
        self.method = method
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.ref = ref

```

```swarmauri/core/distances/__init__.py



```

```swarmauri/core/distances/IDistanceSimilarity.py

from abc import ABC, abstractmethod
from typing import List
from ..vectors.IVector import IVector

class IDistanceSimilarity(ABC):
    """
    Interface for computing distances and similarities between high-dimensional data vectors. This interface
    abstracts the method for calculating the distance and similarity, allowing for the implementation of various 
    distance metrics such as Euclidean, Manhattan, Cosine similarity, etc.
    """

    @abstractmethod
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed distance between vector_a and vector_b.
        """
        pass
    

    @abstractmethod
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> float:
        pass


    @abstractmethod
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors. The definition of similarity (e.g., cosine similarity)
        should be implemented in concrete classes.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        pass

    @abstractmethod
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> float:
        pass


```

```swarmauri/experimental/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/tools/LinkedInArticleTool.py

import requests
from ...standard.tools.base.ToolBase import ToolBase
from ...standard.tools.concrete.Parameter import Parameter

class LinkedInArticleTool(ToolBase):
    """
    A tool to post articles on LinkedIn using the LinkedIn API.
    """
    def __init__(self, access_token):
        """
        Initializes the LinkedInArticleTool with the necessary access token.
        
        Args:
            access_token (str): The OAuth access token for authenticating with the LinkedIn API.
        """
        super().__init__(name="LinkedInArticleTool",
                         description="A tool for posting articles on LinkedIn.",
                         parameters=[
                             Parameter(name="title", type="string", description="The title of the article", required=True),
                             Parameter(name="text", type="string", description="The body text of the article", required=True),
                             Parameter(name="visibility", type="string", description="The visibility of the article", required=True, enum=["anyone", "connectionsOnly"])
                         ])
        self.access_token = access_token
        
    def __call__(self, title: str, text: str, visibility: str = "anyone") -> str:
        """
        Posts an article on LinkedIn.

        Args:
            title (str): The title of the article.
            text (str): The body text of the article.
            visibility (str): The visibility of the article, either "anyone" or "connectionsOnly".

        Returns:
            str: A message indicating the success or failure of the post operation.
        """
        # Construct the request URL and payload according to LinkedIn API documentation
        url = 'https://api.linkedin.com/v2/ugcPosts'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "author": "urn:li:person:YOUR_PERSON_ID_HERE",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": title
                            },
                            "originalUrl": "URL_OF_THE_ARTICLE_OR_IMAGE",
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility.upper()
            }
        }
     
        # Make the POST request to LinkedIn's API
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return f"Article posted successfully: {response.json().get('id')}"
        else:
            return f"Failed to post the article. Status Code: {response.status_code} - {response.text}"

```

```swarmauri/experimental/tools/TwitterPostTool.py

from tweepy import Client

from ...standard.tools.base.ToolBase import ToolBase
from ...standard.tools.concrete.Parameter import Parameter

class TwitterPostTool(ToolBase):
    def __init__(self, bearer_token):
        # Initialize parameters necessary for posting a tweet
        parameters = [
            Parameter(
                name="status",
                type="string",
                description="The status message to post on Twitter",
                required=True
            )
        ]
        
        super().__init__(name="TwitterPostTool", description="Post a status update on Twitter", parameters=parameters)
        
        # Initialize Twitter API Client
        self.client = Client(bearer_token=bearer_token)

    def __call__(self, status: str) -> str:
        """
        Posts a status on Twitter.

        Args:
            status (str): The status message to post.

        Returns:
            str: A confirmation message including the tweet's URL if successful.
        """
        try:
            # Using Tweepy to send a tweet
            response = self.client.create_tweet(text=status)
            tweet_id = response.data['id']
            # Constructing URL to the tweet - Adjust the URL to match Twitter API v2 structure if needed
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            return f"Tweet successful: {tweet_url}"
        except Exception as e:
            return f"An error occurred: {e}"

```

```swarmauri/experimental/tools/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/tools/OutlookSendMailTool.py

import requests
from ....standard.tools.base.ToolBase import ToolBase
from ....standard.tools.concrete.Parameter import Parameter


class OutlookSendMailTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="recipient",
                type="string",
                description="The email address of the recipient",
                required=True
            ),
            Parameter(
                name="subject",
                type="string",
                description="The subject of the email",
                required=True
            ),
            Parameter(
                name="body",
                type="string",
                description="The HTML body of the email",
                required=True
            )
        ]
        
        super().__init__(name="OutlookSendMailTool", 
                         description="Sends an email using the Outlook service.",
                         parameters=parameters)

        # Add your Microsoft Graph API credentials and endpoint URL here
        self.tenant_id = "YOUR_TENANT_ID"
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def get_access_token(self):
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.scope),
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json().get("access_token")

    def __call__(self, recipient, subject, body):
        access_token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient
                        }
                    }
                ]
            }
        }

        send_mail_endpoint = f"{self.graph_endpoint}/users/{self.client_id}/sendMail"
        response = requests.post(send_mail_endpoint, json=email_data, headers=headers)
        if response.status_code == 202:
            return "Email sent successfully"
        else:
            return f"Failed to send email, status code {response.status_code}"

```

```swarmauri/experimental/tools/CypherQueryTool.py

from ..base.ToolBase import ToolBase
from .Parameter import Parameter
from neo4j import GraphDatabase
import json

class CypherQueryTool(ToolBase):
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        
        # Define only the 'query' parameter since uri, user, and password are set at initialization
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="The Cypher query to execute.",
                required=True
            )
        ]
        
        super().__init__(name="CypherQueryTool",
                         description="Executes a Cypher query against a Neo4j database.",
                         parameters=parameters)

    def _get_connection(self):
        return GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def __call__(self, query) -> str:
        # Establish connection to the database
        driver = self._get_connection()
        session = driver.session()

        # Execute the query
        result = session.run(query)
        records = result.data()

        # Close the connection
        session.close()
        driver.close()

        # Convert records to JSON string, assuming it's JSON serializable
        return json.dumps(records)

```

```swarmauri/experimental/tools/FileDownloaderTool.py

import requests
from ....core.tools.ToolBase import ToolBase
from ....core.tools.Parameter import Parameter


class FileDownloaderTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the file to download",
                required=True
            )
        ]
        
        super().__init__(name="FileDownloaderTool",
                         description="Downloads a file from a specified URL into memory.",
                         parameters=parameters)
    
    def __call__(self, url: str) -> bytes:
        """
        Downloads a file from the given URL into memory.
        
        Parameters:
        - url (str): The URL of the file to download.
        
        Returns:
        - bytes: The content of the downloaded file.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the request resulted in an error
            return response.content
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download file from '{url}'. Error: {e}")

```

```swarmauri/experimental/tools/SQLite3QueryTool.py

import sqlite3
from ...base.ToolBase import ToolBase
from ...concrete.Parameter import Parameter

class SQLite3QueryTool(ToolBase):
    def __init__(self, db_name: str):
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="SQL query to execute",
                required=True
            )
        ]
        super().__init__(name="SQLQueryTool", 
                         description="Executes an SQL query and returns the results.", 
                         parameters=parameters)
        self.db_name = db_name

    def __call__(self, query) -> str:
        """
        Execute the provided SQL query.

        Parameters:
        - query (str): The SQL query to execute.

        Returns:
        - str: The results of the SQL query as a string.
        """
        try:
            connection = sqlite3.connect(self.db_name)  # Connect to the specific database file
            cursor = connection.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            result = "\n".join(str(row) for row in rows)
        except Exception as e:
            result = f"Error executing query: {e}"
        finally:
            connection.close()
        
        return f"Query Result:\n{result}"

```

```swarmauri/experimental/conversations/__init__.py



```

```swarmauri/experimental/conversations/SemanticConversation.py

from abc import ABC, abstractmethod
from typing import Callable, Dict, Union
from ...core.messages.IMessage import IMessage
from ...core.conversations.IConversation import IConversation

class SemanticConversation(IConversation, ABC):
    """
    A concrete implementation of the Conversation class that includes semantic routing.
    Semantic routing involves analyzing the content of messages to understand their intent
    or category and then routing them to appropriate handlers based on that analysis.

    This class requires subclasses to implement the _analyze_message method for semantic analysis.
    """


    @abstractmethod
    def register_handler(self, category: str, handler: Callable[[IMessage], None]):
        """
        Registers a message handler for a specific semantic category.

        Args:
            category (str): The category of messages this handler should process.
            handler (Callable[[Message], None]): The function to call for messages of the specified category.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and routes it to the appropriate handler based on its semantic category.

        Args:
            message (Message): The message to be added and processed.
        """
        pass

    @abstractmethod
    def _analyze_message(self, message: IMessage) -> Union[str, None]:
        """
        Analyzes the content of a message to determine its semantic category.

        This method must be implemented by subclasses to provide specific logic for semantic analysis.

        Args:
            message (Message): The message to analyze.

        Returns:
            Union[str, None]: The semantic category of the message, if determined; otherwise, None.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the _analyze_message method to provide semantic analysis.")

    # Additional methods as needed for message retrieval, history management, etc., inherited from Conversation

```

```swarmauri/experimental/conversations/ConsensusBuildingConversation.py

from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages.IMessage import IMessage


class ConsensusBuildingMessage(IMessage):
    def __init__(self, sender_id: str, content: str, message_type: str):
        self._sender_id = sender_id
        self._content = content
        self._role = 'consensus_message'
        self._message_type = message_type

    @property
    def role(self) -> str:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    def as_dict(self) -> dict:
        return {
            "sender_id": self._sender_id,
            "content": self._content,
            "message_type": self._message_type
        }


class ConsensusBuildingConversation(IConversation):
    def __init__(self, topic: str, participants: list):
        self.topic = topic
        self.participants = participants  # List of agent IDs
        self._history = []  # Stores all messages exchanged in the conversation
        self.proposal_votes = {}  # Tracks votes for each proposal

    @property
    def history(self) -> list:
        return self._history

    def add_message(self, message: IMessage):
        if not isinstance(message, ConsensusBuildingMessage):
            raise ValueError("Only instances of ConsensusBuildingMessage are accepted")
        self._history.append(message)

    def get_last(self) -> IMessage:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self) -> None:
        self._history.clear()

    def as_dict(self) -> list:
        return [message.as_dict() for message in self._history]

    def initiate_consensus(self, initiator_id: str, proposal=None):
        """Starts the conversation with an initial proposal, if any."""
        initiate_message = ConsensusBuildingMessage(initiator_id, proposal, "InitiateConsensusMessage")
        self.add_message(initiate_message)

    def add_proposal(self, sender_id: str, proposal: str):
        """Adds a proposal to the conversation."""
        proposal_message = ConsensusBuildingMessage(sender_id, proposal, "ProposalMessage")
        self.add_message(proposal_message)

    def add_comment(self, sender_id: str, comment: str):
        """Adds a comment or feedback regarding a proposal."""
        comment_message = ConsensusBuildingMessage(sender_id, comment, "CommentMessage")
        self.add_message(comment_message)

    def vote(self, sender_id: str, vote: str):
        """Registers a vote for a given proposal."""
        vote_message = ConsensusBuildingMessage(sender_id, vote, "VoteMessage")
        self.add_message(vote_message)
        # Count the vote
        self.proposal_votes[vote] = self.proposal_votes.get(vote, 0) + 1

    def check_agreement(self):
        """
        Checks if there is a consensus on any proposal.
        A simple majority (>50% of the participants) is required for consensus.
        """
        consensus_threshold = len(self.participants) / 2  # Define consensus as a simple majority

        for proposal, votes in self.proposal_votes.items():
            if votes > consensus_threshold:
                # A consensus has been reached
                return True, f"Consensus reached on proposal: {proposal} with {votes} votes."

        # If no consensus is reached
        return False, "No consensus reached."

```

```swarmauri/experimental/conversations/ConsensusBuildingConversation.md

show an example implementation with a ConsensusBuildingConversation, 3 swarm agents with openaimodels that use gpt-4-0125-preview, and a prompttemplate that is used to start their consensus. the prompttemplate should trigger the first agent to make a proposal to solve a task.
To create a ConsensusBuildingConversation scenario with 3 Swarm Agents utilizing OpenAI models based on GPT-4 and initiating the conversation with a PromptTemplate to solve a task, let's structure it step-by-step. We'll start by defining the necessary components:

1. **ConsensusBuildingConversation** - Manages the flow of messages and consensus building among agents.
2. **Swarm Agents** - Three agents equipped with GPT-4-based models, OpenAIToolModel, to generate proposals and participate in consensus.
3. **PromptTemplate** - Used to kickstart the conversation with a specific task.

Here's an example implementation in Python:

```python
# File: OpenAIToolModel.py
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict
from openai import OpenAI

class OpenAIToolModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "gpt-4-0125-preview"):
        super().__init__(model_name)
        self.client = OpenAI(api_key=api_key)

    def predict(self, prompt: str) -> str:
        response = self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].text.strip()

# File: swarmauri/standard/prompts/concrete/PromptTemplate.py (already provided in the defined implementation)
from ..base.PromptBase import PromptBase

class PromptTemplate(PromptBase):
    def __init__(self, template: str = "", variables: Dict[str, str] = {}):
        super().__init__(template, variables)

    def __call__(self, variables: Dict[str, str] = {}):
        formatted_prompt = self.template.format(**variables)
        return formatted_prompt

# File: ConsensusBuildingConversation.py (provided in the example)
# Implementation of `ConsensusBuildingConversation` with method `initiate_consensus` to start the conversation

# Define Swarm Agents with OpenAIToolModel
class SwarmAgent:
    def __init__(self, model):
        self.model = model

    def contribute_to_conversation(self, prompt):
        proposal = self.model.predict(prompt)
        return proposal

# Set up PromptTemplate for initiating the consensus
task_description = "Solve the problem of efficiently distributing vaccines in a fair manner."
prompt_template = PromptTemplate(template="How should we approach: {task}?", variables={"task": task_description})

# Initialize OpenAI Models for each Agent (fake API key for demonstration)
api_key = "your_openai_api_key"
agent1 = SwarmAgent(OpenAIToolModel(api_key))
agent2 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant1"))
agent3 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant2"))

# Start the conversation with a task
initiating_prompt = prompt_template()
print(f"Initiating Prompt: {initiating_prompt}")

# Agent 1 makes the first proposal
first_proposal = agent1.contribute_to_conversation(initiating_prompt)
print(f"Agent 1 proposes: {first_proposal}")

# From here, you could continue the flow where Agent 2 and 3 provide feedback, additional proposals,
# and the conversation is steered towards building consensus as per `ConsensusBuildingConversation` logic.

```

In this example:
- We initialize three agents with the `OpenAIToolModel`, configured to use a GPT-4 model (assuming the `gpt-4-0125-preview` identifier and variants are placeholders for actual GPT-4 model identifiers).
- A `PromptTemplate` is defined and used to kickstart the conversation by generating an initiating prompt.
- Agent 1 reads the initiating prompt and makes the first proposal towards solving the task.
- Next steps (not fully implemented) involve other agents reacting to the proposal, contributing their ideas, and the group collectively moving towards a consensus.

This example provides a starting point. The actual consensus logic, including how proposals are voted on and a consensus is reached, would need to be implemented within the `ConsensusBuildingConversation` logic using methods such as `add_proposal`, `add_comment`, and `check_agreement`.

?  show the rest of the consensusbuildingconversation
Building upon the initial setup, we'll now flesh out the rest of the `ConsensusBuildingConversation` to demonstrate how agents might engage in a consensus-driven discussion, leveraging their unique capabilities or viewpoints generated by their respective GPT-4 models. This extension will include methods for agents to add proposals, comments, and votes, along with the mechanism to check for and reach consensus.

### Step 1: Expansion of ConsensusBuildingMessage and Conversation Classes

We'll start with expanding the `ConsensusBuildingMessage` type for various message kinds, and then work on the conversation logic to incorporate consensus mechanisms.

```python
# Considering ConsensusBuildingMessage and SharedConversation classes are defined,
# let's elaborate on different message types: Proposal and Comment.

class ConsensusBuildingMessage:
    def __init__(self, sender_id: str, content: str, message_type: str = "proposal"):
        self.sender_id = sender_id
        self.content = content
        self.type = message_type  # can be 'proposal', 'comment', or 'vote'
    
    def __str__(self):
        return f"[{self.type.upper()} by {self.sender_id}]: {self.content}"
```

### Step 2: Adding Proposals, Comments, and Votes

Now, let's implement functionalities for agents to add proposals, comments, and how the conversation tracks votes to reach a consensus.

```python
class ConsensusBuildingConversation:
    def __init__(self):
        self.messages = []
        self.votes = {}

    def add_message(self, message: ConsensusBuildingMessage):
        print(str(message))
        self.messages.append(message)
        if message.type == "vote":
            self.votes[message.content] = self.votes.get(message.content, 0) + 1

    def initiate_consensus(self, task_description):
        initiate_message = ConsensusBuildingMessage("admin", task_description, "task")
        self.add_message(initiate_message)

    def add_proposal(self, agent_id, proposal):
        proposal_message = ConsensusBuildingMessage(agent_id, proposal, "proposal")
        self.add_message(proposal_message)

    def add_comment(self, agent_id, comment):
        comment_message = ConsensusBuildingMessage(agent_id, comment, "comment")
        self.add_message(comment_message)

    def vote(self, agent_id, proposal):
        vote_message = ConsensusBuildingMessage(agent_id, proposal, "vote")
        self.add_message(vote_message)

    def check_agreement(self):
        consensus_threshold = 2  # For simplicity, consensus is reached if at least two votes match
        for proposal, count in self.votes.items():
            if count >= consensus_threshold:
                return True, proposal
        return False, ""
```

### Step 3: Running the Consensus-Building Process

Finally, you can simulate agents engaging in the conversation, proposing ideas, commenting, and eventually voting on proposals.

```python
# Initialize the conversation process
conversation = ConsensusBuildingConversation()
task = "Enhancing the efficiency of urban transportation systems."
conversation.initiate_consensus(task)

# Simulate agents contributing to the conversation
conversation.add_proposal("Agent1", "Proposal 1: Implement a dynamic routing system for public transportation.")
conversation.add_comment("Agent2", "Comment: Support Proposal 1 with smart traffic management.")
conversation.add_proposal("Agent3", "Proposal 2: Increase investment in bike-sharing infrastructure.")

# Voting on the proposals
conversation.vote("Agent1", "Proposal 1")
conversation.vote("Agent2", "Proposal 1")
conversation.vote("Agent3", "Proposal 2")

# Check and declare consensus
consensus_reached, consensus_proposal = conversation.check_agreement()
if consensus_reached:
    print(f"Consensus Reached on: {consensus_proposal}")
else:
    print("No Consensus Reached.")
```

This code simulates the process where three agents discuss a task, propose strategies, comment on proposals, and vote to decide on the best approach. A consensus is reported if at least two agents agree on a specific proposal.

This illustrative example focuses on the mechanics of the conversation and consensus process among agents using pre-defined roles and behaviors. In a real-world application, the agents’ contributions would be dynamically generated responses from the GPT-4 AI model based on the prompt provided, accounting for more complex interactions and decision-making processes.

?  show an example implementation with a ConsensusBuildingConversation, 3 swarm agents with openaimodels that use gpt-4-0125-preview, and a prompttemplate that is used to start their consensus. the prompttemplate should trigger the first agent to make a proposal to solve a task. show the complete conversation flow from first proposal to voting to reaching consensus.
To illustrate a complete flow from proposal generation to consensus within a simulated environment using 3 swarm agents, each equipped with an OpenAI GPT-4 model, and a PromptTemplate to kick-start their conversation, we'll set up a structured example. This example will encompass initiating discussions, generating proposals based on the first prompt, allowing agents to respond, and finally voting to reach consensus on how to proceed. 

Let's begin:

### 1. Defining the Base Setup

First, we define our setup, assuming the `OpenAIToolModel`, `PromptTemplate`, `ConsensusBuildingConversation`, and `ConsensusBuildingMessage` are implemented as previously described.

### 2. Initializing the Environment

```python
api_key = "your_openai_api_key"

# Defining three agents with their respective OpenAI models focused on a "gpt-4-0125-preview" and its variants
agent1 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview"))
agent2 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant1"))
agent3 = SwarmAgent(OpenAIToolModel(api_key, "gpt-4-0125-preview-variant2"))

# The task to be solved, initiating the conversation
task_description = "Devise an innovative strategy to improve global literacy rates."
prompt_template = PromptTemplate(template="Initial approach to address: {task}?", variables={"task": task_description})

# Creating the conversation object
conversation = ConsensusBuildingConversation(topic="Global Literacy Strategy", participants=["agent1", "agent2", "agent3"])
```

### 3. Conducting the Conversation

Agent 1 kicks off the conversation:

```python
initiating_prompt = prompt_template()
print(f"Agent 1 Initiating: {initiating_prompt}")

# Agent 1 makes the first proposal based on received prompt
first_proposal = agent1.contribute_to_conversation(initiating_prompt)
conversation.initiate_consensus(initiating_prompt)
conversation.add_proposal("agent1", first_proposal)

# Assume Agent 2 and 3 generate their responses based on the initial proposal
response_agent2 = agent2.contribute_to_conversation("Commenting on the first proposal: " + first_proposal)
conversation.add_comment("agent2", response_agent2)

response_agent3 = agent3.contribute_to_conversation("Suggest an alternative strategy to " + first_proposal)
conversation.add_proposal("agent3", response_agent3)
```

### 4. Voting Phase and Checking for Consensus

After discussion, it's time to vote on the proposed strategies. For simplicity, let's simulate the voting:

```python
# Voting - let's say Agent 2 supports Agent 1's initial proposal, and Agent 3 remains with its own.
conversation.vote("agent2", "Proposal from agent1")
conversation.vote("agent3", "Proposal from agent3")

# Agent 1 votes for its own proposal to push the example towards consensus
conversation.vote("agent1", "Proposal from agent1")
```

### 5. Reaching Consensus

We check whether the consensus has been reached following the votes.

```python
is_agreement, agreement_message = conversation.check_agreement()

if is_agreement:
    print(f"Consensus Reached: {agreement_message}")
else:
    print("The agents could not reach a consensus.")
```

### Notes:

- The actual text for proposals and comments generated will be based on GPT-4 responses to prompts crafted from the conversation context, which can include the initial task and responses from other agents.
- To fully implement this scenario, you'd need access to the OpenAI API with the specified GPT-4 model versions or adjust the model identifiers according to available versions.
- Voting logic in this example is simplified for clarity. In practice, each agent's decision-making process to vote could also be informed by additional GPT-4 generated insights or predefined logic.

This example outlines how swarm intelligence could function in a collaborative task-solving context, demonstrating the concept of consensus-building in multi-agent systems using AI-driven decision-making.

?  we need a mechanism for talking to the agent's exec function so that we can get the agent's vote. additionally we need a function so that we can parse the agent's vote and determine which proposal the agent is voting for
To facilitate the agents' ability to vote and parse these votes effectively, we will enhance our agent setup with a mechanism to communicate votes and a function to parse these votes to understand which proposal an agent is voting for. This involves two key enhancements:

1. **Adding Voting Capability to the Agent's `exec` Function**: The `exec` function will be extended to process input for making a proposal, commenting, or voting. Based on the context or the content of the input, the agent will decide whether to propose a new solution, comment on existing proposals, or vote for the best proposal.

2. **Vote Parsing Function**: A function to parse the agent's response to extract the vote. This function will analyze the agent's text response to determine which proposal the agent supports.

Here's how these enhancements can be implemented:

### Updating the Swarm Agent

The `SwarmAgent` class is extended to include a decision-making capability for voting. This example does not directly integrate OpenAI's GPT-4 because of the complexity and access requirements. However, it demonstrates how you might structure these capabilities.

```python
class SwarmAgent:
    def __init__(self, model, agent_id):
        self.model = model
        self.agent_id = agent_id

    def exec(self, context):
        """
        Process the given context and decide on making a proposal, comment, or casting a vote.
        """
        # Example: Decide based on context (This should be replaced with actual model invocation)
        if "proposal" in context:
            response = self.model.predict(context)
            return response
        elif "vote" in context:
            # Simulate decision making for voting
            vote = self.decide_vote(context)
            return vote
        else:
            return "I need more information."

    def decide_vote(self, context):
        """
        Simulate an analysis to decide on voting - in practice, this could involve analyzing proposals with the model.
        """
        # Dummy logic for demonstration - replace with genuine analysis based on model prediction or explicit logic
        if "Proposal from agent1" in context:
            return "Proposal from agent1"
        else:
            return "Undecided"

    def contribute_to_conversation(self, prompt):
        proposal = self.exec(prompt)
        return proposal
```

### Implementing Vote Parsing

A function is created to parse the explicit vote from an agent's response. This function identifies which proposal the agent supports based on its text response.

```python
def parse_agent_vote(agent_response):
    """
    Parses the agent's text response to extract the vote.

    Parameters:
    agent_response (str): The agent's response text from which to extract the vote.

    Returns:
    str: The extracted vote indicating the supported proposal.
    """
    # Example parsing logic
    if "Proposal from agent1" in agent_response:
        return "Proposal from agent1"
    elif "Proposal from agent2" in agent_response:
        return "Proposal from agent2"
    elif "Proposal from agent3" in agent_response:
        return "Proposal from agent3"
    return "Undecided"
```

### Example Usage

Assuming the conversation and proposals have been initiated and it’s time to vote:

```python
# Assuming the context for voting includes all proposals
voting_context = "Please vote on the proposals: Proposal from agent1, Proposal from agent2, Proposal from agent3"

# Each agent votes
for agent in [agent1, agent2, agent3]:
    agent_vote = agent.exec(voting_context)
    parsed_vote = parse_agent_vote(agent_vote)
    # Add the parsed vote to the conversation
    conversation.vote(agent.agent_id, parsed_vote)

# Check for consensus
is_agreement, agreement_message = conversation.check_agreement()
print(f"Consensus Reached: {is_agreement}, with agreement on: {agreement_message}" if is_agreement else "No consensus reached.")
```

This structure and mechanisms allow agents to make informed decisions based on the context provided, such as proposals made by other agents, and provide a manageable way to parse these decisions to understand voting preferences better. In a real-world scenario, the decision-making process (`decide_vote`) and vote parsing should be enhanced to intelligently analyze the conversation context and proposals to determine the agent's stance accurately.

```

```swarmauri/experimental/models/__init__.py



```

```swarmauri/experimental/models/SageMaker.py

import json
import boto3
from ...core.models.IModel import IModel


class AWSSageMakerModel(IModel):
    def __init__(self, access_key: str, secret_access_key: str, region_name: str, model_name: str):
        """
        Initialize the AWS SageMaker model with AWS credentials, region, and the model name.

        Parameters:
        - access_key (str): AWS access key ID.
        - secret_access_key (str): AWS secret access key.
        - region_name (str): The region where the SageMaker model is deployed.
        - model_name (str): The name of the SageMaker model.
        """
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.client = boto3.client('sagemaker-runtime',
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_access_key,
                                   region_name=region_name)
        super().__init__(model_name)

    def predict(self, payload: str, content_type: str='application/json') -> dict:
        """
        Generate predictions using the AWS SageMaker model.

        Parameters:
        - payload (str): Input data in JSON format.
        - content_type (str): The MIME type of the input data (default: 'application/json').
        
        Returns:
        - dict: The predictions returned by the model.
        """
        endpoint_name = self.model_name  # Assuming the model name is also the endpoint name
        response = self.client.invoke_endpoint(EndpointName=endpoint_name,
                                               Body=payload,
                                               ContentType=content_type)
        result = json.loads(response['Body'].read().decode())
        return result

```

```swarmauri/experimental/models/HierarchicalAttentionModel.py

import tensorflow as tf
from swarmauri.core.models.IModel import IModel
from typing import Any

class HierarchicalAttentionModel(IModel):
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None  # This will hold the TensorFlow model with attention

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str) -> None:
        self._model_name = value

    def load_model(self) -> None:
        """
        Here, we define and compile the TensorFlow model described earlier.
        """
        # The following code is adapted from the attention model example provided earlier
        vocab_size = 10000  # Size of the vocabulary
        embedding_dim = 256  # Dimension of the embedding layer
        sentence_length = 100  # Max length of a sentence
        num_sentences = 10  # Number of sentences in a document
        units = 128  # Dimensionality of the output space of GRU
        
        # Word-level attention layer
        word_input = tf.keras.layers.Input(shape=(sentence_length,), dtype='int32')
        embedded_word = tf.keras.layers.Embedding(vocab_size, embedding_dim)(word_input)
        word_gru = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(units, return_sequences=True))(embedded_word)
        word_attention_layer = tf.keras.layers.Attention(use_scale=True, return_attention_scores=True)
        word_attention_output, word_attention_weights = word_attention_layer([word_gru, word_gru], return_attention_scores=True)
        word_encoder_with_attention = tf.keras.Model(inputs=word_input, outputs=[word_attention_output, word_attention_weights])
        
        # Sentence-level attention layer
        sentence_input = tf.keras.layers.Input(shape=(num_sentences, sentence_length), dtype='int32')
        sentence_encoder_with_attention = tf.keras.layers.TimeDistributed(word_encoder_with_attention)(sentence_input)
        sentence_gru = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(units, return_sequences=True))(sentence_encoder_with_attention[0])
        sentence_attention_layer = tf.keras.layers.Attention(use_scale=True, return_attention_scores=True)
        sentence_attention_output, sentence_attention_weights = sentence_attention_layer([sentence_gru, sentence_gru], return_attention_scores=True)
        doc_representation = tf.keras.layers.Dense(units, activation='tanh')(sentence_attention_output)
        
        # Classifier
        classifier = tf.keras.layers.Dense(1, activation='sigmoid')(doc_representation)
        
        # The model
        self._model = tf.keras.Model(inputs=sentence_input, outputs=[classifier, sentence_attention_weights])
        self._model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def predict(self, input_data: Any) -> Any:
        """
        Predict method to use the loaded model for making predictions.

        This example assumes `input_data` is preprocessed appropriately for the model's expected input.
        """
        if self._model is None:
            raise ValueError("Model is not loaded. Call `load_model` before prediction.")
            
        # Predicting with the model
        predictions, attention_weights = self._model.predict(input_data)
        
        # Additional logic to handle and package the predictions and attention weights could be added here
        
        return predictions, attention_weights

```

```swarmauri/experimental/utils/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/utils/get_last_frame.py

import inspect

def child_function(arg):
    # Get the stack frame of the caller
    caller_frame = inspect.currentframe().f_back
    # Get the name of the caller function
    caller_name = caller_frame.f_code.co_name
    # Inspect the arguments of the caller function
    args, _, _, values = inspect.getargvalues(caller_frame)
    # Assuming the caller has only one argument for simplicity
    arg_name = args[0]
    arg_value = values[arg_name]
    print(f"Caller Name: {caller_name}, Argument Name: {arg_name}, Argument Value: {arg_value}")

def caller_function(l):
    child_function(l)

# Example usage
caller_function("Hello")



```

```swarmauri/experimental/utils/save_schema.py

import inspect
import random

class Storage:
    def __init__(self):
        self.logs = []

    def log(self, log_data):
        self.logs.append(log_data)

    def print_logs(self):
        for log in self.logs:
            print(log)

class Loggable:
    def __init__(self, name, storage):
        self.name = name
        self.storage = storage

    def log_call(self, *args, **kwargs):
        # Inspect the call stack to get the caller's details
        caller_frame = inspect.stack()[2]
        caller_name = inspect.currentframe().f_back.f_code.co_name
        #caller_name = caller_frame.function
        module = inspect.getmodule(caller_frame[0])
        module_name = module.__name__ if module else 'N/A'

        # Log all relevant details
        log_data = {
            'caller_name': caller_name,
            'module_name': module_name,
            'called_name': self.name,
            'called_function': caller_frame[3], # The function in which log_call was invoked
            'args': args,
            'kwargs': kwargs
        }
        self.storage.log(log_data)

class Caller(Loggable):
    def __init__(self, name, storage, others):
        super().__init__(name, storage)
        self.others = others

    def __call__(self, *args, **kwargs):
        if len(self.storage.logs)<10:
            self.log_call(*args, **kwargs)
            # Randomly call another without causing recursive calls
            if args:  # Ensures it's not the first call without actual target
                next_caller_name = random.choice([name for name in self.others if name != self.name])
                self.others[next_caller_name](self.name)

# Initialize storage and callers
storage = Storage()
others = {}

# Creating callers
alice = Caller('Alice', storage, others)
bob = Caller('Bob', storage, others)
charlie = Caller('Charlie', storage, others)
dan = Caller('Dan', storage, others)

others['Alice'] = alice
others['Bob'] = bob
others['Charlie'] = charlie
others['Dan'] = dan

# Simulate the calls
dan(1, taco=23)

# Print the logs
storage.print_logs()


```

```swarmauri/experimental/utils/ISerializable.md

Creating a system that allows for the serialization of object interactions, along with enabling replay and modification of replay schemas in Python, involves several key steps. This process includes capturing the execution state, serializing it, and then providing mechanisms for replay and modification. Here's how you could implement such a system:

### Step 1: Define Serializable Representations
For each class that participates in the interaction, define a method to serialize its state to a dictionary or a similar serializable format. Additionally, include a method to instantiate an object from this serialized state.

```python
class Serializable:
    def serialize(self):
        raise NotImplementedError("Serialization method not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Deserialization method not implemented")
```

Implement these methods in your classes. For example:

```python
class ToolAgent(Serializable):
    def serialize(self):
        # Simplified example, adapt according to actual attributes
        return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

    @classmethod
    def deserialize(cls, data):
        # This method should instantiate the object based on the serialized state.
        # Example assumes the presence of model_name in the serialized state.
        model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
        return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration
```

### Step 2: Capture Executions
Capture executions and interactions by logging or emitting events, including serialized object states and method invocations.

```python
import json

def capture_execution(obj, method_name, args, kwargs):
    # Serialize object state before execution
    pre_exec_state = obj.serialize()

    # Invoke the method
    result = getattr(obj, method_name)(*args, **kwargs)

    # Serialize object state after execution and return value
    post_exec_state = obj.serialize()
    return_value = json.dumps(result) if isinstance(result, dict) else str(result)

    return {
        "object": obj.__class__.__name__,
        "method": method_name,
        "pre_exec_state": pre_exec_state,
        "post_exec_state": post_exec_state,
        "args": args,
        "kwargs": kwargs,
        "return": return_value
    }
```

### Step 3: Serialize Execution Flow
Aggregate captured execution states and interactions into a serializable format (e.g., a list of dictionaries). You can write this data to a file or database.

```python
execution_flow = []
# Example: capturing execution of a single method call
execution_snapshot = capture_execution(agent, "exec", [user_input], {})
execution_flow.append(execution_snapshot)

with open('execution_flow.json', 'w') as f:
    json.dump(execution_flow, f)
```

### Step 4: Replay Functionality
Create functionality to read the serialized execution flow and replay it. This involves deserializing object states and invoking methods according to the captured flow.

```python
def replay_execution_flow(execution_flow):
    for action in execution_flow:
        obj = globals()[action["object"]].deserialize(action["pre_exec_state"])
        getattr(obj, action["method"])(*action["args"], **action["kwargs"])
        print(f"Replayed {action['object']}.{action['method']} with args {action['args']} and kwargs {action['kwargs']}")
```

### Step 5: Modification and Customization
To enable modification of the replay schema, you can provide an interface or utility that allows users to edit the `execution_flow.json` either manually or through a GUI. This might include changing method arguments, reordering actions, or swapping objects.

This example outlines a basic framework and would need to be expanded and adapted to match the specific requirements and complexities of your application, especially for more complex interactions and state management.

```

```swarmauri/experimental/utils/ISerializable.py


# class Serializable:
#     def serialize(self):
#         raise NotImplementedError("Serialization method not implemented")
    
#     @classmethod
#     def deserialize(cls, data):
#         raise NotImplementedError("Deserialization method not implemented")
        
        
# class ToolAgent(Serializable):
#     def serialize(self):
#         # Simplified example, adapt according to actual attributes
#         return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

#     @classmethod
#     def deserialize(cls, data):
#         # This method should instantiate the object based on the serialized state.
#         # Example assumes the presence of model_name in the serialized state.
#         model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
#         return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration

```

```swarmauri/experimental/docs/replay.md

Creating a system that allows for the serialization of object interactions, along with enabling replay and modification of replay schemas in Python, involves several key steps. This process includes capturing the execution state, serializing it, and then providing mechanisms for replay and modification. Here's how you could implement such a system:

### Step 1: Define Serializable Representations
For each class that participates in the interaction, define a method to serialize its state to a dictionary or a similar serializable format. Additionally, include a method to instantiate an object from this serialized state.

```python
class Serializable:
    def serialize(self):
        raise NotImplementedError("Serialization method not implemented")
    
    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError("Deserialization method not implemented")
```

Implement these methods in your classes. For example:

```python
class ToolAgent(Serializable):
    def serialize(self):
        # Simplified example, adapt according to actual attributes
        return {"type": self.__class__.__name__, "state": {"model_name": self.model.model_name}}

    @classmethod
    def deserialize(cls, data):
        # This method should instantiate the object based on the serialized state.
        # Example assumes the presence of model_name in the serialized state.
        model = OpenAIToolModel(api_key="api_key_placeholder", model_name=data["state"]["model_name"])
        return cls(model=model, conversation=None, toolkit=None)  # Simplify, omit optional parameters for illustration
```

### Step 2: Capture Executions
Capture executions and interactions by logging or emitting events, including serialized object states and method invocations.

```python
import json

def capture_execution(obj, method_name, args, kwargs):
    # Serialize object state before execution
    pre_exec_state = obj.serialize()

    # Invoke the method
    result = getattr(obj, method_name)(*args, **kwargs)

    # Serialize object state after execution and return value
    post_exec_state = obj.serialize()
    return_value = json.dumps(result) if isinstance(result, dict) else str(result)

    return {
        "object": obj.__class__.__name__,
        "method": method_name,
        "pre_exec_state": pre_exec_state,
        "post_exec_state": post_exec_state,
        "args": args,
        "kwargs": kwargs,
        "return": return_value
    }
```

### Step 3: Serialize Execution Flow
Aggregate captured execution states and interactions into a serializable format (e.g., a list of dictionaries). You can write this data to a file or database.

```python
execution_flow = []
# Example: capturing execution of a single method call
execution_snapshot = capture_execution(agent, "exec", [user_input], {})
execution_flow.append(execution_snapshot)

with open('execution_flow.json', 'w') as f:
    json.dump(execution_flow, f)
```

### Step 4: Replay Functionality
Create functionality to read the serialized execution flow and replay it. This involves deserializing object states and invoking methods according to the captured flow.

```python
def replay_execution_flow(execution_flow):
    for action in execution_flow:
        obj = globals()[action["object"]].deserialize(action["pre_exec_state"])
        getattr(obj, action["method"])(*action["args"], **action["kwargs"])
        print(f"Replayed {action['object']}.{action['method']} with args {action['args']} and kwargs {action['kwargs']}")
```

### Step 5: Modification and Customization
To enable modification of the replay schema, you can provide an interface or utility that allows users to edit the `execution_flow.json` either manually or through a GUI. This might include changing method arguments, reordering actions, or swapping objects.

This example outlines a basic framework and would need to be expanded and adapted to match the specific requirements and complexities of your application, especially for more complex interactions and state management.

---

To capture everything, including object instantiation like `api_key`, `conversation`, `model`, `tools`, and method calls (`exec`) in a fully comprehensive manner, we need to adopt an approach that not only captures method invocations but also objects as they are created and manipulated. This comprehensive capture and replay mechanism would involve the following stages:

### Stage 1: Capture

1. **Object Creation**: Capture the creation of all relevant objects along with their initial states and construction parameters.
2. **Method Calls**: Capture method invocations, including input parameters and return values.
3. **State Changes**: Optionally capture state changes to objects over time.

To implement this, we can use either decorators or a base class pattern that all relevent classes inherit from, which automates capturing information about object creation, method calls, and state.

#### Decorator for Capturing Method Calls and Object Creation

```python
import json
import functools

capture_log = []

def capture(cls):
    class Wrapper:
        def __init__(self, *args, **kwargs):
            capture_log.append({
                "type": "creation",
                "class_name": cls.__name__,
                "init_args": args,
                "init_kwargs": kwargs
            })
            self._instance = cls(*args, **kwargs)
        
        def __getattr__(self, name):
            attr = getattr(self._instance, name)
            if callable(attr):
                @functools.wraps(attr)
                def wrapper(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    capture_log.append({
                        "type": "method_call",
                        "class_name": cls.__name__,
                        "method_name": name,
                        "method_args": args,
                        "method_kwargs": kwargs,
                        "return_value": result
                    })
                    return result
                return wrapper
            return attr
    return Wrapper

def save_capture_log(filepath="execution_log.json"):
    with open(filepath, "w") as f:
        json.dump(capture_log, f, indent=4)
```

#### Applying the Decorator

Apply the `@capture` decorator to classes you want to monitor.

```python
@capture
class ToolAgent:
    # Your implementation
    
@capture
class OpenAIToolModel:
    # Your implementation

@capture
class Toolkit:
    # Your implementation

# Note: You may use different or additional capturing mechanisms for objects that don't fit well with this approach.
```

### Stage 2: Replay

Replaying involves reading the `execution_log.json`, recreating objects according to the log, and then calling the logged methods with their original parameters.

#### Basic Replay Function

```python
def replay_from_log(filepath="execution_log.json"):
    with open(filepath, "r") as f:
        execution_log = json.load(f)

    for action in execution_log:
        if action["type"] == "creation":
            cls = globals()[action["class_name"]]
            obj = cls(*action["init_args"], **action["init_kwargs"])
            # Additional logic to store a reference to this object for future method calls
        elif action["type"] == "method_call":
            # Logic to invoke method on previously created object
```

This solution outlines a mechanism to capture and replay execution flow, focusing on simplicity and adaptability. Depending on your specific requirements (e.g., handling static methods, managing object relationships), you may need to extend or modify this logic. Additionally, consider security implications when dynamically instantiating classes and executing methods, especially with inputs from external sources.

```

```swarmauri/experimental/parsers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/parsers/PDFToTextParser.py

import fitz  # PyMuPDF
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.ConcreteDocument import ConcreteDocument

class PDFtoTextParser(IParser):
    """
    A parser to extract text from PDF files.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses a PDF file and extracts its text content as Document instances.

        Parameters:
        - data (Union[str, Any]): The path to the PDF file.

        Returns:
        - List[IDocument]: A list with a single IDocument instance containing the extracted text.
        """
        # Ensure data is a valid str path to a PDF file
        if not isinstance(data, str):
            raise ValueError("PDFtoTextParser expects a file path in str format.")

        try:
            # Open the PDF file
            doc = fitz.open(data)
            text = ""

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            # Create a document with the extracted text
            document = ConcreteDocument(doc_id=str(hash(data)), content=text, metadata={"source": data})
            return [document]
        
        except Exception as e:
            print(f"An error occurred while parsing the PDF: {e}")
            return []


```

```swarmauri/experimental/vector_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/vector_stores/Word2VecDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/vector_stores/TriplesDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from rdflib import Graph, URIRef, Literal, BNode
from ampligraph.latent_features import ComplEx
from ampligraph.evaluation import train_test_split_no_unseen
from ampligraph.latent_features import EmbeddingModel
from ampligraph.utils import save_model, restore_model

from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.standard.vectorizers.concrete.AmpligraphVectorizer import AmpligraphVectorizer


class TriplesDocumentStore(IDocumentStore, IRetriever):
    def __init__(self, rdf_file_path: str, model_path: Optional[str] = None):
        """
        Initializes the TriplesDocumentStore.
        """
        self.graph = Graph()
        self.rdf_file_path = rdf_file_path
        self.graph.parse(rdf_file_path, format='turtle')
        self.documents = []
        self.vectorizer = AmpligraphVectorizer()
        self.model_path = model_path
        if model_path:
            self.model = restore_model(model_path)
        else:
            self.model = None
        self.metric = CosineDistance()
        self._load_documents()
        if not self.model:
            self._train_model()

    def _train_model(self):
        """
        Trains a model based on triples in the graph.
        """
        # Extract triples for embedding model
        triples = np.array([[str(s), str(p), str(o)] for s, p, o in self.graph])
        # Split data
        train, test = train_test_split_no_unseen(triples, test_size=0.1)
        self.model = ComplEx(batches_count=100, seed=0, epochs=20, k=150, eta=1,
                             optimizer='adam', optimizer_params={'lr': 1e-3},
                             loss='pairwise', regularizer='LP', regularizer_params={'p': 3, 'lambda': 1e-5},
                             verbose=True)
        self.model.fit(train)
        if self.model_path:
            save_model(self.model, self.model_path)

    def _load_documents(self):
        """
        Load documents into the store from the RDF graph.
        """
        for subj, pred, obj in self.graph:
            doc_id = str(hash((subj, pred, obj)))
            content = f"{subj} {pred} {obj}"
            document = Document(content=content, doc_id=doc_id, metadata={})
            self.documents.append(document)

    def add_document(self, document: IDocument) -> None:
        """
        Adds a single RDF triple document.
        """
        subj, pred, obj = document.content.split()  # Splitting content into RDF components
        self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.append(document)
        self._train_model()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Adds multiple RDF triple documents.
        """
        for document in documents:
            subj, pred, obj = document.content.split()  # Assuming each document's content is "subj pred obj"
            self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.extend(documents)
        self._train_model()

    # Implementation for get_document, get_all_documents, delete_document, update_document remains same as before
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve documents similar to the query string.
        """
        if not self.model:
            self._train_model()
        query_vector = self.vectorizer.infer_vector(model=self.model, samples=[query])[0]
        document_vectors = [self.vectorizer.infer_vector(model=self.model, samples=[doc.content])[0] for doc in self.documents]
        similarities = self.metric.distances(SimpleVector(data=query_vector), [SimpleVector(vector) for vector in document_vectors])
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/tracing/RemoteTrace.py

from __future__ import ITraceContext

import requests
import json
import uuid
from datetime import datetime

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.core.tracing.ITraceContext import ITraceContext

# Implementing the RemoteTraceContext class
class RemoteTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str):
        self.trace_id = trace_id
        self.name = name
        self.start_time = datetime.now()
        self.attributes = {}
        self.annotations = {}

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value):
        self.attributes[key] = value
        
    def add_annotation(self, key: str, value):
        self.annotations[key] = value

# Implementing the RemoteAPITracer class
class RemoteAPITracer(ITracer):
    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    def start_trace(self, name: str, initial_attributes=None) -> 'RemoteTraceContext':
        trace_id = str(uuid.uuid4())
        context = RemoteTraceContext(trace_id, name)
        if initial_attributes:
            for key, value in initial_attributes.items():
                context.add_attribute(key, value)
        return context

    def end_trace(self, trace_context: 'RemoteTraceContext'):
        trace_context.end_time = datetime.now()
        # Pretending to serialize the context information to JSON
        trace_data = {
            "trace_id": trace_context.get_trace_id(),
            "name": trace_context.name,
            "start_time": str(trace_context.start_time),
            "end_time": str(trace_context.end_time),
            "attributes": trace_context.attributes,
            "annotations": trace_context.annotations
        }
        json_data = json.dumps(trace_data)
        # POST the serialized data to the remote REST API
        response = requests.post(self.api_endpoint, json=json_data)
        if not response.ok:
            raise Exception(f"Failed to send trace data to {self.api_endpoint}. Status code: {response.status_code}")

    def annotate_trace(self, trace_context: 'RemoteTraceContext', key: str, value):
        trace_context.add_annotation(key, value)

```

```swarmauri/experimental/tracing/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/chains/ChainOrderStrategy.py

from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainOrderStrategy(IChainOrderStrategy):
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        """
        Orders the chain steps in reverse order.

        Args:
            steps (List[IChainStep]): The original list of chain steps to be ordered.

        Returns:
            List[IChainStep]: List of chain steps in order.
        """
        # Reverse the list of steps.
        steps = list(steps)
        return steps

```

```swarmauri/experimental/chains/ChainOrderStrategyBase.py

from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainOrderStrategyBase(IChainOrderStrategy):
    """
    A base implementation of the IChainOrderStrategy interface.
    """

    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        """
        Default implementation doesn't reorder steps but must be overridden by specific strategies.
        """
        return steps

```

```swarmauri/experimental/chains/ChainProcessingStrategy.py

from typing import List, Any
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainProcessingStrategy(IChainProcessingStrategy):
    def execute_steps(self, steps: List[IChainStep]) -> Any:
        """
        Executes the given list of ordered chain steps based on the specific strategy 
        and collects their results.

        Args:
            steps (List[IChainStep]): The ordered list of chain steps to be executed.
        
        Returns:
            Any: The result of executing the steps. This could be tailored as per requirement.
        """
        results = []
        for step in steps:
            result = step.method(*step.args, **step.kwargs)
            results.append(result)
        return results

```

```swarmauri/experimental/chains/ChainProcessingStrategyBase.py

from typing import List
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainProcessingStrategyBase(IChainProcessingStrategy):
    """
    A base implementation of the IChainProcessingStrategy interface.
    """
    
    def execute_steps(self, steps: List[IChainStep]):
        """
        Default implementation which should be overridden by specific processing strategies.
        """
        for step in steps:
            print(step)
            step.method(*step.args, **step.kwargs)

```

```swarmauri/experimental/chains/IChainOrderStrategy.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.chains.IChainStep import IChainStep

# Defines how chain steps are ordered
class IChainOrderStrategy(ABC):
    @abstractmethod
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        pass

```

```swarmauri/experimental/chains/IChainProcessingStrategy.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.chains.IChainStep import IChainStep

class IChainProcessingStrategy(ABC):
    """
    Interface for defining the strategy to process the execution of chain steps.
    """
    
    @abstractmethod
    def execute_steps(self, steps: List[IChainStep]):
        """
        Executes the given list of ordered chain steps based on the specific strategy.
        
        Parameters:
            steps (List[IChainStep]): The ordered list of chain steps to be executed.
        """
        pass

```

```swarmauri/experimental/chains/MatrixOrderStrategy.py

from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class MatrixOrderStrategy(IChainOrderStrategy):
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        # Assuming 'steps' are already organized in a matrix-like structure
        ordered_steps = self.arrange_matrix(steps)
        return ordered_steps

    def arrange_matrix(self, steps_matrix):
        # Implement the logic to arrange/order steps based on matrix positions.
        # This is just a placeholder. The actual implementation would depend on the matrix specifications and task dependencies.
        return steps_matrix

```

```swarmauri/experimental/chains/MatrixProcessingStrategy.py

import asyncio
from typing import List, Any
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class MatrixProcessingStrategy(IChainProcessingStrategy):
    async def execute_steps(self, steps: List[IChainStep]) -> Any:
        # Launch tasks asynchronously, maintaining the matrix structure
        results = await self.execute_matrix(steps)
        return results

    async def execute_matrix(self, matrix):
        matrix_results = []

        # Example: Execute tasks row by row, waiting for each row to complete before moving on.
        for row in matrix:
            row_results = await asyncio.gather(*[step.method(*step.args, **step.kwargs) for step in row])
            matrix_results.append(row_results)
            # Optionally, add a call to a row callback here

        # After processing all rows, you may call a final matrix callback
        # This could be a place for final aggregation or analysis of all results
        return matrix_results

```

```swarmauri/experimental/chains/TypeAgnosticCallableChain.py

from typing import Any, Callable, List, Dict, Optional, Tuple, Union

CallableDefinition = Tuple[Callable, List[Any], Dict[str, Any], Union[str, Callable, None]]

class TypeAgnosticCallableChain:
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        self.callables = callables if callables is not None else []

    @staticmethod
    def _ignore_previous(_previous_result, *args, **kwargs):
        return args, kwargs

    @staticmethod
    def _use_first_arg(previous_result, *args, **kwargs):
        return [previous_result] + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_first(previous_result, *args, **kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result) + list(args), kwargs

    @staticmethod
    def _use_all_previous_args_only(previous_result, *_args, **_kwargs):
        if not isinstance(previous_result, (list, tuple)):
            previous_result = [previous_result]
        return list(previous_result), {}

    @staticmethod
    def _add_previous_kwargs_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**kwargs, **previous_result}

    @staticmethod
    def _add_previous_kwargs_no_overwrite(previous_result, args, kwargs):
        if not isinstance(previous_result, dict):
            raise ValueError("Previous result is not a dictionary.")
        return args, {**previous_result, **kwargs}

    @staticmethod
    def _use_all_args_all_kwargs_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {}
        combined_kwargs.update(kwargs)
        return combined_args, combined_kwargs

    @staticmethod
    def _use_all_args_all_kwargs_no_overwrite(previous_result_args, previous_result_kwargs, *args, **kwargs):
        combined_args = list(previous_result_args) + list(args) if isinstance(previous_result_args, (list, tuple)) else list(args)
        combined_kwargs = kwargs if isinstance(kwargs, dict) else {}
        combined_kwargs = {**combined_kwargs, **(previous_result_kwargs if isinstance(previous_result_kwargs, dict) else {})}
        return combined_args, combined_kwargs

    def add_callable(self, func: Callable, args: List[Any] = None, kwargs: Dict[str, Any] = None, input_handler: Union[str, Callable, None] = None) -> None:
        if isinstance(input_handler, str):
            # Map the string to the corresponding static method
            input_handler_method = getattr(self, f"_{input_handler}", None)
            if input_handler_method is None:
                raise ValueError(f"Unknown input handler name: {input_handler}")
            input_handler = input_handler_method
        elif input_handler is None:
            input_handler = self._ignore_previous
        self.callables.append((func, args or [], kwargs or {}, input_handler))

    def __call__(self, *initial_args, **initial_kwargs) -> Any:
        result = None
        for func, args, kwargs, input_handler in self.callables:
            if isinstance(input_handler, str):
                # Map the string to the corresponding static method
                input_handler_method = getattr(self, f"_{input_handler}", None)
                if input_handler_method is None:
                    raise ValueError(f"Unknown input handler name: {input_handler}")
                input_handler = input_handler_method
            elif input_handler is None:
                input_handler = self._ignore_previous
                
            args, kwargs = input_handler(result, *args, **kwargs) if result is not None else (args, kwargs)
            result = func(*args, **kwargs)
        return result

    def __or__(self, other: "TypeAgnosticCallableChain") -> "TypeAgnosticCallableChain":
        if not isinstance(other, TypeAgnosticCallableChain):
            raise TypeError("Operand must be an instance of TypeAgnosticCallableChain")
        
        new_chain = TypeAgnosticCallableChain(self.callables + other.callables)
        return new_chain

```

```swarmauri/experimental/chains/__init__.py

#

```

```swarmauri/experimental/vectorizers/DGLVectorizer.py

import dgl
import torch
import torch.nn.functional as F
import numpy as np
from dgl.nn import GraphConv
from typing import List, Union, Any
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class DGLGraphConv(torch.nn.Module):
    def __init__(self, in_feats, out_feats, activation=F.relu):
        super(DGLGraphConv, self).__init__()
        self.conv1 = GraphConv(in_feats, 128)
        self.conv2 = GraphConv(128, out_feats)
        self.activation = activation

    def forward(self, g, inputs):
        # Apply graph convolution and activation.
        h = self.conv1(g, inputs)
        h = self.activation(h)
        h = self.conv2(g, h)
        return h

class DGLVectorizer(IVectorize):
    def __init__(self, in_feats, out_feats, model=None):
        self.in_feats = in_feats
        self.out_feats = out_feats
        self.model = model or DGLGraphConv(in_feats, out_feats)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def fit(self, graphs, features, epochs=10, learning_rate=0.01):
        self.model.to(self.device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            for g, feat in zip(graphs, features):
                g = g.to(self.device)
                feat = feat.to(self.device)
                outputs = self.model(g, feat)
                loss = F.mse_loss(outputs, feat)  # Example loss; adjust as needed
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            print(f'Epoch {epoch + 1}, Loss: {loss.item()}')
    
    def infer_vector(self, graph, features):
        graph = graph.to(self.device)
        features = features.to(self.device)
        with torch.no_grad():
            embeddings = self.model(graph, features)
        return SimpleVector(embeddings.cpu().numpy())

```

```swarmauri/experimental/vectorizers/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/document_stores/TriplesDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from rdflib import Graph, URIRef, Literal, BNode
from ampligraph.latent_features import ComplEx
from ampligraph.evaluation import train_test_split_no_unseen
from ampligraph.latent_features import EmbeddingModel
from ampligraph.utils import save_model, restore_model

from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.standard.vectorizers.concrete.AmpligraphVectorizer import AmpligraphVectorizer


class TriplesDocumentStore(IDocumentStore, IRetriever):
    def __init__(self, rdf_file_path: str, model_path: Optional[str] = None):
        """
        Initializes the TriplesDocumentStore.
        """
        self.graph = Graph()
        self.rdf_file_path = rdf_file_path
        self.graph.parse(rdf_file_path, format='turtle')
        self.documents = []
        self.vectorizer = AmpligraphVectorizer()
        self.model_path = model_path
        if model_path:
            self.model = restore_model(model_path)
        else:
            self.model = None
        self.metric = CosineDistance()
        self._load_documents()
        if not self.model:
            self._train_model()

    def _train_model(self):
        """
        Trains a model based on triples in the graph.
        """
        # Extract triples for embedding model
        triples = np.array([[str(s), str(p), str(o)] for s, p, o in self.graph])
        # Split data
        train, test = train_test_split_no_unseen(triples, test_size=0.1)
        self.model = ComplEx(batches_count=100, seed=0, epochs=20, k=150, eta=1,
                             optimizer='adam', optimizer_params={'lr': 1e-3},
                             loss='pairwise', regularizer='LP', regularizer_params={'p': 3, 'lambda': 1e-5},
                             verbose=True)
        self.model.fit(train)
        if self.model_path:
            save_model(self.model, self.model_path)

    def _load_documents(self):
        """
        Load documents into the store from the RDF graph.
        """
        for subj, pred, obj in self.graph:
            doc_id = str(hash((subj, pred, obj)))
            content = f"{subj} {pred} {obj}"
            document = Document(content=content, doc_id=doc_id, metadata={})
            self.documents.append(document)

    def add_document(self, document: IDocument) -> None:
        """
        Adds a single RDF triple document.
        """
        subj, pred, obj = document.content.split()  # Splitting content into RDF components
        self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.append(document)
        self._train_model()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Adds multiple RDF triple documents.
        """
        for document in documents:
            subj, pred, obj = document.content.split()  # Assuming each document's content is "subj pred obj"
            self.graph.add((URIRef(subj), URIRef(pred), URIRef(obj) if obj.startswith('http') else Literal(obj)))
        self.documents.extend(documents)
        self._train_model()

    # Implementation for get_document, get_all_documents, delete_document, update_document remains same as before
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve documents similar to the query string.
        """
        if not self.model:
            self._train_model()
        query_vector = self.vectorizer.infer_vector(model=self.model, samples=[query])[0]
        document_vectors = [self.vectorizer.infer_vector(model=self.model, samples=[doc.content])[0] for doc in self.documents]
        similarities = self.metric.distances(SimpleVector(data=query_vector), [SimpleVector(vector) for vector in document_vectors])
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/document_stores/Word2VecDocumentStore.py

from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/experimental/document_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/experimental/distances/CanberraDistance.py

import numpy as np
from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class CanberraDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Canberra distance metric.
    This class now processes IVector instances instead of raw lists.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Canberra distance between two IVector instances.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Canberra distance between the vectors.
        """
        # Extract data from IVector
        data_a = np.array(vector_a.data)
        data_b = np.array(vector_b.data)

        # Checking dimensions match
        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Computing Canberra distance
        distance = np.sum(np.abs(data_a - data_b) / (np.abs(data_a) + np.abs(data_b)))
        # Handling the case where both vectors have a zero value for the same dimension
        distance = np.nan_to_num(distance)
        return distance
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute similarity using the Canberra distance. Since this distance metric isn't
        directly interpretable as a similarity, a transformation is applied to map the distance
        to a similarity score.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        # One way to derive a similarity from distance is through inversion or transformation.
        # Here we use an exponential decay based on the computed distance. This is a placeholder
        # that assumes closer vectors (smaller distance) are more similar.
        distance = self.distance(vector_a, vector_b)

        # Transform the distance into a similarity score
        similarity = np.exp(-distance)

        return similarity
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/ChebyshevDistance.py

from typing import List
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity

class ChebyshevDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Chebyshev distance metric.
    Chebyshev distance is the maximum absolute distance between two vectors' elements.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Chebyshev distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Chebyshev distance between vector_a and vector_b.
        """
        max_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            max_distance = max(max_distance, abs(a - b))
        return max_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity between two vectors based on the Chebyshev distance.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: The similarity score between the two vectors.
        """

        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/HaversineDistance.py

from typing import List
from math import radians, cos, sin, sqrt, atan2
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class HaversineDistance(IDistanceSimilarity):
    """
    Concrete implementation of IDistanceSimiliarity interface using the Haversine formula.
    
    Haversine formula determines the great-circle distance between two points on a sphere given their 
    longitudes and latitudes. This implementation is particularly useful for geo-spatial data.
    """ 

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Haversine distance between two geo-spatial points.

        Args:
            vector_a (IVector): The first point in the format [latitude, longitude].
            vector_b (IVector): The second point in the same format [latitude, longitude].

        Returns:
            float: The Haversine distance between vector_a and vector_b in kilometers.
        """
        # Earth radius in kilometers
        R = 6371.0

        lat1, lon1 = map(radians, vector_a.data)
        lat2, lon2 = map(radians, vector_b.data)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")

```

```swarmauri/experimental/distances/ManhattanDistance.py

from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class ManhattanDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Manhattan distance.
    
    The Manhattan distance between two points is the sum of the absolute differences of their Cartesian coordinates.
    This is also known as L1 distance.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Manhattan distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The Manhattan distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")
        
        return sum(abs(a - b) for a, b in zip(vector_a.data, vector_b.data))

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        The similarity based on Manhattan distance can be inversely related to the distance for some applications,
        but this method intentionally returns NotImplementedError to signal that Manhattan distance is typically
        not directly converted to similarity in the conventional sense used in this context.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            NotImplementedError: This is intended as this distance metric doesn't directly offer a similarity measure.
        """
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity measure.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity measure.")

```

```swarmauri/experimental/distances/MinkowskiDistance.py

from typing import List
from scipy.spatial.distance import minkowski
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class MinkowskiDistance(IDistanceSimilarity):
    """
    Implementation of the IDistanceSimiliarity interface using the Minkowski distance metric.
    Minkowski distance is a generalized metric form that includes Euclidean distance,
    Manhattan distance, and others depending on the order (p) parameter.

    The class provides methods to compute the Minkowski distance between two vectors.
    """

    def __init__(self, p: int = 2):
        """
        Initializes the MinkowskiDistance calculator with the specified order.

        Parameters:
        - p (int): The order of the Minkowski distance. p=2 corresponds to the Euclidean distance,
                   while p=1 corresponds to the Manhattan distance. Default is 2.
        """
        self.p = p

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Minkowski distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Minkowski distance between vector_a and vector_b.
        """
        # Check if both vectors have the same dimensionality
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")

        # Extract data from IVector instances
        data_a = vector_a.data
        data_b = vector_b.data

        # Calculate and return the Minkowski distance
        return minkowski(data_a, data_b, p=self.p)

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors based on the Minkowski distance.
        The similarity is inversely related to the distance.

        Args:
            vector_a (IVector): The first vector to compare for similarity.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)  # An example similarity score
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/experimental/distances/ScannVectorStore.py

import numpy as np
import scann
from typing import List, Dict, Union

from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vector_stores.ISimiliarityQuery import ISimilarityQuery
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector


class ScannVectorStore(IVectorStore, ISimilarityQuery):
    """
    A vector store that utilizes ScaNN (Scalable Nearest Neighbors) for efficient similarity searches.
    """

    def __init__(self, dimension: int, num_leaves: int = 100, num_leaves_to_search: int = 10, reordering_num_neighbors: int = 100):
        """
        Initialize the ScaNN vector store with given parameters.

        Parameters:
        - dimension (int): The dimensionality of the vectors being stored.
        - num_leaves (int): The number of leaves for the ScaNN partitioning tree.
        - num_leaves_to_search (int): The number of leaves to search for query time. Must be <= num_leaves.
        - reordering_num_neighbors (int): The number of neighbors to re-rank based on the exact distance after searching leaves.
        """
        self.dimension = dimension
        self.num_leaves = num_leaves
        self.num_leaves_to_search = num_leaves_to_search
        self.reordering_num_neighbors = reordering_num_neighbors

        self.searcher = None  # Placeholder for the ScaNN searcher initialized during building
        self.dataset_vectors = []
        self.id_to_metadata = {}

    def _build_scann_searcher(self):
        """Build the ScaNN searcher based on current dataset vectors."""
        self.searcher = scann.ScannBuilder(np.array(self.dataset_vectors, dtype=np.float32), num_neighbors=self.reordering_num_neighbors, distance_measure="dot_product").tree(
            num_leaves=self.num_leaves, num_leaves_to_search=self.num_leaves_to_search, training_sample_size=25000
        ).score_ah(
            dimensions_per_block=2
        ).reorder(self.reordering_num_neighbors).build()

    def add_vector(self, vector_id: str, vector: Union[np.ndarray, List[float]], metadata: Dict = None) -> None:
        """
        Adds a vector along with its identifier and optional metadata to the store.

        Args:
            vector_id (str): Unique identifier for the vector.
            vector (Union[np.ndarray, List[float]]): The high-dimensional vector to be stored.
            metadata (Dict, optional): Optional metadata related to the vector.
        """
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector, dtype=np.float32)
        
        if self.searcher is None:
            self.dataset_vectors.append(vector)
        else:
            raise Exception("Cannot add vectors after building the index. Rebuild the index to include new vectors.")

        if metadata is None:
            metadata = {}
        self.id_to_metadata[vector_id] = metadata

    def build_index(self):
        """Builds or rebuilds the ScaNN searcher to reflect the current dataset vectors."""
        self._build_scann_searcher()

    def get_vector(self, vector_id: str) -> Union[IVector, None]:
        """
        Retrieve a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector.

        Returns:
            Union[IVector, None]: The vector associated with the given id, or None if not found.
        """
        if vector_id in self.id_to_metadata:
            metadata = self.id_to_metadata[vector_id]
            return SimpleVector(data=metadata.get('vector'), metadata=metadata)
        return None

    def delete_vector(self, vector_id: str) -> None:
        """
        Deletes a vector from the ScannVectorStore and marks the index for rebuilding.
        Note: For simplicity, this function assumes vectors are uniquely identifiable by their metadata.

        Args:
            vector_id (str): The unique identifier for the vector to be deleted.
        """
        if vector_id in self.id_to_metadata:
            # Identify index of the vector to be deleted
            vector = self.id_to_metadata[vector_id]['vector']
            index = self.dataset_vectors.index(vector)

            # Remove vector and its metadata
            del self.dataset_vectors[index]
            del self.id_to_metadata[vector_id]

            # Since vector order is important for matching ids, rebuild the searcher to reflect deletion
            self.searcher = None
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")

    def update_vector(self, vector_id: str, new_vector: Union[np.ndarray, List[float]], new_metadata: Dict = None) -> None:
        """
        Updates an existing vector in the ScannVectorStore and marks the index for rebuilding.

        Args:
            vector_id (str): The unique identifier for the vector to be updated.
            new_vector (Union[np.ndarray, List[float]]): The updated vector.
            new_metadata (Dict, optional): Optional updated metadata for the vector.
        """
        # Ensure new_vector is numpy array for consistency
        if not isinstance(new_vector, np.ndarray):
            new_vector = np.array(new_vector, dtype=np.float32)

        if vector_id in self.id_to_metadata:
            # Update operation follows delete then add strategy because vector order matters in ScaNN
            self.delete_vector(vector_id)
            self.add_vector(vector_id, new_vector, new_metadata)
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")



    def search_by_similarity_threshold(self, query_vector: Union[np.ndarray, List[float]], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (Union[np.ndarray, List[float]]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within. Not used in this implementation.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector, dtype=np.float32)
        
        if self.searcher is None:
            self._build_scann_searcher()
        
        _, indices = self.searcher.search(query_vector, final_num_neighbors=self.reordering_num_neighbors)
        results = [{"id": str(idx), "metadata": self.id_to_metadata.get(str(idx), {})} for idx in indices if idx < similarity_threshold]
        return results

```

```swarmauri/experimental/distances/SorensenDiceDistance.py

import numpy as np
from typing import List
from collections import Counter

from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SorensenDiceDistance(IDistanceSimilarity):
    """
    Implementing a concrete Vector Store class for calculating Sörensen-Dice Index Distance.
    The Sörensen-Dice Index, or Dice's coefficient, is a measure of the similarity between two sets.
    """

    def distance(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Compute the Sörensen-Dice distance between two vectors.
        
        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.
        
        Returns:
            float: The computed Sörensen-Dice distance between vector_a and vector_b.
        """
        # Convert vectors to binary sets
        set_a = set([i for i, val in enumerate(vector_a) if val])
        set_b = set([i for i, val in enumerate(vector_b) if val])
        
        # Calculate the intersection size
        intersection_size = len(set_a.intersection(set_b))
        
        # Sorensen-Dice Index calculation
        try:
            sorensen_dice_index = (2 * intersection_size) / (len(set_a) + len(set_b))
        except ZeroDivisionError:
            sorensen_dice_index = 0.0
        
        # Distance is inverse of similarity for Sörensen-Dice
        distance = 1 - sorensen_dice_index
        
        return distance
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarity(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for SorensenDiceDistance.")

```

```swarmauri/experimental/distances/SquaredEuclideanDistance.py

from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SquaredEuclideanDistance(IDistanceSimilarity):
    """
    A concrete class for computing the squared Euclidean distance between two vectors.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the squared Euclidean distance between vectors `vector_a` and `vector_b`.

        Parameters:
        - vector_a (IVector): The first vector in the comparison.
        - vector_b (IVector): The second vector in the comparison.

        Returns:
        - float: The computed squared Euclidean distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must be of the same dimensionality.")

        squared_distance = sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data))
        return squared_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Squared Euclidean distance is not used for calculating similarity.
        
        Parameters:
        - vector_a (IVector): The first vector.
        - vector_b (IVector): The second vector.

        Raises:
        - NotImplementedError: Indicates that similarity calculation is not implemented.
        """
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")
        
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")

```

```swarmauri/experimental/distances/SSASimilarity.py

from typing import Set, List, Dict
from ....core.vector_stores.ISimilarity import ISimilarity
from ....core.vectors.IVector import IVector


class SSASimilarity(ISimilarity):
    """
    Implements the State Similarity in Arity (SSA) similarity measure to
    compare states (sets of variables) for their similarity.
    """

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Calculate the SSA similarity between two documents by comparing their metadata,
        assumed to represent states as sets of variables.

        Args:
        - vector_a (IDocument): The first document.
        - vector_b (IDocument): The second document to compare with the first document.

        Returns:
        - float: The SSA similarity measure between vector_a and vector_b, ranging from 0 to 1
                 where 0 represents no similarity and 1 represents identical states.
        """
        state_a = set(vector_a.metadata.keys())
        state_b = set(vector_b.metadata.keys())

        return self.calculate_ssa(state_a, state_b)

    @staticmethod
    def calculate_ssa(state_a: Set[str], state_b: Set[str]) -> float:
        """
        Calculate the State Similarity in Arity (SSA) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.

        Returns:6
        - float: The SSA similarity measure, ranging from 0 (no similarity) to 1 (identical states).
        """
        # Calculate the intersection (shared variables) between the two states
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the union (total unique variables) of the two states
        total_variables = state_a.union(state_b)
        
        # Calculate the SSA measure as the ratio of shared to total variables
        ssa = len(shared_variables) / len(total_variables) if total_variables else 1
        
        return ssa

```

```swarmauri/experimental/distances/SSIVSimilarity.py

from typing import List, Dict, Set
from ....core.vector_stores.ISimilarity import ISimilarity

class SSIVSimilarity(ISimilarity):
    """
    Concrete class that implements ISimilarity interface using
    State Similarity of Important Variables (SSIV) as the similarity measure.
    """

    def similarity(self, state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the SSIV between two states represented by sets of variables.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        """
        return self.calculate_ssiv(state_a, state_b, importance_a, importance_b)

    @staticmethod
    def calculate_ssiv(state_a: Set[str], state_b: Set[str], importance_a: Dict[str, float], importance_b: Dict[str, float]) -> float:
        """
        Calculate the State Similarity of Important Variables (SSIV) between two states.

        Parameters:
        - state_a (Set[str]): A set of variables representing state A.
        - state_b (Set[str]): A set of variables representing state B.
        - importance_a (Dict[str, float]): A dictionary where keys are variables in state A and values are their importance weights.
        - importance_b (Dict[str, float]): A dictionary where keys are variables in state B and values are their importance weights.

        Returns:
        - float: The SSIV similarity measure, ranging from 0 to 1.
        
        Note: It is assumed that the importance weights are non-negative.
        """
        shared_variables = state_a.intersection(state_b)
        
        # Calculate the summed importance of shared variables
        shared_importance_sum = sum(importance_a[var] for var in shared_variables) + sum(importance_b[var] for var in shared_variables)
        
        # Calculate the total importance of all variables in both states
        total_importance_sum = sum(importance_a.values()) + sum(importance_b.values())
        
        # Calculate and return the SSIV
        ssiv = (2 * shared_importance_sum) / total_importance_sum if total_importance_sum != 0 else 0
        return ssiv


```

```swarmauri/experimental/distances/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/README.md

# Standard Library

The Standard Library extends the Core Library with concrete implementations of models, agents, tools, parsers, and more. It aims to provide ready-to-use components that can be easily integrated into machine learning projects.

## Features

- **Predefined Models and Agents**: Implements standard models and agents ready for use.
- **Toolkit**: A collection of tools for various tasks (e.g., weather information, math operations).
- **Parsers Implementations**: Various parsers for text data, including HTML and CSV parsers.
- **Conversations and Chunkers**: Manage conversation histories and chunk text data.
- **Vectorizers**: Transform text data into vector representations.
- **Document Stores and Vector Stores**: Concrete implementations for storing and retrieving data.

## Getting Started

To make the best use of the Standard Library, first ensure that the Core Library is set up in your project as the Standard Library builds upon it.

```python
# Example usage of a concrete model from the Standard Library
from swarmauri.standard.models.concrete import OpenAIModel

# Initialize the model with necessary configuration
model = OpenAIModel(api_key="your_api_key_here")
```

## Documentation

For more detailed guides and API documentation, check the [Docs](/docs) directory within the library. You'll find examples, configuration options, and best practices for utilizing the provided components.

## Contributing

Your contributions can help the Standard Library grow! Whether it's adding new tools, improving models, or writing documentation, we appreciate your help. Please send a pull request with your contributions.

## License

Please see the `LICENSE` file in the repository for details.

```

```swarmauri/standard/__init__.py



```

```swarmauri/standard/models/__init__.py



```

```swarmauri/standard/models/base/__init__.py



```

```swarmauri/standard/models/base/ModelBase.py

from abc import ABC, abstractmethod
from typing import Any
from ....core.models.IModel import IModel

class ModelBase(IModel, ABC):
    """
    Concrete implementation of the IModel abstract base class.
    This version includes managing the model name through a property and a setter.
    """
    @abstractmethod
    def __init__(self, model_name: str):
        self._model_name = model_name
    
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, value: str) -> None:
        """
        Property setter that sets the name of the model.

        Parameters:
        - value (str): The new name of the model.
        """
        self._model_name = value
       
    


```

```swarmauri/standard/models/concrete/__init__.py



```

```swarmauri/standard/models/concrete/OpenAIModel.py

import json
from typing import List
from openai import OpenAI
from swarmauri.core.models.IPredict import IPredict
from swarmauri.standard.models.base.ModelBase import ModelBase


class OpenAIModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the OpenAI model with an API key.

        Parameters:
        - api_key (str): Your OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)
        
    
    def predict(self, messages, temperature=0.7, max_tokens=256, enable_json=False, stop: List[str] = None):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        
        Returns:
        - The generated message content.
        """
        if self.client is None:
            raise Exception("OpenAI client is not initialized. Call 'load_model' first.")
        
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        
        return message_content

```

```swarmauri/standard/models/concrete/AzureGPT.py

import json
from openai import AzureOpenAI
from ..base.ModelBase import ModelBase
from ....core.models.IPredict import IPredict

class AzureGPT(ModelBase, IPredict):
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str, model_name: str):
        """
        Initialize the Azure model with an API key.

        Parameters:
        - api_key (str): Your OpenAI API key.
        """
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.client = AzureOpenAI(
                azure_endpoint = azure_endpoint, 
                api_key = api_key,  
                api_version = api_version
            )
        super().__init__(model_name)
       

    
    def predict(self, messages, temperature=0.7, max_tokens=256, enable_json=True):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        
        Returns:
        - The generated message content.
        """
        if self.client is None:
            raise Exception("OpenAI client is not initialized. Call 'load_model' first.")
        
        if enable_json:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        
        result = response.json()
        message_content = json.loads(result['choices'][0]['message']['content'])
        
        return message_content

```

```swarmauri/standard/models/concrete/OpenAIImageGenerator.py

import json
from openai import OpenAI
from ..base.ModelBase import ModelBase
from ....core.models.IPredict import IPredict

class OpenAIImageGenerator(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "dall-e"):
        """
        Initializes the OpenAI image generator model.

        Parameters:
        - api_key (str): The API key provided by OpenAI for access to their services.
        - model_name (str): Name of the image generation model provided by OpenAI.
                            Defaults to "dall-e" for DALL·E, their image generation model.
        """
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)

    def predict(self, prompt: str, size: str = "1024x1024", 
                quality: str = "standard", n: int = 1) -> str:
        """
        Generates an image based on the given prompt and other parameters.

        Parameters:
        - prompt (str): A description of the image you want to generate.
        - **kwargs: Additional parameters that the image generation endpoint might use.

        Returns:
        - str: A URL or identifier for the generated image.
        """
        try:
            response = self.client.images.generate(
                model=self.model_name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            result = response.json()
            return result
        
        except Exception as e:
            return str(e)

```

```swarmauri/standard/models/concrete/OpenAIToolModel.py

from openai import OpenAI
from swarmauri.standard.models.base.ModelBase import ModelBase
from swarmauri.core.models.IPredict import IPredict

class OpenAIToolModel(ModelBase, IPredict):
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo-0125"):
        self.client = OpenAI(api_key=api_key)
        super().__init__(model_name)

    def predict(self, messages, tools=None, tool_choice=None, temperature=0.7, max_tokens=1024):
        if tools and not tool_choice:
            tool_choice = "auto"
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response

```

```swarmauri/standard/agents/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/base/NamedAgentBase.py

from typing import Any, Optional
from abc import ABC
from swarmauri.core.agents.IAgentName import IAgentName


class NamedAgentBase(IAgentName,ABC):
    
    def __init__(self, name: str):
        self._name = name

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value) -> None:
        self._name = value     

```

```swarmauri/standard/agents/base/ConversationAgentBase.py

from typing import Any, Optional
from abc import ABC

from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase

class ConversationAgentBase(AgentBase, IAgentConversation, ABC):
    def __init__(self, model: IModel, conversation: IConversation):
        AgentBase.__init__(self, model)
        self._conversation = conversation

    
    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
      

    @property
    def conversation(self) -> IConversation:
        return self._conversation

    @conversation.setter
    def conversation(self, value) -> None:
        self._conversation = value



```

```swarmauri/standard/agents/base/ToolAgentBase.py

from abc import ABC
from typing import Any, Optional
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase


class ToolAgentBase(ConversationAgentBase, IAgentConversation, ABC):
    
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation,
                 toolkit: IToolkit):
        ConversationAgentBase.__init__(self, model, conversation)
        self._toolkit = toolkit

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def toolkit(self) -> IToolkit:
        return self._toolkit
    
    @toolkit.setter
    def toolkit(self, value) -> None:
        self._toolkit = value        


```

```swarmauri/standard/agents/base/AgentBase.py

from typing import Any, Optional
from abc import ABC
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.models.IModel import IModel



class AgentBase(IAgent, ABC):
    def __init__(self, model: IModel):
        self._model = model

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    @property
    def model(self) -> IModel:
        return self._model
    
    @model.setter
    def model(self, value) -> None:
        self._model = value        

    
    def __getattr__(self, name):
        # Example of transforming attribute name from simplified to internal naming convention
        internal_name = f"_{name}"
        if internal_name in self.__dict__:
            return self.__dict__[internal_name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        # Direct assignment to the __dict__ to bypass any potential infinite recursion
        # from setting attributes that do not explicitly exist.
        object.__setattr__(self, name, value) 
        
        
    def __str__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{class_name} {variables_str}>"
        
    def __repr__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{class_name} ({variables_str})"

```

```swarmauri/standard/agents/base/DocumentAgentBase.py

from typing import Any, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.agents.IAgentDocument import IAgentDocumentStore
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase


class DocumentAgentBase(ConversationAgentBase, NamedAgentBase, IAgentDocumentStore):
    """
    Base class for agents that handle and store documents within their processing scope.
    Extends ConversationAgentBase and NamedAgentBase to utilize conversational context,
    naming capabilities, and implements IAgentDocumentStore for document storage.
    """

    def __init__(self, name: str, model: IModel, conversation: IConversation, document_store: IDocumentStore):
        NamedAgentBase.__init__(self, name=name)  # Initialize name through NamedAgentBase
        ConversationAgentBase.__init__(self, model, conversation)  # Initialize conversation and model
        self._document_store = document_store  # Document store initialization

    @property
    def document_store(self) -> Optional[IDocument]:
        """
        Gets the document store associated with this agent.
        
        Returns:
            Optional[IDocument]: The document store of the agent, if any.
        """
        return self._document_store

    @document_store.setter
    def document_store(self, value: IDocument) -> None:
        """
        Sets the document store for this agent.

        Args:
            value (IDocument): The new document store to be associated with the agent.
        """
        self._document_store = value
    
    def exec(self, input_data: Optional[Any]) -> Any:
        """
        Placeholder method to demonstrate expected behavior of derived classes.
        Subclasses should implement their specific logic for processing input data and optionally interacting with the document store.

        Args:
            input_data (Optional[Any]): Input data to process, can be of any format that the agent is designed to handle.

        Returns:
            Any: The result of processing the input data.
        """
        raise NotImplementedError("Subclasses must implement the exec method.")

```

```swarmauri/standard/agents/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/concrete/ToolAgent.py

from typing import Any, Optional, Union, Dict
import json

from swarmauri.core.models.IModel import IModel
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.ToolAgentBase import ToolAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class ToolAgent(ToolAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation, 
                 toolkit: IToolkit):
        super().__init__(model, conversation, toolkit)

    def exec(self, input_data: Union[str, IMessage],  model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model
        toolkit = self.toolkit
        

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)

            
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        
        prediction = model.predict(messages=messages, 
                                   tools=toolkit.tools, 
                                   tool_choice="auto", 
                                   **model_kwargs)
        
        prediction_message = prediction.choices[0].message
        
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message.content, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
            
            messages = conversation.as_dict()
            rag_prediction = model.predict(messages=messages, 
                                           tools=toolkit.tools, 
                                           tool_choice="none",
                                           **model_kwargs)
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            agent_message = AgentMessage(agent_response)
            conversation.add_message(agent_message)
            prediction = rag_prediction
            
        return agent_response 
    

```

```swarmauri/standard/agents/concrete/ChatSwarmAgent.py

from typing import Any, Optional, Union, Dict
from swarmauri.core.models.IModel import IModel
from swarmauri.core.messages import IMessage
from swarmauri.core.conversations import IConversation
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage

class ChatSwarmAgent(ConversationAgentBase):
    def __init__(self, model: IModel, conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_data: Union[str, IMessage], model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        return prediction

```

```swarmauri/standard/agents/concrete/SingleCommandAgent.py

from typing import Any, Optional

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase

class SingleCommandAgent(AgentBase):
    def __init__(self, model: IModel, 
                 conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_str: Optional[str] = None) -> Any:
        model = self.model
        prediction = model.predict(input_str)
        
        return prediction

```

```swarmauri/standard/agents/concrete/SimpleSwarmAgent.py

from typing import Any, Optional

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation


from swarmauri.standard.agents.base.SwarmAgentBase import AgentBase
from swarmauri.standard.messages.concrete import HumanMessage

class SimpleSwarmAgent(AgentBase):
    def __init__(self, model: IModel, 
                 conversation: IConversation):
        super().__init__(model, conversation)

    def exec(self, input_str: Optional[str] = None) -> Any:
        conversation = self.conversation
        model = self.model

        # Construct a new human message (for example purposes)
        if input_str:
            human_message = HumanMessage(input_str)
            conversation.add_message(human_message)
        
        messages = conversation.as_dict()
        prediction = model.predict(messages=messages)
        return prediction

```

```swarmauri/standard/agents/concrete/MultiPartyChatSwarmAgent.py

from typing import Any, Optional, Union, Dict

from swarmauri.core.models.IModel import IModel
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase
from swarmauri.standard.conversations.concrete.SharedConversation import SharedConversation
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage

class MultiPartyChatSwarmAgent(ConversationAgentBase, NamedAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: SharedConversation,
                 name: str):
        ConversationAgentBase.__init__(self, model, conversation)
        NamedAgentBase.__init__(self, name)

    def exec(self, input_data: Union[str, IMessage] = "", model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        if input_data != "":
            # Add the human message to the conversation
            conversation.add_message(human_message, sender_id=self.name)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()

        
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        if prediction != '':
            agent_message = AgentMessage(prediction)
            conversation.add_message(agent_message, sender_id=self.name)
        
        return prediction

```

```swarmauri/standard/agents/concrete/MultiPartyToolAgent.py

from typing import Any, Optional, Union, Dict
import json

from swarmauri.core.models.IModel import IModel
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.ToolAgentBase import ToolAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class MultiPartyToolAgent(ToolAgentBase, NamedAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: IConversation, 
                 toolkit: IToolkit,
                 name: str):
        ToolAgentBase.__init__(self, model, conversation, toolkit)
        NamedAgentBase.__init__(self, name)

    def exec(self, input_data: Union[str, IMessage], model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        model = self.model
        toolkit = self.toolkit
        

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        if input_data != "":
            # Add the human message to the conversation
            conversation.add_message(human_message, sender_id=self.name)
            
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        

        if model_kwargs:
            prediction = model.predict(messages=messages, 
                                   tools=toolkit.tools, 
                                   tool_choice="auto",
                                   **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        
        
        prediction_message = prediction.choices[0].message
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message.content, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message, sender_id=self.name)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message, sender_id=self.name)
            
            
            messages = conversation.as_dict()
            rag_prediction = model.predict(messages=messages, 
                                           tools=toolkit.tools, 
                                           tool_choice="none")
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            if agent_response != "":
                agent_message = AgentMessage(agent_response)
                conversation.add_message(agent_message, sender_id=self.name)
            prediction = rag_prediction
            
        return agent_response 
    

```

```swarmauri/standard/agents/concrete/RagAgent.py

from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.DocumentAgentBase import DocumentAgentBase
from swarmauri.standard.document_stores.base.DocumentStoreRetrieveBase import DocumentStoreRetrieveBase

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class RagAgent(DocumentAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, model: IModel, conversation: SystemContextBase, document_store: DocumentStoreRetrieveBase):
        super().__init__(name=name, model=model, conversation=conversation, document_store=document_store)

    def exec(self, 
             input_data: Union[str, IMessage], 
             top_k: int = 5, 
             model_kwargs: Optional[Dict] = {}
             ) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")
        
        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        
        
        similar_documents = self.document_store.retrieve(query=input_data, top_k=top_k)
        substr = '\n'.join([doc.content for doc in similar_documents])
        
        # Use substr to set system context
        system_context = SystemMessage(substr)
        conversation.system_context = system_context
        

        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
            
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        return prediction
    
    
    


```

```swarmauri/standard/agents/concrete/GenerativeRagAgent.py

from typing import Any, Optional, Union, Dict
from swarmauri.core.messages import IMessage
from swarmauri.core.models.IModel import IModel
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.agents.base.DocumentAgentBase import DocumentAgentBase
from swarmauri.standard.document_stores.base.DocumentStoreRetrieveBase import DocumentStoreRetrieveBase
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.chunkers.concrete.MdSnippetChunker import MdSnippetChunker
from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

class GenerativeRagAgent(DocumentAgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """

    def __init__(self, name: str, model: IModel, conversation: SystemContextBase, document_store: DocumentStoreRetrieveBase):
        super().__init__(name=name, model=model, conversation=conversation, document_store=document_store)

    def exec(self, 
             input_data: Union[str, IMessage], 
             top_k: int = 5, 
             model_kwargs: Optional[Dict] = {}
             ) -> Any:
        conversation = self.conversation
        model = self.model

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")
        
        # Add the human message to the conversation
        conversation.add_message(human_message)
        
        
        
        similar_documents = self.document_store.retrieve(query=input_data, top_k=top_k)
        substr = '\n'.join([doc.content for doc in similar_documents])
        
        # Use substr to set system context
        system_context = SystemMessage(substr)
        conversation.system_context = system_context
        

        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
            
        # Create an AgentMessage instance with the model's response and update the conversation
        agent_message = AgentMessage(prediction)
        conversation.add_message(agent_message)
        
        chunker = MdSnippetChunker()
        
        new_documents = [Document(doc_id=self.document_store.document_count()+1,
                                     content=each[2], 
                                     metadata={"source": "RagSaverAgent", 
                                               "language": each[1],
                                               "comments": each[0]})
                     for each in chunker.chunk_text(prediction)]

        self.document_store.add_documents(new_documents)
        
        return prediction
    
    
    


```

```swarmauri/standard/utils/__init__.py



```

```swarmauri/standard/utils/load_documents_from_json.py

import json
from typing import List
from swarmauri.standard.documents.concrete.Document import Document

def load_documents_from_json(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    documents = [Document(doc_id=str(_), content=doc['content'], metadata={"document_name": doc['document_name']}) for _, doc in enumerate(data) if doc['content']]
    return documents

```

```swarmauri/standard/conversations/__init__.py



```

```swarmauri/standard/conversations/base/__init__.py



```

```swarmauri/standard/conversations/base/ConversationBase.py

from abc import ABC
from typing import List, Union
from ....core.messages.IMessage import IMessage
from ....core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ABC):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
        self._history: List[IMessage] = []

    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history
    
    def add_message(self, message: IMessage):
        self._history.append(message)

    def get_last(self) -> Union[IMessage, None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()

    def as_dict(self) -> List[dict]:
        return [message.as_dict() for message in self.history] # This must utilize the public self.history
    
    
    # def __repr__(self):
        # return repr([message.as_dict() for message in self._history])

```

```swarmauri/standard/conversations/base/SystemContextBase.py

from abc import ABC
from typing import Optional, Union
from swarmauri.core.conversations.ISystemContext import ISystemContext
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class SystemContextBase(ConversationBase, ISystemContext, ABC):
    def __init__(self, *args, system_message_content: Optional[SystemMessage] = None):
        ConversationBase.__init__(self)
        # Automatically handle both string and SystemMessage types for initializing system context
        self._system_context = None  # Initialize with None
        if system_message_content:
            self.system_context = system_message_content
    
    @property
    def system_context(self) -> Union[SystemMessage, None]:
        """Get the system context message. Raises an error if it's not set."""
        if self._system_context is None:
            raise ValueError("System context has not been set.")
        return self._system_context
    
    @system_context.setter
    def system_context(self, new_system_message: Union[SystemMessage, str]) -> None:
        """
        Set a new system context message. The new system message can be a string or 
        an instance of SystemMessage. If it's a string, it converts it to a SystemMessage.
        """
        if isinstance(new_system_message, SystemMessage):
            self._system_context = new_system_message
        elif isinstance(new_system_message, str):
            self._system_context = SystemMessage(new_system_message)
        else:
            raise ValueError("System context must be a string or a SystemMessage instance.")

```

```swarmauri/standard/conversations/concrete/__init__.py



```

```swarmauri/standard/conversations/concrete/LimitedSizeConversation.py

from ..base.ConversationBase import ConversationBase
from ....core.messages.IMessage import IMessage
from ....core.conversations.IMaxSize import IMaxSize

class LimitedSizeConversation(ConversationBase, IMaxSize):
    def __init__(self, max_size: int):
        super().__init__()
        self._max_size = max_size
        
    @property
    def max_size(self) -> int:
        """
        Provides read-only access to the conversation history.
        """
        return self._max_size
    
    @max_size.setter
    def max_size(self, new_max_size: int) -> int:
        """
        Provides read-only access to the conversation history.
        """
        if new_max_size > 0:
            self._max_size = int
        else:
            raise ValueError('Cannot set conversation size to 0.')


    def add_message(self, message: IMessage):
        """Adds a message and ensures the conversation does not exceed the max size."""
        super().add_message(message)
        self._enforce_max_size_limit()

    def _enforce_max_size_limit(self):
        """
        Enforces the maximum size limit of the conversation history.
        If the current history size exceeds the maximum size, the oldest messages are removed.
        """
        while len(self._history) > self.max_size:
            self._history.pop(0)

```

```swarmauri/standard/conversations/concrete/SimpleConversation.py

from typing import List, Union
from ....core.messages.IMessage import IMessage
from ..base.ConversationBase import ConversationBase

class SimpleConversation(ConversationBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
       super().__init__()

```

```swarmauri/standard/conversations/concrete/LimitedSystemContextConversation.py

from typing import Optional, Union, List
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class LimitedSystemContextConversation(SystemContextBase, IMaxSize):
    def __init__(self, max_size: int, system_message_content: Optional[SystemMessage] = None):
        """
        Initializes the conversation with a system context message and a maximum history size.
        
        Parameters:
            max_size (int): The maximum number of messages allowed in the conversation history.
            system_message_content (Optional[str], optional): The initial system message content. Can be a string.
        """
        SystemContextBase.__init__(self, system_message_content=system_message_content if system_message_content else "")  # Initialize SystemContext with a SystemMessage
        self._max_size = max_size  # Set the maximum size
    
    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        
        
        res = [] 
        res.append(self.system_context)
        res.extend(self._history)
        return res
        
        
    @property
    def max_size(self) -> int:
        """
        Provides access to the max_size property.
        """
        return self._max_size
    
    @max_size.setter
    def max_size(self, new_max_size: int) -> None:
        """
        Sets a new maximum size for the conversation history.
        """
        if new_max_size <= 0:
            raise ValueError("max_size must be greater than 0.")
        self._max_size = new_max_size

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        else:
            super().add_message(message)
        self._enforce_max_size_limit()
        
    def _enforce_max_size_limit(self):
        """
        Remove messages from the beginning of the conversation history if the limit is exceeded.
        """
        while len(self._history) + 1 > self._max_size:
            self._history.pop(0)

    @property
    def system_context(self) -> Union[SystemMessage, None]:
        """Get the system context message. Raises an error if it's not set."""
        if self._system_context is None:
            raise ValueError("System context has not been set.")
        return self._system_context


    @system_context.setter
    def system_context(self, new_system_message: Union[SystemMessage, str]) -> None:
        """
        Set a new system context message. The new system message can be a string or 
        an instance of SystemMessage. If it's a string, it converts it to a SystemMessage.
        """
        if isinstance(new_system_message, SystemMessage):
            self._system_context = new_system_message
        elif isinstance(new_system_message, str):
            self._system_context = SystemMessage(new_system_message)
        else:
            raise ValueError("System context must be a string or a SystemMessage instance.")
            

```

```swarmauri/standard/conversations/concrete/SharedConversation.py

import inspect
from threading import Lock
from typing import Optional, Dict, List, Tuple
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class SharedConversation(ConversationBase):
    """
    A thread-safe conversation class that supports individual system contexts for each SwarmAgent.
    """
    def __init__(self):
        super().__init__()
        self._lock = Lock()  # A lock to ensure thread safety
        self._agent_system_contexts: Dict[str, SystemMessage] = {}  # Store system contexts for each agent
        self._history: List[Tuple[str, IMessage]] = []  # Stores tuples of (sender_id, IMessage)


    @property
    def history(self):
        history = []
        for each in self._history:
            history.append((each[0], each[1]))
        return history

    def add_message(self, message: IMessage, sender_id: str):
        with self._lock:
            self._history.append((sender_id, message))

    def reset_messages(self) -> None:
        self._history = []
        

    def _get_caller_name(self) -> Optional[str]:
        for frame_info in inspect.stack():
            # Check each frame for an instance with a 'name' attribute in its local variables
            local_variables = frame_info.frame.f_locals
            for var_name, var_value in local_variables.items():
                if hasattr(var_value, 'name'):
                    # Found an instance with a 'name' attribute. Return its value.
                    return getattr(var_value, 'name')
        # No suitable caller found
        return None

    def as_dict(self) -> List[Dict]:
        caller_name = self._get_caller_name()
        history = []

        with self._lock:
            # If Caller is not one of the agents, then give history
            if caller_name not in self._agent_system_contexts.keys():
                for sender_id, message in self._history:
                    history.append((sender_id, message.as_dict()))
                
                
            else:
                system_context = self.get_system_context(caller_name)
                #print(caller_name, system_context, type(system_context))
                if type(system_context) == str:
                    history.append(SystemMessage(system_context).as_dict())
                else:
                    history.append(system_context.as_dict())
                    
                for sender_id, message in self._history:
                    #print(caller_name, sender_id, message, type(message))
                    if sender_id == caller_name:
                        if message.__class__.__name__ == 'AgentMessage' or 'FunctionMessage':
                            # The caller is the sender; treat as AgentMessage
                            history.append(message.as_dict())
                            
                            # Print to see content that is empty.
                            #if not message.content:
                                #print('\n\t\t\t=>', message, message.content)
                    else:
                        if message.content:
                            # The caller is not the sender; treat as HumanMessage
                            history.append(HumanMessage(message.content).as_dict())
        return history
    
    def get_last(self) -> IMessage:
        with self._lock:
            return super().get_last()


    def clear_history(self):
        with self._lock:
            super().clear_history()


        

    def set_system_context(self, agent_id: str, context: SystemMessage):
        """
        Sets the system context for a specific agent.

        Args:
            agent_id (str): Unique identifier for the agent.
            context (SystemMessage): The context message to be set for the agent.
        """
        with self._lock:
            self._agent_system_contexts[agent_id] = context

    def get_system_context(self, agent_id: str) -> Optional[SystemMessage]:
        """
        Retrieves the system context for a specific agent.

        Args:
            agent_id (str): Unique identifier for the agent.

        Returns:
            Optional[SystemMessage]: The context message of the agent, or None if not found.
        """
        return self._agent_system_contexts.get(agent_id, None)

```

```swarmauri/standard/documents/__init__.py



```

```swarmauri/standard/documents/base/__init__.py



```

```swarmauri/standard/documents/base/EmbeddedBase.py

from abc import ABC
from typing import List, Any
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.core.vectors.IVector import IVector

class EmbeddedBase(IEmbed, ABC):
    def __init__(self, embedding):
        self._embedding = embedding
            
    @property
    def embedding(self) -> IVector:
        return self._embedding

    @embedding.setter
    def embedding(self, value: IVector) -> None:
        self._embedding = value

```

```swarmauri/standard/documents/base/DocumentBase.py

from abc import ABC, abstractmethod
from typing import Dict
from swarmauri.core.documents.IDocument import IDocument

class DocumentBase(IDocument, ABC):
    
    def __init__(self, doc_id,  content, metadata):
        self._id = doc_id
        self._content = content
        self._metadata = metadata        
    
    def __str__(self):
        return f"Document ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}"

    def __repr__(self):
        return f"Document(id={self.id}, content={self.content}, metadata={self.metadata})"

    def as_dict(self):
        return self.__dict__
    
    @property
    def id(self) -> str:
        """
        Get the document's ID.
        """
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """
        Set the document's ID.
        """
        self._id = value

    @property
    def content(self) -> str:
        """
        Get the document's content.
        """
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """
        Set the document's content.
        """
        if value:
            self._content = value
        else:
            raise ValueError('Cannot create a document with no content.')

    @property
    def metadata(self) -> Dict:
        """
        Get the document's metadata.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict) -> None:
        """
        Set the document's metadata.
        """
        self._metadata = value

```

```swarmauri/standard/documents/concrete/__init__.py



```

```swarmauri/standard/documents/concrete/EmbeddedDocument.py

from typing import Optional, Any
from swarmauri.standard.documents.base.DocumentBase import DocumentBase
from swarmauri.standard.documents.base.EmbeddedBase import EmbeddedBase

class EmbeddedDocument(DocumentBase, EmbeddedBase):
    def __init__(self, doc_id,  content, metadata, embedding: Optional[Any] = None):
        DocumentBase.__init__(self, doc_id=doc_id, content=content, metadata=metadata)
        EmbeddedBase.__init__(self, embedding=embedding)



```

```swarmauri/standard/documents/concrete/Document.py

from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class Document(DocumentBase):
    pass
    
        


```

```swarmauri/standard/messages/__init__.py



```

```swarmauri/standard/messages/base/__init__.py



```

```swarmauri/standard/messages/base/MessageBase.py

from abc import ABC, abstractmethod
from swarmauri.core.messages.IMessage import IMessage

class MessageBase(IMessage, ABC):
    
    @abstractmethod
    def __init__(self, role: str, content: str):
        self._role = role
        self._content = content
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def content(self) -> str:
        return self._content

    
    def as_dict(self) -> dict:
        """
        Dynamically return a dictionary representation of the object,
        including all properties.
        """
        result_dict = {}
        # Iterate over all attributes
        for attr in dir(self):
            # Skip private attributes and anything not considered a property
            if attr.startswith("_") or callable(getattr(self, attr)):
                continue
            result_dict[attr] = getattr(self, attr)
            
        return result_dict

    def __repr__(self) -> str:
        """
        Return the string representation of the ConcreteMessage.
        """
        return f"{self.__class__.__name__}(role='{self.role}')"
    
    def __getattr__(self, name):
        """
        Return the value of the named attribute of the instance.
        """
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    
    def __setattr__(self, name, value):
        """
        Set the value of the named attribute of the instance.
        """
        self.__dict__[name] = value

```

```swarmauri/standard/messages/concrete/__init__.py

from .HumanMessage import HumanMessage
from .AgentMessage import AgentMessage
from .FunctionMessage import FunctionMessage
from .SystemMessage import SystemMessage

```

```swarmauri/standard/messages/concrete/AgentMessage.py

from typing import Optional, Any
from swarmauri.standard.messages.base.MessageBase import MessageBase


class AgentMessage(MessageBase):
    def __init__(self, content, tool_calls: Optional[Any] = None):
        super().__init__(role='assistant', content=content)
        if tool_calls:
            self.tool_calls = tool_calls

```

```swarmauri/standard/messages/concrete/HumanMessage.py

from swarmauri.standard.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    """
    Represents a message created by a human user.

    Extends the `Message` class to specifically represent messages input by human users in a conversational
    interface. It contains the message content and assigns the type "HumanMessage" to distinguish it from
    other types of messages.
    """

    def __init__(self, content, name=None):
        """
        Initializes a new instance of HumanMessage with specified content.

        Args:
            content (str): The text content of the human-created message.
            name (str, optional): The name of the human sender.
        """
        super().__init__(role='user', content=content)



```

```swarmauri/standard/messages/concrete/FunctionMessage.py

from swarmauri.standard.messages.base.MessageBase import MessageBase


class FunctionMessage(MessageBase):
    """
    Represents a message created by a human user.

    This class extends the `Message` class to specifically represent messages that
    are input by human users in a conversational interface. It contains the message
    content and assigns the type "HumanMessage" to distinguish it from other types
    of messages.

    Attributes:
        content (str): The text content of the message.

    Methods:
        display: Returns a dictionary representation of the message for display,
                 tagging it with the role "user".
    """

    def __init__(self, content, name, tool_call_id):
        super().__init__(role='tool', content=content)
        self.name = name
        self.tool_call_id = tool_call_id
    

```

```swarmauri/standard/messages/concrete/SystemMessage.py

from swarmauri.standard.messages.base.MessageBase import MessageBase

class SystemMessage(MessageBase):
    """
    SystemMessage class represents a message generated by the system. 
    
    This type of message is used to communicate system-level information such as 
    errors, notifications, or updates to the user. Inherits from the Message base class.
    
    Attributes:
        content (str): The content of the system message.
    """
    
    def __init__(self, content):
        super().__init__(role='system', content=content)
    


```

```swarmauri/standard/parsers/__init__.py



```

```swarmauri/standard/parsers/base/__init__.py



```

```swarmauri/standard/parsers/concrete/__init__.py



```

```swarmauri/standard/parsers/concrete/CSVParser.py

import csv
from io import StringIO
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class CSVParser(IParser):
    """
    Concrete implementation of IParser for parsing CSV formatted text into Document instances.

    The parser can handle input as a CSV formatted string or from a file, with each row
    represented as a separate Document. Assumes the first row is the header which will
    be used as keys for document metadata.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given CSV data into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The input data to parse, either as a CSV string or file path.

        Returns:
        - List[IDocument]: A list of documents parsed from the CSV data.
        """
        # Prepare an in-memory string buffer if the data is provided as a string
        if isinstance(data, str):
            data_stream = StringIO(data)
        else:
            raise ValueError("Data provided is not a valid CSV string")

        # Create a list to hold the parsed documents
        documents: List[IDocument] = []

        # Read CSV content row by row
        reader = csv.DictReader(data_stream)
        for row in reader:
            # Each row represents a document, where the column headers are metadata fields
            document = Document(doc_id=row.get('id', None), 
                                        content=row.get('content', ''), 
                                        metadata=row)
            documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/EntityRecognitionParser.py

import spacy
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class EntityRecognitionParser(IParser):
    """
    EntityRecognitionParser leverages NER capabilities to parse text and 
    extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.
    """

    def __init__(self):
        # Load a SpaCy model. The small model is used for demonstration; larger models provide improved accuracy.
        self.nlp = spacy.load("en_core_web_sm")
    
    def parse(self, text: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input text, identifies entities, and returns a list of documents with entities tagged.

        Parameters:
        - text (Union[str, Any]): The input text to be parsed and analyzed for entities.

        Returns:
        - List[IDocument]: A list of IDocument instances representing the identified entities in the text.
        """
        # Ensure the input is a string type before processing
        if not isinstance(text, str):
            text = str(text)
        
        # Apply the NER model
        doc = self.nlp(text)

        # Compile identified entities into documents
        entities_docs = []
        for ent in doc.ents:
            # Create a document for each entity with metadata carrying entity type
            entity_doc = Document(doc_id=ent.text, content=ent.text, metadata={"entity_type": ent.label_})
            entities_docs.append(entity_doc)
        
        return entities_docs

```

```swarmauri/standard/parsers/concrete/HtmlTagStripParser.py

from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
import html
import re

class HTMLTagStripParser(IParser):
    """
    A concrete parser that removes HTML tags and unescapes HTML content,
    leaving plain text.
    """

    def parse(self, data):
        """
        Strips HTML tags from input data and unescapes HTML content.
        
        Args:
            data (str): The HTML content to be parsed.
        
        Returns:
            List[IDocument]: A list containing a single IDocument instance of the stripped text.
        """

        # Ensure that input is a string
        if not isinstance(data, str):
            raise ValueError("HTMLTagStripParser expects input data to be of type str.")
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', data)  # Matches anything in < > and replaces it with empty string
        
        # Unescape HTML entities
        text = html.unescape(text)

        # Wrap the cleaned text into a Document and return it in a list
        document = Document(doc_id="1", content=text, metadata={"original_length": len(data)})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/KeywordExtractorParser.py

import yake
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class KeywordExtractorParser(IParser):
    """
    Extracts keywords from text using the YAKE keyword extraction library.
    """

    def __init__(self, lang: str = 'en', num_keywords: int = 10):
        """
        Initialize the keyword extractor with specified language and number of keywords.

        Parameters:
        - lang (str): The language of the text for keyword extraction. Default is 'en' for English.
        - num_keywords (int): The number of top keywords to extract. Default is 10.
        """
        self.lang = lang
        self.num_keywords = num_keywords
        # Initialize YAKE extractor with specified parameters
        self.kw_extractor = yake.KeywordExtractor(lan=lang, n=3, dedupLim=0.9, dedupFunc='seqm', windowsSize=1, top=num_keywords, features=None)

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Extract keywords from input text and return as list of IDocument instances containing keyword information.

        Parameters:
        - data (Union[str, Any]): The input text from which to extract keywords.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing information about an extracted keyword.
        """
        # Ensure data is in string format for analysis
        text = str(data) if not isinstance(data, str) else data

        # Extract keywords using YAKE
        keywords = self.kw_extractor.extract_keywords(text)

        # Create Document instances for each keyword
        documents = [Document(doc_id=str(index), content=keyword, metadata={"score": score}) for index, (keyword, score) in enumerate(keywords)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/MarkdownParser.py

import re
from markdown import markdown
from bs4 import BeautifulSoup
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class MarkdownParser(IParser):
    """
    A concrete implementation of the IParser interface that parses Markdown text.
    
    This parser takes Markdown formatted text, converts it to HTML using Python's
    markdown library, and then uses BeautifulSoup to extract plain text content. The
    resulting plain text is then wrapped into IDocument instances.
    """
    
    def parse(self, data: str) -> list[IDocument]:
        """
        Parses the input Markdown data into a list of IDocument instances.
        
        Parameters:
        - data (str): The input Markdown formatted text to be parsed.
        
        Returns:
        - list[IDocument]: A list containing a single IDocument instance with the parsed text content.
        """
        # Convert Markdown to HTML
        html_content = markdown(data)
        
        # Use BeautifulSoup to extract text content from HTML
        soup = BeautifulSoup(html_content, features="html.parser")
        plain_text = soup.get_text(separator=" ", strip=True)
        
        # Generate a document ID
        doc_id = "1"  # For this implementation, a simple fixed ID is used. 
                      # A more complex system might generate unique IDs for each piece of text.

        # Create and return a list containing the single extracted plain text document
        document = Document(doc_id=doc_id, content=plain_text, metadata={"source_format": "markdown"})
        return [document]

```

```swarmauri/standard/parsers/concrete/OpenAPISpecParser.py

from typing import List, Union, Any
import yaml
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class OpenAPISpecParser(IParser):
    """
    A parser that processes OpenAPI Specification files (YAML or JSON format)
    and extracts information into structured Document instances. 
    This is useful for building documentation, APIs inventory, or analyzing the API specification.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses an OpenAPI Specification from a YAML or JSON string into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The OpenAPI specification in YAML or JSON format as a string.

        Returns:
        - List[IDocument]: A list of Document instances representing the parsed information.
        """
        try:
            # Load the OpenAPI spec into a Python dictionary
            spec_dict = yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse the OpenAPI specification: {e}")
        
        documents = []
        # Iterate over paths in the OpenAPI spec to extract endpoint information
        for path, path_item in spec_dict.get("paths", {}).items():
            for method, operation in path_item.items():
                # Create a Document instance for each operation
                doc_id = f"{path}_{method}"
                content = yaml.dump(operation)
                metadata = {
                    "path": path,
                    "method": method.upper(),
                    "operationId": operation.get("operationId", "")
                }
                document = Document(doc_id=doc_id, content=content, metadata=metadata)
                documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/PhoneNumberExtractorParser.py

import re
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class PhoneNumberExtractorParser(IParser):
    """
    A parser that extracts phone numbers from the input text.
    Utilizes regular expressions to identify phone numbers in various formats.
    """

    def __init__(self):
        """
        Initializes the PhoneNumberExtractorParser.
        """
        super().__init__()

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input data, looking for phone numbers employing a regular expression.
        Each phone number found is contained in a separate IDocument instance.

        Parameters:
        - data (Union[str, Any]): The input text to be parsed for phone numbers.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing a phone number.
        """
        # Define a regular expression for phone numbers.
        # This is a simple example and might not capture all phone number formats accurately.
        phone_regex = r'\+?\d[\d -]{8,}\d'

        # Find all occurrences of phone numbers in the text
        phone_numbers = re.findall(phone_regex, str(data))

        # Create a new IDocument for each phone number found
        documents = [Document(doc_id=str(index), content=phone_number, metadata={}) for index, phone_number in enumerate(phone_numbers)]

        return documents

```

```swarmauri/standard/parsers/concrete/PythonParser.py

from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
import ast
import uuid

class PythonParser(IParser):
    """
    A parser that processes Python source code to extract structural elements
    such as functions, classes, and their docstrings.
    
    This parser utilizes the `ast` module to parse the Python code into an abstract syntax tree (AST)
    and then walks the tree to extract relevant information.
    """
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given Python source code to extract structural elements.

        Args:
            data (Union[str, Any]): The input Python source code as a string.

        Returns:
            List[IDocument]: A list of IDocument objects, each representing a structural element 
                             extracted from the code along with its metadata.
        """
        if not isinstance(data, str):
            raise ValueError("PythonParser expects a string input.")
        
        documents = []
        tree = ast.parse(data)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                element_name = node.name
                docstring = ast.get_docstring(node)
                
                # Generate a unique ID for each element
                doc_id = str(uuid.uuid4())
                
                # Create a metadata dictionary
                metadata = {
                    "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                    "name": element_name,
                    "docstring": docstring
                }
                
                # Create a Document for each structural element
                document = Document(doc_id=doc_id, content=docstring, metadata=metadata)
                documents.append(document)
                
        return documents

```

```swarmauri/standard/parsers/concrete/RegExParser.py

import re
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class RegExParser(IParser):
    """
    A parser that uses a regular expression to extract information from text.
    """

    def __init__(self, pattern: str):
        """
        Initializes the RegExParser with a specific regular expression pattern.

        Parameters:
        - pattern (str): The regular expression pattern used for parsing the text.
        """
        self.pattern = pattern

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input data using the specified regular expression pattern and
        returns a list of IDocument instances containing the extracted information.

        Parameters:
        - data (Union[str, Any]): The input data to be parsed. It can be a string or any format 
                                   that the concrete implementation can handle.

        Returns:
        - List[IDocument]: A list of IDocument instances containing the parsed information.
        """
        # Ensure data is a string
        if not isinstance(data, str):
            data = str(data)

        # Use the regular expression pattern to find all matches in the text
        matches = re.findall(self.pattern, data)

        # Create a Document for each match and collect them into a list
        documents = [Document(doc_id=str(i+1), content=match, metadata={}) for i, match in enumerate(matches)]

        return documents

```

```swarmauri/standard/parsers/concrete/TextBlobNounParser.py

from typing import List, Union, Any
from textblob import TextBlob
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class TextBlobNounParser(IParser):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.
    
    This parser leverages TextBlob's functionalities such as noun phrase extraction, 
    sentiment analysis, classification, language translation, and more for parsing texts.
    """
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input data using TextBlob to perform basic NLP tasks 
        and returns a list of documents with the parsed information.
        
        Parameters:
        - data (Union[str, Any]): The input data to parse, expected to be text data for this parser.
        
        Returns:
        - List[IDocument]: A list of documents with metadata generated from the parsing process.
        """
        # Ensure the data is a string
        if not isinstance(data, str):
            raise ValueError("TextBlobParser expects a string as input data.")
        
        # Use TextBlob for NLP tasks
        blob = TextBlob(data)
        
        # Extracts noun phrases to demonstrate one of TextBlob's capabilities. 
        # In practice, this parser could be expanded to include more sophisticated processing.
        noun_phrases = list(blob.noun_phrases)
        
        # Example: Wrap the extracted noun phrases into an IDocument instance
        # In real scenarios, you might want to include more details, like sentiment, POS tags, etc.
        document = Document(doc_id="0", content=data, metadata={"noun_phrases": noun_phrases})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/TextBlobSentenceParser.py

from textblob import TextBlob
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document
from typing import List, Union, Any

class TextBlobParser(IParser):
    """
    A parser that leverages TextBlob to break text into sentences.

    This parser uses the natural language processing capabilities of TextBlob
    to accurately identify sentence boundaries within large blocks of text.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input text into sentence-based document chunks using TextBlob.

        Args:
            data (Union[str, Any]): The input text to be parsed.

        Returns:
            List[IDocument]: A list of IDocument instances, each representing a sentence.
        """
        # Ensure the input is a string
        if not isinstance(data, str):
            data = str(data)

        # Utilize TextBlob for sentence tokenization
        blob = TextBlob(data)
        sentences = blob.sentences

        # Create a document instance for each sentence
        documents = [
            Document(doc_id=str(index), content=str(sentence), metadata={'parser': 'TextBlobParser'})
            for index, sentence in enumerate(sentences)
        ]

        return documents

```

```swarmauri/standard/parsers/concrete/TFIDFParser.py

from sklearn.feature_extraction.text import TfidfVectorizer
from swarmauri.core.parsers.IParser import IParser
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document

class TFIDFParser(IParser):
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        super().__init__()

    def parse(self, data):
        # Assuming `data` is a list of strings (documents)
        tfidf_matrix = self.vectorizer.fit_transform(data)
        # Depending on how you want to use the output, you could return Document objects
        # For demonstration, let's return a list of IDocument with vectorized content
        documents = [Document(doc_id=str(i), content=vector, metadata={}) for i, vector in enumerate(tfidf_matrix.toarray())]
        return documents

```

```swarmauri/standard/parsers/concrete/URLExtractorParser.py

from typing import List, Union, Any
from urllib.parse import urlparse
import re
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class URLExtractorParser(IParser):
    """
    A concrete implementation of IParser that extracts URLs from text.
    
    This parser scans the input text for any URLs and creates separate
    documents for each extracted URL. It utilizes regular expressions
    to identify URLs within the given text.
    """

    def __init__(self):
        """
        Initializes the URLExtractorParser.
        """
        super().__init__()
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parse input data (string) and extract URLs, each URL is then represented as a document.
        
        Parameters:
        - data (Union[str, Any]): The input data to be parsed for URLs.
        
        Returns:
        - List[IDocument]: A list of documents, each representing an extracted URL.
        """
        if not isinstance(data, str):
            raise ValueError("URLExtractorParser expects input data to be of type str.")

        # Regular expression for finding URLs
        url_regex = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        
        # Find all matches in the text
        urls = re.findall(url_regex, data)
        
        # Create a document for each extracted URL
        documents = [Document(doc_id=str(i), content=url, metadata={"source": "URLExtractor"}) for i, url in enumerate(urls)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/XMLParser.py

import xml.etree.ElementTree as ET
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class XMLParser(IParser):
    """
    A parser that extracts information from XML data and converts it into IDocument objects.
    This parser assumes a simple use-case where each targeted XML element represents a separate document.
    """

    def __init__(self, element_tag: str):
        """
        Initialize the XMLParser with the tag name of the XML elements to be extracted as documents.

        Parameters:
        - element_tag (str): The tag name of XML elements to parse into documents.
        """
        self.element_tag = element_tag

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses XML data and converts elements with the specified tag into IDocument instances.

        Parameters:
        - data (Union[str, Any]): The XML data as a string to be parsed.

        Returns:
        - List[IDocument]: A list of IDocument instances created from the XML elements.
        """
        if isinstance(data, str):
            root = ET.fromstring(data)  # Parse the XML string into an ElementTree element
        else:
            raise TypeError("Data for XMLParser must be a string containing valid XML.")

        documents = []
        for element in root.findall(self.element_tag):
            # Extracting content and metadata from each element
            content = "".join(element.itertext())  # Get text content
            metadata = {child.tag: child.text for child in element}  # Extract child elements as metadata

            # Create a Document instance for each element
            doc = Document(doc_id=None, content=content, metadata=metadata)
            documents.append(doc)

        return documents

```

```swarmauri/standard/parsers/concrete/BERTEmbeddingParser.py

from typing import List, Union, Any
from transformers import BertTokenizer, BertModel
import torch
from swarmauri.core.parsers.IParser import IParser
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document

class BERTEmbeddingParser(IParser):
    """
    A parser that transforms input text into document embeddings using BERT.
    
    This parser tokenizes the input text, passes it through a pre-trained BERT model,
    and uses the resulting embeddings as the document content.
    """

    def __init__(self, model_name: str = 'bert-base-uncased'):
        """
        Initializes the BERTEmbeddingParser with a specific BERT model.
        
        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()  # Set model to evaluation mode

    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Tokenizes input data and generates embeddings using a BERT model.

        Parameters:
        - data (Union[str, Any]): Input data, expected to be a single string or batch of strings.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with BERT embeddings as content.
        """
        
        # Tokenization
        inputs = self.tokenizer(data, return_tensors='pt', padding=True, truncation=True, max_length=512)

        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use the last hidden state as document embeddings (batch_size, sequence_length, hidden_size)
        embeddings = outputs.last_hidden_state
        
        # Convert to list of numpy arrays
        embeddings = embeddings.detach().cpu().numpy()
        
        # For simplicity, let's consider the mean of embeddings across tokens to represent the document
        doc_embeddings = embeddings.mean(axis=1)
        
        # Creating document object(s)
        documents = [Document(doc_id=str(i), content=emb, metadata={"source": "BERTEmbeddingParser"}) for i, emb in enumerate(doc_embeddings)]
        
        return documents

```

```swarmauri/standard/prompts/__init__.py



```

```swarmauri/standard/prompts/base/__init__.py



```

```swarmauri/standard/prompts/concrete/__init__.py



```

```swarmauri/standard/prompts/concrete/Prompt.py

from ....core.prompts.IPrompt import IPrompt

class Prompt(IPrompt):
    """
    The ChatPrompt class represents a simple, chat-like prompt system where a 
    message can be set and retrieved as needed. It's particularly useful in 
    applications involving conversational agents, chatbots, or any system that 
    requires dynamic text-based interactions.
    """

    def __init__(self, prompt: str = ""):
        """
        Initializes an instance of ChatPrompt with an optional initial message.
        
        Parameters:
        - message (str, optional): The initial message for the prompt. Defaults to an empty string.
        """
        self.prompt = prompt

    def __call__(self, prompt):
        """
        Enables the instance to be callable, allowing direct retrieval of the message. 
        This method facilitates intuitive access to the prompt's message, mimicking callable 
        behavior seen in functional programming paradigms.
        
        Returns:
        - str: The current message stored in the prompt.
        """
        return self.prompt

    def set_prompt(self, prompt: str):
        """
        Updates the internal message of the chat prompt. This method provides a way to change 
        the content of the prompt dynamically, reflecting changes in the conversational context 
        or user inputs.
        
        Parameters:
        - message (str): The new message to set for the prompt.
        """
        self.prompt = prompt


```

```swarmauri/standard/prompts/concrete/PromptTemplate.py

from typing import Dict
from ....core.prompts.IPrompt import IPrompt

class PromptTemplate(IPrompt):
    """
    A class that represents a template for generating prompts, 
    allowing dynamic content insertion into pre-defined template slots.

    Attributes:
        template (str): A string template with placeholders for content insertion.
        variables (Dict[str, str]): A dictionary mapping placeholder names in the template to their content.
    """

    def __init__(self, template: str = "", variables: Dict[str, str] = {}):
        """
        Initializes a new instance of the PromptTemplate class.

        Args:
            template (str): The string template for the prompt.
            variables (Dict[str, str]): A dictionary mapping variables in the template to their values.
        """
        self.template = template
        self.variables = variables

    def __call__(self, variables: Dict[str, str] = {}):
        """
        Generates the prompt string by substituting variables into the template.

        Returns:
            str: The generated prompt with variables substituted.
        """
        variables = variables or self.variables
        formatted_prompt = self.template.format(**variables)
        return formatted_prompt

    def set_template(self, template: str):
        """
        Sets a new template string for the prompt.

        Args:
            template (str): The new string template to use.
        """
        self.template = template

    def set_variables(self, variables: Dict[str, str]):
        """
        Sets the variables to be substituted into the template.

        Args:
            variables (Dict[str, str]): A dictionary of variables to be substituted into the template.
        
        Raises:
            TypeError: If the provided variables argument is not a dictionary.
        """
        if isinstance(variables, dict):
            self.variables = variables
        else:
            raise TypeError("Invalid type. Expected dict for variables.")

```

```swarmauri/standard/states/__init__.py



```

```swarmauri/standard/states/base/__init__.py



```

```swarmauri/standard/states/concrete/__init__.py



```

```swarmauri/standard/swarms/__init__.py



```

```swarmauri/standard/swarms/base/__init__.py



```

```swarmauri/standard/swarms/base/SwarmComponentBase.py

from swarmauri.core.swarms.ISwarmComponent import ISwarmComponent

class SwarmComponentBase(ISwarmComponent):
    """
    Interface for defining basics of any component within the swarm system.
    """
    def __init__(self, key: str, name: str, superclass: str, module: str, class_name: str, args=None, kwargs=None):
        self.key = key
        self.name = name
        self.superclass = superclass
        self.module = module
        self.class_name = class_name
        self.args = args or []
        self.kwargs = kwargs or {}
    

```

```swarmauri/standard/swarms/concrete/__init__.py



```

```swarmauri/standard/swarms/concrete/SimpleSwarmFactory.py

import json
import pickle
from typing import List
from swarmauri.core.chains.ISwarmFactory import (
    ISwarmFactory , 
    CallableChainItem, 
    AgentDefinition, 
    FunctionDefinition
)
class SimpleSwarmFactory(ISwarmFactory):
    def __init__(self):
        self.swarms = []
        self.callable_chains = []

    def create_swarm(self, agents=[]):
        swarm = {"agents": agents}
        self.swarms.append(swarm)
        return swarm

    def create_agent(self, agent_definition: AgentDefinition):
        # For simplicity, agents are stored in a list
        # Real-world usage might involve more sophisticated management and instantiation based on type and configuration
        agent = {"definition": agent_definition._asdict()}
        self.agents.append(agent)
        return agent

    def create_callable_chain(self, chain_definition: List[CallableChainItem]):
        chain = {"definition": [item._asdict() for item in chain_definition]}
        self.callable_chains.append(chain)
        return chain

    def register_function(self, function_definition: FunctionDefinition):
        if function_definition.identifier in self.functions:
            raise ValueError(f"Function {function_definition.identifier} is already registered.")
        
        self.functions[function_definition.identifier] = function_definition
    
    def export_configuration(self, format_type: str = 'json'):
        # Now exporting both swarms and callable chains
        config = {"swarms": self.swarms, "callable_chains": self.callable_chains}
        if format_type == "json":
            return json.dumps(config)
        elif format_type == "pickle":
            return pickle.dumps(config)

    def load_configuration(self, config_data, format_type: str = 'json'):
        # Loading both swarms and callable chains
        config = json.loads(config_data) if format_type == "json" else pickle.loads(config_data)
        self.swarms = config.get("swarms", [])
        self.callable_chains = config.get("callable_chains", [])

```

```swarmauri/standard/toolkits/__init__.py



```

```swarmauri/standard/toolkits/base/__init__.py



```

```swarmauri/standard/toolkits/base/ToolkitBase.py

from abc import ABC, abstractmethod
from typing import Dict
from ....core.toolkits.IToolkit import IToolkit
from ....core.tools.ITool import ITool  

class ToolkitBase(IToolkit, ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @abstractmethod
    def __init__(self, initial_tools: Dict[str, ITool] = None):
        """
        Initialize the Toolkit with an optional dictionary of initial tools.
        """
        # If initial_tools is provided, use it; otherwise, use an empty dictionary
        self._tools = initial_tools if initial_tools is not None else {}

    @property
    def tools(self) -> Dict[str, ITool]:
        return [self._tools[tool].as_dict() for tool in self._tools]

    def add_tools(self, tools: Dict[str, ITool]):
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self._tools.update(tools)

    def add_tool(self, tool: ITool):
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self._tools[tool.function['name']] = tool

    def remove_tool(self, tool_name: str):
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def get_tool_by_name(self, tool_name: str) -> ITool:
        """
        Get a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Tool: The tool instance with the specified name.
        """
        if tool_name in self._tools:
            return self._tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolkit.

        Returns:
            int: The number of tools in the toolkit.
        """
        return len(self._tools)

```

```swarmauri/standard/toolkits/concrete/__init__.py



```

```swarmauri/standard/toolkits/concrete/Toolkit.py

from typing import Dict
from ..base.ToolkitBase import ToolkitBase
from ....core.tools.ITool import ITool

class Toolkit(ToolkitBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    def __init__(self, initial_tools: Dict[str, ITool] = None):
        """
        Initialize the Toolkit with an optional dictionary of initial tools.
        """
        
        super().__init__(initial_tools)
    

```

```swarmauri/standard/tools/__init__.py



```

```swarmauri/standard/tools/base/__init__.py



```

```swarmauri/standard/tools/base/ToolBase.py

from typing import Optional, List, Any
from abc import ABC, abstractmethod
import json
from swarmauri.core.tools.ITool import ITool
        
class ToolBase(ITool, ABC):
    
    @abstractmethod
    def __init__(self, name, description, parameters=[]):
        self._name = name
        self._description = description
        self._parameters = parameters
        self.type = "function"
        self.function = {
            "name": name,
            "description": description,
        }
        
        # Dynamically constructing the parameters schema
        properties = {}
        required = []
        
        for param in parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)
        
        self.function['parameters'] = {
            "type": "object",
            "properties": properties,
        }
        
        if required:  # Only include 'required' if there are any required parameters
            self.function['parameters']['required'] = required


    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def parameters(self):
        return self._parameters

    def __iter__(self):
        yield ('type', self.type)
        yield ('function', self.function)
        

    def as_dict(self):
        return {'type': self.type, 'function': self.function}
        # return self.__dict__

    def to_json(obj):
        return json.dumps(obj, default=lambda obj: obj.__dict__)

    def __getstate__(self):
        return {'type': self.type, 'function': self.function}


    def __call__(self, *args, **kwargs):
        """
        Placeholder method for executing the functionality of the tool.
        Subclasses should override this method to define specific tool behaviors.

        Parameters:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        raise NotImplementedError("Subclasses must implement the call_function method.")

```

```swarmauri/standard/tools/concrete/__init__.py



```

```swarmauri/standard/tools/concrete/TestTool.py

import json
import subprocess as sp
from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class TestTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="program",
                type="string",
                description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
                required=True,
                enum=["notepad", "calc", "mspaint"]
            )
        ]
        
        super().__init__(name="TestTool", 
                         description="This opens a program based on the user's request.", 
                         parameters=parameters)

    def __call__(self, program) -> str:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Program Opened: {program}\n"


```

```swarmauri/standard/tools/concrete/WeatherTool.py

import json
from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class WeatherTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="location",
                type="string",
                description="The location for which to fetch weather information",
                required=True
            ),
            Parameter(
                name="unit",
                type="string",
                description="The unit for temperature ('fahrenheit' or 'celsius')",
                required=True,
                enum=["fahrenheit", "celsius"]
            )
        ]
        
        super().__init__(name="WeatherTool", description="Fetch current weather info for a location", parameters=parameters)

    def __call__(self, location, unit="fahrenheit") -> str:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Weather Info: {weather_info}\n"


```

```swarmauri/standard/tools/concrete/Parameter.py

from typing import Optional, List, Any
import json
from ....core.tools.IParameter import IParameter

class Parameter(IParameter):
    """
    A class to represent a parameter for a tool.

    Attributes:
        name (str): Name of the parameter.
        type (str): Data type of the parameter (e.g., 'int', 'str', 'float').
        description (str): A brief description of the parameter.
        required (bool): Whether the parameter is required or optional.
        enum (Optional[List[any]]): A list of acceptable values for the parameter, if any.
    """

    def __init__(self, name: str, type: str, description: str, required: bool = True, enum: Optional[List[Any]] = None):
        """
        Initializes a new instance of the Parameter class.

        Args:
            name (str): The name of the parameter.
            type (str): The type of the parameter.
            description (str): A brief description of what the parameter is used for.
            required (bool, optional): Specifies if the parameter is required. Defaults to True.
            enum (Optional[List[Any]], optional): A list of acceptable values for the parameter. Defaults to None.
        """
        self._name = name
        self._type = type
        self._description = description
        self._required = required
        self._enum = enum
        
    @property
    def name(self) -> str:
        """
        Abstract property for getting the name of the parameter.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Abstract setter for setting the name of the parameter.
        """
        self._name = value

    @property
    def type(self) -> str:
        """
        Abstract property for getting the type of the parameter.
        """
        return self._type

    @type.setter
    def type(self, value: str):
        """
        Abstract setter for setting the type of the parameter.
        """
        self._type = value

    @property
    def description(self) -> str:
        """
        Abstract property for getting the description of the parameter.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Abstract setter for setting the description of the parameter.
        """
        self._description = value

    @property
    def required(self) -> bool:
        """
        Abstract property for getting the required status of the parameter.
        """
        return self._required

    @required.setter
    def required(self, value: bool):
        """
        Abstract setter for setting the required status of the parameter.
        """
        self._required = value

    @property
    def enum(self) -> Optional[List[Any]]:
        """
        Abstract property for getting the enum list of the parameter.
        """
        return self._enum

    @enum.setter
    def enum(self, value: Optional[List[Any]]):
        """
        Abstract setter for setting the enum list of the parameter.
        """
        self._enum = value

```

```swarmauri/standard/tools/concrete/AdditionTool.py

from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class AdditionTool(ToolBase):
    
    def __init__(self):
        parameters = [
            Parameter(
                name="x",
                type="integer",
                description="The left operand",
                required=True
            ),
            Parameter(
                name="y",
                type="integer",
                description="The right operand",
                required=True
            )
        ]
        super().__init__(name="TestTool", 
                         description="This opens a program based on the user's request.", 
                         parameters=parameters)

    def __call__(self, x: int, y: int) -> int:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - int: The sum of x and y.
        """
        return x + y

```

```swarmauri/standard/apis/__init__.py



```

```swarmauri/standard/apis/base/__init__.py



```

```swarmauri/standard/apis/concrete/__init__.py



```

```swarmauri/standard/vector_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/base/VectorDocumentStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class VectorDocumentStoreBase(IDocumentStore, ABC):
    """
    Abstract base class for document stores, implementing the IDocumentStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[IDocument]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass
    
    def document_count(self):
        return len(self.documents)
    
    def dump(self, file_path):
        with open(file_path, 'w') as f:
            json.dumps([each.__dict__ for each in self.documents], f, indent=4)
            
    def load(self, file_path):
        with open(file_path, 'r') as f:
            self.documents = json.loads(f)

```

```swarmauri/standard/vector_stores/base/VectorDocumentStoreRetrieveBase.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri.standard.vector_stores.base.VectorDocumentStoreBase import VectorDocumentStoreBase

class VectorDocumentStoreRetrieveBase(VectorDocumentStoreBase, IDocumentRetrieve, ABC):
        
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/standard/vector_stores/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/concrete/FaissVectorStore.py

import faiss
import numpy as np
from typing import List, Dict

from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vector_stores.ISimilarityQuery import ISimilarityQuery
from swarmauri.core.vectors.IVector import IVector

class FaissVectorStore(IVectorStore, ISimilarityQuery):
    """
    A vector store that utilizes FAISS for efficient similarity searches.
    """

    def __init__(self, dimension: int, index_type: str = "IVF256,Flat"):
        """
        Initialize the FAISS vector store with the given dimension and index type.

        Parameters:
        - dimension (int): The dimensionality of the vectors being stored.
        - index_type (str): The FAISS index type. Defaults to "IVF256,Flat" for an inverted file index.
        """
        self.dimension = dimension
        self.index = faiss.index_factory(dimension, index_type)
        self.id_to_vector = {}
        self.id_to_metadata = {}

    def add_vector(self, vector_id: str, vector: IVector, metadata: Dict = None) -> None:
        """
        Add a vector along with its identifier and optional metadata to the store.

        Parameters:
        - vector_id (str): Unique identifier for the vector.
        - vector (IVector): The high-dimensional vector to be stored.
        - metadata (Dict, optional): Optional metadata related to the vector.
        """
        # Ensure the vector is a numpy array and add it to the FAISS index
        np_vector = np.array(vector.data, dtype='float32').reshape(1, -1)
        self.index.add(np_vector)
        self.id_to_vector[vector_id] = vector
        if metadata:
            self.id_to_metadata[vector_id] = metadata

    def get_vector(self, vector_id: str) -> IVector:
        """
        Retrieve a vector by its identifier.

        Parameters:
        - vector_id (str): The unique identifier for the vector.

        Returns:
        - IVector: The vector associated with the given ID.
        """
        return self.id_to_vector.get(vector_id)

    def search_by_similarity_threshold(self, query_vector: List[float], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Parameters:
        - query_vector (List[float]): The high-dimensional query vector.
        - similarity_threshold (float): The similarity threshold for filtering results.

        Returns:
        - List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        # FAISS requires numpy arrays in float32 for searches
        np_query_vector = np.array(query_vector, dtype='float32').reshape(1, -1)

        # Perform the search. FAISS returns distances, which can be converted to similarities.
        _, I = self.index.search(np_query_vector, k=self.index.ntotal)  # Searching the entire index
        results = []
        for idx in I[0]:
            vector_id = list(self.id_to_vector.keys())[idx]
            # Simulate a similarity score based on the FAISS distance metric (e.g., L2 distance for now).
            # Note: Depending on the index type and application, you might want to convert distances to actual similarities.
            results.append({"id": vector_id, "score": similarity_threshold, "metadata": self.id_to_metadata.get(vector_id)})

        return results

```

```swarmauri/standard/vector_stores/concrete/WeaviateVectorStore.py

from typing import List, Dict
import weaviate
from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class WeaviateVectorStore(IVectorStore):
    def __init__(self, weaviate_url: str):
        self.client = weaviate.Client(url=weaviate_url)
        # Set up schema if not exists, etc.
        pass
    
    def add_vector(self, vector_id: str, vector: IVector, metadata: Dict = None) -> None:
        data_object = {
            "vector": vector.data
        }
        if metadata:
            data_object["metadata"] = metadata
        self.client.data_object.create(data_object=data_object, class_name="Vector", uuid=vector_id)
    
    def get_vector(self, vector_id: str) -> IVector:
        result = self.client.data_object.get_by_id(vector_id, ["vector"])
        return SimpleVector(result['vector'])
    
    def delete_vector(self, vector_id: str) -> None:
        self.client.data_object.delete(vector_id)
    
    def update_vector(self, vector_id: str, new_vector: IVector, new_metadata: Dict = None) -> None:
        update_object = {
            "vector": new_vector.data
        }
        if new_metadata:
            update_object["metadata"] = new_metadata
        self.client.data_object.update(object_id=vector_id, data_object=update_object)
    
    # Implement other methods like search_by_similarity_threshold from ISimilarityQuery interface, etc.

```

```swarmauri/standard/vector_stores/concrete/TFIDFVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vectorizers.concrete.TFIDFVectorizer import TFIDFVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

class TFIDFVectorStore(VectorDocumentStoreRetrieveBase):
    def __init__(self):
        self.vectorizer = TFIDFVectorizer()
        self.metric = CosineDistance()
        self.documents = []      

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None

    def get_all_documents(self) -> List[IDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        transform_matrix = self.vectorizer.fit_transform(query, self.documents)

        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self.metric.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/BERTVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.BERTEmbeddingVectorizer import BERTEmbeddingVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

class BERTVectorStore(VectorDocumentStoreRetrieveBase):
    def __init__(self):
        self.documents: List[EmbeddedDocument] = []
        self.vectorizer = BERTEmbeddingVectorizer()  # Assuming this is already implemented
        self.metric = CosineDistance()

    def add_document(self, document: IDocument) -> None:
        """
        Override: Now documents are expected to have labels for fine-tuning when added. 
        For unsupervised use-cases, labels can be ignored at the vectorizer level.
        """
        self.documents.append(document)
        documents_text = [doc.content for doc in self.documents]
        documents_labels = [doc.metadata['label'] for doc in self.documents]
        self.vectorizer.fit(documents_text, documents_labels)
        embeddings = self.vectorizer.infer_vector(document.content)

        embedded_document = EmbeddedDocument(doc_id=document.id, 
            content=document.content, 
            metadata=document.metadata, 
            embedding=embeddings)

        self.documents.append(embedded_document)

    def add_documents(self, documents: List[IDocument]) -> None:
        # Batch addition of documents with potential fine-tuning trigger
        self.documents.extend(documents)
        documents_text = [doc.content for doc in documents]
        documents_labels = [doc.metadata['label'] for doc in self.documents]
        self.vectorizer.fit(documents_text, documents_labels)

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str) -> None:
        raise NotImplementedError('Update_document not implemented on BERTDocumentStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [doc.embedding for doc in self.documents]
        distances = [self.metric.similarities(query_vector, document_vectors)]
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i], reverse=True)[:top_k]
        
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/Doc2VecVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

class Doc2VecVectorStore(VectorDocumentStoreRetrieveBase):
    def __init__(self):
        self.vectorizer = Doc2VecVectorizer()
        self.metric = CosineDistance()
        self.documents = []      

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        self._recalculate_embeddings()

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        self._recalculate_embeddings()

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None

    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        self._recalculate_embeddings()

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break
        self._recalculate_embeddings()

    def _recalculate_embeddings(self):
        # Recalculate document embeddings for the current set of documents
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self.vectorizer.fit_transform(documents_text)

        embedded_documents = [EmbeddedDocument(doc_id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents)
            if _d.content]

        self.documents = embedded_documents

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]

        distances = self.metric.distances(query_vector, document_vectors)

        # Get the indices of the top_k least distant (most similar) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/MLMVectorStore.py

from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.MLMVectorizer import MLMVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

class MLMVectorStore(VectorDocumentStoreRetrieveBase):
    def __init__(self):
        self.documents: List[EmbeddedDocument] = []
        self.vectorizer = MLMVectorizer()  # Assuming this is already implemented
        self.metric = CosineDistance()

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self.vectorizer.fit_transform(documents_text)

        embedded_documents = [EmbeddedDocument(doc_id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count])

        for _count, _d in enumerate(self.documents) if _d.content]

        self.documents = embedded_documents

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self.vectorizer.fit_transform(documents_text)

        embedded_documents = [EmbeddedDocument(doc_id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents) 
            if _d.content]

        self.documents = embedded_documents

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != doc_id]

    def update_document(self, doc_id: str) -> None:
        raise NotImplementedError('Update_document not implemented on BERTDocumentStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self.metric.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/document_stores/__init__.py



```

```swarmauri/standard/document_stores/base/__init__.py



```

```swarmauri/standard/document_stores/base/DocumentStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class DocumentStoreBase(IDocumentStore, ABC):
    """
    Abstract base class for document stores, implementing the IDocumentStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[IDocument]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass
    
    def document_count(self):
        return len(self.documents)
    
    def dump(self, file_path):
        with open(file_path, 'w') as f:
            json.dumps([each.__dict__ for each in self.documents], f, indent=4)
            
    def load(self, file_path):
        with open(file_path, 'r') as f:
            self.documents = json.loads(f)

```

```swarmauri/standard/document_stores/base/DocumentStoreRetrieveBase.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.document_stores.base.DocumentStoreBase import DocumentStoreBase

class DocumentStoreRetrieveBase(DocumentStoreBase, IDocumentRetrieve, ABC):

        
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/standard/document_stores/concrete/__init__.py



```

```swarmauri/standard/chunkers/__init__.py



```

```swarmauri/standard/chunkers/base/__init__.py



```

```swarmauri/standard/chunkers/concrete/__init__.py



```

```swarmauri/standard/chunkers/concrete/SlidingWindowChunker.py

from typing import List
from swarmauri.core.chunkers.IChunker import IChunker

class SlidingWindowChunker(IChunker):
    """
    A concrete implementation of IChunker that uses sliding window technique
    to break the text into chunks.
    """
    
    def __init__(self, window_size: int, step_size: int, overlap: bool = True):
        """
        Initialize the SlidingWindowChunker with specific window and step sizes.
        
        Parameters:
        - window_size (int): The size of the window for each chunk (in terms of number of words).
        - step_size (int): The step size for the sliding window (in terms of number of words).
        - overlap (bool, optional): Whether the windows should overlap. Default is True.
        """
        self.window_size = window_size
        self.step_size = step_size if overlap else window_size  # Non-overlapping if window size equals step size.
           
    def chunk_text(self, text: str, *args, **kwargs) -> List[str]:
        """
        Splits the input text into chunks based on the sliding window technique.
        
        Parameters:
        - text (str): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        words = text.split()  # Tokenization by whitespaces. More sophisticated tokenization might be necessary.
        chunks = []
        
        for i in range(0, len(words) - self.window_size + 1, self.step_size):
            chunk = ' '.join(words[i:i+self.window_size])
            chunks.append(chunk)
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/DelimiterBasedChunker.py

from typing import List, Union, Any
import re
from swarmauri.core.chunkers.IChunker import IChunker

class DelimiterBasedChunker(IChunker):
    """
    A concrete implementation of IChunker that splits text into chunks based on specified delimiters.
    """

    def __init__(self, delimiters: List[str] = None):
        """
        Initializes the chunker with a list of delimiters.

        Parameters:
        - delimiters (List[str], optional): A list of strings that will be used as delimiters for splitting the text.
                                            If not specified, a default list of sentence-ending punctuation is used.
        """
        if delimiters is None:
            delimiters = ['.', '!', '?']  # Default delimiters
        # Create a regex pattern that matches any of the specified delimiters.
        # The pattern uses re.escape on each delimiter to ensure special regex characters are treated literally.
        self.delimiter_pattern = f"({'|'.join(map(re.escape, delimiters))})"
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Chunks the given text based on the delimiters specified during initialization.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks split based on the specified delimiters.
        """
        # Split the text based on the delimiter pattern, including the delimiters in the result
        chunks = re.split(self.delimiter_pattern, text)
        # Combine delimiters with the preceding text chunk since re.split() separates them
        combined_chunks = []
        for i in range(0, len(chunks) - 1, 2):  # Step by 2 to process text chunk with its following delimiter
            combined_chunks.append(chunks[i] + (chunks[i + 1] if i + 1 < len(chunks) else ''))
        return combined_chunks

```

```swarmauri/standard/chunkers/concrete/FixedLengthChunker.py

from typing import List, Union, Any
from swarmauri.core.chunkers.IChunker import IChunker

class FixedLengthChunker(IChunker):
    """
    Concrete implementation of IChunker that divides text into fixed-length chunks.
    
    This chunker breaks the input text into chunks of a specified size, making sure 
    that each chunk has exactly the number of characters specified by the chunk size, 
    except for possibly the last chunk.
    """

    def __init__(self, chunk_size: int):
        """
        Initializes a new instance of the FixedLengthChunker class with a specific chunk size.

        Parameters:
        - chunk_size (int): The fixed size (number of characters) for each chunk.
        """
        self.chunk_size = chunk_size

    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Splits the input text into fixed-length chunks.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks, each of a specified fixed length.
        """
        # Check if the input is a string, if not, attempt to convert to a string.
        if not isinstance(text, str):
            text = str(text)
        
        # Using list comprehension to split text into chunks of fixed size
        chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/SimpleSentenceChunker.py

import re
from swarmauri.core.chunkers.IChunker import IChunker

class SimpleSentenceChunker(IChunker):
    """
    A simple implementation of the IChunker interface to chunk text into sentences.
    
    This class uses basic punctuation marks (., !, and ?) as indicators for sentence boundaries.
    """
    
    def chunk_text(self, text, *args, **kwargs):
        """
        Chunks the given text into sentences using basic punctuation.

        Args:
            text (str): The input text to be chunked into sentences.
        
        Returns:
            List[str]: A list of sentence chunks.
        """
        # Split text using a simple regex pattern that looks for periods, exclamation marks, or question marks.
        # Note: This is a very simple approach and might not work well with abbreviations or other edge cases.
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out any empty strings that may have resulted from the split operation
        sentences = [sentence.strip() for sentence in sentences if sentence]
        
        return sentences

```

```swarmauri/standard/chunkers/concrete/MdSnippetChunker.py

from typing import List, Union, Any, Optional
import re
from swarmauri.core.chunkers.IChunker import IChunker

class MdSnippetChunker(IChunker):
    def __init__(self, language: Optional[str] = None):
        """
        Initializes the MdSnippetChunker with a specific programming language
        to look for within Markdown fenced code blocks.
        """
        self.language = language
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[tuple]:
        """
        Extracts paired comments and code blocks from Markdown content based on the 
        specified programming language.
        """
        if self.language:
            # If language is specified, directly extract the corresponding blocks
            pattern = fr'```{self.language}\s*(.*?)```'
            scripts = re.findall(pattern, text, re.DOTALL)
            comments_temp = re.split(pattern, text, flags=re.DOTALL)
        else:
            # Extract blocks and languages dynamically if no specific language is provided
            scripts = []
            languages = []
            for match in re.finditer(r'```(\w+)?\s*(.*?)```', text, re.DOTALL):
                if match.group(1) is not None:  # Checks if a language identifier is present
                    languages.append(match.group(1))
                    scripts.append(match.group(2))
                else:
                    languages.append('')  # Default to an empty string if no language is found
                    scripts.append(match.group(2))
            comments_temp = re.split(r'```.*?```', text, flags=re.DOTALL)

        comments = [comment.strip() for comment in comments_temp]

        if text.strip().startswith('```'):
            comments = [''] + comments
        if text.strip().endswith('```'):
            comments.append('')

        if self.language:
            structured_output = [(comments[i], self.language, scripts[i].strip()) for i in range(len(scripts))]
        else:
            structured_output = [(comments[i], languages[i], scripts[i].strip()) for i in range(len(scripts))]

        return structured_output


```

```swarmauri/standard/vectors/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/base/VectorBase.py

from abc import ABC, abstractmethod
from typing import List
import numpy as np
from swarmauri.core.vectors.IVector import IVector

class VectorBase(IVector, ABC):
    def __init__(self, data: List[float]):
        self._data = data

    @property
    def data(self) -> List[float]:
        """
        Returns the vector's data.
        """
        return self._data
    
    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self._data)
    
    def __repr__(self):
        return str(self.data)
    
    def __len__(self):
        return len(self.data)

```

```swarmauri/standard/vectors/concrete/SimpleVector.py

from typing import List
from swarmauri.standard.vectors.base.VectorBase import VectorBase

class SimpleVector(VectorBase):
    def __init__(self, data: List[float]):
        super().__init__(data)
        

```

```swarmauri/standard/vectors/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/concrete/VectorProduct.py

import numpy as np
from typing import List

from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vectors.IVectorProduct import IVectorProduct
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class VectorProduct(IVectorProduct):
    def dot_product(self, vector_a: IVector, vector_b: IVector) -> float:
        a = np.array(vector_a.data).flatten()
        b = np.array(vector_b.data).flatten()
        return np.dot(a, b)
    
    def cross_product(self, vector_a: IVector, vector_b: IVector) -> IVector:
        if len(vector_a.data) != 3 or len(vector_b.data) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        cross = np.cross(a, b)
        return SimpleVector(cross.tolist())
    
    def vector_triple_product(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> IVector:
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        c = np.array(vector_c.data)
        result = np.cross(a, np.cross(b, c))
        return SimpleVector(result.tolist())
    
    def scalar_triple_product(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> float:
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        c = np.array(vector_c.data)
        return np.dot(a, np.cross(b, c))

```

```swarmauri/standard/vectorizers/__init__.py

#

```

```swarmauri/standard/vectorizers/base/__init__.py

#

```

```swarmauri/standard/vectorizers/concrete/__init__.py

#

```

```swarmauri/standard/vectorizers/concrete/Doc2VecVectorizer.py

from typing import List, Union, Any
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class Doc2VecVectorizer(IVectorize, IFeature):
    def __init__(self):
        self.model = Doc2Vec(vector_size=2000, window=10, min_count=1, workers=5)

    def extract_features(self):
        return list(self.model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self.model.build_vocab(tagged_data)
        self.model.train(tagged_data, total_examples=self.model.corpus_count, epochs=self.model.epochs)

    def transform(self, documents: List[str]) -> List[IVector]:
        vectors = [self.model.infer_vector(doc.split()) for doc in documents]
        return [SimpleVector(vector) for vector in vectors]

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: str) -> IVector:
        vector = self.model.infer_vector(data.split())
        return SimpleVector(vector.squeeze().tolist())

```

```swarmauri/standard/vectorizers/concrete/MLMVectorizer.py

from typing import List, Union, Any
import numpy as np

import torch
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector


class MLMVectorizer(IVectorize, IFeature):
    """
    IVectorize implementation that fine-tunes a Masked Language Model (MLM).
    """

    def __init__(self, model_name='bert-base-uncased', 
        batch_size = 32, 
        learning_rate = 5e-5, 
        masking_ratio: float = 0.15, 
        randomness_ratio: float = 0.10):
        """
        Initializes the vectorizer with a pre-trained MLM model and tokenizer for fine-tuning.
        
        Parameters:
        - model_name (str): Identifier for the pre-trained model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.epochs = 0
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.masking_ratio = masking_ratio
        self.randomness_ratio = randomness_ratio
        self.mask_token_id = self.tokenizer.convert_tokens_to_ids([self.tokenizer.mask_token])[0]

    def extract_features(self):
        raise NotImplementedError('Extract_features not implemented on MLMVectorizer.')

    def _mask_tokens(self, encodings):
        input_ids = encodings.input_ids.to(self.device)
        attention_mask = encodings.attention_mask.to(self.device)

        labels = input_ids.detach().clone()

        probability_matrix = torch.full(labels.shape, self.masking_ratio, device=self.device)
        special_tokens_mask = [
            self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool, device=self.device), value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()

        labels[~masked_indices] = -100
        
        indices_replaced = torch.bernoulli(torch.full(labels.shape, self.masking_ratio, device=self.device)).bool() & masked_indices
        input_ids[indices_replaced] = self.mask_token_id

        indices_random = torch.bernoulli(torch.full(labels.shape, self.randomness_ratio, device=self.device)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long, device=self.device)
        input_ids[indices_random] = random_words[indices_random]

        return input_ids, attention_mask, labels

    # work on this
    def fit(self, documents: List[Union[str, Any]]):
        encodings = self.tokenizer(documents, return_tensors='pt', padding=True, truncation=True, max_length=512)
        input_ids, attention_mask, labels = self._mask_tokens(encodings)       
        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate)
        dataset = TensorDataset(input_ids, attention_mask, labels)
        data_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()

        for batch in data_loader:
            # Move batch to the correct device
            batch = {k: v.to(self.device) for k, v in zip(['input_ids', 'attention_mask', 'labels'], batch)}
            
            outputs = self.model(**batch)
            loss = outputs.loss

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        self.epochs += 1
        print(f"Epoch {self.epochs} complete. Loss {loss.item()}")


    def transform(self, documents: List[Union[str, Any]]) -> List[IVector]:
        """
        Generates embeddings for a list of documents using the fine-tuned MLM.
        """
        embedding_list = []
        
        for document in documents:
            inputs = self.tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Extract embedding (for simplicity, averaging the last hidden states)
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            embedding = embedding.cpu().numpy()
            embedding_list.append(SimpleVector(embedding.squeeze().tolist()))

        return embedding_list

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> IVector:
        """
        Generates an embedding for the input data.

        Parameters:
        - data (Union[str, Any]): The input data, expected to be a textual representation.
                                  Could be a single string or a batch of strings.
        """
        # Tokenize the input data and ensure the tensors are on the correct device.
        inputs = self.tokenizer(data, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embeddings using the model
        with torch.no_grad():
            outputs = self.model(**inputs)

        if hasattr(outputs, 'last_hidden_state'):
            # Access the last layer and calculate the mean across all tokens (simple pooling)
            embedding = outputs.last_hidden_state.mean(dim=1)
        else:
            embedding = outputs['logits'].mean(1)
        # Move the embeddings back to CPU for compatibility with downstream tasks if necessary
        embedding = embedding.cpu().numpy()

        return SimpleVector(embedding.squeeze().tolist())


```

```swarmauri/standard/vectorizers/concrete/TFIDFVectorizer.py

from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
from typing import List, Union, Any
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class TFIDFVectorizer(IVectorize, IFeature):
    def __init__(self):
        # Using scikit-learn's TfidfVectorizer as the underlying mechanism
        self.model = SklearnTfidfVectorizer()
        super().__init__()
        
    def extract_features(self):
        return self.model.get_feature_names_out()

    def fit(self, data: Union[str, Any]) -> List[IVector]:
        """
        Vectorizes the input data using the TF-IDF scheme.

        Parameters:
        - data (Union[str, Any]): The input data to be vectorized. Expected to be a single string (document)
                                  or a list of strings (corpus).

        Returns:
        - List[IVector]: A list containing IVector instances, each representing a document's TF-IDF vector.
        """
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        
        self.fit_matrix = self.model.fit_transform(data)

        # Convert the sparse matrix rows into SimpleVector instances
        vectors = [SimpleVector(vector.toarray().flatten()) for vector in self.fit_matrix]

        return vectors

    def fit_transform(self, data: Union[str, Any], documents) -> List[IVector]:
        documents = [doc.content for doc in documents]
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        documents.extend(data)

        transform_matrix = self.model.fit_transform(documents)

        # Convert the sparse matrix rows into SimpleVector instances
        vectors = [SimpleVector(vector.toarray().flatten()) for vector in transform_matrix]
        return vectors
    
    def transform(self, data: Union[str, Any], documents) -> List[IVector]:
        raise NotImplementedError('Transform not implemented on TFIDFVectorizer.')

    def infer_vector(self, data: str, documents) -> IVector:
        documents = [doc.content for doc in documents]
        documents.append(data)
        tmp_tfidf_matrix = self.transform(documents)
        query_vector = tmp_tfidf_matrix[-1]
        return query_vector

```

```swarmauri/standard/tracing/__init__.py

#

```

```swarmauri/standard/tracing/base/__init__.py

#

```

```swarmauri/standard/tracing/concrete/SimpleTracer.py

from datetime import datetime
import uuid
from typing import Dict, Any, Optional

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.standard.tracing.concrete.SimpleTraceContext import SimpleTraceContext

class SimpleTracer(ITracer):
    _instance = None  # Singleton instance placeholder

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if SimpleTracer._instance is not None:
            raise RuntimeError("SimpleTracer is a singleton. Use SimpleTracer.instance().")
        self.trace_stack = []

    def start_trace(self, name: str, initial_attributes: Optional[Dict[str, Any]] = None) -> SimpleTraceContext:
        trace_id = str(uuid.uuid4())
        trace_context = SimpleTraceContext(trace_id, name, initial_attributes)
        self.trace_stack.append(trace_context)
        return trace_context

    def end_trace(self):
        if self.trace_stack:
            completed_trace = self.trace_stack.pop()
            completed_trace.close()
            # Example of simply printing the completed trace; in practice, you might log it or store it elsewhere
            print(f"Trace Completed: {completed_trace.name}, Duration: {completed_trace.start_time} to {completed_trace.end_time}, Attributes: {completed_trace.attributes}")

    def annotate_trace(self, key: str, value: Any):
        if not self.trace_stack:
            print("No active trace to annotate.")
            return
        current_trace = self.trace_stack[-1]
        current_trace.add_attribute(key, value)

```

```swarmauri/standard/tracing/concrete/TracedVariable.py

from typing import Any
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer  # Assuming this is the path to the tracer

class TracedVariable:
    """
    Wrapper class to trace multiple changes to a variable within the context manager.
    """
    def __init__(self, name: str, value: Any, tracer: SimpleTracer):
        self.name = name
        self._value = value
        self._tracer = tracer
        self._changes = []  # Initialize an empty list to track changes

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any):
        # Record the change before updating the variable's value
        change_annotation = {"from": self._value, "to": new_value}
        self._changes.append(change_annotation)
        
        # Update the trace by appending the latest change to the list under a single key
        # Note that the key is now constant and does not change with each update
        self._tracer.annotate_trace(key=f"{self.name}_changes", value=self._changes)
        
        self._value = new_value

```

```swarmauri/standard/tracing/concrete/ChainTracer.py

from swarmauri.core.tracing.IChainTracer import IChainTracer
from typing import Callable, List, Tuple, Dict, Any   
        
class ChainTracer(IChainTracer):
    def __init__(self):
        self.traces = []

    def process_chain(self, chain: List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]) -> "ChainTracer":
        """
        Processes each item in the operation chain by executing the specified external function
        with its args and kwargs. Logs starting, annotating, and ending the trace based on tuple position.

        Args:
            chain (List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]): A list where each tuple contains:
                - An external function to execute.
                - A list of positional arguments for the function.
                - A dictionary of keyword arguments for the function.
        """
        for i, (func, args, kwargs) in enumerate(chain):
            # Infer operation type and log
            
            if i == 0:
                operation = "Start"
                self.start_trace(*args, **kwargs)
            elif i == len(chain) - 1:
                operation = "End"
                self.end_trace(*args, **kwargs)
            else:
                operation = "Annotate"
                self.annotate_trace(*args, **kwargs)
                
            # For the actual external function call
            result = func(*args, **kwargs)
            print(f"Function '{func.__name__}' executed with result: {result}")

            self.traces.append((operation, func, args, kwargs, result))

        return self

    def start_trace(self, *args, **kwargs) -> None:
        print(f"Starting trace with args: {args}, kwargs: {kwargs}")
        
    def annotate_trace(self, *args, **kwargs) -> None:
        print(f"Annotating trace with args: {args}, kwargs: {kwargs}")

    def end_trace(self, *args, **kwargs) -> None:
        print(f"Ending trace with args: {args}, kwargs: {kwargs}")

    def show(self) -> None:
        for entry in self.traces:
            print(entry)

```

```swarmauri/standard/tracing/concrete/SimpleTraceContext.py

from datetime import datetime
from typing import Dict, Any, Optional

from swarmauri.core.tracing.ITraceContext import ITraceContext

class SimpleTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str, initial_attributes: Optional[Dict[str, Any]] = None):
        self.trace_id = trace_id
        self.name = name
        self.attributes = initial_attributes if initial_attributes else {}
        self.start_time = datetime.now()
        self.end_time = None

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def close(self):
        self.end_time = datetime.now()

```

```swarmauri/standard/tracing/concrete/VariableTracer.py

from contextlib import contextmanager

from swarmauri.standard.tracing.concrete.TracedVariable import TracedVariable
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer

# Initialize a global instance of SimpleTracer for use across the application
global_tracer = SimpleTracer()

@contextmanager
def VariableTracer(name: str, initial_value=None):
    """
    Context manager for tracing the declaration, modification, and usage of a variable.
    """
    trace_context = global_tracer.start_trace(name=f"Variable: {name}", initial_attributes={"initial_value": initial_value})
    traced_variable = TracedVariable(name, initial_value, global_tracer)
    
    try:
        yield traced_variable
    finally:
        # Optionally record any final value or state of the variable before it goes out of scope
        global_tracer.annotate_trace(key=f"{name}_final", value={"final_value": traced_variable.value})
        # End the trace, marking the variable's lifecycle
        global_tracer.end_trace()

```

```swarmauri/standard/tracing/concrete/CallableTracer.py

import functools
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer  # Import SimpleTracer from the previously defined path

# Initialize the global tracer object
tracer = SimpleTracer()

def CallableTracer(func):
    """
    A decorator to trace function or method calls, capturing inputs, outputs, and the caller.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Trying to automatically identify the caller details; practical implementations 
        # might need to adjust based on specific requirements or environment.
        caller_info = f"{func.__module__}.{func.__name__}"
        
        # Start a new trace context for this callable
        trace_context = tracer.start_trace(name=caller_info, initial_attributes={'args': args, 'kwargs': kwargs})
        
        try:
            # Call the actual function/method
            result = func(*args, **kwargs)
            tracer.annotate_trace(key="result", value=result)
            return result
        except Exception as e:
            # Optionally annotate the trace with the exception details
            tracer.annotate_trace(key="exception", value=str(e))
            raise  # Re-raise the exception to not interfere with the program's flow
        finally:
            # End the trace after the function call is complete
            tracer.end_trace()
    return wrapper

```

```swarmauri/standard/tracing/concrete/__init__.py



```

```swarmauri/standard/chains/__init__.py



```

```swarmauri/standard/chains/base/__init__.py

#

```

```swarmauri/standard/chains/base/ChainBase.py

from typing import List
from swarmauri.core.chains.IChain import IChain
from swarmauri.core.chains.IChainStep import IChainStep

class ChainBase(IChain):
    """
    A base implementation of the IChain interface.
    """

    def __init__(self, 
                 steps: List[IChainStep] = None,
                 **configs):
        self.steps = steps if steps is not None else []
        self.configs = configs

    def add_step(self, step: IChainStep) -> None:
        self.steps.append(step)

    def remove_step(self, step: IChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (IChainStep): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError('this is not yet impplemented')

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError('this is not yet impplemented')

    def get_schema_info(self) -> Dict[str, Any]:
        # Return a serialized version of the Chain instance's configuration
        return {
            "steps": [str(step) for step in self.steps],
            "configs": self.configs
        }

```

```swarmauri/standard/chains/base/ChainStepBase.py

from typing import Any, Callable, List, Dict
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep):
    """
    Represents a single step within an execution chain.
    """
    
    def __init__(self, key: str, method: Callable, args: List[Any] = None, kwargs: Dict[str, Any] = None, ref: str = None):
        """
        Initialize a chain step.

        Args:
            key (str): Unique key or identifier for the step.
            method (Callable): The callable object (function or method) to execute in this step.
            args (List[Any], optional): Positional arguments for the callable.
            kwargs (Dict[str, Any], optional): Keyword arguments for the callable.
            ref (str, optional): Reference to another component or context variable, if applicable.
        """
        self.key = key
        self.method = method
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.ref = ref
        


```

```swarmauri/standard/chains/concrete/__init__.py



```

```swarmauri/standard/chains/concrete/CallableChain.py

from typing import Any, Callable, List, Dict, Optional
from swarmauri.core.chains.ICallableChain import ICallableChain, CallableDefinition


class CallableChain(ICallableChain):
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        
        self.callables = callables if callables is not None else []

    def __call__(self, *initial_args, **initial_kwargs):
        result = None
        for func, args, kwargs in self.callables:
            if result is not None:
                # If there was a previous result, use it as the first argument for the next function
                args = [result] + list(args)
            result = func(*args, **kwargs)
        return result
    
    def add_callable(self, func: Callable[[Any], Any], args: List[Any] = None, kwargs: Dict[str, Any] = None) -> None:
        # Add a new callable to the chain
        self.callables.append((func, args or [], kwargs or {}))
    
    def __or__(self, other: "CallableChain") -> "CallableChain":
        if not isinstance(other, CallableChain):
            raise TypeError("Operand must be an instance of CallableChain")
        
        new_chain = CallableChain(self.callables + other.callables)
        return new_chain

```

```swarmauri/standard/distances/__init__.py



```

```swarmauri/standard/distances/base/__init__.py



```

```swarmauri/standard/distances/concrete/ChiSquaredDistance.py

from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class ChiSquaredDistance(IDistanceSimilarity):
    """
    Implementation of the IDistanceSimilarity interface using Chi-squared distance metric.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Chi-squared distance between two vectors.
        """
        if len(vector_a.data) != len(vector_b.data):
            raise ValueError("Vectors must have the same dimensionality.")

        chi_squared_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            if (a + b) != 0:
                chi_squared_distance += (a - b) ** 2 / (a + b)

        return 0.5 * chi_squared_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors based on the Chi-squared distance.
        """
        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/CosineDistance.py

from numpy.linalg import norm
from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.VectorProduct import VectorProduct

class CosineDistance(IDistanceSimilarity, VectorProduct):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
       
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """ 
        Computes the cosine distance between two vectors: 1 - cosine similarity.
    
        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.
    
        Returns:
            float: The computed cosine distance between vector_a and vector_b.
                   It ranges from 0 (completely similar) to 2 (completely dissimilar).
        """
        norm_a = norm(vector_a.data)
        norm_b = norm(vector_b.data)
    
        # Check if either of the vector norms is close to zero
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 1.0  # Return maximum distance for cosine which varies between -1 to 1, so 1 indicates complete dissimilarity
    
        # Compute the cosine similarity between the vectors
        cos_sim = self.dot_product(vector_a, vector_b) / (norm_a * norm_b)
    
        # Covert cosine similarity to cosine distance
        cos_distance = 1 - cos_sim
    
        return cos_distance
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the cosine similarity between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The cosine similarity between vector_a and vector_b.
        """
        return 1 - self.distance(vector_a, vector_b)

    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/EuclideanDistance.py

from math import sqrt
from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class EuclideanDistance(IDistanceSimilarity):
    """
    Class to compute the Euclidean distance between two vectors.
    Implements the IDistanceSimiliarity interface.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Euclidean distance between vector_a and vector_b.
        """
        if len(vector_a.data) != len(vector_b.data):
            raise ValueError("Vectors do not have the same dimensionality.")
        
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data)))
        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity score as the inverse of the Euclidean distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The similarity score between vector_a and vector_b.
        """
        distance = self.distance(vector_a, vector_b)
        return 1 / (1 + distance)
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/JaccardIndexDistance.py

from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class JaccardIndexDistance(IDistanceSimilarity):
    """
    A class implementing Jaccard Index as a similarity and distance metric between two vectors.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Jaccard distance between two vectors.

        The Jaccard distance, which is 1 minus the Jaccard similarity,
        measures dissimilarity between sample sets. It's defined as
        1 - (the intersection of the sets divided by the union of the sets).

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: The Jaccard distance between vector_a and vector_b.
        """
        set_a = set(vector_a.data)
        set_b = set(vector_b.data)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In the special case where the union is zero, return 1.0 which implies complete dissimilarity.
        if union == 0:
            return 1.0

        # Compute Jaccard similarity and then return the distance as 1 - similarity.
        jaccard_similarity = intersection / union
        return 1 - jaccard_similarity

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Jaccard similarity between two vectors.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: Jaccard similarity score between vector_a and vector_b.
        """
        set_a = set(vector_a.data)
        set_b = set(vector_b.data)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In case the union is zero, which means both vectors have no elements, return 1.0 implying identical sets.
        if union == 0:
            return 1.0

        # Compute and return Jaccard similarity.
        return intersection / union
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/LevenshteinDistance.py

from typing import List
import numpy as np
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class LevenshteinDistance(IDistanceSimilarity):
    """
    Implements the IDistance interface to calculate the Levenshtein distance between two vectors.
    The Levenshtein distance between two strings is given by the minimum number of operations needed to transform
    one string into the other, where an operation is an insertion, deletion, or substitution of a single character.
    """
    
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the Levenshtein distance between two vectors.

        Note: Since Levenshtein distance is typically calculated between strings,
        it is assumed that the vectors represent strings where each element of the
        vector corresponds to the ASCII value of a character in the string.

        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.

        Returns:
           float: The computed Levenshtein distance between vector_a and vector_b.
        """
        string_a = ''.join([chr(int(round(value))) for value in vector_a.data])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.data])
        
        return self.levenshtein(string_a, string_b)
    
    def levenshtein(self, seq1: str, seq2: str) -> float:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            seq1 (str): The first string.
            seq2 (str): The second string.
        
        Returns:
            float: The Levenshtein distance between seq1 and seq2.
        """
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros((size_x, size_y))
        
        for x in range(size_x):
            matrix[x, 0] = x
        for y in range(size_y):
            matrix[0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x-1] == seq2[y-1]:
                    matrix[x, y] = min(matrix[x-1, y] + 1, matrix[x-1, y-1], matrix[x, y-1] + 1)
                else:
                    matrix[x, y] = min(matrix[x-1, y] + 1, matrix[x-1, y-1] + 1, matrix[x, y-1] + 1)
        
        return matrix[size_x - 1, size_y - 1]
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        string_a = ''.join([chr(int(round(value))) for value in vector_a.data])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.data])
        return 1 - self.levenshtein(string_a, string_b) / max(len(vector_a), len(vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/__init__.py



```