swarmauri/README.md
swarmauri/__init__.py
swarmauri/community/__init__.py
swarmauri/community/tools/__init__.py
swarmauri/community/tools/base/__init__.py
swarmauri/community/tools/concrete/__init__.py
swarmauri/community/tools/concrete/EntityRecognitionTool.py
swarmauri/community/tools/concrete/GmailSendTool.py
swarmauri/community/tools/concrete/GmailReadTool.py
swarmauri/community/tools/concrete/SentimentAnalysisTool.py
swarmauri/community/tools/concrete/WebScrapingTool.py
swarmauri/community/tools/concrete/DownloadPdfTool.py
swarmauri/community/tools/concrete/PaCMAP.py
swarmauri/community/tools/concrete/ZapierHookTool.py
swarmauri/community/retrievers/__init__.py
swarmauri/community/retrievers/base/__init__.py
swarmauri/community/retrievers/concrete/__init__.py
swarmauri/community/retrievers/concrete/RedisDocumentRetriever.py
swarmauri/community/document_stores/__init__.py
swarmauri/community/document_stores/base/__init__.py
swarmauri/community/document_stores/concrete/__init__.py
swarmauri/community/document_stores/concrete/RedisDocumentStore.py
swarmauri/core/README.md
swarmauri/core/__init__.py
swarmauri/core/models/__init__.py
swarmauri/core/models/IPredict.py
swarmauri/core/models/IFit.py
swarmauri/core/models/IModel.py
swarmauri/core/agent_apis/__init__.py
swarmauri/core/agent_apis/IAgentCommands.py
swarmauri/core/agent_apis/IAgentRouterCRUD.py
swarmauri/core/conversations/__init__.py
swarmauri/core/conversations/IMaxSize.py
swarmauri/core/conversations/IConversation.py
swarmauri/core/conversations/ISystemContext.py
swarmauri/core/documents/__init__.py
swarmauri/core/documents/IDocument.py
swarmauri/core/documents/IEmbed.py
swarmauri/core/messages/IMessage.py
swarmauri/core/messages/__init__.py
swarmauri/core/parsers/__init__.py
swarmauri/core/parsers/IParser.py
swarmauri/core/prompts/__init__.py
swarmauri/core/prompts/IPrompt.py
swarmauri/core/agents/__init__.py
swarmauri/core/agents/IAgentToolkit.py
swarmauri/core/agents/IAgentConversation.py
swarmauri/core/agents/IAgentRetriever.py
swarmauri/core/agents/IAgentParser.py
swarmauri/core/agents/IAgentName.py
swarmauri/core/agents/IAgent.py
swarmauri/core/agents/IAgentDocument.py
swarmauri/core/swarms/__init__.py
swarmauri/core/swarms/ISwarm.py
swarmauri/core/swarms/ISwarmComponent.py
swarmauri/core/swarms/ISwarmConfigurationExporter.py
swarmauri/core/swarms/ISwarmFactory.py
swarmauri/core/swarms/ISwarmAgentRegistration.py
swarmauri/core/toolkits/__init__.py
swarmauri/core/toolkits/IToolkit.py
swarmauri/core/tools/__init__.py
swarmauri/core/tools/ITool.py
swarmauri/core/tools/IParameter.py
swarmauri/core/utils/__init__.py
swarmauri/core/utils/ITransactional.py
swarmauri/core/vector_stores/ISimiliarityQuery.py
swarmauri/core/vector_stores/IGradient.py
swarmauri/core/vector_stores/IAngleBetweenVectors.py
swarmauri/core/vector_stores/IDecompose.py
swarmauri/core/vector_stores/IDivergence.py
swarmauri/core/vector_stores/IOrthogonalProject.py
swarmauri/core/vector_stores/IProject.py
swarmauri/core/vector_stores/IReflect.py
swarmauri/core/vector_stores/ISimilarity.py
swarmauri/core/vector_stores/IVectorSpan.py
swarmauri/core/vector_stores/IVectorArithmetic.py
swarmauri/core/vector_stores/IVectorLinearCombination.py
swarmauri/core/vector_stores/IVectorNorm.py
swarmauri/core/vector_stores/IVectorRotate.py
swarmauri/core/vector_stores/IVectorBasisCheck.py
swarmauri/core/vector_stores/IVectorStore.py
swarmauri/core/vector_stores/__init__.py
swarmauri/core/document_stores/IDocumentStore.py
swarmauri/core/document_stores/__init__.py
swarmauri/core/document_stores/IDocumentRetrieve.py
swarmauri/core/chunkers/__init__.py
swarmauri/core/chunkers/IChunker.py
swarmauri/core/vectors/IVectorMeta.py
swarmauri/core/vectors/IVectorTransform.py
swarmauri/core/vectors/IVector.py
swarmauri/core/vectors/__init__.py
swarmauri/core/vectors/IVectorProduct.py
swarmauri/core/swarm_apis/__init__.py
swarmauri/core/swarm_apis/ISwarmAPI.py
swarmauri/core/swarm_apis/IAgentRegistrationAPI.py
swarmauri/core/vectorizers/__init__.py
swarmauri/core/vectorizers/IVectorize.py
swarmauri/core/vectorizers/IFeature.py
swarmauri/core/tracing/__init__.py
swarmauri/core/tracing/ITraceContext.py
swarmauri/core/tracing/ITracer.py
swarmauri/core/tracing/IChainTracer.py
swarmauri/core/chains/ICallableChain.py
swarmauri/core/chains/__init__.py
swarmauri/core/chains/IChain.py
swarmauri/core/chains/IChainFactory.py
swarmauri/core/chains/IChainStep.py
swarmauri/core/distances/__init__.py
swarmauri/core/distances/IDistanceSimilarity.py
swarmauri/experimental/__init__.py
swarmauri/experimental/tools/LinkedInArticleTool.py
swarmauri/experimental/tools/TwitterPostTool.py
swarmauri/experimental/tools/__init__.py
swarmauri/experimental/tools/OutlookSendMailTool.py
swarmauri/experimental/tools/CypherQueryTool.py
swarmauri/experimental/tools/FileDownloaderTool.py
swarmauri/experimental/tools/SQLite3QueryTool.py
swarmauri/experimental/conversations/__init__.py
swarmauri/experimental/conversations/SemanticConversation.py
swarmauri/experimental/conversations/ConsensusBuildingConversation.py
swarmauri/experimental/conversations/ConsensusBuildingConversation.md
swarmauri/experimental/models/__init__.py
swarmauri/experimental/models/SageMaker.py
swarmauri/experimental/models/HierarchicalAttentionModel.py
swarmauri/experimental/utils/__init__.py
swarmauri/experimental/utils/get_last_frame.py
swarmauri/experimental/utils/save_schema.py
swarmauri/experimental/utils/ISerializable.md
swarmauri/experimental/utils/ISerializable.py
swarmauri/experimental/docs/replay.md
swarmauri/experimental/parsers/__init__.py
swarmauri/experimental/parsers/PDFToTextParser.py
swarmauri/experimental/vector_stores/__init__.py
swarmauri/experimental/vector_stores/Word2VecDocumentStore.py
swarmauri/experimental/vector_stores/TriplesDocumentStore.py
swarmauri/experimental/tracing/RemoteTrace.py
swarmauri/experimental/tracing/__init__.py
swarmauri/experimental/chains/ChainOrderStrategy.py
swarmauri/experimental/chains/ChainOrderStrategyBase.py
swarmauri/experimental/chains/ChainProcessingStrategy.py
swarmauri/experimental/chains/ChainProcessingStrategyBase.py
swarmauri/experimental/chains/IChainOrderStrategy.py
swarmauri/experimental/chains/IChainProcessingStrategy.py
swarmauri/experimental/chains/MatrixOrderStrategy.py
swarmauri/experimental/chains/MatrixProcessingStrategy.py
swarmauri/experimental/chains/TypeAgnosticCallableChain.py
swarmauri/experimental/chains/__init__.py
swarmauri/experimental/vectorizers/DGLVectorizer.py
swarmauri/experimental/vectorizers/__init__.py
swarmauri/experimental/document_stores/TriplesDocumentStore.py
swarmauri/experimental/document_stores/Word2VecDocumentStore.py
swarmauri/experimental/document_stores/__init__.py
swarmauri/experimental/distances/CanberraDistance.py
swarmauri/experimental/distances/ChebyshevDistance.py
swarmauri/experimental/distances/HaversineDistance.py
swarmauri/experimental/distances/ManhattanDistance.py
swarmauri/experimental/distances/MinkowskiDistance.py
swarmauri/experimental/distances/ScannVectorStore.py
swarmauri/experimental/distances/SorensenDiceDistance.py
swarmauri/experimental/distances/SquaredEuclideanDistance.py
swarmauri/experimental/distances/SSASimilarity.py
swarmauri/experimental/distances/SSIVSimilarity.py
swarmauri/experimental/distances/__init__.py
swarmauri/standard/README.md
swarmauri/standard/__init__.py
swarmauri/standard/models/__init__.py
swarmauri/standard/models/base/__init__.py
swarmauri/standard/models/base/ModelBase.py
swarmauri/standard/models/concrete/__init__.py
swarmauri/standard/models/concrete/OpenAIModel.py
swarmauri/standard/models/concrete/AzureGPT.py
swarmauri/standard/models/concrete/OpenAIImageGenerator.py
swarmauri/standard/models/concrete/OpenAIToolModel.py
swarmauri/standard/agents/__init__.py
swarmauri/standard/agents/base/__init__.py
swarmauri/standard/agents/base/NamedAgentBase.py
swarmauri/standard/agents/base/ConversationAgentBase.py
swarmauri/standard/agents/base/ToolAgentBase.py
swarmauri/standard/agents/base/AgentBase.py
swarmauri/standard/agents/base/DocumentAgentBase.py
swarmauri/standard/agents/concrete/__init__.py
swarmauri/standard/agents/concrete/ToolAgent.py
swarmauri/standard/agents/concrete/ChatSwarmAgent.py
swarmauri/standard/agents/concrete/SingleCommandAgent.py
swarmauri/standard/agents/concrete/SimpleSwarmAgent.py
swarmauri/standard/agents/concrete/MultiPartyChatSwarmAgent.py
swarmauri/standard/agents/concrete/MultiPartyToolAgent.py
swarmauri/standard/agents/concrete/RagAgent.py
swarmauri/standard/agents/concrete/GenerativeRagAgent.py
swarmauri/standard/utils/__init__.py
swarmauri/standard/utils/load_documents_from_json.py
swarmauri/standard/conversations/__init__.py
swarmauri/standard/conversations/base/__init__.py
swarmauri/standard/conversations/base/ConversationBase.py
swarmauri/standard/conversations/base/SystemContextBase.py
swarmauri/standard/conversations/concrete/__init__.py
swarmauri/standard/conversations/concrete/LimitedSizeConversation.py
swarmauri/standard/conversations/concrete/SimpleConversation.py
swarmauri/standard/conversations/concrete/LimitedSystemContextConversation.py
swarmauri/standard/conversations/concrete/SharedConversation.py
swarmauri/standard/documents/__init__.py
swarmauri/standard/documents/base/__init__.py
swarmauri/standard/documents/base/EmbeddedBase.py
swarmauri/standard/documents/base/DocumentBase.py
swarmauri/standard/documents/concrete/__init__.py
swarmauri/standard/documents/concrete/EmbeddedDocument.py
swarmauri/standard/documents/concrete/Document.py
swarmauri/standard/messages/__init__.py
swarmauri/standard/messages/base/__init__.py
swarmauri/standard/messages/base/MessageBase.py
swarmauri/standard/messages/concrete/__init__.py
swarmauri/standard/messages/concrete/AgentMessage.py
swarmauri/standard/messages/concrete/HumanMessage.py
swarmauri/standard/messages/concrete/FunctionMessage.py
swarmauri/standard/messages/concrete/SystemMessage.py
swarmauri/standard/parsers/__init__.py
swarmauri/standard/parsers/base/__init__.py
swarmauri/standard/parsers/concrete/__init__.py
swarmauri/standard/parsers/concrete/CSVParser.py
swarmauri/standard/parsers/concrete/EntityRecognitionParser.py
swarmauri/standard/parsers/concrete/HtmlTagStripParser.py
swarmauri/standard/parsers/concrete/KeywordExtractorParser.py
swarmauri/standard/parsers/concrete/MarkdownParser.py
swarmauri/standard/parsers/concrete/OpenAPISpecParser.py
swarmauri/standard/parsers/concrete/PhoneNumberExtractorParser.py
swarmauri/standard/parsers/concrete/PythonParser.py
swarmauri/standard/parsers/concrete/RegExParser.py
swarmauri/standard/parsers/concrete/TextBlobNounParser.py
swarmauri/standard/parsers/concrete/TextBlobSentenceParser.py
swarmauri/standard/parsers/concrete/TFIDFParser.py
swarmauri/standard/parsers/concrete/URLExtractorParser.py
swarmauri/standard/parsers/concrete/XMLParser.py
swarmauri/standard/parsers/concrete/BERTEmbeddingParser.py
swarmauri/standard/prompts/__init__.py
swarmauri/standard/prompts/base/__init__.py
swarmauri/standard/prompts/concrete/__init__.py
swarmauri/standard/prompts/concrete/Prompt.py
swarmauri/standard/prompts/concrete/PromptTemplate.py
swarmauri/standard/states/__init__.py
swarmauri/standard/states/base/__init__.py
swarmauri/standard/states/concrete/__init__.py
swarmauri/standard/swarms/__init__.py
swarmauri/standard/swarms/base/__init__.py
swarmauri/standard/swarms/base/SwarmComponentBase.py
swarmauri/standard/swarms/concrete/__init__.py
swarmauri/standard/swarms/concrete/SimpleSwarmFactory.py
swarmauri/standard/toolkits/__init__.py
swarmauri/standard/toolkits/base/__init__.py
swarmauri/standard/toolkits/base/ToolkitBase.py
swarmauri/standard/toolkits/concrete/__init__.py
swarmauri/standard/toolkits/concrete/Toolkit.py
swarmauri/standard/tools/__init__.py
swarmauri/standard/tools/base/__init__.py
swarmauri/standard/tools/base/ToolBase.py
swarmauri/standard/tools/concrete/__init__.py
swarmauri/standard/tools/concrete/TestTool.py
swarmauri/standard/tools/concrete/WeatherTool.py
swarmauri/standard/tools/concrete/Parameter.py
swarmauri/standard/tools/concrete/AdditionTool.py
swarmauri/standard/apis/__init__.py
swarmauri/standard/apis/base/__init__.py
swarmauri/standard/apis/concrete/__init__.py
swarmauri/standard/vector_stores/__init__.py
swarmauri/standard/vector_stores/base/__init__.py
swarmauri/standard/vector_stores/base/VectorDocumentStoreBase.py
swarmauri/standard/vector_stores/base/VectorDocumentStoreRetrieveBase.py
swarmauri/standard/vector_stores/concrete/__init__.py
swarmauri/standard/vector_stores/concrete/FaissVectorStore.py
swarmauri/standard/vector_stores/concrete/WeaviateVectorStore.py
swarmauri/standard/vector_stores/concrete/TFIDFVectorStore.py
swarmauri/standard/vector_stores/concrete/BERTVectorStore.py
swarmauri/standard/vector_stores/concrete/Doc2VecVectorStore.py
swarmauri/standard/vector_stores/concrete/MLMVectorStore.py
swarmauri/standard/document_stores/__init__.py
swarmauri/standard/document_stores/base/__init__.py
swarmauri/standard/document_stores/base/DocumentStoreBase.py
swarmauri/standard/document_stores/base/DocumentStoreRetrieveBase.py
swarmauri/standard/document_stores/concrete/__init__.py
swarmauri/standard/chunkers/__init__.py
swarmauri/standard/chunkers/base/__init__.py
swarmauri/standard/chunkers/concrete/__init__.py
swarmauri/standard/chunkers/concrete/SlidingWindowChunker.py
swarmauri/standard/chunkers/concrete/DelimiterBasedChunker.py
swarmauri/standard/chunkers/concrete/FixedLengthChunker.py
swarmauri/standard/chunkers/concrete/SimpleSentenceChunker.py
swarmauri/standard/chunkers/concrete/MdSnippetChunker.py
swarmauri/standard/vectors/__init__.py
swarmauri/standard/vectors/base/__init__.py
swarmauri/standard/vectors/base/VectorBase.py
swarmauri/standard/vectors/concrete/SimpleVector.py
swarmauri/standard/vectors/concrete/__init__.py
swarmauri/standard/vectors/concrete/VectorProduct.py
swarmauri/standard/vectorizers/__init__.py
swarmauri/standard/vectorizers/base/__init__.py
swarmauri/standard/vectorizers/concrete/__init__.py
swarmauri/standard/vectorizers/concrete/Doc2VecVectorizer.py
swarmauri/standard/vectorizers/concrete/MLMVectorizer.py
swarmauri/standard/vectorizers/concrete/TFIDFVectorizer.py
swarmauri/standard/tracing/__init__.py
swarmauri/standard/tracing/base/__init__.py
swarmauri/standard/tracing/concrete/SimpleTracer.py
swarmauri/standard/tracing/concrete/TracedVariable.py
swarmauri/standard/tracing/concrete/ChainTracer.py
swarmauri/standard/tracing/concrete/SimpleTraceContext.py
swarmauri/standard/tracing/concrete/VariableTracer.py
swarmauri/standard/tracing/concrete/CallableTracer.py
swarmauri/standard/tracing/concrete/__init__.py
swarmauri/standard/chains/__init__.py
swarmauri/standard/chains/base/__init__.py
swarmauri/standard/chains/base/ChainBase.py
swarmauri/standard/chains/base/ChainStepBase.py
swarmauri/standard/chains/concrete/__init__.py
swarmauri/standard/chains/concrete/CallableChain.py
swarmauri/standard/distances/__init__.py
swarmauri/standard/distances/base/__init__.py
swarmauri/standard/distances/concrete/ChiSquaredDistance.py
swarmauri/standard/distances/concrete/CosineDistance.py
swarmauri/standard/distances/concrete/EuclideanDistance.py
swarmauri/standard/distances/concrete/JaccardIndexDistance.py
swarmauri/standard/distances/concrete/LevenshteinDistance.py
swarmauri/standard/distances/concrete/__init__.py