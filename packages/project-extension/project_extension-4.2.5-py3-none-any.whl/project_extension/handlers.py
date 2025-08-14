import os
import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from tornado.web import StaticFileHandler
import shutil
import pdb; 

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    
    def get(self):
        # pdb.set_trace()
        # 获取项目ID

        project_id = os.environ.get('PROJECT_ID', '')

        if not project_id:
            self.set_status(400)
            self.finish(json.dumps({
                "error": "项目ID不能为空"
            }))
            return
            
        # 使用环境变量或默认值设置源目录和基础目标目录
        # default_src_path = os.path.join(os.path.dirname(__file__), '..')
        # self.log.info('default_src_path', {default_src_path})
        # default_dst_path = os.path.join(os.path.expanduser('~'), 'project_templates')
        # self.log.info('default_dst_path', {default_dst_path})
        
        # src_dir1 = os.environ.get('PROJECT_TEMPLATE_SRC', default_src_path)
        # base_dst_dir1 = os.environ.get('PROJECT_TEMPLATE_DST', default_dst_path)
        # self.log.info('src_dir1', {src_dir1})
        # self.log.info('base_dst_dir1', {base_dst_dir1})

        
        # Use raw string for Windows paths to handle backslashes correctly
        #src_dir = r'F:\Project\uustudy\jupyterlab-project-extension\project_extension\labextension'
        # 获取jupyterlab  工作空间
        src_dir = os.environ.get('HOME', os.path.expanduser('~'))
        base_dst_dir = '/mnt/project_templates'

        
        # 使用项目ID创建特定的目标目录
        dst_dir = os.path.join(base_dst_dir, project_id)
        
        self.log.info(f"开始复制项目模板，项目ID: {project_id}")
        self.log.info(f"源目录: {src_dir}")
        self.log.info(f"目标目录: {dst_dir}")
        
        try:
            # 确保目标目录存在
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            else:
                # 如果目标目录已存在，先清空它
                for item in os.listdir(dst_dir):
                    item_path = os.path.join(dst_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            
            # 遍历源目录下的所有内容
            for item in os.listdir(src_dir):
                # 跳过某些不需要复制的目录或文件
                if item in ['.git', '__pycache__', 'node_modules']:
                    continue
                if item.startswith('.'):
                    continue
                    
                s = os.path.join(src_dir, item)
                d = os.path.join(dst_dir, item)
                
                if os.path.isdir(s):
                    # 复制整个目录
                    self.log.info(f"复制目录: {item}")
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    # 复制文件
                    self.log.info(f"复制文件: {item}")
                    shutil.copy2(s, d)
                    
            self.finish(json.dumps({
                "data": f"项目模板已成功保存到 {dst_dir}"
            }))
            
        except PermissionError:
            self.log.error(f"复制文件时权限被拒绝: {dst_dir}")
            self.set_status(403)
            self.finish(json.dumps({
                "error": "复制文件时权限被拒绝"
            }))
        except OSError as e:
            self.log.error(f"复制文件时发生系统错误: {str(e)}")
            self.set_status(500)
            self.finish(json.dumps({
                "error": f"复制文件时发生系统错误: {str(e)}"
            }))
        except Exception as e:
            self.log.error(f"复制文件时发生未知错误: {str(e)}")
            self.set_status(500)
            self.finish(json.dumps({
                "error": f"复制文件时发生未知错误: {str(e)}"
            }))
    # @tornado.web.authenticated
    # def post(self):
    #     # input_data is a dictionary with a key "name"
    #     input_data = self.get_json_body()
    #     data = {"greetings": "Hello {}, enjoy JupyterLab!".format(input_data["name"])}
    #     self.finish(json.dumps(data))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    # Prepend the base_url so that it works in a JupyterHub setting
    route_pattern = url_path_join(base_url, "project_extension", "save")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # # Prepend the base_url so that it works in a JupyterHub setting
    # doc_url = url_path_join(base_url, "myextension", "public")
    # doc_dir = os.getenv(
    #     "JLAB_SERVER_EXAMPLE_STATIC_DIR",
    #     os.path.join(os.path.dirname(__file__), "public"),
    # )
    # handlers = [("{}/(.*)".format(doc_url), StaticFileHandler, {"path": doc_dir})]
    # web_app.add_handlers(host_pattern, handlers)
