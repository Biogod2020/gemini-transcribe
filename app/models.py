from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict

class ThinkingConfig(BaseModel):
    include_process: bool = Field(default=True, alias="includeProcess")
    thinking_budget: int = Field(default=1024, alias="thinkingBudget")
    thinking_level: Optional[str] = Field(default=None, alias="thinkingLevel")
    
    model_config = ConfigDict(populate_by_name=True)

class GenerationConfig(BaseModel):
    response_mime_type: str = Field(default="application/json", alias="responseMimeType")
    response_schema: Optional[Any] = Field(default=None, alias="responseSchema")
    thinking_config: Optional[ThinkingConfig] = Field(default=None, alias="thinkingConfig")
    temperature: Optional[float] = None
    top_p: Optional[float] = Field(default=None, alias="topP")
    top_k: Optional[int] = Field(default=None, alias="topK")
    max_output_tokens: Optional[int] = Field(default=None, alias="maxOutputTokens")
    
    model_config = ConfigDict(populate_by_name=True)

class InlineData(BaseModel):
    mime_type: str = Field(alias="mimeType")
    data: str

class FileData(BaseModel):
    mime_type: str = Field(alias="mimeType")
    file_uri: str = Field(alias="fileUri")

class Part(BaseModel):
    text: Optional[str] = None
    inline_data: Optional[InlineData] = Field(default=None, alias="inlineData")
    file_data: Optional[FileData] = Field(default=None, alias="fileData")
    thought: Optional[bool] = None
    thought_signature: Optional[str] = Field(default=None, alias="thoughtSignature")
    
    model_config = ConfigDict(populate_by_name=True)

class Content(BaseModel):
    role: str
    parts: List[Part]

class GenerateContentRequest(BaseModel):
    contents: List[Content]
    generation_config: Optional[GenerationConfig] = Field(default=None, alias="generationConfig")
    system_instruction: Optional[Content] = Field(default=None, alias="systemInstruction")
    
    model_config = ConfigDict(populate_by_name=True)
