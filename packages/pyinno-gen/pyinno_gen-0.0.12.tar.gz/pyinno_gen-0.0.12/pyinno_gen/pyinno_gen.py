from jinja2 import Environment, FileSystemLoader,BaseLoader
import logging
from pathlib import Path

"""
innosetup .iss file generator library in python
innosetupt is a tool that used for creating windows installer exe.
there was no way to generate exe file programmatically so i wrote this library in python
this library generates iss file dynamically from jinja2 template.
we give arguments, it willbe added to iss file .and output is returned as string or file

author: github.com/its-me-abi
date : 12/7/2025
 
usage :
    give template file name , also you can give template_path with it or template string
    
    tmp = InnoSetup("template.iss")
    result =  tmp.generate({"MyAppName": "heloapp"})
    print( result )
    
"""
logging.basicConfig(
    filename='inno_setup.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class template_man:
    def __init__(self,name = "",path = ".",template_str="",output="",options = {}):
        self.name = name
        self.path = path
        self.output = output
        self.options = options
        self.context = {}
        self.template_str = template_str
        if self.template_str == "":
            self.env = Environment(loader=FileSystemLoader(self.path),**self.options)
        else:
            self.env = Environment(loader=BaseLoader(), **self.options)

    def set_context(self,context):
        self.context = context

    def generate(self):
        if self.template_str == "":
            logger.info(f"template string is empty")
            template = self.env.get_template(self.name)
        else:
            logger.info(f"template string is not empty ")
            template = self.env.from_string(self.template_str)
        return template.render(self.context)

    def write_to_file(self,args,file=""):
        if not file:
            file = self.output
            if not file:
                logger.error("writing template to file but not provided filepath,unable to write stoping execution")
                return

        with open(file, "w+") as f:
            self.set_context(args)
            data = self.generate()
            f.write(data)
            return True

class InnoSetup:
    """
       generates iss file for  innosetup
       opt varible is used for changing jinjas canry values that used for identifing jinja delimiters, we csan change it
    """
    def __init__(self, template_name="",template_path=".",template_str=""):
        # opt meass delimiters and patterns for replacing
        self.opt = {
                  "block_start_string": "[%",
                  "block_end_string": "%]",
                  "variable_start_string": "[[",
                  "variable_end_string": "]]",
                  "comment_start_string": "[#",
                  "comment_end_string": "#]",
                  }
        if template_name and template_str:
            logger.warn(" template name and template string provided, please input only one")
        elif template_name or template_str:
            pass
        else:
            logger.error("either template name or template string should be provided to template_man ")
        self.template = template_man(template_name, template_path, template_str, options=self.opt)

    def generate(self,args):
        self.template.set_context(args)
        return self.template.generate()

    def write_to_file(self,args,file=""):
        val = self.template.write_to_file(args,file)
        logger.info(f"written to file {file}")
        return val

def generate_iss(args,input_path,output_path):
    file , folder = Path( input_path ).name , str( Path( input_path ).parent )
    obj = InnoSetup(file,folder)
    obj.write_to_file(args,output_path)

if __name__ == "__main__":
    generate_iss({"MyAppName":"TestApp2"},"test/template.iss",output_path = "test/out.txt")