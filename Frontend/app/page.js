'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaSpinner } from 'react-icons/fa';
import { processAudioAPI } from '@/lib/api';

export default function MeetingPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');
  const [recordTime, setRecordTime] = useState(0);
  const [audioURL, setAudioURL] = useState('');  // ← NEW: Audio preview URL
  const [debugInfo, setDebugInfo] = useState('');  // ← NEW: Debug information
  const recorderRef = useRef(null);
  const intervalRef = useRef(null);

  // Start Recording (browser)
  const startRecording = async () => {
    try {
      console.log('🎬 Starting recording...');
      setError('');
      setTranscription('');
      setSummary('');
      setAudioURL('');
      setDebugInfo('');
      setIsRecording(true);
      setRecordTime(0);

      // Start recording from browser mic
      console.log('🎤 Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('✅ Microphone access granted!');
      
      const recorder = new MediaRecorder(stream);
      console.log('📹 MediaRecorder created');
      
      const audioChunks = [];
      
      recorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
        console.log(`📦 Audio chunk received: ${e.data.size} bytes`);
      };
      
      // When recording stops, send audio to backend for processing
      recorder.onstop = async () => {
        console.log('🛑 Recording stopped');
        console.log(`📊 Total chunks: ${audioChunks.length}`);
        
        const blob = new Blob(audioChunks, { type: 'audio/wav' });
        console.log(`🎵 Audio blob created: ${blob.size} bytes`);
        
        // Create audio preview URL
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        console.log('🔗 Audio preview URL created');
        
        setDebugInfo(`Audio recorded: ${(blob.size / 1024).toFixed(2)} KB`);
        setIsProcessing(true);
        
        console.log('📤 Sending audio to backend...');
        
        // Call API to process audio (Whisper transcription + Mistral summary)
        const result = await processAudioAPI(blob);
        
        console.log('📥 Backend response:', result);
        
        if (!result.success) {
          throw new Error(result.error);
        }

        console.log('✅ Transcription received:', result.data.transcription?.substring(0, 50) + '...');
        console.log('✅ Summary received:', result.data.summary?.substring(0, 50) + '...');

        // Display results
        setTranscription(result.data.transcription);
        setSummary(result.data.summary);
        setIsProcessing(false);
        setDebugInfo(`Audio processed successfully! ${(blob.size / 1024).toFixed(2)} KB sent to backend`);
      };

      recorderRef.current = recorder;
      recorder.start();
      console.log('🔴 Recording started!');

      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordTime((prev) => prev + 1);
      }, 1000);

      setTranscription('🎙️ Recording started... Speak now!');
      setDebugInfo('Recording audio from microphone...');
    } catch (err) {
      console.error('❌ Start recording error:', err);
      setError('Failed to start recording: ' + err.message);
      setIsRecording(false);
      setIsProcessing(false);
    }
  };

  const stopRecording = () => {
    if (!isRecording || !recorderRef.current) return;
    recorderRef.current.stop();
    clearInterval(intervalRef.current);
    setIsRecording(false);
    setTranscription('Processing your audio...');
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <motion.div
        className="max-w-6xl mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-gradient mb-4">
            Meeting Summarizer
          </h1>
          <p className="text-secondary text-lg">
            Record, transcribe, and summarize your meetings with AI
          </p>
        </div>

        {/* Control Buttons */}
        <div className="flex justify-center gap-6 mb-12">
          <motion.button
            onClick={startRecording}
            disabled={isRecording || isProcessing}
            className={`btn-primary flex items-center gap-3 ${
              (isRecording || isProcessing) ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            whileHover={!isRecording && !isProcessing ? { scale: 1.05 } : {}}
            whileTap={!isRecording && !isProcessing ? { scale: 0.95 } : {}}
          >
            <FaMicrophone size={20} />
            Start Meeting
          </motion.button>

          <motion.button
            onClick={stopRecording}
            disabled={!isRecording || isProcessing}
            className={`btn-outline flex items-center gap-3 border-red-500/30 text-red-400 hover:border-red-400 hover:text-red-300 ${
              (!isRecording || isProcessing) ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            whileHover={isRecording && !isProcessing ? { scale: 1.05 } : {}}
            whileTap={isRecording && !isProcessing ? { scale: 0.95 } : {}}
          >
            {isProcessing ? (
              <>
                <FaSpinner className="animate-spin" size={20} />
                Processing...
              </>
            ) : (
              <>
                <FaStop size={20} />
                End Meeting
              </>
            )}
          </motion.button>
        </div>

        {/* Status Indicator */}
        {(isRecording || isProcessing) && (
          <motion.div
            className="flex justify-center mb-8"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div
              className={`px-6 py-2 rounded-full border ${
                isProcessing
                  ? 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400'
                  : 'border-red-500/50 bg-red-500/10 text-red-400'
              } flex items-center gap-2`}
            >
              {isProcessing ? (
                <>
                  <FaSpinner className="animate-spin" />
                  Processing with AI...
                </>
              ) : (
                <>
                  <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  Recording {recordTime}s
                </>
              )}
            </div>
          </motion.div>
        )}

        {/* Error Message */}
        {error && (
          <motion.div
            className="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-center"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {error}
          </motion.div>
        )}

        {/* Debug Info & Audio Player */}
        {debugInfo && (
          <motion.div
            className="mb-8 p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="text-blue-400 text-center mb-3">
              <strong>🔍 Debug Info:</strong> {debugInfo}
            </div>
            
            {audioURL && (
              <div className="flex flex-col items-center gap-2">
                <p className="text-blue-300 text-sm">🎵 Recorded Audio Preview:</p>
                <audio 
                  controls 
                  src={audioURL}
                  className="w-full max-w-md"
                  style={{ height: '40px' }}
                >
                  Your browser does not support audio playback.
                </audio>
                <p className="text-blue-300 text-xs">
                  ✅ Audio captured successfully! This is what will be sent to backend.
                </p>
              </div>
            )}
          </motion.div>
        )}

        {/* Text Fields */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <TextField
            label="📝 Transcription"
            value={transcription}
            placeholder="Transcription will appear here..."
          />
          <TextField
            label="🤖 AI Summary"
            value={summary}
            placeholder="AI-generated summary will appear here..."
          />
        </div>
      </motion.div>
    </div>
  );
}

function TextField({ label, value, placeholder }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.2 }}
    >
      <label className="block mb-3">
        <span className="text-xl font-bold text-accent">{label}</span>
      </label>
      <textarea
        value={value}
        readOnly
        placeholder={placeholder}
        className="w-full h-96 bg-gradient-primary border border-primary rounded-xl p-6 text-white resize-none focus:outline-none focus:border-primary-hover transition-all"
        style={{ fontFamily: 'monospace' }}
      />
      <p className="text-secondary text-sm mt-2">{value.length} characters</p>
    </motion.div>
  );
}
