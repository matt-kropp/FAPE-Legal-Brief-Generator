import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';

function Narrative() {
  const [narrativeContent, setNarrativeContent] = useState('');
  const [project, setProject] = useState(null);
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    fetchNarrativeContent();
  }, [projectId]);

  const fetchNarrativeContent = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/narrative`);
      setNarrativeContent(response.data.narrative_content);
      setProject(response.data.project);
    } catch (error) {
      console.error('Error fetching narrative:', error);
    }
  };

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Narrative: {project?.name}</h1>
        <div>
          <button onClick={() => navigate('/projects')} className="btn btn-secondary me-2">Back to Projects</button>
          <button onClick={() => navigate('/')} className="btn btn-secondary me-2">Home</button>
          <button onClick={logout} className="btn btn-secondary">Logout</button>
        </div>
      </div>

      <div className="card">
        <div className="card-body markdown-content">
          <ReactMarkdown>{narrativeContent}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default Narrative;
