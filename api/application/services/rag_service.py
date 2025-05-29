import logging
from api.application.interfaces.database_repository import IDatabaseRepository
from api.application.interfaces.conversation_repository import IConversationRepository
from api.application.interfaces.embedding_service import IEmbeddingService
from api.application.interfaces.llm_service import ILLMService
from api.application.interfaces.rag_service import IRAGService
from api.domain.entities import Conversation

logger = logging.getLogger(__name__)

class RAGService(IRAGService):
    def __init__(
        self,
        conversation_repo: IConversationRepository,
        database_repo: IDatabaseRepository,
        embedding_service: IEmbeddingService,
        llm_service: ILLMService
    ):
        self.conversation_repo = conversation_repo
        self.database_repo = database_repo
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.system_prompt = (
            "You are an expert assistant that answers questions based on the provided context."
            "If the answer is not in the context, clearly state that you do not have that information.\n\n"
            "Context:\n{context}\n\n"
            "Conversation History:\n{history}\n\n"
            "Instruction: Answer the following question concisely and precisely: {user_query}"
        )


    def generate_response(self, user_id: str, user_query: str) -> str:
        """Generates a response for the user based on their query and conversation history"""
        logger.info(f"Generated response for user {user_id} with query: {user_query}")
        conversation_history = self._format_history(self.conversation_repo.get_conversation_history(user_id))

        context_documents = self._get_relevant_documents(user_query)
        
        prompt = self._build_prompt(
            user_query=user_query,
            context="\n".join(context_documents),
            history=conversation_history
        )
        
        llm_response = self.llm_service.generate_response(prompt)
        
        self.conversation_repo.save_conversation(
            Conversation(
                user_id=user_id,
                user_msg=user_query,
                bot_msg=llm_response
            )
        )
        
        return llm_response

    def _format_history(self, history: list[Conversation]) -> str:
        """Formats the conversation history for the prompt"""
        logger.info(f"Formatting conversation history {history}")
        return "\n".join(
            [f"User: {conversation.user_msg}\nBot: {conversation.bot_msg}" 
             for conversation in reversed(history)]
        )

    def _get_relevant_documents(self, user_query: str) -> list[str]:
        """Search for relevant documents based on the user query"""
        logger.info(f"Searching for relevant documents for query: {user_query}")
        query_embedding = self.embedding_service.get_embedding(user_query)
        results = self.database_repo.search_similar(query_embedding, n_results=5)
        
        if not results or not results.get('documents') or not results['documents'][0]:
            logger.info("documents not found for the query")
            return []
        return results['documents'][0]

    def _build_prompt(self, user_query: str, context: str, history: str) -> str:
        """Builds the prompt for the LLM"""
        logger.info("building prompt for LLM")
        return self.system_prompt.format(
            context=context,
            history=history if history else "No hay historial previo",
            user_query=user_query
        )