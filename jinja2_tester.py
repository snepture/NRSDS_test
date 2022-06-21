import argparse

import yaml
from jinja2 import Template
from yaml import Loader
from os import walk


class CustomTemplate():
    def __init__(self,name,raw_data):
        self.name = name
        self.raw_data = raw_data
        self.description = ""
        self.timeout = 10
        self.variables = {}
        self.parse_comments(self.get_comments_part())

    def get_comments_part(self):
        comment = None
        if "'''" in self.raw_data:
            comment = "'''"
        elif '"""' in self.raw_data:
            comment = '"""'
        if comment:
            parts = self.raw_data.split(comment)
            if len(parts)<3:
                return ""
            else:
                return parts[1]

    def parse_comments(self,part):
        try:
            data = yaml.load(part,Loader=Loader)
            self.description = data.get("Description","")
            if data.get("Timeout"):
                if type(data["Timeout"])==int:
                    self.timeout = data["Timeout"]
                else:
                    print(f"Invalid timeout defined in template: {data['Timeout']}")
            if data.get("Variables"):
                if type(data["Variables"])==dict:
                    for key,description in data["Variables"].items():
                        real_key = key.split("(")[0]
                        key_type = key.split("(")[1].split(")")[0]
                        if not self.variables.get(real_key):
                            self.variables[real_key]={}
                        self.variables[real_key]["type"] = key_type
                        self.variables[real_key]["description"] = description
                        self.variables[real_key]["required"] = True
            if data.get("Defaults"):
                if type(data["Defaults"])==dict:
                    for key,default_value in data["Defaults"].items():
                        if not self.variables.get(key):
                            print(f"{key} is not defined, aborting")
                            continue
                        else:
                            self.variables[key]["default"] = default_value
                            self.variables[key]["required"] = False
        except Exception as e:
            print(e)

    def generate_argparser(self):
        parser = argparse.ArgumentParser(description=self.description)
        for k,v in  self.variables.items():
            if v.get("default"):
                parser.add_argument("--"+k,type=eval(v["type"]),help=v["description"],required=v["required"],default=v["default"])
            else:
                parser.add_argument("--"+k,type=eval(v["type"]),help=v["description"],required=v["required"])

        return parser





def open_template(name):
    with open(f"template/{name}.j2") as file:
        data = file.read()
        return data

def open_all_templates():
    template_names = []
    for (dirpath, dirnames, filenames) in walk("template"):
        for file in filenames:
            if file[-3:] ==".j2":
                template_names.append(file.split(".j2")[0])
        break
    # print(template_names)
    templates = []
    for name in template_names:
        data = open_template(name)
        template = CustomTemplate(name,data)
        templates.append(template)
    return templates



if __name__ == '__main__':
    templates = open_all_templates()
    parser = argparse.ArgumentParser("jinja2_tester")
    sub_parsers = parser.add_subparsers(help='sub-command help')
    for template in templates:
        sub_parser = template.generate_argparser()
        sub_parsers.add_parser(template.name,parents=[sub_parser],add_help=False)


    # template_name = "test_command"
    #
    # data = open_template(template_name)
    # temp = CustomTemplate(data)
    args=parser.parse_args()
    print(args)
    print("HI")

