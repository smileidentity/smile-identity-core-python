from .TestAuthentication import TestAuthentication
from .TestEnrollWithIDCard import TestEnrollWithIDCard
from .TestEnrollWithIDInfo import TestEnrollWithIDInfo
from .TestIDValidation import TestIDValidation
from .TestUpdatePhoto import TestUpdatePhoto
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
api_key = u"""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnlG24VNQIbD8LMmHRwHsQWzO1
                           q1b+ymJDyiVrpch+av9ermS/njWzo1wpUg7jOX5vc7utF/nJCmekUDr4vXPz1dfX
                           HDnyYtBnlleBTtYKwipwLzDj0PO7aGX7rz/ebkHcS/PdlP+prLFw584qcesnq4rQ
                           n64nLz7y0BE/RCDQAwIDAQAB"""
