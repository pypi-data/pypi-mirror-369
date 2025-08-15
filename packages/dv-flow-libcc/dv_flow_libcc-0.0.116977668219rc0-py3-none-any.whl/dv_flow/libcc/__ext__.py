
import os

def dvfm_packages():
    cc_dir = os.path.dirname(os.path.abspath(__file__))

    return {
        'cc': os.path.join(cc_dir, "flow.dv"),
    }