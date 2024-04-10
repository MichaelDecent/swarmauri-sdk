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