'use client';

import { motion } from 'framer-motion';

export default function AboutSection() {
  return (
    <section className="py-20 px-4" id="about">
      <motion.div 
        className="max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
      >
        <h2 className="text-5xl md:text-6xl font-bold text-center mb-12 bg-gradient-to-r from-emerald-400 to-green-600 bg-clip-text text-transparent">
          About Project Keera
        </h2>
        
        <motion.div 
          className="relative group"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.3 }}
        >
          {/* Glowing border effect */}
          <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 to-green-600 rounded-3xl opacity-20 group-hover:opacity-40 blur transition-all duration-500" />
          
          {/* Card content */}
          <div className="relative bg-gradient-to-br from-gray-900 to-black border border-emerald-500/30 rounded-3xl p-8 md:p-12">
            <motion.p 
              className="text-xl md:text-2xl text-gray-300 leading-relaxed text-center"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              At <span className="text-emerald-400 font-semibold">Project Keera</span>, we're challenging ourselves to build{' '}
              <span className="text-emerald-400 font-semibold">30 AI-powered solutions in 30 days</span> — pushing the limits of creativity, speed, and collaboration. 
              From social media to health tech, we explore how AI can create real impact.
            </motion.p>

            {/* Animated particles */}
            <div className="absolute top-4 right-4 w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <div className="absolute bottom-4 left-4 w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }} />
            <div className="absolute top-1/2 left-4 w-1.5 h-1.5 bg-emerald-300 rounded-full animate-pulse" style={{ animationDelay: '1s' }} />
            <div className="absolute top-1/4 right-8 w-1.5 h-1.5 bg-green-300 rounded-full animate-pulse" style={{ animationDelay: '1.5s' }} />
          </div>
        </motion.div>

        {/* Stats or highlights */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4, duration: 0.8 }}
        >
          <StatCard number="30" label="Days of Innovation" />
          <StatCard number="30" label="AI Solutions" />
          <StatCard number="5" label="Industry Domains" />
        </motion.div>
      </motion.div>
    </section>
  );
}

function StatCard({ number, label }) {
  return (
    <motion.div 
      className="text-center p-6 bg-gradient-to-br from-gray-900/50 to-black/50 border border-emerald-500/20 rounded-xl hover:border-emerald-400/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]"
      whileHover={{ y: -5 }}
    >
      <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-emerald-400 to-green-600 bg-clip-text text-transparent mb-2">
        {number}
      </div>
      <div className="text-gray-400 text-sm md:text-base">
        {label}
      </div>
    </motion.div>
  );
}