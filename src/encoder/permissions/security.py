from typing import Any, List

from fastapi import HTTPException

from encoder.encode import repository
from encoder.database import get_db


class Voter:
    def supports(self, attribute: str, subject: Any) -> bool:
        raise NotImplementedError

    def vote(self, attribute: str, subject: Any) -> bool:
        raise NotImplementedError


class MediaVoter(Voter):
    attribute_encode = "ENCODE"

    def supports(self, attribute: str, subject: Any) -> bool:
        return attribute in MediaVoter.get_supported_attributes()

    def vote(self, attribute: str, subject: Any) -> bool:
        db_generator = get_db()
        db = next(db_generator)

        queued_encode = repository.get_encode_by_uuid_and_status(db, subject.uuid)

        return queued_encode is None

    @staticmethod
    def get_supported_attributes() -> List[str]:
        return [MediaVoter.attribute_encode]


class DecisionManager:
    def __init__(self, voters: List[Voter]):
        self.voters = voters

    def decide(self, attribute: str, subject: Any) -> bool:
        for voter in self.voters:
            if not voter.supports(attribute, subject):
                return False
            if voter.vote(attribute, subject):
                return True
        return False


def has_permission(attribute: str, subject: Any = None) -> bool:
    manager = DecisionManager([MediaVoter()])
    if not manager.decide(attribute, subject):
        uuid = subject.uuid if subject else None
        raise HTTPException(
            status_code=403,
            detail={
                "message": "You do not have permission",
                "uuid": uuid,
                "attribute": attribute,
            },
        )
    return True


def decorate_media_with_permissions(subject: Any = None):
    manager = DecisionManager([MediaVoter()])
    attributes = MediaVoter.get_supported_attributes()

    for attribute in attributes:
        subject.permissions[attribute] = manager.decide(attribute, subject)

    return subject
