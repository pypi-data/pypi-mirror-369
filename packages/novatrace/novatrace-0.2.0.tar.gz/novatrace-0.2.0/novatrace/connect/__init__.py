from sqlalchemy import create_engine
from decouple import config as deconfig

from datetime import datetime
import pytz
hora = pytz.utc

#engine a sqlite
engine = create_engine(deconfig("DATABASE_URL", default="sqlite:///connect.db"))

