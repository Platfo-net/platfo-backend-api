





class ContentCategory():
    __tablename__ = "content_categories"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id"),
        nullable=True,
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
    )

    category = relationship("Category", back_populates="content_categories")
    Content = relationship("Content", back_populates="content_categories")
