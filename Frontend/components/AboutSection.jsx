'use client';

import { motion } from 'framer-motion';

export default function AboutSection() {
  return (
    <section className="section" id="about">
      <motion.div 
        className="max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
      >
        <h2 className="section-title">
          About Project Keera
        </h2>
        
        <motion.div 
          className="relative group"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.3 }}
        >
          {/* Glowing border effect */}
          <div className="absolute -inset-1 btn-primary rounded-3xl opacity-20 group-hover:opacity-40 blur transition-all duration-500" />
          
          {/* Card content */}
          <div className="card-lg relative">
            <motion.p 
              className="text-xl md:text-2xl text-gray-300 leading-relaxed text-center"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              At <span className="text-accent font-semibold">Project Keera</span>, we're challenging ourselves to build{' '}
              <span className="text-accent font-semibold">30 AI-powered solutions in 30 days</span> — pushing the limits of creativity, speed, and collaboration. 
              From social media to health tech, we explore how AI can create real impact.
            </motion.p>

            {/* Animated particles */}
            <div className="absolute top-4 right-4 w-2 h-2 bg-primary-light rounded-full animate-pulse-glow" />
            <div className="absolute bottom-4 left-4 w-2 h-2 bg-primary rounded-full animate-pulse-glow" style={{ animationDelay: '0.5s' }} />
            <div className="absolute top-1/2 left-4 w-1.5 h-1.5 bg-accent rounded-full animate-pulse-glow" style={{ animationDelay: '1s' }} />
            <div className="absolute top-1/4 right-8 w-1.5 h-1.5 bg-primary rounded-full animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
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
      className="card text-center hover-glow"
      whileHover={{ y: -5 }}
    >
      <div className="text-4xl md:text-5xl font-bold text-gradient mb-2">
        {number}
      </div>
      <div className="text-secondary text-sm md:text-base">
        {label}
      </div>
    </motion.div>
  );
}