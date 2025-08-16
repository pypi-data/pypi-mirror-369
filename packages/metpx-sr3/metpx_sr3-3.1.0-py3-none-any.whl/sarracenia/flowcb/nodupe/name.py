import logging
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)


class Name(FlowCB):
    """
      Override the the comparison so that files with the same name,
      regardless of what directory they are in, are considered the same.
      This is useful when receiving data from two different sources (two different trees)
      and winnowing between them.

      Note: files that have different checksums, sizes, modification times, etc. are NOT
            considered duplicates, even if they have the same name.
    """
    def after_accept(self, worklist):
        for m in worklist.incoming:
            if not 'nodupe_override' in m:
                m['_deleteOnPost'] |= set(['nodupe_override'])
                m['nodupe_override'] = {}

            m['nodupe_override']['path'] = m['relPath'].split('/')[-1]
