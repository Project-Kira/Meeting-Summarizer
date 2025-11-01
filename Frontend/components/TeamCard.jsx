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
      <div className="card relative overflow-hidden group-hover:border-primary-hover">
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-transparent to-transparent group-hover:from-emerald-500/5 group-hover:to-green-500/5 transition-all duration-500" />
        
        {/* Content */}
        <div className="relative z-10">
          {/* Profile Image */}
          <div className="mb-4 flex justify-center">
            <div className="profile-image">
              <img 
                src={member.image} 
                alt={member.name}
              />
            </div>
          </div>

          {/* Name */}
          <h3 className="text-2xl font-bold text-center mb-2 text-accent group-hover:text-primary-light transition-colors">
            {member.name}
          </h3>

          {/* Bio */}
          <p className="text-secondary text-center text-sm mb-6 min-h-[60px]">
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
      className="social-icon"
      whileHover={{ scale: 1.1, rotate: 5 }}
      whileTap={{ scale: 0.95 }}
      aria-label={label}
    >
      <Icon size={18} />
    </motion.a>
  );
}