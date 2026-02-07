"""
Open-source TTS (Text-to-Speech) voice synthesis
Uses Coqui TTS for local, high-quality voice generation
Male voice for Model A, Female voice for Model B
"""

import os
from typing import Optional, Tuple
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

class VoiceSynthesizer:
    """Local TTS using Coqui TTS (open-source)"""
    
    def __init__(self, enable_tts: bool = False):
        self.enable_tts = enable_tts
        self.tts = None
        self.model_name = "tts_models/en/ljspeech/glow-tts"  # Default model
        self.audio_dir = Path.home() / ".trillm_arena" / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        if self.enable_tts:
            self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize Coqui TTS (lazy load)"""
        try:
            from TTS.api import TTS
            self.tts = TTS(model_name=self.model_name, verbose=False)
        except ImportError:
            print("⚠️ Coqui TTS not installed. Install with: pip install TTS")
            self.enable_tts = False
    
    def synthesize(
        self,
        text: str,
        speaker: str = "model_a"  # "model_a" (male) or "model_b" (female)
    ) -> Optional[str]:
        """
        Convert text to speech
        Returns path to audio file
        """
        
        if not self.enable_tts or not self.tts:
            return None
        
        try:
            # Clean text
            text = self._clean_text(text)
            
            if len(text) < 3:
                return None
            
            # Generate filename
            speaker_label = "male" if speaker == "model_a" else "female"
            filename = self.audio_dir / f"{speaker}_{hash(text) % 10000}.wav"
            
            # Skip if already generated
            if filename.exists():
                return str(filename)
            
            # Generate speech
            self.tts.tts_to_file(
                text=text,
                file_path=str(filename),
                speaker=speaker_label  # Coqui supports multiple speakers
            )
            
            return str(filename)
        
        except Exception as e:
            print(f"❌ TTS Error: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        # Remove special chars
        text = text.replace("*", "").replace("_", "").replace("`", "")
        # Remove URLs
        text = text.split("http")[0] if "http" in text else text
        # Truncate long text
        text = text[:500] if len(text) > 500 else text
        
        return text.strip()
    
    def synthesize_debate_results(
        self,
        debate_result: dict,
        include_opening: bool = True
    ) -> dict:
        """Generate audio for debate results"""
        
        if not self.enable_tts:
            return {"audio_files": {}, "status": "TTS disabled"}
        
        audio_files = {}
        
        # Model A opening
        if include_opening and "model_a" in debate_result:
            model_a_arg = debate_result["model_a"].get("argument", "")[:200]
            audio_files["model_a"] = self.synthesize(model_a_arg, "model_a")
        
        # Model B opening
        if include_opening and "model_b" in debate_result:
            model_b_arg = debate_result["model_b"].get("argument", "")[:200]
            audio_files["model_b"] = self.synthesize(model_b_arg, "model_b")
        
        # Verdict
        verdict = debate_result.get("fast_verdict", "")[:150]
        if verdict:
            audio_files["verdict"] = self.synthesize(verdict, "model_a")
        
        return {
            "audio_files": audio_files,
            "status": "generated" if audio_files else "no_audio"
        }


# Global voice synthesizer instance
voice_synthesizer = VoiceSynthesizer(enable_tts=False)  # Default disabled


def enable_voice_synthesis():
    """Enable voice synthesis globally"""
    global voice_synthesizer
    voice_synthesizer.enable_tts = True
    voice_synthesizer._initialize_tts()


def disable_voice_synthesis():
    """Disable voice synthesis"""
    global voice_synthesizer
    voice_synthesizer.enable_tts = False


if __name__ == "__main__":
    # Test without TTS enabled
    print("Voice module loaded. Enable with: enable_voice_synthesis()")
