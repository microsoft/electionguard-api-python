from typing import Any, List, Optional
from enum import Enum
from electionguard.election import CiphertextElectionContext

from app.api.v1.common.type_mapper import (
    string_to_element_mod_p,
    string_to_element_mod_q,
)

from .base import Base, BaseRequest, BaseResponse
from .manifest import ElectionManifest


__all__ = [
    "Election",
    "ElectionState",
    "ElectionQueryRequest",
    "ElectionQueryResponse",
    "MakeElectionContextRequest",
    "MakeElectionContextResponse",
    "SubmitElectionRequest",
]


class CiphertextElectionContextDto(Base):
    """The meta-data required for an election including keys, manifest, number of guardians, and quorum"""

    number_of_guardians: int
    """
    The number of guardians necessary to generate the public key
    """
    quorum: int
    """
    The quorum of guardians necessary to decrypt an election.  Must be less than `number_of_guardians`
    """

    elgamal_public_key: str
    """the `joint public key (K)` in the [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)"""

    commitment_hash: str
    """
    the `commitment hash H(K 1,0 , K 2,0 ... , K n,0 )` of the public commitments
    guardians make to each other in the [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)
    """

    manifest_hash: str
    """The hash of the election metadata"""

    crypto_base_hash: str
    """The `base hash code (𝑄)` in the [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)"""

    crypto_extended_base_hash: str
    """The `extended base hash code (𝑄')` in [ElectionGuard Spec](https://github.com/microsoft/electionguard/wiki)"""

    def to_sdk_format(self) -> CiphertextElectionContext:
        sdk_context = CiphertextElectionContext(
            self.number_of_guardians,
            self.quorum,
            string_to_element_mod_p(self.elgamal_public_key),
            string_to_element_mod_q(self.commitment_hash),
            string_to_element_mod_q(self.manifest_hash),
            string_to_element_mod_q(self.crypto_base_hash),
            string_to_element_mod_q(self.crypto_extended_base_hash),
        )
        return sdk_context


class ElectionState(str, Enum):
    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PUBLISHED = "PUBLISHED"


class Election(Base):
    """An election object."""

    def get_name(self) -> str:
        text = self.manifest["name"]["text"]
        # todo: replace "en" with user's current culture
        enText = [t["value"] for t in text if t["language"] == "en"]
        return str(enText[0])

    election_id: str
    key_name: str
    state: ElectionState
    context: CiphertextElectionContextDto
    manifest: ElectionManifest


class ElectionQueryRequest(BaseRequest):
    """A request for elections using the specified filter."""

    filter: Optional[Any] = None
    """
    a json object filter that will be applied to the search.
    """

    class Config:
        schema_extra = {"example": {"filter": {"election_id": "some-election-id-123"}}}


class ElectionQueryResponse(BaseResponse):
    """A collection of elections."""

    elections: List[Election] = []


class ElectionSummaryDto(Base):
    election_id: str
    name: Any
    state: str
    number_of_guardians: int
    quorum: int
    cast_ballot_count: int
    spoiled_ballot_count: int
    index: int


class ElectionListResponseDto(BaseResponse):
    """A collection of elections."""

    elections: List[ElectionSummaryDto] = []


class SubmitElectionRequest(BaseRequest):
    """Submit an election."""

    election_id: str
    key_name: str
    context: CiphertextElectionContextDto
    manifest: Optional[ElectionManifest] = None


class MakeElectionContextRequest(BaseRequest):
    """
    A request to build an Election Context for a given election.
    """

    elgamal_public_key: str
    commitment_hash: str
    number_of_guardians: int
    quorum: int
    manifest_hash: Optional[str] = None
    manifest: Optional[ElectionManifest] = None


class MakeElectionContextResponse(BaseResponse):
    """A Ciphertext Election Context."""

    context: CiphertextElectionContextDto
