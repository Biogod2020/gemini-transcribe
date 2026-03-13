import time
import evaluate
from typing import List, Dict, Any
from app.utils import normalize_text

class MetricsCalculator:
    def __init__(self):
        self.wer_metric = evaluate.load("wer")
        # Note: Depending on library version, additional metrics like MER/WIL might need specific loading
        # For simplicity in MVP, we focus on WER and RTF.

    def compute_all(self, predictions: List[str], references: List[str], duration_sec: float, processing_time_sec: float) -> Dict[str, Any]:
        """
        Calculates a 6-dimension scoring matrix.
        """
        norm_preds = [normalize_text(p) for p in predictions]
        norm_refs = [normalize_text(r) for r in references]
        
        wer = self.wer_metric.compute(predictions=norm_preds, references=norm_refs)
        
        return {
            "wer": wer,
            "accuracy": (1 - wer) * 100,
            "rtf": processing_time_sec / duration_sec if duration_sec > 0 else 0,
            "real_time_speed": duration_sec / processing_time_sec if processing_time_sec > 0 else 0,
            "total_duration_sec": duration_sec,
            "total_processing_time_sec": processing_time_sec
        }
