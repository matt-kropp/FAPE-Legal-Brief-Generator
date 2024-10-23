import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';

function Narrative() {
  const [narrativeContent, setNarrativeContent] = useState('');
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    fetchNarrativeContent();
  }, [projectId]);

  const fetchNarrativeContent = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axios.get(`/api/projects/${projectId}/narrative`);
      setNarrativeContent(response.data.narrative_content);
      setProject(response.data.project);
    } catch (error) {
      console.error('Error fetching narrative:', error);
      setError(error.response?.data?.message || 'Error loading narrative');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

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

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <div className="card">
        <div className="card-body markdown-content">
          <ReactMarkdown>{narrativeContent || 'No narrative content available'}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default Narrative;
