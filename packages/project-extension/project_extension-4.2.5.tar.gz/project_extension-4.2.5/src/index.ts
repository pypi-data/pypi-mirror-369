import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import ProjectSidebarWidget from './projectSidebarWidget';
// import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IDocumentManager } from '@jupyterlab/docmanager';
const PROJECT_EXTENSION_ID = 'project_extension:plugin';

/**
 * Initialization data for the project_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PROJECT_EXTENSION_ID,
  description: '项目步骤',
  autoStart: true,
  requires: [IDocumentManager],
  activate: (app: JupyterFrontEnd, documentManager: IDocumentManager) => {
    // console.log('JupyterLab extension poject_extension is activated!');
    const { commands } = app;
    const sidebarWidget = new ProjectSidebarWidget(app, documentManager);
    // const command = OPEN_COMMAND;
    app.shell.add(sidebarWidget, 'left', { rank: 10, activate: true });
    console.log('Project sidebar widget added to the application shell.');

    app.restored.then(() => {
      console.log('JupyterLab application restored.');
      // 默认展开
      app.shell.activateById(sidebarWidget.id);
    });

    // 从环境变量中获取 project_id
    // const settings = ServerConnection.makeSettings();
    // console.log(settings);
    // const envConfig = JSON.parse(PageConfig.getOption('env') || '{}');
    // console.log('Environment Config:', envConfig);
    // const project_id = envConfig['PROJECT_ID'] || '';
    // console.log('Project ID:', project_id);
    // console.log(localStorage.getItem('sp-token'));
    // 获取默认文件浏览器实例
    //注册打开文件命令
    const command = 'project-sidebar:open-file';
    commands.addCommand(command, {
      label: '打开文件',
      caption: '打开文件',
      execute: (args: any) => {
        const path = args['path'] as string;
        if (!path) {
          console.error('No file path specified');
          return;
        }
        commands.execute('docmanager:open', { path });
      }
    });
  }
};

export default plugin;
