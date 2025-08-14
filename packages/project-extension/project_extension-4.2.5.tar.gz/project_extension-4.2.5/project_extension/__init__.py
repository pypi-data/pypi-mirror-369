try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'project_extension' outside a proper installation.")
    __version__ = "dev"
from jupyter_server.serverapp import ServerApp 
from .handlers import setup_handlers
import os
def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "project_extension"
    }]

def _jupyter_server_extension_points():
    return [{
        "module": "project_extension"
    }]

def _load_jupyter_server_extension(nbapp: ServerApp):
     # 获取 page_config_data，如果不存在则初始化
    page_config = nbapp.web_app.settings.setdefault("page_config_data", {})
    # 添加自定义数据
    page_config["project_env_id"] = os.environ.get("PROJECT_ENV_ID")
    page_config["project_id"] = os.environ.get("PROJECT_ID")
    # 你也可以添加更多自定义内容
    setup_handlers(nbapp.web_app)
    name = "myextension"
    nbapp.log.info(f"Registered {name} server extension========")

    # 处理文件 复制模板

    # ~ 
    # mnt 根据 userid projectid
