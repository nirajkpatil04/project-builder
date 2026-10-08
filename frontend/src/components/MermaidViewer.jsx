import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Copy, Check, Eye } from 'lucide-react';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#0d111a',
    primaryColor: '#2563eb',
    primaryTextColor: '#f8fafc',
    primaryBorderColor: '#3b82f6',
    lineColor: '#38bdf8',
    secondaryColor: '#1e293b',
    tertiaryColor: '#0f172a',
  },
  securityLevel: 'loose',
  fontFamily: 'Inter, -apple-system, sans-serif',
});

export default function MermaidViewer({ chartCode, title = 'Diagram' }) {
  const containerRef = useRef(null);
  const [svgContent, setSvgContent] = useState('');
  const [renderError, setRenderError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [showCode, setShowCode] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const renderChart = async () => {
      if (!chartCode) return;
      try {
        setRenderError(null);
        const uniqueId = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(uniqueId, chartCode.trim());
        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err) {
        if (isMounted) {
          console.warn('Mermaid rendering failed:', err);
          setRenderError('Could not render interactive diagram. Raw code view is available below.');
        }
      }
    };

    renderChart();
    return () => {
      isMounted = false;
    };
  }, [chartCode]);

  const handleCopy = () => {
    navigator.clipboard.writeText(chartCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      background: 'rgba(13, 17, 26, 0.75)',
      borderRadius: 'var(--radius-md)',
      border: '1px solid var(--border-subtle)',
      overflow: 'hidden',
      marginTop: '16px',
      marginBottom: '24px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 18px',
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(255, 255, 255, 0.02)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Eye size={18} color="var(--accent-cyan)" />
          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowCode(!showCode)}
            className="btn btn-secondary btn-sm"
          >
            {showCode ? 'View Visual' : 'View Mermaid Code'}
          </button>
          <button
            onClick={handleCopy}
            className="btn btn-secondary btn-sm"
          >
            {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>

      <div style={{ padding: '24px', overflowX: 'auto', textAlign: 'center', minHeight: '180px' }}>
        {showCode ? (
          <pre style={{
            textAlign: 'left',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.85rem',
            background: 'var(--bg-primary)',
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            color: 'var(--accent-cyan)',
            overflowX: 'auto',
          }}>
            {chartCode}
          </pre>
        ) : renderError ? (
          <div style={{ color: 'var(--accent-amber)', padding: '20px' }}>
            <p style={{ marginBottom: '12px' }}>{renderError}</p>
            <pre style={{
              textAlign: 'left',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.82rem',
              background: 'var(--bg-primary)',
              padding: '14px',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-secondary)',
            }}>
              {chartCode}
            </pre>
          </div>
        ) : (
          <div
            ref={containerRef}
            dangerouslySetInnerHTML={{ __html: svgContent }}
            style={{ display: 'inline-block', maxWidth: '100%' }}
          />
        )}
      </div>
    </div>
  );
}
