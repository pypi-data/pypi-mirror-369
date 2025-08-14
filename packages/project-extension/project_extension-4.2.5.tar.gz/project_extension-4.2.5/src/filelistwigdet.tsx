// import { JupyterFrontEnd } from '@jupyterlab/application';
import React, { useEffect, useState } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { FileBrowserModel } from '@jupyterlab/filebrowser';
import { IDocumentManager } from '@jupyterlab/docmanager';
export interface IFileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
}

interface IFileListProps {
  documentManager: IDocumentManager;
  // files: IFileItem[];
  onItemClick?: (item: IFileItem) => void;
}

export const FileList: React.FC<IFileListProps> = ({
  documentManager,
  // files,
  onItemClick
}) => {
  const [files, setFiles] = useState<IFileItem[]>([]);
  const [currentPath, setCurrentPath] = useState<string>('/');
  const [selectedPath, setSelectedPath] = useState<string>('');
  useEffect(() => {
    const model = new FileBrowserModel({
      manager: documentManager
    });
    model.cd(currentPath).then(() => {
      setFiles(
        Array.from(model.items())
          .map<IFileItem>(item => {
            return {
              name: item.name,
              path: item.path,
              type: item.type === 'directory' ? 'directory' : 'file'
            };
          })
          .filter(item => {
            return (
              item.type === 'directory' ||
              item.path.endsWith('.ipynb') ||
              item.path.endsWith('.md') ||
              item.path.endsWith('.py') ||
              item.path.endsWith('.txt') ||
              item.path.endsWith('.js') ||
              item.path.endsWith('.css') ||
              item.path.endsWith('.yml') ||
              item.path.endsWith('.yaml') ||
              item.path.endsWith('.xml') ||
              item.path.endsWith('.csv')
            );
          })
          .sort((a, b) => {
            if (a.type !== b.type) {
              return a.type === 'directory' ? -1 : 1;
            }
            return a.name.localeCompare(b.name);
          })
      );
    });
  }, [documentManager, currentPath]);

  // 生成面包屑
  const pathParts =
    currentPath === '/' ? [''] : currentPath.split('/').filter(Boolean);
  const breadcrumbItems = [
    <span
      key="root"
      style={{
        cursor: currentPath !== '/' ? 'pointer' : 'default',
        color: currentPath !== '/' ? '#1890ff' : undefined
      }}
      onClick={() => currentPath !== '/' && setCurrentPath('/')}
    >
      根目录
    </span>
  ];
  let pathAcc = '';
  pathParts.forEach((part, idx) => {
    pathAcc += '/' + part;
    breadcrumbItems.push(
      <span key={`sep-${idx}`}> / </span>,
      <span
        key={pathAcc}
        style={{
          cursor: idx !== pathParts.length - 1 ? 'pointer' : 'default',
          color: idx !== pathParts.length - 1 ? '#1890ff' : undefined
        }}
        onClick={() => {
          if (idx !== pathParts.length - 1) {
            setCurrentPath(pathAcc);
          }
        }}
      >
        {part}
      </span>
    );
  });
  return (
    <div className="jp-filelist-widget">
      <div className="jp-filelist-widget-breadcrumbs">{breadcrumbItems}</div>
      <div className="jp-filelist-widget-list-container">
        {files.map(item => (
          <div
            key={item.path}
            style={{
              padding: '6px 12px',
              background:
                selectedPath === item.path ? '#e6f7ff' : 'transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
            onClick={() => {
              setSelectedPath(item.path);
              onItemClick?.(item);
            }}
            onDoubleClick={() => {
              if (item.type === 'directory') {
                setCurrentPath(item.path);
              }
            }}
          >
            <span style={{ marginRight: 8 }}>
              {item.type === 'directory' ? '📁' : '📄'}
            </span>
            <span>{item.name}</span>
          </div>
        ))}
        {files.length === 0 && (
          <div style={{ color: '#888', padding: '12px' }}>暂无文件</div>
        )}
      </div>
    </div>
  );
};

export class FileListWidget extends ReactWidget {
  // private app: JupyterFrontEnd;
  private documentManager: IDocumentManager;
  // private fileBrowserFactory: IFileBrowserFactory;
  private selectedPath: string = '';
  // private files: IFileItem[] = [];
  constructor(
    // app: JupyterFrontEnd,
    // factory: IFileBrowserFactory,
    documentManager: IDocumentManager
  ) {
    super();
    // this.app = app;
    this.documentManager = documentManager;
    // this.fileBrowserFactory = factory;
    this.id = 'project-file-list-widget';
  }
  public getValue(): string {
    return this.selectedPath;
  }
  // protected async onBeforeAttach(msg: Message) {
  //   console.log('-----------beforeAttache:');
  //   const model = new FileBrowserModel({
  //     manager: this.documentManager
  //     // driveName: 'local'
  //   });
  //   await model.cd('/');
  //   (window as any).model = model;
  //   this.files = Array.from(model.items()).map<IFileItem>(item => {
  //     return {
  //       name: item.name,
  //       path: item.path,
  //       type: item.type === 'directory' ? 'directory' : 'file'
  //     };
  //   });
  //   console.log('-----------afterAttache:', this.files);
  // }
  protected render(): React.JSX.Element {
    return (
      <FileList
        documentManager={this.documentManager}
        onItemClick={(item: IFileItem) => {
          console.log(item);
          if (item.type === 'directory') {
            this.selectedPath = '';
            return;
          } else {
            this.selectedPath = item.path;
          }
        }}
      />
    );
  }
}
