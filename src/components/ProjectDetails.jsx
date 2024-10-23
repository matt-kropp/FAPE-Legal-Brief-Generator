import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

function ProjectDetails() {
  const [project, setProject] = useState(null)
  const [projectName, setProjectName] = useState('')
  const [outline, setOutline] = useState(null)
  const [documents, setDocuments] = useState([])
  const navigate = useNavigate()
  const { logout } = useAuth()

  useEffect(() => {
    fetchCurrentProject()
  }, [])

  const fetchCurrentProject = async () => {
    try {
      const response = await axios.get('/api/current_project')
      if (response.data.project) {
        setProject(response.data.project)
      }
    } catch (error) {
      console.error('Error fetching current project:', error)
    }
  }

  const handleCreateProject = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post('/api/projects', { name: projectName })
      if (response.data.success) {
        setProject(response.data.project)
        setProjectName('')
      }
    } catch (error) {
      console.error('Error creating project:', error)
    }
  }

  const handleOutlineUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('outline', file)

    try {
      const response = await axios.post(
        `/api/projects/${project.id}/upload_outline`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      fetchCurrentProject()
    } catch (error) {
      console.error('Error uploading outline:', error)
    }
  }

  const handleDocumentsUpload = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    const formData = new FormData()
    files.forEach(file => {
      formData.append('documents', file)
    })

    try {
      const response = await axios.post(
        `/api/projects/${project.id}/upload_documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      fetchCurrentProject()
    } catch (error) {
      console.error('Error uploading documents:', error)
    }
  }

  const handleProcessProject = async () => {
    try {
      await axios.post(`/api/projects/${project.id}/process`)
      fetchCurrentProject()
    } catch (error) {
      console.error('Error processing project:', error)
    }
  }

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Legal Court Brief Generator</h1>
        <div>
          <button onClick={() => navigate('/projects')} className="btn btn-secondary me-2">My Projects</button>
          <button onClick={logout} className="btn btn-secondary">Logout</button>
        </div>
      </div>

      {!project ? (
        <div className="card mb-4">
          <div className="card-body">
            <h5 className="card-title">Create New Project</h5>
            <form onSubmit={handleCreateProject}>
              <div className="mb-3">
                <label htmlFor="project_name" className="form-label">Project Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="project_name"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary">Create Project</button>
            </form>
          </div>
        </div>
      ) : (
        <div className="card mb-4">
          <div className="card-body">
            <h5 className="card-title">Current Project: {project.name}</h5>
            
            <div className="row">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <h6 className="card-subtitle mb-3">Upload Outline</h6>
                    <div className="mb-3">
                      <label htmlFor="outline" className="form-label">Select Outline File (.txt)</label>
                      <input
                        type="file"
                        className="form-control"
                        id="outline"
                        accept=".txt"
                        onChange={handleOutlineUpload}
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <h6 className="card-subtitle mb-3">Upload Supporting Documents</h6>
                    <div className="mb-3">
                      <label htmlFor="documents" className="form-label">Select Supporting Documents (.pdf)</label>
                      <input
                        type="file"
                        className="form-control"
                        id="documents"
                        multiple
                        accept=".pdf"
                        onChange={handleDocumentsUpload}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {project.documents && project.documents.length > 0 && (
              <div className="mt-4">
                <h6>Uploaded Documents:</h6>
                <ul className="list-group">
                  {project.documents.map(doc => (
                    <li key={doc.id} className="list-group-item d-flex justify-content-between align-items-center">
                      {doc.filename}
                      <span className="badge bg-primary">{doc.file_type}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {project.has_output && (
              <div className="mt-4">
                <h6>Generated Content:</h6>
                <div className="btn-group">
                  <button onClick={() => window.location.href = `/view/timeline/${project.id}`} className="btn btn-info">
                    View Timeline
                  </button>
                  <button onClick={() => window.location.href = `/view/narrative/${project.id}`} className="btn btn-info">
                    View Narrative
                  </button>
                </div>
              </div>
            )}

            {project.documents && project.documents.some(doc => doc.file_type === 'outline') &&
             project.documents.some(doc => doc.file_type === 'supporting') && (
              <div className="mt-4">
                <button onClick={handleProcessProject} className="btn btn-success">
                  Process Project
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectDetails
