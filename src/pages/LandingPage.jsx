import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-container">
      <header className="landing-header">
        <h1>Welcome to AI Chat History</h1>
        <p className="subtitle">Your conversations with AI, organized and searchable</p>
      </header>

      <section className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">📝</div>
          <h3>Save Your Chats</h3>
          <p>Never lose an important AI conversation again. Save and organize all your chat histories.</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Smart Search</h3>
          <p>Quickly find specific conversations with our powerful search functionality.</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>Analytics</h3>
          <p>Get insights into your AI conversations with detailed analytics and summaries.</p>
        </div>
      </section>

      <section className="cta-section">
        <h2>Start Organizing Your AI Conversations Today</h2>
        <p>Join thousands of users who are already managing their AI chat histories effectively.</p>
        <Link to="/signup" className="cta-button">Get Started</Link>
      </section>

      <section className="how-it-works">
        <h2>How It Works</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h4>Sign Up</h4>
            <p>Create your free account in seconds</p>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <h4>Import Chats</h4>
            <p>Upload your AI conversation history</p>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <h4>Organize</h4>
            <p>Sort, tag, and search your conversations</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage; 