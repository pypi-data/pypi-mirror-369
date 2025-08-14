import { Dialog, showDialog } from '@jupyterlab/apputils';

import { TitleEditWidget } from './titleEditWigdet';
import { IProjectStep } from './type';
// import { JupyterFrontEnd } from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { FileListWidget } from './filelistwigdet';
export function addChapter() {
  return showDialog({
    title: '新增章节', // Can be text or a react element
    body: new TitleEditWidget(), // Can be text, a widget or a react element
    host: document.body, // Parent element for rendering the dialog
    buttons: [
      // List of buttons
      {
        label: '确定', // Button label
        caption: '确定', // Button title
        className: 'my-button', // Additional button CSS class
        accept: true, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '确定',
        actions: [],
        iconClass: '',
        iconLabel: ''
      },
      {
        label: '取消', // Button label
        caption: '取消', // Button title
        className: 'j-project-create-dialog-button', // Additional button CSS class
        accept: false, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '取消',
        actions: [],
        iconClass: '',
        iconLabel: ''
      }
    ],
    defaultButton: 0, // Index of the default button
    focusNodeSelector: '.my-input', // Selector for focussing an input element when dialog opens
    hasClose: true, // Whether to display a close button or not
    renderer: undefined // To define customized dialog structure
  });
}

export function editSubTask(nodeData?: Partial<IProjectStep>) {
  return showDialog({
    title: nodeData?.missionId ? '编辑子任务' : '添加子任务',
    body: new TitleEditWidget(nodeData),
    buttons: [
      // List of buttons
      {
        label: '确定', // Button label
        caption: '确定', // Button title
        className: 'my-button', // Additional button CSS class
        accept: true, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '确定',
        actions: [],
        iconClass: '',
        iconLabel: ''
      },
      {
        label: '取消', // Button label
        caption: '取消', // Button title
        className: 'j-project-create-dialog-button', // Additional button CSS class
        accept: false, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '取消',
        actions: [],
        iconClass: '',
        iconLabel: ''
      }
    ],
    defaultButton: 0, // Index of the default button
    focusNodeSelector: '.my-input', // Selector for focussing an input element when dialog opens
    hasClose: true, // Whether to display a close button or not
    renderer: undefined // To define customized dialog structure
  });
}
export function deleteDialog(nodeData?: Partial<IProjectStep>) {
  return showDialog({
    title: '删除项目步骤',
    body: `确定删除项目步骤：${nodeData?.name}`,
    buttons: [
      // List of buttons
      {
        label: '确定', // Button label
        caption: '确定', // Button title
        className: 'my-button', // Additional button CSS class
        accept: true, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '确定',
        actions: [],
        iconClass: '',
        iconLabel: ''
      }
    ],
    defaultButton: 0, // Index of the default button
    focusNodeSelector: '.my-input', // Selector for focussing an input element when dialog opens
    hasClose: true, // Whether to display a close button or not
    renderer: undefined // To define customized dialog structure
  });
}

export function loginDialog() {
  return showDialog({
    title: '认证失败',
    body: '证失败或已过期，请重新登录!',
    buttons: [
      // List of buttons
      {
        label: '去登录', // Button label
        caption: '去登录', // Button title
        className: 'my-button', // Additional button CSS class
        accept: true, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '去登录',
        actions: [],
        iconClass: '',
        iconLabel: ''
      },
      {
        label: '取消', // Button label
        caption: '取消', // Button title
        className: 'my-button', // Additional button CSS class
        accept: true, // Whether this button will discard or accept the dialog
        displayType: 'default', // applies 'default' or 'warn' styles
        ariaLabel: '取消',
        actions: [],
        iconClass: '',
        iconLabel: ''
      }
    ],
    defaultButton: 0, // Index of the default button
    focusNodeSelector: '.my-input', // Selector for focussing an input element when dialog opens
    hasClose: true, // Whether to display a close button or not
    renderer: undefined // To define customized dialog structure
  });
}

export async function showFileSelectorDialog(
  // app: JupyterFrontEnd,
  // factory: IFileBrowserFactory,
  documentManager: IDocumentManager
  // model: FileBrowserModel
) {
  // 获取文件列表
  // const model = new FileBrowserModel({
  //   manager: documentManager,
  //   driveName: 'local'
  // });
  // await model.cd('/'); // 进入根目录
  // const items = Array.from(model.items()); // 获取文件和文件夹

  return showDialog({
    title: '选择文件',
    body: new FileListWidget(documentManager),
    buttons: [Dialog.cancelButton(), Dialog.okButton({ label: '选择' })]
  });
}
