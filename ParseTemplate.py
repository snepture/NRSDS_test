import argparse

import yaml
from jinja2 import Template
from yaml import Loader
from os import walk
from collections import defaultdict


class CustomTemplate:
    def __init__(self, name, raw_data):
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
            if len(parts) < 3:
                return ""
            else:
                return parts[1]

    def parse_comments(self, part):
        try:
            data = yaml.load(part, Loader=Loader)
            self.description = data.get("Description", "")
            if data.get("Timeout"):
                if type(data["Timeout"]) == int:
                    self.timeout = data["Timeout"]
                else:
                    print(f"Invalid timeout defined in template: {data['Timeout']}")
            if data.get("Variables"):
                if type(data["Variables"]) == dict:
                    for key, description in data["Variables"].items():
                        real_key = key.split("(")[0]
                        key_type = key.split("(")[1].split(")")[0]
                        if not self.variables.get(real_key):
                            self.variables[real_key] = {}
                        self.variables[real_key]["type"] = key_type
                        self.variables[real_key]["description"] = description
                        self.variables[real_key]["required"] = True
            if data.get("Defaults"):
                if type(data["Defaults"]) == dict:
                    for key, default_value in data["Defaults"].items():
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
        parser.add_argument("--settimeout", type=int, help="Set timeout for template, range(1,99)")

        for k, v in self.variables.items():
            if v.get("default"):
                parser.add_argument("--" + k, type=eval(v["type"]), help=v["description"], required=v["required"],
                                    default=v["default"])
            else:
                parser.add_argument("--" + k, type=eval(v["type"]), help=v["description"], required=v["required"])

        return parser


class OperateTemplate:
    def __init__(self):
        pass

    def open_template(self, name):
        with open(f"template/{name}.j2") as file:
            data = file.read()
            return data

    def open_all_templates(self):
        template_names = []
        for (dirpath, dirnames, filenames) in walk("template"):
            for file in filenames:
                if file[-3:] == ".j2":
                    template_names.append(file.split(".j2")[0])
            break
        # print(template_names)
        templates = []
        for name in template_names:
            data = self.open_template(name)
            template = CustomTemplate(name, data)
            templates.append(template)
        return templates

    def set_timeout(self, args, name):
        if args.settimeout and 0 < args.settimeout < 100:
            content_add = str(args.settimeout)
            if len(content_add) < 2:
                content_add += " "
            content = self.open_template(name)
            pos = content.find("Timeout: ")
            if pos != -1:
                content = content[:pos+9] + content_add + content[pos + 11:]
                file = open(f"template/{name}.j2", "w")
                file.write(content)
                file.close()
                return True
            else:
                print("Template format wrong, failed to write.")
                return False
        else:
            return False

    def generate_command(self, name):
        templates = self.open_all_templates()
        parser = argparse.ArgumentParser("Non_Reside_SDS")
        sub_parsers = parser.add_subparsers(help='Please choose one from the commands here.')
        target = None
        tinydict = defaultdict(str)
        for template in templates:
            sub_parser = template.generate_argparser()
            sub_parsers.add_parser(template.name, parents=[sub_parser], add_help=False)
            if template.name == name:
                target = template

        args = parser.parse_args()
        if self.set_timeout(args, name):
            target.timeout = args.settimeout
        command_template = Template(self.open_template(name))

        for k, v in target.variables.items():
            if k not in vars(args):
                if v.get("default"):
                    tinydict[k] = v["default"]
                else:
                    tinydict[k] = None
            else:
                tinydict[k] = vars(args)[k]

        command = command_template.render(**tinydict)
        final_command = command.split('"""')[2].strip() + '\n'
        return final_command, target.timeout
