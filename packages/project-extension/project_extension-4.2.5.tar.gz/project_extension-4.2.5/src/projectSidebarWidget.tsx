import { LabIcon, ReactWidget, newFolderIcon } from '@jupyterlab/ui-components';
import React, { useState, useEffect } from 'react';

import { showErrorMessage } from '@jupyterlab/apputils';
import { IProjectStep } from './type';
import {
  deleteProjectMission,
  getProjectMissions,
  updateMissionFile,
  updateProjectMission
} from './sdk';
import { PageConfig } from '@jupyterlab/coreutils';
import {
  addChapter,
  deleteDialog,
  editSubTask,
  showFileSelectorDialog
} from './dialog';
// import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { DirectoryNode } from './directoryNode';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { requestAPI } from './handler';
// eslint-disable-next-line @typescript-eslint/naming-convention
interface ProjectSidebarContentProps {
  projectId: string;
  app: JupyterFrontEnd;
  documentManager: IDocumentManager;
  onSaveChapter: () => void;
}

function ProjectSidebarContent({
  projectId,
  app,
  documentManager,
  onSaveChapter
}: ProjectSidebarContentProps) {
  // 使用 useState 管理步骤
  const [steps, setSteps] = useState<IProjectStep[]>([]);
  const [loading, setLoading] = useState(true);
  // 初始化时通过接口加载数据
  useEffect(() => {
    getProjectMissions(projectId).then(data => {
      setSteps(data);
      setLoading(false);
    });
  }, []);
  const handleNodeClick = (node: IProjectStep) => {
    if (node.path && app.commands) {
      console.log('---open::', node.path);
      app.commands.execute('docmanager:open', {
        path: node.path
      });
    }
  };
  const linkHandler = (nodeData: IProjectStep) => {
    showFileSelectorDialog(documentManager).then(res => {
      if (res.button.label === '选择') {
        const path = res.value;
        console.log('---linkL:', res);
        updateMissionFile({
          missionId: nodeData.id,
          path
        }).then(() => {
          getProjectMissions(projectId).then(data => {
            setSteps(data);
            setLoading(false);
          });
        });
      }
    });
  };
  const deleteTask = (nodeData: IProjectStep) => {
    deleteDialog(nodeData).then(() => {
      deleteProjectMission(nodeData.id).then(() => {
        getProjectMissions(projectId).then(data => {
          setSteps(data);
          setLoading(false);
        });
      });
    });
  };
  const showEditTaskDialog = (nodeData?: IProjectStep) => {
    editSubTask(nodeData).then(({ button, value }: any) => {
      console.log('showEditTaskDialog:', value);
      if (!value) {
        showErrorMessage('错误', '输入内容为空');
        return;
      }
      if (button.label === '确定') {
        updateProjectMission(projectId, value)?.then(() => {
          getProjectMissions(projectId).then(data => {
            setSteps(data);
            setLoading(false);
          });
        });
      }
    });
  };
  const showEditChapterDialog = () => {
    console.log('showDialog');
    if (!projectId) {
      showErrorMessage('错误', '项目不存在');
      return;
    }
    addChapter().then(({ value }: any) => {
      if (!value) {
        showErrorMessage('错误', '输入内容为空');
        return;
      }
      updateProjectMission(projectId, value)?.then(() => {
        getProjectMissions(projectId).then(data => {
          setSteps(data);
          setLoading(false);
        });
      });
    });
  };
  return (
    <>
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'flex-end',
          padding: '0px 10px',
          backgroundColor: '#f5f5f5',
          borderBottom: '1px solid #ddd'
        }}
      >
        <button
          className="jp-ToolbarButton jp-mod-styled flex-center"
          onClick={showEditChapterDialog}
        >
          <LabIcon.resolveReact icon={newFolderIcon} className="flex-center" />
          <div style={{ marginLeft: '5px' }}>新建章节</div>
        </button>
        <button
          className="jp-ToolbarButton jp-mod-styled flex-center"
          onClick={onSaveChapter}
        >
          <LabIcon.resolveReact icon={newFolderIcon} className="flex-center" />
          <div style={{ marginLeft: '5px' }}>保存</div>
        </button>
      </div>
      <div className="sidebar-content">
        {loading ? (
          <div>加载中...</div>
        ) : (
          <>
            {steps.length > 0 ? (
              steps.map(node => (
                <DirectoryNode
                  key={node.id}
                  app={app}
                  node={node}
                  onNodeClick={handleNodeClick}
                  onEditName={node => {
                    showEditTaskDialog(node);
                  }}
                  onDelete={node => {
                    deleteTask(node);
                  }}
                  onLink={node => {
                    linkHandler(node);
                  }}
                  onAddBelow={node => {
                    showEditTaskDialog({
                      id: '',
                      key: '',
                      name: '',
                      parentId: node.id,
                      missionId: '',
                      title: '',
                      description: '',
                      path: '',
                      isChapter: false,
                      progress: 0,
                      children: []
                    });
                  }}
                />
              ))
            ) : (
              <div className="j-project-empty-container">
                <div className="j-project-empty-text">暂无内容</div>
                <button
                  className="j-project-create-button"
                  onClick={() => showEditChapterDialog()}
                >
                  新建章节
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}

export default class ProjectSidebarWidget extends ReactWidget {
  private projectId: string;
  private app: JupyterFrontEnd;
  private documentManager: IDocumentManager;
  constructor(app: JupyterFrontEnd, documentManager: IDocumentManager) {
    super();
    this.id = 'project-sidebar';
    this.addClass('project-sidebar-widget');
    this.title.closable = true;
    this.title.iconLabel = '项目步骤';
    this.title.caption = '打开项目步骤';
    this.app = app;
    this.documentManager = documentManager;
    this.projectId = PageConfig.getOption('project_id');
    (window as any).PageConfig = PageConfig;
    // Extend the Window interface to allow 'factory'
  }
  onSaveChapter(): void {
    console.log('onSaveChapter');
    requestAPI<any>('save')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The project_extension server extension appears to be missing.\n${reason}`
        );
      });
  }
  protected render(): React.JSX.Element {
    return (
      <ProjectSidebarContent
        app={this.app}
        projectId={this.projectId}
        documentManager={this.documentManager}
        onSaveChapter={this.onSaveChapter}
      />
    );
  }
}
