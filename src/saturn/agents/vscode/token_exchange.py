"""VS Code bridge token exchange."""

from sqlalchemy.orm import Session

from saturn.identity.service import IdentityService
from saturn.plugins.db_models import VSCodeTokenExchange
from saturn.plugins.repository import PluginRepository
from saturn.shared.ids import new_id
from saturn.shared.time import utc_now


class VSCodeTokenExchangeService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PluginRepository(session)
        self.identity = IdentityService(session)

    def create_exchange(self, session_token: str) -> VSCodeTokenExchange:
        user_session = self.identity.get_session(session_token)
        if user_session is None:
            raise PermissionError("Invalid session")
        exchange = self.repository.add(
            VSCodeTokenExchange(
                exchange_token=new_id(),
                session_token=session_token,
                org_id=user_session.org_id,
                user_id=user_session.user_id,
            )
        )
        self.session.flush()
        return exchange

    def consume_exchange(self, exchange_token: str) -> VSCodeTokenExchange:
        exchange = self.repository.get_token_exchange(exchange_token)
        if exchange is None or exchange.status != "pending":
            raise PermissionError("Invalid token exchange")
        exchange.status = "consumed"
        exchange.consumed_at = utc_now()
        self.session.flush()
        return exchange
