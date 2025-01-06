import logging
import asyncio
from langchain_openai import ChatOpenAI  # Synchronous ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

from .hybrid_retriever import HybridRetriever
from ..utils.helpers import run_async

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CustomConversationalRAGPipeline:
    def __init__(self, vectorstore_manager, openai_api_key: str, all_docs_text=None):
        self.vectorstore_manager = vectorstore_manager

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Synchronous ChatOpenAI
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            temperature=0
        )

        self.hybrid_retriever = HybridRetriever(
            vectorstore_manager=self.vectorstore_manager,
            all_docs_text=all_docs_text or []
        )

    async def query(self, user_query: str) -> str:
        logger.info(f"[CustomConversationalRAGPipeline] New user query: {user_query}")

        # 1) Retrieving Docs here
        retrieved = await self.hybrid_retriever.retrieve(user_query)
        docs_text = "\n\n".join(r[0] for r in retrieved)

        # 2) Get conversation history
        chat_history = self.memory.load_memory_variables({})["chat_history"]

        # 3) Build messages
        messages = [
            SystemMessage(
                content=(
                    "You are a helpful AI assistant for a company. Your task is to respond accurately with the asked user query and provided response. Please be polite and ensure response is in little detail. Act like you are Nymcard's assistant, do not pretend like you are a 3rd party API."
                    "Maintain context from previous interactions. "
                    "If the current query is related to a previous one, incorporate that context."
                )
            )
        ]
        for msg in chat_history:
            messages.append(msg)

        messages.append(
            HumanMessage(
                content=(
                    f"{user_query}\n\n"
                    "If the current query is linked to the previous query, please use it. "
                    "Here are some relevant docs:\n"
                    f"{docs_text}"
                )
            )
        )

        logger.debug("[CustomConversationalRAGPipeline] Built Messages: %s", messages)

        # 4) Because ChatOpenAI is synchronous, wrap it in asyncio.to_thread
        try:
            def sync_call_llm(msgs):
                """Helper to call the LLM synchronously."""
                return self.llm(msgs)

            llm_response = await asyncio.to_thread(sync_call_llm, messages)

            generated_content = llm_response.content.strip()

            logger.debug("[CustomConversationalRAGPipeline] LLM Response: %s", generated_content)
        except Exception as e:
            logger.error(f"[CustomConversationalRAGPipeline] LLM error: {e}", exc_info=True)
            return "Sorry, an error occurred while generating the response."

        # 5) Save context
        self.memory.save_context(
            {"input": user_query},
            {"output": generated_content}
        )

        return generated_content
