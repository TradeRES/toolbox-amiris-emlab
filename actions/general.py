#-*- coding:utf-8 -*-

__version__ = '0.1.0'
__author__ = 'Benjamin Fuchs, Judith Vesper 20.03.2019'
__status__ = 'dev'  # options are: dev, test, prod

from ioproc.tools import action
from ioproc.logger import mainlogger


@action('general')
def printData(dmgr, config, params):
    '''
    simple debugging printing function. Prints all data in the data manager.

    Does not have any parameters.
    '''
    for k, v in dmgr.items():
        mainlogger.info(k+' = \n'+str(v))


@action('general')
def checkpoint(dmgr, config, params):
    '''
    Creates a checkpoint file in the current working directory with name
    Cache_TAG while TAG is supplied by the action config.

    :param tag: the tag for this checkpoint, this can never be "start"
    '''
    assert params['tag'] != 'start', 'checkpoints can not be named start'
    dmgr.toCache(params['tag'])
    mainlogger.info('set checkpoint "{}"'.format(params['tag']))

