import ParseTemplate
import sys
from collections import defaultdict
import yaml

def dictoplain(**kwargs):
    return

LEABA_SDK_PATH = 'haha/usr/lib/cisco/pylib/leaba'
LEABA_VALIDATION_PATH = 'haha/validation_tool/validation-gibraltar-ex-1.53.0.ph2EA3.1'

if __name__ == '__main__':

    # init_pack = f"""
    #                 import sys\n \
    #                 import os\n \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba/..\")\n \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba\")\n   \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba/debug_tools\")\n   \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba/debug_tools/hw_tables/lpm\")\n \
    #                 sys.LEABA_SDK_PATH=\"{LEABA_SDK_PATH}\"\n \
    #                 sys.LEABA_VALIDATION_PATH=\"{LEABA_VALIDATION_PATH}\"\n    \
    #                 sys.path.append(sys.LEABA_VALIDATION_PATH)\n    \
    #                 sys.path.append(sys.LEABA_SDK_PATH)\n   \
    #                 from leaba import sdk\n \
    #                 la_device = sdk.la_get_device(0)\n  \
    #                 from leaba_val import *\n   \
    #                 os.environ['BASE_OUTPUT_DIR'] = \"/opt/cisco/silicon-one/\"\n   \
    #                 set_dev(la_device)\n    \
    #                 from leaba.debug_api import *\n \
    #                 dapi = DebugApi()\n \
    #                 from leaba.dbg import *\n   \
    #                 dbg=dbg_dev(la_device)\n    \
    #                 """
    # print(init_pack)
    # init_pack2 = """
    #                 import sys\n \
    #                 import os\n \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba/..\")\n \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba\")\n   \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba/debug_tools\")\n   \
    #                 sys.path.append(\"/usr/lib/cisco/pylib/leaba/debug_tools/hw_tables/lpm\")\n \
    #                 sys.LEABA_SDK_PATH=\"/usr/lib/cisco/pylib/leaba\"\n \
    #                 sys.LEABA_VALIDATION_PATH=\"/validation_tool/validation-gibraltar-ex-1.53.0.ph2EA3.1\"\n    \
    #                 sys.path.append(sys.LEABA_VALIDATION_PATH)\n    \
    #                 sys.path.append(sys.LEABA_SDK_PATH)\n   \
    #                 from leaba import sdk\n \
    #                 la_device = sdk.la_get_device(0)\n  \
    #                 from leaba_val import *\n   \
    #                 os.environ['BASE_OUTPUT_DIR'] = \"/opt/cisco/silicon-one/\"\n   \
    #                 set_dev(la_device)\n    \
    #                 from leaba.debug_api import *\n \
    #                 dapi = DebugApi()\n \
    #                 from leaba.dbg import *\n   \
    #                 dbg=dbg_dev(la_device)\n    \
    #                 """
    # print(init_pack2)
    data = {
        'default':{
            'LEABA_SDK_PATH': '/usr/lib/cisco/pylib/leaba',
            'LEABA_VALIDATION_PATH': '/usr/lib/cisco/pylib/leaba/debug_tools/hw_tables/lpm'
        }
    }
    # with open('config.yaml','w') as f:
    #     yaml.dump(data, f)

    try:
        f = open('config.yaml','r',encoding='utf-8')
        cont = f.read()
        x = yaml.safe_load(cont).get("default")
        LEABA_SDK_PATH = x.get("LEABA_SDK_PATH")
        LEABA_VALIDATION_PATH = x.get("LEABA_VALIDATION_PATH")
    except Exception:
        print("")



    print(LEABA_SDK_PATH, LEABA_VALIDATION_PATH)
