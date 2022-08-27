
class Content(Base):

    __tablename__ = "contents"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    title = Column(String(1024), nullable=True)
    detail = Column(Text(), nullable=True)

    content_attachement = relationship(
        "ContentAttachment", back_populates="content")
    content_category = relationship(
        "ContentCategory", back_populates="content")
