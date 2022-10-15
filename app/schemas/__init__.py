from app.schemas import academy, bot_builder, live_chat
from .role import Role, RoleCreate, RoleInDB, RoleUpdate
from .token import Token, TokenPayload, Login, LoginForm
from .user import User, UserCreate, \
    UserInDB, UserUpdate, UserRegister,\
    UserBase, ForgetPassword, ChangePassword, UserUpdatePassword

from .instagram_page import InstagramPageCreate,\
    InstagramPageUpdate, InstagramPage, ConnectPage


from .account import Account, AccountDetail

from .connection import Connection, ConnectionCreate, \
    ConnectionUpdate

from .pagination import Pagination
from .notification import Notification, NotificationCreate,\
    NotificationUpdate, NotificationListApi, NotificationListItem

from .file import FileUpload