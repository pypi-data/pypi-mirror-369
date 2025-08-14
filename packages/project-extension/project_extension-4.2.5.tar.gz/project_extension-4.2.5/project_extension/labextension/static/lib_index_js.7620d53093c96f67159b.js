"use strict";
(self["webpackChunkproject_extension"] = self["webpackChunkproject_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/dialog.js":
/*!***********************!*\
  !*** ./lib/dialog.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   addChapter: () => (/* binding */ addChapter),
/* harmony export */   deleteDialog: () => (/* binding */ deleteDialog),
/* harmony export */   editSubTask: () => (/* binding */ editSubTask),
/* harmony export */   loginDialog: () => (/* binding */ loginDialog),
/* harmony export */   showFileSelectorDialog: () => (/* binding */ showFileSelectorDialog)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _titleEditWigdet__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./titleEditWigdet */ "./lib/titleEditWigdet.js");
/* harmony import */ var _filelistwigdet__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./filelistwigdet */ "./lib/filelistwigdet.js");



function addChapter() {
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
        title: '新增章节', // Can be text or a react element
        body: new _titleEditWigdet__WEBPACK_IMPORTED_MODULE_1__.TitleEditWidget(), // Can be text, a widget or a react element
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
function editSubTask(nodeData) {
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
        title: (nodeData === null || nodeData === void 0 ? void 0 : nodeData.missionId) ? '编辑子任务' : '添加子任务',
        body: new _titleEditWigdet__WEBPACK_IMPORTED_MODULE_1__.TitleEditWidget(nodeData),
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
function deleteDialog(nodeData) {
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
        title: '删除项目步骤',
        body: `确定删除项目步骤：${nodeData === null || nodeData === void 0 ? void 0 : nodeData.name}`,
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
function loginDialog() {
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
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
async function showFileSelectorDialog(
// app: JupyterFrontEnd,
// factory: IFileBrowserFactory,
documentManager
// model: FileBrowserModel
) {
    // 获取文件列表
    // const model = new FileBrowserModel({
    //   manager: documentManager,
    //   driveName: 'local'
    // });
    // await model.cd('/'); // 进入根目录
    // const items = Array.from(model.items()); // 获取文件和文件夹
    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
        title: '选择文件',
        body: new _filelistwigdet__WEBPACK_IMPORTED_MODULE_2__.FileListWidget(documentManager),
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.cancelButton(), _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: '选择' })]
    });
}


/***/ }),

/***/ "./lib/directoryNode.js":
/*!******************************!*\
  !*** ./lib/directoryNode.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DirectoryNode: () => (/* binding */ DirectoryNode)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);


function DirectoryNode({ node, app, onNodeClick, onAddBelow, onEditName, onDelete, onLink }) {
    const [expanded, setExpanded] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(true);
    const [currentNode, setCurrentNode] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)('');
    const [hovered, setHovered] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const hasChildren = node.children && node.children.length > 0;
    const isChapter = node.isChapter;
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: { marginLeft: 16 } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: ['j-chapter', node.id === currentNode ? 'current' : ''].join(' '), style: {
                fontWeight: node.isChapter ? 'bold' : 'normal',
                fontSize: node.isChapter ? '14px' : '14px'
            }, onClick: () => {
                if (node.path) {
                    setCurrentNode(node.id);
                    onNodeClick(node);
                }
                if (hasChildren) {
                    setExpanded(e => !e);
                }
            }, onMouseEnter: () => setHovered(true), onMouseLeave: () => setHovered(false) },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: {
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'start',
                    alignItems: 'center'
                } },
                !isChapter ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.circleIcon, className: "jp-project-node-mini-icon" })) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: {
                        display: 'flex',
                        flexDirection: 'row',
                        width: 30,
                        height: 30
                    } }, hasChildren && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { style: { marginRight: 4 } }, expanded ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.caretDownEmptyIcon, className: "jp-project-node-icon" })) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.caretDownEmptyIcon, className: "jp-project-node-icon rotate-90" })))))),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null,
                    " ",
                    node.name,
                    " ")),
            hovered && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: {
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'flex-end',
                    alignItems: 'center'
                } },
                !isChapter && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { onClick: e => {
                        e.stopPropagation();
                        console.log('link');
                        onLink(node);
                    } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.linkIcon, className: "jp-project-node-icon" }))),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { onClick: e => {
                        e.stopPropagation();
                        console.log('editname');
                        onEditName(node);
                    } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.editIcon, className: "jp-project-node-icon" })),
                isChapter && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { onClick: e => {
                        e.stopPropagation();
                        console.log('click');
                        onAddBelow(node);
                    } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.addBelowIcon, className: "jp-project-node-icon" }))),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { onClick: e => {
                        e.stopPropagation();
                        console.log('click');
                        onDelete(node);
                    } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.deleteIcon, className: "jp-project-node-icon" }))))),
        hasChildren && expanded && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null, node.children.map(child => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(DirectoryNode, { key: child.id, app: app, node: child, onNodeClick: onNodeClick, onAddBelow: onAddBelow, onEditName: onEditName, onDelete: onDelete, onLink: onLink })))))));
}


/***/ }),

/***/ "./lib/filelistwigdet.js":
/*!*******************************!*\
  !*** ./lib/filelistwigdet.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   FileList: () => (/* binding */ FileList),
/* harmony export */   FileListWidget: () => (/* binding */ FileListWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2__);
// import { JupyterFrontEnd } from '@jupyterlab/application';



const FileList = ({ documentManager, 
// files,
onItemClick }) => {
    const [files, setFiles] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [currentPath, setCurrentPath] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)('/');
    const [selectedPath, setSelectedPath] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)('');
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        const model = new _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2__.FileBrowserModel({
            manager: documentManager
        });
        model.cd(currentPath).then(() => {
            setFiles(Array.from(model.items())
                .map(item => {
                return {
                    name: item.name,
                    path: item.path,
                    type: item.type === 'directory' ? 'directory' : 'file'
                };
            })
                .filter(item => {
                return (item.type === 'directory' ||
                    item.path.endsWith('.ipynb') ||
                    item.path.endsWith('.md') ||
                    item.path.endsWith('.py') ||
                    item.path.endsWith('.txt') ||
                    item.path.endsWith('.js') ||
                    item.path.endsWith('.css') ||
                    item.path.endsWith('.yml') ||
                    item.path.endsWith('.yaml') ||
                    item.path.endsWith('.xml') ||
                    item.path.endsWith('.csv'));
            })
                .sort((a, b) => {
                if (a.type !== b.type) {
                    return a.type === 'directory' ? -1 : 1;
                }
                return a.name.localeCompare(b.name);
            }));
        });
    }, [documentManager, currentPath]);
    // 生成面包屑
    const pathParts = currentPath === '/' ? [''] : currentPath.split('/').filter(Boolean);
    const breadcrumbItems = [
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { key: "root", style: {
                cursor: currentPath !== '/' ? 'pointer' : 'default',
                color: currentPath !== '/' ? '#1890ff' : undefined
            }, onClick: () => currentPath !== '/' && setCurrentPath('/') }, "\u6839\u76EE\u5F55")
    ];
    let pathAcc = '';
    pathParts.forEach((part, idx) => {
        pathAcc += '/' + part;
        breadcrumbItems.push(react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { key: `sep-${idx}` }, " / "), react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { key: pathAcc, style: {
                cursor: idx !== pathParts.length - 1 ? 'pointer' : 'default',
                color: idx !== pathParts.length - 1 ? '#1890ff' : undefined
            }, onClick: () => {
                if (idx !== pathParts.length - 1) {
                    setCurrentPath(pathAcc);
                }
            } }, part));
    });
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-filelist-widget" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-filelist-widget-breadcrumbs" }, breadcrumbItems),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-filelist-widget-list-container" },
            files.map(item => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { key: item.path, style: {
                    padding: '6px 12px',
                    background: selectedPath === item.path ? '#e6f7ff' : 'transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center'
                }, onClick: () => {
                    setSelectedPath(item.path);
                    onItemClick === null || onItemClick === void 0 ? void 0 : onItemClick(item);
                }, onDoubleClick: () => {
                    if (item.type === 'directory') {
                        setCurrentPath(item.path);
                    }
                } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { style: { marginRight: 8 } }, item.type === 'directory' ? '📁' : '📄'),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, item.name)))),
            files.length === 0 && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: { color: '#888', padding: '12px' } }, "\u6682\u65E0\u6587\u4EF6")))));
};
class FileListWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    // private files: IFileItem[] = [];
    constructor(
    // app: JupyterFrontEnd,
    // factory: IFileBrowserFactory,
    documentManager) {
        super();
        // private fileBrowserFactory: IFileBrowserFactory;
        this.selectedPath = '';
        // this.app = app;
        this.documentManager = documentManager;
        // this.fileBrowserFactory = factory;
        this.id = 'project-file-list-widget';
    }
    getValue() {
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
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(FileList, { documentManager: this.documentManager, onItemClick: (item) => {
                console.log(item);
                if (item.type === 'directory') {
                    this.selectedPath = '';
                    return;
                }
                else {
                    this.selectedPath = item.path;
                }
            } }));
    }
}


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'project_extension', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _projectSidebarWidget__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./projectSidebarWidget */ "./lib/projectSidebarWidget.js");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0__);

// import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

const PROJECT_EXTENSION_ID = 'project_extension:plugin';
/**
 * Initialization data for the project_extension extension.
 */
const plugin = {
    id: PROJECT_EXTENSION_ID,
    description: '项目步骤',
    autoStart: true,
    requires: [_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0__.IDocumentManager],
    activate: (app, documentManager) => {
        // console.log('JupyterLab extension poject_extension is activated!');
        const { commands } = app;
        const sidebarWidget = new _projectSidebarWidget__WEBPACK_IMPORTED_MODULE_1__["default"](app, documentManager);
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
            execute: (args) => {
                const path = args['path'];
                if (!path) {
                    console.error('No file path specified');
                    return;
                }
                commands.execute('docmanager:open', { path });
            }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/projectSidebarWidget.js":
/*!*************************************!*\
  !*** ./lib/projectSidebarWidget.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ProjectSidebarWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _sdk__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./sdk */ "./lib/sdk.js");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _dialog__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./dialog */ "./lib/dialog.js");
/* harmony import */ var _directoryNode__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./directoryNode */ "./lib/directoryNode.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");






// import { IFileBrowserFactory } from '@jupyterlab/filebrowser';


function ProjectSidebarContent({ projectId, app, documentManager, onSaveChapter }) {
    // 使用 useState 管理步骤
    const [steps, setSteps] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)([]);
    const [loading, setLoading] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(true);
    // 初始化时通过接口加载数据
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.getProjectMissions)(projectId).then(data => {
            setSteps(data);
            setLoading(false);
        });
    }, []);
    const handleNodeClick = (node) => {
        if (node.path && app.commands) {
            console.log('---open::', node.path);
            app.commands.execute('docmanager:open', {
                path: node.path
            });
        }
    };
    const linkHandler = (nodeData) => {
        (0,_dialog__WEBPACK_IMPORTED_MODULE_5__.showFileSelectorDialog)(documentManager).then(res => {
            if (res.button.label === '选择') {
                const path = res.value;
                console.log('---linkL:', res);
                (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.updateMissionFile)({
                    missionId: nodeData.id,
                    path
                }).then(() => {
                    (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.getProjectMissions)(projectId).then(data => {
                        setSteps(data);
                        setLoading(false);
                    });
                });
            }
        });
    };
    const deleteTask = (nodeData) => {
        (0,_dialog__WEBPACK_IMPORTED_MODULE_5__.deleteDialog)(nodeData).then(() => {
            (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.deleteProjectMission)(nodeData.id).then(() => {
                (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.getProjectMissions)(projectId).then(data => {
                    setSteps(data);
                    setLoading(false);
                });
            });
        });
    };
    const showEditTaskDialog = (nodeData) => {
        (0,_dialog__WEBPACK_IMPORTED_MODULE_5__.editSubTask)(nodeData).then(({ button, value }) => {
            var _a;
            console.log('showEditTaskDialog:', value);
            if (!value) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.showErrorMessage)('错误', '输入内容为空');
                return;
            }
            if (button.label === '确定') {
                (_a = (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.updateProjectMission)(projectId, value)) === null || _a === void 0 ? void 0 : _a.then(() => {
                    (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.getProjectMissions)(projectId).then(data => {
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
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.showErrorMessage)('错误', '项目不存在');
            return;
        }
        (0,_dialog__WEBPACK_IMPORTED_MODULE_5__.addChapter)().then(({ value }) => {
            var _a;
            if (!value) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.showErrorMessage)('错误', '输入内容为空');
                return;
            }
            (_a = (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.updateProjectMission)(projectId, value)) === null || _a === void 0 ? void 0 : _a.then(() => {
                (0,_sdk__WEBPACK_IMPORTED_MODULE_4__.getProjectMissions)(projectId).then(data => {
                    setSteps(data);
                    setLoading(false);
                });
            });
        });
    };
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: {
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'flex-end',
                padding: '0px 10px',
                backgroundColor: '#f5f5f5',
                borderBottom: '1px solid #ddd'
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("button", { className: "jp-ToolbarButton jp-mod-styled flex-center", onClick: showEditChapterDialog },
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.newFolderIcon, className: "flex-center" }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: { marginLeft: '5px' } }, "\u65B0\u5EFA\u7AE0\u8282")),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("button", { className: "jp-ToolbarButton jp-mod-styled flex-center", onClick: onSaveChapter },
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon.resolveReact, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.newFolderIcon, className: "flex-center" }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: { marginLeft: '5px' } }, "\u4FDD\u5B58"))),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "sidebar-content" }, loading ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", null, "\u52A0\u8F7D\u4E2D...")) : (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null, steps.length > 0 ? (steps.map(node => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_directoryNode__WEBPACK_IMPORTED_MODULE_6__.DirectoryNode, { key: node.id, app: app, node: node, onNodeClick: handleNodeClick, onEditName: node => {
                showEditTaskDialog(node);
            }, onDelete: node => {
                deleteTask(node);
            }, onLink: node => {
                linkHandler(node);
            }, onAddBelow: node => {
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
            } })))) : (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "j-project-empty-container" },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "j-project-empty-text" }, "\u6682\u65E0\u5185\u5BB9"),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("button", { className: "j-project-create-button", onClick: () => showEditChapterDialog() }, "\u65B0\u5EFA\u7AE0\u8282"))))))));
}
class ProjectSidebarWidget extends _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(app, documentManager) {
        super();
        this.id = 'project-sidebar';
        this.addClass('project-sidebar-widget');
        this.title.closable = true;
        this.title.iconLabel = '项目步骤';
        this.title.caption = '打开项目步骤';
        this.app = app;
        this.documentManager = documentManager;
        this.projectId = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getOption('project_id');
        window.PageConfig = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig;
        // Extend the Window interface to allow 'factory'
    }
    onSaveChapter() {
        console.log('onSaveChapter');
        (0,_handler__WEBPACK_IMPORTED_MODULE_7__.requestAPI)('save')
            .then(data => {
            console.log(data);
        })
            .catch(reason => {
            console.error(`The project_extension server extension appears to be missing.\n${reason}`);
        });
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(ProjectSidebarContent, { app: this.app, projectId: this.projectId, documentManager: this.documentManager, onSaveChapter: this.onSaveChapter }));
    }
}


/***/ }),

/***/ "./lib/sdk.js":
/*!********************!*\
  !*** ./lib/sdk.js ***!
  \********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   deleteProjectMission: () => (/* binding */ deleteProjectMission),
/* harmony export */   getProjectMissions: () => (/* binding */ getProjectMissions),
/* harmony export */   updateMissionFile: () => (/* binding */ updateMissionFile),
/* harmony export */   updateProjectMission: () => (/* binding */ updateProjectMission)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ "webpack/sharing/consume/default/axios/axios");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _util__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./util */ "./lib/util.js");
/* harmony import */ var _dialog__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./dialog */ "./lib/dialog.js");



const apiUrl = '/poros/api';
const axios = axios__WEBPACK_IMPORTED_MODULE_0___default().create({});
axios.interceptors.request.use(config => {
    if (localStorage.getItem('sp-token')) {
        config.headers.Authorization = `Bearer ${localStorage.getItem('sp-token')}`;
    }
    console.log('---request', config);
    return config;
});
axios.interceptors.response.use(res => {
    console.log('---response', res);
    return res;
}, error => {
    var _a;
    console.log('---error', error);
    const status = (_a = error === null || error === void 0 ? void 0 : error.response) === null || _a === void 0 ? void 0 : _a.status;
    switch (status) {
        case 401:
            // console.warn('未授权，请重新登录');
            // window.location.href = '/login';
            // 可触发登出逻辑
            (0,_dialog__WEBPACK_IMPORTED_MODULE_1__.loginDialog)().then((value) => {
                console.log(value);
                console.log(' authurl', (0,_util__WEBPACK_IMPORTED_MODULE_2__.getAuthUrl)());
                if (value.button.label === '去登录') {
                    window.location.href = (0,_util__WEBPACK_IMPORTED_MODULE_2__.getAuthUrl)();
                }
            });
            break;
        case 404:
            console.warn('请求资源不存在');
            break;
        case 500:
            console.error('服务器内部错误');
            break;
        default:
            console.warn('网络异常，请稍后再试');
    }
    return Promise.reject(error);
});
/**
 * 根据 项目ID 获取项目指导
 * @param projectId
 * @returns
 */
const getProjectMissions = (projectId) => {
    return axios
        .get(`${apiUrl}/projects/${projectId}/jupyter`)
        .then((res) => {
        console.log('---getProject Missions', res);
        return (0,_util__WEBPACK_IMPORTED_MODULE_2__.parseProjectRes)(res.data.data);
    });
};
const updateProjectMission = (projectId, data) => {
    if (!data.id) {
        return axios
            .post(`${apiUrl}/project_missions/`, {
            name: data.name,
            projectId,
            parentId: data.parentId
        })
            .then((res) => {
            console.log('---createProjectMission', res);
            return res.data.data;
        });
    }
    else {
        console.log('---updateProjectMission', data);
        return axios
            .patch(`${apiUrl}/project_missions/${data.id}`, {
            ...data
        })
            .then((res) => {
            console.log('---updateProjectMission', res);
            return res.data.data;
        });
    }
};
const updateMissionFile = (data) => {
    return axios.post(`${apiUrl}/jupyters`, {
        missionId: data.missionId,
        path: data.path
    });
};
const deleteProjectMission = (missionId) => {
    return axios
        .delete(`${apiUrl}/project_missions/${missionId}`)
        .then((res) => {
        console.log('---deleteProjectMission', res);
        return res.data.data;
    });
};


/***/ }),

/***/ "./lib/titleEditWigdet.js":
/*!********************************!*\
  !*** ./lib/titleEditWigdet.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TitleEditWidget: () => (/* binding */ TitleEditWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);


const TitleWidget = ({ nodeData, valueChange }) => {
    const [title, setTitle] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(nodeData === null || nodeData === void 0 ? void 0 : nodeData.title);
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("input", { value: title, onChange: e => {
                setTitle(e.target.value);
                valueChange && valueChange(e.target.value);
            } })));
};
class TitleEditWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(nodeData) {
        super();
        this.id = 'project-title-edit-widget';
        // this.addClass('project-sidebar-widget');
        // this.title.closable = true;
        // this.title.iconLabel = '项目步骤';
        // this.title.caption = '打开项目步骤';
        // this.commands = commands;
        this.nodeData = nodeData
            ? {
                ...nodeData
            }
            : { name: '', title: '' };
    }
    getValue() {
        return this.nodeData;
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(TitleWidget, { nodeData: this.nodeData, valueChange: value => {
                this.nodeData.name = value;
                this.nodeData.title = value;
            } }));
    }
}


/***/ }),

/***/ "./lib/util.js":
/*!*********************!*\
  !*** ./lib/util.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   getAuthUrl: () => (/* binding */ getAuthUrl),
/* harmony export */   parseProjectRes: () => (/* binding */ parseProjectRes)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);

// import { PointerIcon } from './pointerIcon';
function parseStep(data, mission) {
    var _a, _b, _c;
    const file = (_a = data.jupyterList) === null || _a === void 0 ? void 0 : _a.find((f) => f.missionId === mission.id);
    const progressItem = (_b = data.progressList) === null || _b === void 0 ? void 0 : _b.find((p) => p.missionId === mission.id);
    return {
        id: mission.id,
        key: mission.id,
        name: mission.name,
        title: mission.name,
        description: mission.description,
        path: file === null || file === void 0 ? void 0 : file.path,
        progress: progressItem === null || progressItem === void 0 ? void 0 : progressItem.progress_percentage,
        missionId: mission.id,
        parentId: mission.parentId,
        isChapter: !mission.parentId,
        children: ((_c = data.missions
            .filter((item) => item.parentId === mission.id)) === null || _c === void 0 ? void 0 : _c.map((item) => parseStep(data, item))) || []
    };
}
function parseProjectRes(data) {
    const steps = [];
    const missions = data.missions;
    if (missions && missions.length) {
        missions
            .filter((item) => !item.parentId)
            .forEach((mission) => {
            const step = parseStep(data, mission);
            steps.push(step);
        });
        return steps;
    }
    else {
        return [];
    }
}
function getAuthUrl() {
    const envConfig = JSON.parse(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getOption('env') || '{}');
    console.log('Environment Config:', envConfig);
    const auth_url = envConfig['AUTH_URL'] || '';
    return auth_url;
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.7620d53093c96f67159b.js.map