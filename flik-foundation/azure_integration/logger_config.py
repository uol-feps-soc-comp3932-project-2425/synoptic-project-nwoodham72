""" PROTOTYPE: Azure DevOps Integration: Logger """

"""
    Import logging to track actions in the project.
"""

import logging 

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
