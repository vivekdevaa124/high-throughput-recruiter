import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { UploadCloud, ChevronDown, ChevronUp, CheckCircle, Database, Search, Cpu, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './index.css';

function App() {
  const [file, setFile] = useState(null);
  const [useBundled, setUseBundled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [topN, setTopN] = useState(25);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleRank = async () => {
    if (!file && !useBundled) return;
    
    setLoading(true);
    const formData = new FormData();
    if (file) formData.append('file', file);
    
    try {
      const response = await axios.post(`http://127.0.0.1:8000/api/rank?use_bundled=${useBundled}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setData(response.data.candidates);
      if (response.data.candidates.length > 0) {
        setExpandedId(response.data.candidates[0].id);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to rank candidates. Check console.');
    } finally {
      setLoading(false);
    }
  };

  const renderComponentChart = (components) => {
    const chartData = Object.keys(components).map(key => ({
      name: key.split(' ')[0],
      score: components[key]
    }));

    return (
      <div style={{ height: 200, marginTop: '20px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" stroke="#a0a0b0" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#a0a0b0" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip 
              contentStyle={{ background: '#14141e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
              itemStyle={{ color: '#8d52fa' }}
            />
            <Bar dataKey="score" fill="#8d52fa" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.score > 0.8 ? '#8d52fa' : '#5a32fa'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="app-container">
      
      {/* Sidebar Controls */}
      <div className="sidebar">
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.2rem' }}>Configuration</h2>
          
          {/* JD Dropdown */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div className="glass-panel" style={{ padding: '0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
                <FileText size={16} color="var(--text-muted)" /> Job Description (Senior AI Engineer)
              </div>
              <ChevronDown size={16} color="var(--text-muted)" />
            </div>
          </div>
          
          <div 
            className="upload-zone"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload').click()}
          >
            <UploadCloud size={48} color={file ? '#ff4b4b' : '#8d52fa'} style={{ marginBottom: '1rem' }} />
            <p style={{ color: 'var(--text-muted)' }}>
              {file ? file.name : "Drag & Drop JSONL here"}
            </p>
            <input 
              id="file-upload" 
              type="file" 
              style={{ display: 'none' }} 
              onChange={e => setFile(e.target.files[0])} 
            />
          </div>

          <div className="checkbox-wrapper" style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
            <input 
              type="checkbox" 
              id="bundled" 
              checked={useBundled}
              onChange={(e) => setUseBundled(e.target.checked)}
              style={{ width: '18px', height: '18px', accentColor: '#ff4b4b' }}
            />
            <label htmlFor="bundled" style={{ userSelect: 'none' }}>Use bundled sample dataset</label>
          </div>
          
          {/* Top N Slider */}
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              <span style={{color: 'var(--text-muted)'}}>Top N to display</span>
              <span style={{color: '#ff4b4b', fontWeight: 'bold'}}>{topN}</span>
            </div>
            <input 
              type="range" 
              min="10" 
              max="100" 
              value={topN} 
              onChange={(e) => setTopN(parseInt(e.target.value))}
              style={{ width: '100%', accentColor: '#ff4b4b' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
              <span>10</span>
              <span>100</span>
            </div>
          </div>

          <button 
            className="btn-primary" 
            style={{ width: '100%', background: '#ff4b4b', boxShadow: '0 4px 15px rgba(255, 75, 75, 0.4)' }}
            onClick={handleRank}
            disabled={(!file && !useBundled) || loading}
          >
            {loading ? 'Analyzing Neural Data...' : '🚀 Rank Candidates'}
          </button>
        </div>
        
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={18} color="#ff4b4b"/> Engine Status
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Hybrid BM25 + TF-IDF matrix loaded. Semantic vectors ready.
          </p>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        <div className="header-banner">
          <div>
            <h1 className="header-title">Redrob AI Recruiter</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
              Next-generation talent intelligence platform
            </p>
          </div>
          <Database size={64} color="rgba(255,255,255,0.1)" />
        </div>

        {data && (
          <>
            <div className="metrics-grid">
              <div className="glass-panel metric-card">
                <span className="metric-title">Profiles Parsed</span>
                <span className="metric-value">{data.length}</span>
              </div>
              <div className="glass-panel metric-card">
                <span className="metric-title">Recalled Matches</span>
                <span className="metric-value">{data.filter(c => c.score > 0).length}</span>
              </div>
              <div className="glass-panel metric-card">
                <span className="metric-title">Top Score</span>
                <span className="metric-value">{data[0].score.toFixed(3)}</span>
              </div>
              <div className="glass-panel metric-card">
                <span className="metric-title">Avg Top-{Math.min(topN, 25)}</span>
                <span className="metric-value">
                  {(data.slice(0, Math.min(topN, 25)).reduce((acc, curr) => acc + curr.score, 0) / Math.min(topN, 25, data.length)).toFixed(3)}
                </span>
              </div>
            </div>
            
            {/* Score Distribution Chart */}
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>Score Distribution (Top N)</h2>
              <div className="glass-panel" style={{ height: 250, padding: '1.5rem 1rem 1rem 0' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.slice(0, topN).map((c, i) => ({ rank: i, score: c.score }))} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="rank" stroke="#a0a0b0" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#a0a0b0" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{ background: '#14141e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      itemStyle={{ color: '#4dabf5' }}
                      formatter={(value) => value.toFixed(3)}
                      labelFormatter={(label) => `Rank #${label + 1}`}
                      cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    />
                    <Bar dataKey="score" fill="#4dabf5" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>Top {topN} Ranked Candidates</h2>
              {data.slice(0, topN).map((cand, index) => (
                <div 
                  key={cand.id} 
                  className={`glass-panel candidate-card ${expandedId === cand.id ? 'expanded' : ''}`}
                >
                  <div className="candidate-header" onClick={() => setExpandedId(expandedId === cand.id ? null : cand.id)}>
                    <div className="candidate-info">
                      <div className={`rank-badge ${index < 3 ? 'top-3' : ''}`}>#{index + 1}</div>
                      <div>
                        <h3 style={{ fontSize: '1.1rem', margin: 0 }}>{cand.title}</h3>
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>
                          {cand.exp.toFixed(1)} years experience • ID: {cand.id}
                        </p>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span className="score-badge">Score: {cand.score.toFixed(3)}</span>
                      {expandedId === cand.id ? <ChevronUp size={20} color="var(--text-muted)" /> : <ChevronDown size={20} color="var(--text-muted)" />}
                    </div>
                  </div>
                  
                  <div className="candidate-body">
                    <div style={{ padding: '1rem', background: 'rgba(141, 82, 250, 0.1)', borderRadius: '8px', borderLeft: '4px solid var(--primary)', marginBottom: '1.5rem' }}>
                      <strong>AI Reasoning:</strong> {cand.reasoning}
                    </div>

                    <h4 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
                      Component Breakdown
                    </h4>
                    {renderComponentChart(cand.details.components)}

                    <div className="sub-metrics">
                      {Object.entries(cand.details.metrics).map(([key, val]) => (
                        <div key={key} className="sub-metric">
                          <span className="sub-metric-title">{key}</span>
                          <span className="sub-metric-val">{Number(val).toFixed(3)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

    </div>
  );
}

export default App;
