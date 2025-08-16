# Abnormal Hieratic Indexer

Script that indexes annotations in the [Abnormal Hieratic Global Portal][ahgp].
This script is specifically tailored towards the annotations created for the AHGP.

Annotations in the AHGP are stored in a [Simple Annotation Server][sas],
but for search we use [Elasticsearch][es].

[ahgp]: https://lab.library.universiteitleiden.nl/abnormalhieratic/
[sas]: https://github.com/glenrobson/SimpleAnnotationServer
[es]: https://www.elastic.co/guide/en/elasticsearch/

## Installation

This script was developed with Python 3.9. It may run on other versions, but tests are very limited.

To install, run `pip install abnormal-hieratic-indexer` in your environment.

## Usage

```
$ abhier-indexer -h
usage: abhier-indexer [-h] [--canvas-uri-prefix CANVAS_URI_PREFIX] [--index INDEX] source target

positional arguments:
  source                Base URL for the Simple Annotation Server
  target                Base URL for ElasticSearch (default: http://localhost:9200)

optional arguments:
  -h, --help            show this help message and exit
  --canvas-uri-prefix CANVAS_URI_PREFIX
                        Index only annotations targeting canvases whose URIs start with this prefix (default:
                        https://lab.library.universiteitleiden.nl/manifests/external/louvre/)
  --index INDEX         URI path to the ElasticSearch index (default: /annotations/)
```

To enable periodic indexing, you can set up a cronjob or Systemd timer.

# Author and license

Abnormal Hieratic Indexer was created by Ben Companjen at the Centre for Digital Scholarship.

© 2024 Leiden University Libraries

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
