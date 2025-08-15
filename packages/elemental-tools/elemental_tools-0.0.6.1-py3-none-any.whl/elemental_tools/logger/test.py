from elemental_tools.logger import Logger

logger = Logger('log', 'me')

for e in range(10):
	logger.log('info', 'test message')
