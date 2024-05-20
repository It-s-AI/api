import pydantic
from typing import List, Optional
import bittensor as bt


class TextSynapse(bt.Synapse):
    """
    A protocol representation which uses bt.Synapse as its base.
    This protocol helps in handling request and response communication between
    the miner and the validator.

    Attributes:
    - texts: List of texts that needs to be evaluated for AI generation
    - predictions: List of probabilities in response to texts

    """

    texts: List[str] = pydantic.Field(
        ...,
        title="Texts",
        description="A list of texts to check. Immuatable.",
        allow_mutation=False,
    )

    predictions: List[float] = pydantic.Field(
        ...,
        title="Predictions",
        description="List of predicted probabilities. This attribute is mutable and can be updated.",
    ) 

    required_hash_fields: List[str] = pydantic.Field(
        ["texts", "predictions"],
        title="Required Hash Fields",
        description="A list of required fields for the hash.",
        allow_mutation=False,
    )

    def deserialize(self) -> float:
        """
        Deserialize output. This method retrieves the response from
        the miner in the form of self.text, deserializes it and returns it
        as the output of the dendrite.query() call.

        Returns:
        - List[float]: The deserialized response, which in this case is the list of preidictions.
        """
        return self
