# Research: Official Gemini API and CLI JSON Patterns

## 1. REST API Request Structure (v1beta)

The official Gemini REST API (specifically `v1beta` used for newer features like native thinking) uses **camelCase** for fields within `generationConfig`.

### Standard `generationConfig`
```json
{
  "responseMimeType": "application/json",
  "responseSchema": {
    "type": "object",
    "properties": {
      "field1": { "type": "string" }
    }
  },
  "thinkingConfig": {
    "includeProcess": true,
    "thinkingBudget": 1024,
    "thinkingLevel": "HIGH"
  },
  "temperature": 0.7,
  "topP": 0.95,
  "topK": 40,
  "maxOutputTokens": 8192
}
```

### Field Definitions:
- **`responseMimeType`**: Should be `application/json` for structured output.
- **`responseSchema`**: Defines the expected JSON structure.
- **`thinkingConfig`**:
  - `includeProcess` (boolean): Whether to return thoughts in the response.
  - `thinkingBudget` (integer): Max tokens for reasoning.
  - `thinkingLevel` (enum): `MINIMAL`, `LOW`, `MEDIUM`, `HIGH`.

## 2. Response Parsing Patterns

### Multipart Responses with Thoughts
When `includeProcess` is true, the response contains `thought` parts.

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          { "thought": true, "text": "Reasoning steps..." },
          { "text": "{\"actual\": \"json_output\"}" }
        ],
        "role": "model"
      },
      "finishReason": "STOP"
    }
  ]
}
```

### Best Practices:
1.  **Iterate Parts**: Do not assume the first part is text. Filter by `thought` flag.
2.  **Thought Signatures**: In multi-turn chat, the first function call or model turn in an active loop should include a `thoughtSignature` if thinking is enabled, to maintain state (found in `gemini-cli` source).
3.  **JSON Extraction**: While `responseMimeType: "application/json"` usually guarantees valid JSON, robust implementations should still handle cases where the model might wrap it in markdown blocks (e.g., using regex).

## 3. Official `gemini-cli` Internals

The official `google-gemini/gemini-cli` (TypeScript) uses a converter to map between internal SDK objects and the API payload.

- **`packages/core/src/code_assist/converter.ts`**: Handles conversion to `VertexGenerateContentRequest` which uses camelCase for `generationConfig` fields.
- **`packages/core/src/core/geminiChat.ts`**: 
  - Implements complex validation for thought parts.
  - Uses `thoughtSignature` to ensure request validation in multi-turn loops.
  - Consolidates text parts from multiple candidates/chunks.

## 4. Discrepancies in `gemini-transcribe`

| Feature | Current (Incorrect) | Official (Correct) |
| --- | --- | --- |
| Casing | `response_mime_type` | `responseMimeType` |
| Schema Casing | `response_schema` | `responseSchema` |
| Thinking Flag | `include_thoughts` | `includeProcess` |
| Thinking Budget | N/A | `thinkingBudget` |
| Thinking Config Casing | `thinking_config` | `thinkingConfig` |
| Multi-turn | Ignores `thoughtSignature` | Requires `thoughtSignature` |
