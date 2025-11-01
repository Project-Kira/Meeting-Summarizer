'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaSpinner } from 'react-icons/fa';

export default function MeetingPage() {
  const [sessionId, setSessionId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');

  // Start Meeting
  const startMeeting = async () => {
    try {
      setError('');
      setTranscription('');
      setSummary('');
      
      const response = await fetch('/api/meeting/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to start meeting');
      }

      const data = await response.json();
      setSessionId(data.sessionId);
      setIsRecording(true);
      setTranscription('Recording started... Speak now!');
      
    } catch (err) {
      setError(err.message || 'Failed to start meeting');
      console.error('Start meeting error:', err);
    }
  };

  // End Meeting
  const endMeeting = async () => {
    if (!sessionId) {
      setError('No active session');
      return;
    }

    try {
      setIsRecording(false);
      setIsProcessing(true);
      setTranscription('Processing audio...');
      
      const response = await fetch('/api/meeting/end', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to end meeting');
      }

      const data = await response.json();
      
      // Update with results
      setTranscription(data.transcription || 'No transcription available');
      setSummary(data.summary ? JSON.stringify(data.summary, null, 2) : 'No summary available');
      setIsProcessing(false);
      setSessionId(null);
      
    } catch (err) {
      setError(err.message || 'Failed to end meeting');
      setIsProcessing(false);
      console.error('End meeting error:', err);
    }
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
            onClick={startMeeting}
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
            onClick={endMeeting}
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

        {/* Status Badge */}
        {(isRecording || isProcessing) && (
          <motion.div 
            className="flex justify-center mb-8"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className={`px-6 py-2 rounded-full border ${
              isProcessing 
                ? 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400'
                : 'border-red-500/50 bg-red-500/10 text-red-400'
            } flex items-center gap-2`}>
              {isProcessing ? (
                <>
                  <FaSpinner className="animate-spin" />
                  Processing with AI...
                </>
              ) : (
                <>
                  <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  Recording in progress
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

        {/* Text Fields */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Transcription Field */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <label className="block mb-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl font-bold text-accent">📝 Transcription</span>
                {isRecording && (
                  <span className="text-sm text-secondary">(Live)</span>
                )}
              </div>
            </label>
            <textarea
              value={transcription}
              readOnly
              placeholder="Transcription will appear here..."
              className="w-full h-96 bg-gradient-primary border border-primary rounded-xl p-6 text-white resize-none focus:outline-none focus:border-primary-hover transition-all"
              style={{ fontFamily: 'monospace' }}
            />
            <p className="text-secondary text-sm mt-2">
              {transcription.length} characters
            </p>
          </motion.div>

          {/* Summary Field */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <label className="block mb-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl font-bold text-accent">🤖 AI Summary</span>
                {isProcessing && (
                  <FaSpinner className="animate-spin text-accent" />
                )}
              </div>
            </label>
            <textarea
              value={summary}
              readOnly
              placeholder="AI-generated summary will appear here..."
              className="w-full h-96 bg-gradient-primary border border-primary rounded-xl p-6 text-white resize-none focus:outline-none focus:border-primary-hover transition-all"
              style={{ fontFamily: 'monospace' }}
            />
            <p className="text-secondary text-sm mt-2">
              {summary.length} characters
            </p>
          </motion.div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <InfoCard
            icon="🎙️"
            title="Step 1"
            description="Click 'Start Meeting' to begin recording"
          />
          <InfoCard
            icon="🗣️"
            title="Step 2"
            description="Speak naturally during your meeting"
          />
          <InfoCard
            icon="✨"
            title="Step 3"
            description="Click 'End Meeting' to get AI summary"
          />
        </div>
      </motion.div>
    </div>
  );
}

function InfoCard({ icon, title, description }) {
  return (
    <motion.div
      className="card text-center hover-glow"
      whileHover={{ y: -5 }}
    >
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-bold text-accent mb-2">{title}</h3>
      <p className="text-secondary text-sm">{description}</p>
    </motion.div>
  );
}