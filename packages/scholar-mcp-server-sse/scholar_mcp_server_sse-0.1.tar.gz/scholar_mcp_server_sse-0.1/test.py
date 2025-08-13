from scholarly import scholarly, ProxyGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pg = ProxyGenerator()

success = pg.SingleProxy(http="http://127.0.0.1:17890", https="http://127.0.0.1:17890")
# success = pg.SingleProxy(http=None, https=None)
if not success:
    logging.warning("Failed to set up proxy.")
    # success = pg.FreeProxies()
    scholarly.use_proxy(pg)

    print("Failed to set up proxy.")
    # success = pg.FreeProxies()
    scholarly.use_proxy(pg)
    
results = scholarly.search_pubs("model based testing")

import json

for i, result in enumerate(results):
    if i >= 1:  # Limit to first 1 results
        break
    print(json.dumps(result, indent=2))