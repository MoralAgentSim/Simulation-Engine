import json
from typing import Optional
from pydantic import BaseModel

class CompletionResult(BaseModel):
    """
    Encapsulates the result from a completion request.

    Attributes:
        content (str): The primary completion content.
        reasoning (str): Additional reasoning content if provided.
        input_tokens (Optional[int]): Number of input/prompt tokens.
        output_tokens (Optional[int]): Number of output/completion tokens.
        model (Optional[str]): Model identifier used for this completion.
        duration_s (Optional[float]): Wall-clock seconds for the API call.
    """
    content: str
    reasoning: str = ""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    model: Optional[str] = None
    duration_s: Optional[float] = None

    def model_dump_json(self, **kwargs):
        """Return a JSON string representation of the model"""
        return json.dumps(self.model_dump(), **kwargs)

    def model_dump(self):
        """Return a dict representation of the model"""
        d = {"content": self.content, "reasoning": self.reasoning}
        if self.input_tokens is not None:
            d["input_tokens"] = self.input_tokens
        if self.output_tokens is not None:
            d["output_tokens"] = self.output_tokens
        if self.model is not None:
            d["model"] = self.model
        if self.duration_s is not None:
            d["duration_s"] = self.duration_s
        return d 