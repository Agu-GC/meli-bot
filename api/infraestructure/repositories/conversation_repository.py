import redis
import json
import logging
from datetime import datetime
from typing import List
from api.domain.entities import Conversation
from api.application.interfaces.conversation_repository import IConversationRepository

logger = logging.getLogger(__name__)

class ConversationRepository(IConversationRepository):
    """Repository to manage conversation history using Redis"""

    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host, port, db, decode_responses=True)

    def save_conversation(self, conversation: Conversation) -> None:
        """Saves a conversation in Redis, storing the last 10 interactions per user"""
        logger.info(f"saving conversation for user {conversation.user_id}")
        key = f"conversations:{conversation.user_id}"
        interaction = json.dumps({
            "user": conversation.user_msg,
            "bot": conversation.bot_msg,
            "timestamp": conversation.timestamp.isoformat()
        })
        try:
            with self.client.pipeline() as pipe:
                pipe.lpush(key, interaction)
                pipe.ltrim(key, 0, 9)
                pipe.execute()
        except redis.RedisError as e:
            logger.error(f"Error saving conversation to Redis: {str(e)}")
            raise Exception(f"Error saving conversation to Redis: {str(e)}")

    def get_conversation_history(self, user_id: str) -> List[Conversation]:
        """Gets the last 10 interactions of a user from Redis"""
        key = f"conversations:{user_id}"
        interactions = self.client.lrange(key, 0, 9)
        
        history = []
        try:
            for item in interactions:
                data = json.loads(item)
                timestamp = datetime.fromisoformat(data.get("timestamp") or datetime.now().isoformat())
                history.append(Conversation(
                    user_id=user_id,
                    user_msg=data["user"],
                    bot_msg=data["bot"],
                    timestamp=timestamp
                ))
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            raise Exception(f"Error retrieving conversation history: {str(e)}")
        return history