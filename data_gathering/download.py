from landsat import downloader as d
from landsat import search as s
import json as j
import definitions

class Downloader:

    def __init__(self):

        self.searcher = s.Search()
        self.downloader = d.Downloader()

    def search(self) -> str:
        """Returns a json dumps string containing the results of landsat search."""

        result = self.searcher.search(paths_rows=str(definitions.DEFAULT_PATH) + ',' + str(definitions.DEFAULT_ROW),
                                      cloud_max=definitions.DEFAULT_CLOUD_COVERAGE,
                                      start_date=definitions.DEFAULT_START_DATE,
                                      end_date=definitions.DEFAULT_END_DATE,
                                      limit=definitions.DEFAULT_LIMIT)

        json = j.dumps(result, indent=4)
        return json

    def get_scene_ids(self):

        json = self.search()
        json = j.loads(json)

        for counter, item in enumerate(json.items()):
            for result in item:
                print(json['results'][counter]['sceneID'])



