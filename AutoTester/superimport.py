import cv2   # @UnresolvedImport
import numpy as np
import math
import time
import os
import sys
import platform
import datetime
import _pickle
import copy
import logging
from logging.handlers import RotatingFileHandler
from Learn import loadModel
import traceback
import django
from django.utils.timezone import activate
from django.utils.dateparse import parse_datetime
import pytz

import rpyc   # @UnresolvedImport
import atexit
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from rpyc.utils.server import ThreadedServer   # @UnresolvedImport
import schedule    # @UnresolvedImport
import requests   # @UnresolvedImport
import shutil
import glob
from skimage.color.rgb_colors import greenyellow
import random
from random import randint

from skimage.feature import hog
from sklearn import svm
from sklearn.externals import joblib
import dlib

import warnings

