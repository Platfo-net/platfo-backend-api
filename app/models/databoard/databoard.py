from sqlalchemy import Column, Integer, DateTime
from app.db.base_class import Base


class CommentStat(Base):
    __tablename__ = 'databoard_comment_stats'

    facebook_page_id = Column(Integer(), index=True)
    year = Column(Integer(), index=True)
    month = Column(Integer(), index=True)
    day = Column(Integer(), index=True)
    hour = Column(Integer())
    count = Column(Integer())


class LiveCommentStat(Base):
    __tablename__ = 'databoard_live_comment_stats'

    facebook_page_id = Column(Integer(), index=True)
    year = Column(Integer(), index=True)
    month = Column(Integer(), index=True)
    day = Column(Integer(), index=True)
    hour = Column(Integer())
    count = Column(Integer())


class ContactStat(Base):
    __tablename__ = 'databoard_contact_stats'

    facebook_page_id = Column(Integer(), index=True)
    year = Column(Integer(), index=True)
    month = Column(Integer(), index=True)
    day = Column(Integer(), index=True)
    hour = Column(Integer())
    count = Column(Integer())


class ContactMessageStat(Base):
    __tablename__ = 'databoard_contact_message_stats'

    facebook_page_id = Column(Integer(), index=True)

    year = Column(Integer(), index=True)
    month = Column(Integer(), index=True)
    day = Column(Integer(), index=True)
    hour = Column(Integer())
    count = Column(Integer())


class FollowerStat(Base):
    __tablename__ = 'databoard_follower_stats'

    facebook_page_id = Column(Integer(), index=True)
    year = Column(Integer(), index=True)
    month = Column(Integer(), index=True)
    day = Column(Integer(), index=True)
    hour = Column(Integer())
    count = Column(Integer())

    from_datetime = Column(DateTime())
