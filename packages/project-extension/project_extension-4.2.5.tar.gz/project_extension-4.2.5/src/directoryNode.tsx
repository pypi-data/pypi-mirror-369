import React, { useState } from 'react';
import { IProjectStep } from './type';
import {
  addBelowIcon,
  caretDownEmptyIcon,
  circleIcon,
  deleteIcon,
  editIcon,
  LabIcon,
  linkIcon
} from '@jupyterlab/ui-components';
import { JupyterFrontEnd } from '@jupyterlab/application';

export function DirectoryNode({
  node,
  app,
  onNodeClick,
  onAddBelow,
  onEditName,
  onDelete,
  onLink
}: {
  node: IProjectStep;
  app: JupyterFrontEnd;
  onNodeClick: (node: IProjectStep) => void;
  onEditName: (node: IProjectStep) => void;
  onDelete: (node: IProjectStep) => void;
  onLink: (node: IProjectStep) => void;
  onAddBelow: (node: IProjectStep) => void;
}) {
  const [expanded, setExpanded] = useState(true);
  const [currentNode, setCurrentNode] = useState('');

  const [hovered, setHovered] = useState(false);
  const hasChildren = node.children && node.children.length > 0;
  const isChapter = node.isChapter;
  return (
    <div style={{ marginLeft: 16 }}>
      <div
        className={['j-chapter', node.id === currentNode ? 'current' : ''].join(
          ' '
        )}
        style={{
          fontWeight: node.isChapter ? 'bold' : 'normal',
          fontSize: node.isChapter ? '14px' : '14px'
        }}
        onClick={() => {
          if (node.path) {
            setCurrentNode(node.id);
            onNodeClick(node);
          }
          if (hasChildren) {
            setExpanded(e => !e);
          }
        }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'start',
            alignItems: 'center'
          }}
        >
          {!isChapter ? (
            <LabIcon.resolveReact
              icon={circleIcon}
              className="jp-project-node-mini-icon"
            />
          ) : (
            <div
              style={{
                display: 'flex',
                flexDirection: 'row',
                width: 30,
                height: 30
              }}
            >
              {hasChildren && (
                <span style={{ marginRight: 4 }}>
                  {expanded ? (
                    <LabIcon.resolveReact
                      icon={caretDownEmptyIcon}
                      className="jp-project-node-icon"
                    />
                  ) : (
                    <LabIcon.resolveReact
                      icon={caretDownEmptyIcon}
                      className="jp-project-node-icon rotate-90"
                    />
                  )}
                </span>
              )}
            </div>
          )}

          <span> {node.name} </span>
        </div>
        {hovered && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              justifyContent: 'flex-end',
              alignItems: 'center'
            }}
          >
            {!isChapter && (
              <div
                onClick={e => {
                  e.stopPropagation();
                  console.log('link');
                  onLink(node);
                }}
              >
                <LabIcon.resolveReact
                  icon={linkIcon}
                  className="jp-project-node-icon"
                />
              </div>
            )}
            <div
              onClick={e => {
                e.stopPropagation();
                console.log('editname');
                onEditName(node);
              }}
            >
              <LabIcon.resolveReact
                icon={editIcon}
                className="jp-project-node-icon"
              />
            </div>
            {isChapter && (
              <div
                onClick={e => {
                  e.stopPropagation();
                  console.log('click');
                  onAddBelow(node);
                }}
              >
                <LabIcon.resolveReact
                  icon={addBelowIcon}
                  className="jp-project-node-icon"
                />
              </div>
            )}
            <div
              onClick={e => {
                e.stopPropagation();
                console.log('click');
                onDelete(node);
              }}
            >
              <LabIcon.resolveReact
                icon={deleteIcon}
                className="jp-project-node-icon"
              />
            </div>
          </div>
        )}
      </div>
      {hasChildren && expanded && (
        <div>
          {node.children!.map(child => (
            <DirectoryNode
              key={child.id}
              app={app}
              node={child}
              onNodeClick={onNodeClick}
              onAddBelow={onAddBelow}
              onEditName={onEditName}
              onDelete={onDelete}
              onLink={onLink}
            />
          ))}
        </div>
      )}
    </div>
  );
}
