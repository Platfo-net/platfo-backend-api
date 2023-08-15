from app import services
from app.core.instagram.handlers.base import BotBaseHandler


class MessagePostbackBotHandler(BotBaseHandler):
    def run(self, application: str, postback_payload: str, chatflow_id: int):
        if services.connection.is_chatflow_connected_to_page(
                self.db,
                account_id=self.user_page_data.account_id,
                chatflow_id=chatflow_id,
                application_name=application,
        ):
            node = services.bot_builder.node.get_next_node(
                self.db,
                from_id=postback_payload,
                chatflow_id=chatflow_id,
            )
            if not node:
                return

            self.send_widget(
                widget=node.widget,
                quick_replies=node.quick_replies,
                chatflow_id=chatflow_id,
                lead_igs_id=self.instagram_data.sender_id,
            )
