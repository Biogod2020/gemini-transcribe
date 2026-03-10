import json
import os
from typing import List, Dict, Any

class TranscriptExporter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_json(self, project_id: str, global_memory: Dict[str, Any], processed_chunks: List[Dict[str, Any]]):
        """Exports the entire transcription state to a JSON file."""
        data = {
            "project_id": project_id,
            "global_memory": global_memory,
            "processed_chunks": processed_chunks
        }
        file_path = os.path.join(self.output_dir, f"{project_id}_transcript.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path

    def export_markdown(self, project_id: str, global_memory: Dict[str, Any], processed_chunks: List[Dict[str, Any]]):
        """Exports the transcription to a readable Markdown file."""
        lines = []
        lines.append(f"# Transcription Report: {project_id}")
        lines.append(f"\n## Global Context")
        lines.append(f"- **Theme**: {global_memory.get('theme', 'N/A')}")
        lines.append(f"- **Tone**: {global_memory.get('tone', 'N/A')}")
        lines.append(f"- **Narrative Structure**: {global_memory.get('narrative_structure', 'N/A')}")
        
        lines.append(f"\n### Key Decisions")
        for decision in global_memory.get('key_decisions', []):
            lines.append(f"- {decision}")
            
        lines.append(f"\n### Speakers")
        for speaker in global_memory.get('speakers', []):
            lines.append(f"- **{speaker.get('id')}**: {speaker.get('characteristics')}")

        lines.append(f"\n### Glossary")
        lines.append(", ".join(global_memory.get('glossary', [])))

        lines.append(f"\n---\n")
        lines.append(f"## Transcript\n")

        for chunk in processed_chunks:
            lines.append(f"### Chunk {chunk.get('chunk_index')}")
            
            # Add thought as a hidden markdown comment or a subtle block
            thought = chunk.get('thought', '')
            if thought:
                lines.append(f"\n<details>\n<summary>Model Thinking Process</summary>\n\n{thought}\n\n</details>\n")

            raw_json = chunk.get('raw_json', [])
            if isinstance(raw_json, list):
                for turn in raw_json:
                    speaker = turn.get('speaker_id', 'Unknown')
                    text = turn.get('text', '')
                    lines.append(f"> **{speaker}**: {text}")
            else:
                lines.append(chunk.get('transcript', ''))
            lines.append("\n")

        file_path = os.path.join(self.output_dir, f"{project_id}_transcript.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return file_path
