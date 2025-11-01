'use client';

import { motion } from 'framer-motion';
import { FaGithub, FaLinkedin, FaInstagram, FaTiktok } from 'react-icons/fa';

export default function TeamCard({ member, index }) {
  const cardVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        delay: index * 0.1,
        duration: 0.6
      }
    }
  };

  return (
    <motion.div
      className="group relative"
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
    >
      <div className="relative bg-gradient-to-br from-gray-900 to-black border border-emerald-500/20 rounded-2xl p-6 overflow-hidden transition-all duration-500 hover:border-emerald-400/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.2)]">
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/0 to-green-500/0 group-hover:from-emerald-500/5 group-hover:to-green-500/5 transition-all duration-500" />
        
        {/* Content */}
        <div className="relative z-10">
          {/* Profile Image */}
          <div className="mb-4 flex justify-center">
            <div className="relative w-32 h-32 rounded-full overflow-hidden border-4 border-emerald-500/30 group-hover:border-emerald-400 transition-all duration-300 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.4)]">
              <img 
                src={member.image} 
                alt={member.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
            </div>
          </div>

          {/* Name */}
          <h3 className="text-2xl font-bold text-center mb-2 text-emerald-300 group-hover:text-emerald-400 transition-colors">
            {member.name}
          </h3>

          {/* Bio */}
          <p className="text-gray-400 text-center text-sm mb-6 min-h-[60px]">
            {member.bio}
          </p>

          {/* Social Links */}
          <div className="flex justify-center gap-4">
            <SocialIcon href={member.github} icon={FaGithub} label="GitHub" />
            <SocialIcon href={member.linkedin} icon={FaLinkedin} label="LinkedIn" />
            <SocialIcon href={member.instagram} icon={FaInstagram} label="Instagram" />
            <SocialIcon href={member.tiktok} icon={FaTiktok} label="TikTok" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function SocialIcon({ href, icon: Icon, label }) {
  return (
    <motion.a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="w-10 h-10 flex items-center justify-center rounded-full border border-emerald-500/30 text-emerald-400 hover:border-emerald-400 hover:text-emerald-300 hover:shadow-[0_0_15px_rgba(16,185,129,0.4)] transition-all duration-300"
      whileHover={{ scale: 1.1, rotate: 5 }}
      whileTap={{ scale: 0.95 }}
      aria-label={label}
    >
      <Icon size={18} />
    </motion.a>
  );
}