#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import os

from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Starting Datatailr app...")
    entrypoint = os.environ.get("DATATAILR_ENTRYPOINT")

    if entrypoint is None:
        raise ValueError("Environment variable 'DATATAILR_ENTRYPOINT' is not set.")

    os.system(entrypoint)
    logger.info(f"Running entrypoint: {entrypoint}")
