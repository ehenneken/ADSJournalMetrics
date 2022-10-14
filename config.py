# ============================= LOGGING ======================================== #
LOGGING_LEVEL = 'INFO'
LOG_STDOUT = False
# ============================= ADS ============================================ #
ADS_API_TOKEN = "<secret>"
ADS_API_URL = "https://ui.adsabs.harvard.edu/v1"
ADS_CITATION_DATA = '/tmp/ADS_citations.tsv'
# ============================= APPLICATION ==================================== #
# 
# Collections we are reporting on (overriding the default)
COLLECTIONS = ['AST']
# Metrics supported
METRICS = ['EIGENFACTOR', 'SNIP', 'JIF']
# The root of the output location
OUTPUT_DIRECTORY = '/tmp/reports'

