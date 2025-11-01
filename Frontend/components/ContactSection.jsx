'use client';

import { motion } from 'framer-motion';
import { FaGithub, FaLinkedin, FaInstagram, FaTiktok, FaPhone, FaEnvelope } from 'react-icons/fa';

export default function ContactSection() {
  const contacts = [
    { name: "Alex Chen", phone: "+1 (555) 123-4567" },
    { name: "Maya Patel", phone: "+1 (555) 234-5678" },
    { name: "Jordan Kim", phone: "+1 (555) 345-6789" },
    { name: "Sam Rivera", phone: "+1 (555) 456-7890" }
  ];

  const socialLinks = [
    { 
      name: "GitHub", 
      icon: FaGithub, 
      url: "https://github.com/projectkeera",
      color: "hover:text-purple-400 hover:border-purple-400 hover:glow-sm"
    },
    { 
      name: "LinkedIn", 
      icon: FaLinkedin, 
      url: "https://linkedin.com/company/projectkeera",
      color: "hover:text-blue-400 hover:border-blue-400 hover:glow-sm"
    },
    { 
      name: "Instagram", 
      icon: FaInstagram, 
      url: "https://instagram.com/projectkeera",
      color: "hover:text-pink-400 hover:border-pink-400 hover:glow-sm"
    },
    { 
      name: "TikTok", 
      icon: FaTiktok, 
      url: "https://tiktok.com/@projectkeera",
      color: "hover:text-cyan-400 hover:border-cyan-400 hover:glow-sm"
    }
  ];

  return (
    <section className="section bg-gradient-to-b from-black to-gray-900" id="contact">
      <motion.div 
        className="max-w-6xl mx-auto"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8 }}
      >
        <h2 className="section-title">
          Get in Touch
        </h2>
        <p className="section-subtitle">
          Let's collaborate and build something amazing together
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Numbers */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <h3 className="text-2xl font-bold text-accent mb-6 flex items-center gap-3">
              <FaPhone className="text-accent" />
              Team Contacts
            </h3>
            <div className="space-y-4">
              {contacts.map((contact, index) => (
                <motion.div
                  key={contact.name}
                  className="card hover-glow"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3 + index * 0.1, duration: 0.5 }}
                  whileHover={{ x: 5 }}
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300 font-medium">{contact.name}</span>
                    <a 
                      href={`tel:${contact.phone}`}
                      className="text-accent hover:text-primary-light transition-colors"
                    >
                      {contact.phone}
                    </a>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Email */}
            <motion.div
              className="mt-8 card hover-glow"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center gap-3 text-accent mb-2">
                <FaEnvelope size={20} />
                <span className="font-semibold">Email Us</span>
              </div>
              <a 
                href="mailto:hello@projectkeera.com"
                className="text-gray-300 hover:text-accent transition-colors text-lg"
              >
                hello@projectkeera.com
              </a>
            </motion.div>
          </motion.div>

          {/* Social Links */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <h3 className="text-2xl font-bold text-accent mb-6">
              Follow Our Journey
            </h3>
            <p className="text-secondary mb-8">
              Connect with us on social media to stay updated on our daily progress, behind-the-scenes content, and AI innovations.
            </p>
            
            <div className="grid grid-cols-2 gap-6">
              {socialLinks.map((social, index) => (
                <motion.a
                  key={social.name}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`card group flex flex-col items-center justify-center gap-4 p-8 ${social.color}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4 + index * 0.1, duration: 0.5 }}
                  whileHover={{ y: -8, scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {/* Glow effect */}
                  <div className="absolute inset-0 bg-gradient-to-br from-transparent to-transparent group-hover:from-emerald-500/5 group-hover:to-green-500/5 rounded-2xl transition-all duration-300" />
                  
                  <social.icon className="text-5xl text-accent transition-all duration-300 relative z-10" />
                  <span className="text-lg font-semibold text-gray-300 group-hover:text-white transition-colors relative z-10">
                    {social.name}
                  </span>
                </motion.a>
              ))}
            </div>
          </motion.div>
        </div>

        {/* CTA */}
        <motion.div 
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6, duration: 0.8 }}
        >
          <div className="card-lg inline-block">
            <p className="text-xl text-gray-300 mb-4">
              Interested in collaborating or learning more about our project?
            </p>
            <motion.a
              href="mailto:hello@projectkeera.com"
              className="btn-primary"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Let's Build Together
            </motion.a>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}