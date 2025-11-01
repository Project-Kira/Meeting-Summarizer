#!/usr/bin/env python3
"""
Voice Meeting Demo - Capture audio and send to Meeting Summarizer backend
Requires: pip install pyaudio openai-whisper requests
"""
import os
import sys
import time
import wave
import json
import requests
import threading
from datetime import datetime
from pathlib import Path

try:
    import pyaudio
except ImportError:
    print("❌ pyaudio not installed. Install with:")
    print("   sudo apt install portaudio19-dev python3-pyaudio")
    print("   pip install pyaudio")
    sys.exit(1)

try:
    import whisper
except ImportError:
    print("❌ whisper not installed. Install with:")
    print("   pip install openai-whisper")
    sys.exit(1)


# Configuration
API_URL = "http://localhost:8000"
CHUNK_DURATION = 10  # Record in 10-second chunks
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Load Whisper model
print("🔄 Loading Whisper model (tiny)...")
model = whisper.load_model("tiny")  # Options: tiny, base, small, medium, large
print("✅ Whisper loaded")


class VoiceMeetingRecorder:
    def __init__(self, meeting_id, speaker_name="You"):
        self.meeting_id = meeting_id
        self.speaker_name = speaker_name
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        
    def record_chunk(self, duration=CHUNK_DURATION):
        """Record audio for specified duration"""
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=1024
        )
        
        print(f"🎤 Recording for {duration} seconds...")
        frames = []
        
        for i in range(0, int(SAMPLE_RATE / 1024 * duration)):
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        return b''.join(frames)
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper"""
        # Save to temporary file
        temp_file = "/tmp/voice_chunk.wav"
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)
        
        # Transcribe
        result = model.transcribe(temp_file, language="en")
        text = result["text"].strip()
        
        os.remove(temp_file)
        return text
    
    def send_segment(self, text):
        """Send transcribed text to backend"""
        if not text or len(text) < 10:
            return False
        
        payload = {
            "meeting_id": self.meeting_id,
            "speaker": self.speaker_name,
            "timestamp_iso": datetime.utcnow().isoformat() + "Z",
            "text_segment": text
        }
        
        try:
            response = requests.post(f"{API_URL}/ingest/segment", json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Sent: {text[:60]}...")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_summary(self):
        """Get current summary"""
        try:
            response = requests.get(f"{API_URL}/meetings/{self.meeting_id}/summary", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def start_recording_loop(self):
        """Main recording loop"""
        self.is_recording = True
        chunk_count = 0
        
        print("\n" + "="*70)
        print("🎙️  VOICE MEETING RECORDER")
        print("="*70)
        print(f"Meeting ID: {self.meeting_id}")
        print(f"Speaker: {self.speaker_name}")
        print("\nPress Ctrl+C to stop and finalize meeting")
        print("="*70 + "\n")
        
        try:
            while self.is_recording:
                chunk_count += 1
                print(f"\n--- Chunk {chunk_count} ---")
                
                # Record
                audio_data = self.record_chunk(CHUNK_DURATION)
                
                # Transcribe
                print("🔄 Transcribing...")
                text = self.transcribe_audio(audio_data)
                
                if text:
                    print(f"📝 Transcript: {text}")
                    self.send_segment(text)
                else:
                    print("⚠️  No speech detected")
                
                # Show summary every 3 chunks
                if chunk_count % 3 == 0:
                    print("\n📊 Fetching current summary...")
                    summary = self.get_summary()
                    if summary and summary.get("content"):
                        content = summary["content"]
                        print(f"Summary: {content.get('summary', 'N/A')[:100]}...")
                    else:
                        print("No summary yet")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping recording...")
            self.is_recording = False
    
    def finalize(self):
        """Finalize the meeting"""
        print("\n🔄 Finalizing meeting...")
        try:
            response = requests.post(f"{API_URL}/meetings/{self.meeting_id}/finalize", timeout=5)
            if response.status_code == 200:
                print("✅ Meeting finalized")
                
                # Wait for final summary
                print("⏳ Waiting 3 seconds for final summary...")
                time.sleep(3)
                
                # Get final summary
                summary = self.get_summary()
                if summary:
                    print("\n" + "="*70)
                    print("📊 FINAL SUMMARY")
                    print("="*70)
                    content = summary.get("content", {})
                    print(f"\nSummary: {content.get('summary', 'N/A')}")
                    
                    if content.get("decisions"):
                        print(f"\nDecisions ({len(content['decisions'])}):")
                        for d in content["decisions"][:5]:
                            print(f"  • {d['text']}")
                    
                    if content.get("action_items"):
                        print(f"\nAction Items ({len(content['action_items'])}):")
                        for a in content["action_items"][:5]:
                            print(f"  • {a['text']} (Owner: {a.get('owner', 'N/A')})")
                    
                    print("="*70)
                else:
                    print("⚠️  No final summary available")
        except Exception as e:
            print(f"❌ Error finalizing: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.audio.terminate()


def create_meeting(title):
    """Create a new meeting"""
    payload = {"title": title, "metadata": {"source": "voice_demo"}}
    try:
        response = requests.post(f"{API_URL}/meetings", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["id"]
        else:
            print(f"❌ Failed to create meeting: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/healthz", timeout=2)
        if response.status_code != 200:
            print("❌ Backend server not healthy")
            sys.exit(1)
    except:
        print("❌ Backend server not running!")
        print("   Start it with: bash dev.sh start")
        sys.exit(1)
    
    print("✅ Backend server is running")
    
    # Get meeting details
    meeting_title = input("\nEnter meeting title (or press Enter for default): ").strip()
    if not meeting_title:
        meeting_title = f"Voice Meeting {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    speaker_name = input("Enter your name (or press Enter for 'You'): ").strip()
    if not speaker_name:
        speaker_name = "You"
    
    # Create meeting
    print(f"\n🔄 Creating meeting: {meeting_title}")
    meeting_id = create_meeting(meeting_title)
    
    if not meeting_id:
        print("❌ Failed to create meeting")
        sys.exit(1)
    
    print(f"✅ Meeting created: {meeting_id}")
    
    # Start recording
    recorder = VoiceMeetingRecorder(meeting_id, speaker_name)
    
    try:
        recorder.start_recording_loop()
    finally:
        recorder.finalize()
        recorder.cleanup()
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
