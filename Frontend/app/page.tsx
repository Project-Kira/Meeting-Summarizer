'use client';

import { motion } from 'framer-motion';
import TeamCard from '../components/TeamCard';
import AboutSection from '../components/AboutSection';
import ContactSection from '../components/ContactSection';

export default function Home() {
  const teamMembers = [
    {
      name: "Alex Chen",
      bio: "Full-stack wizard specializing in AI integration and scalable architectures. Passionate about making AI accessible.",
      image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
      github: "https://github.com/alexchen",
      linkedin: "https://linkedin.com/in/alexchen",
      instagram: "https://instagram.com/alexchen",
      tiktok: "https://tiktok.com/@alexchen"
    },
    {
      name: "Maya Patel",
      bio: "AI/ML engineer with a focus on healthcare and education tech. Building solutions that make a real difference.",
      image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Maya",
      github: "https://github.com/mayapatel",
      linkedin: "https://linkedin.com/in/mayapatel",
      instagram: "https://instagram.com/mayapatel",
      tiktok: "https://tiktok.com/@mayapatel"
    },
    {
      name: "Jordan Kim",
      bio: "Frontend developer and UX enthusiast. Crafting beautiful, intuitive interfaces for AI-powered applications.",
      image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jordan",
      github: "https://github.com/jordankim",
      linkedin: "https://linkedin.com/in/jordankim",
      instagram: "https://instagram.com/jordankim",
      tiktok: "https://tiktok.com/@jordankim"
    },
    {
      name: "Sam Rivera",
      bio: "Data scientist and real estate tech innovator. Transforming industries through intelligent automation and insights.",
      image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sam",
      github: "https://github.com/samrivera",
      linkedin: "https://linkedin.com/in/samrivera",
      instagram: "https://instagram.com/samrivera",
      tiktok: "https://tiktok.com/@samrivera"
    }
  ];

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section */}
      <motion.section 
        className="min-h-screen flex flex-col items-center justify-center px-4 py-20"
        initial="hidden"
        animate="visible"
        variants={fadeIn}
      >
        <motion.div 
          className="text-center space-y-6"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-6xl md:text-8xl font-bold text-gradient">
            Project Keera
          </h1>
          <motion.p 
            className="text-2xl md:text-3xl text-accent font-light"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            30 Days, 30 AI Solutions
          </motion.p>
          <motion.div 
            className="w-24 h-1 btn-primary mx-auto rounded-full"
            initial={{ width: 0 }}
            animate={{ width: 96 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          />
        </motion.div>

        {/* Domains */}
        <motion.div 
          className="mt-16 flex flex-wrap justify-center gap-4 max-w-3xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
        >
          {['Social Media', 'SMEs', 'Education Tech', 'Real Estate Tech', 'Health Care Tech'].map((domain, i) => (
            <motion.span
              key={domain}
              className="tag"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1 + i * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              {domain}
            </motion.span>
          ))}
        </motion.div>
      </motion.section>

      {/* About Section */}
      <AboutSection />

      {/* Team Section */}
      <section className="section" id="team">
        <motion.div 
          className="max-w-7xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={fadeIn}
        >
          <h2 className="section-title">
            Meet the Team
          </h2>
          <p className="section-subtitle">
            Four developers, one mission: push the boundaries of AI
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamMembers.map((member, index) => (
              <TeamCard key={member.name} member={member} index={index} />
            ))}
          </div>
        </motion.div>
      </section>

      {/* Contact Section */}
      <ContactSection />

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-primary">
        <div className="max-w-7xl mx-auto text-center text-secondary">
          <p>© 2024 Project Keera. Building the future, one AI solution at a time.</p>
        </div>
      </footer>
    </div>
  );
}