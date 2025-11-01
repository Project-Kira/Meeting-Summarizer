'use client';

import { motion } from 'framer-motion';

export default function MeetingPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <motion.div 
        className="max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-5xl font-bold text-emerald-400 mb-4">
          Team Meeting
        </h1>
        <p className="text-gray-300 text-lg">
          Welcome to our meeting page! This is where we discuss progress.
        </p>
      </motion.div>
    </div>
  )
}