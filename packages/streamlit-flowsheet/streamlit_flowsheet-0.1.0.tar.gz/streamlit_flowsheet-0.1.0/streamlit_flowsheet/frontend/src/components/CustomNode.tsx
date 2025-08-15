import React from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import { getNodeIcon } from './NodeIcons';

interface CustomNodeData {
  label: string;
  type: string;
  properties?: any[];
  showBox: boolean;
  onNodeClick?: (nodeData: any) => void;
  theme?: any;
}

const CustomNode: React.FC<NodeProps<CustomNodeData>> = ({ id, data, selected }) => {
  const Icon = getNodeIcon(data.type);
  const theme = data.theme || {};
  
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (data.onNodeClick) {
      data.onNodeClick({
        id,
        label: data.label,
        type: data.type,
        properties: data.properties,
      });
    }
  };

  const nodeStyle = {
    padding: '10px',
    borderRadius: '8px',
    background: theme.backgroundColor || '#fff',
    border: data.showBox ? `2px solid ${selected ? theme.primaryColor || '#0ea5e9' : theme.textColor || '#d1d5db'}` : 'none',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: selected ? `0 0 0 2px ${theme.primaryColor || '#0ea5e9'}33` : undefined,
  };

  const labelStyle = {
    marginTop: '8px',
    fontSize: '12px',
    fontWeight: selected ? '600' : '500',
    textAlign: 'center' as const,
    color: theme.textColor || '#000',
  };

  const iconColor = selected ? (theme.primaryColor || '#0ea5e9') : (theme.textColor || '#6b7280');

  return (
    <div style={nodeStyle} onClick={handleClick}>
      <Handle type="source" position={Position.Top} style={{ opacity: 0 }} id="top-source" />
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} id="top-target" />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} id="bottom-source" />
      <Handle type="target" position={Position.Bottom} style={{ opacity: 0 }} id="bottom-target" />
      <Handle type="source" position={Position.Left} style={{ opacity: 0 }} id="left-source" />
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} id="left-target" />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} id="right-source" />
      <Handle type="target" position={Position.Right} style={{ opacity: 0 }} id="right-target" />
      
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Icon size={40} color={iconColor} />
        <div style={labelStyle}>{data.label}</div>
      </div>
    </div>
  );
};

export default CustomNode;