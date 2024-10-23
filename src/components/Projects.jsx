import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

function Projects() {
  const [activeProjects, setActiveProjects] = useState([])
  const [archivedProjects, setArchivedProjects] = useState([])
  const navigate = useNavigate()
  const { logout, user } = useAuth()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects')
      setActiveProjects(response.data.active_projects)
      setArchivedProjects(response.data.archived_projects)
    } catch (error) {
      console.error('Error fetching projects:', error)
    }
  }

  const handleArchive = async (projectId) => {
    try {
      await axios.post(`/api/projects/${projectId}/archive`)
      fetchProjects()
    } catch (error) {
      console.error('Error archiving project:', error)
    }
  }

  const handleUnarchive = async (projectId) => {
    try {
      await axios.post(`/api/projects/${projectId}/unarchive`)
      fetchProjects()
    } catch (error) {
      console.error('Error unarchiving project:', error)
    }
  }

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>My Projects</h1>
        <div>
          <button onClick={() => navigate('/')} className="btn btn-secondary me-2">Home</button>
          <button onClick={logout} className="btn btn-secondary">Logout</button>
        </div>
      </div>

      <h2 className="mb-4">Active Projects</h2>
      <div className="row">
        {activeProjects.map(project => (
          <div key={project.id} className="col-md-6 mb-4">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">{project.name}</h5>
                <p className="card-text">Created: {new Date(project.created_at).toLocaleString()}</p>
                <div className="d-flex justify-content-between mt-3">
                  <button 
                    onClick={() => navigate(`/project/${project.id}`)} 
                    className="btn btn-primary"
                  >
                    Select Project
                  </button>
                  <button 
                    onClick={() => handleArchive(project.id)} 
                    className="btn btn-warning"
                  >
                    Archive
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <h2 className="mb-4 mt-5">Archived Projects</h2>
      <div className="row">
        {archivedProjects.map(project => (
          <div key={project.id} className="col-md-6 mb-4">
            <div className="card bg-secondary">
              <div className="card-body">
                <h5 className="card-title">{project.name}</h5>
                <p className="card-text">Created: {new Date(project.created_at).toLocaleString()}</p>
                <button 
                  onClick={() => handleUnarchive(project.id)} 
                  className="btn btn-success"
                >
                  Unarchive
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Projects
