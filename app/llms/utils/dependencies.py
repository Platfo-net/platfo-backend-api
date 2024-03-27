import inspect
from typing import Type, List

import chromadb
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.llms.repository.base_repository import BaseRepository
from app.llms.services.base_service import BaseService
from app.llms.vectordb.chroma_client import ChromaClient
from app.llms.vectordb.config import ChromaConfig


def get_chroma_client():
    chroma = chromadb.HttpClient(host=ChromaConfig.HOST,
                                 port=ChromaConfig.PORT)
    return ChromaClient(chroma=chroma)


def get_repositories(*repositories):
    """
    Returns a list of repository instances.
    Every repo needs a session, we need to call get_db() for that
    """

    def _get_repositories(session: Session = Depends(get_db)):
        instantiated_repositories = []
        for repo in repositories:
            instantiated_repositories.append(repo(session))
        return instantiated_repositories

    return _get_repositories


def get_service(service_type: Type[BaseService]):
    """
    Returns an instance of the service with the needed repositories.
    The needed repositories are the ones declared in its __init__ method with type hint.
    By definition a repository inherit from BaseRepository.
    """
    repository_classes = [
        Repo for Repo in service_type.__init__.__annotations__.values()
        if BaseRepository in inspect.getmro(Repo)
    ]

    def _get_service(repositories: Type[List[BaseRepository]] = Depends(get_repositories(*repository_classes))):
        return service_type(*repositories)  # type: ignore

    return _get_service
