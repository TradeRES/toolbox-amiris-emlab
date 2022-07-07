from domain.energy import *
from domain.actors import *
from domain.reps import *
from util.repository import Repository
from spinedb import *


import pandas as pd


db_url_amiris = sys.argv[1]
db_amiris = SpineDB(db_url_amiris)

def addCoststoCandidatePowerPlants(db_amiris):
    """
    This function adds investment costs to candidate power plants
    :param db_amiris: SpineDB
    """



def addCashFlowtoCandidatePowerPlants(db_amiris):
    """
    This function adds cash and loans to Candidate power plants
    :param
    """






if __name__ == "__main__":
    print('===== Starting Initialization script =====')
    initializePowerPlants()
    addCoststoCandidatePowerPlants()
    print('===== End of Initialization script =====')