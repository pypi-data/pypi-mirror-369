from ahocorasick_rs import AhoCorasick, Implementation
from anystore.decorators import anycache
from anystore.logging import get_logger
from anystore.io import logged_items
from anystore.types import StrGenerator, Uri
from anystore.util import join_uri

from juditha.aggregator import Aggregator
from anystore.store import get_store

from normality import normalize


log = get_logger(__name__)


def build_automaton(aggregator: Aggregator) -> AhoCorasick:
    names = map(normalize, aggregator.iter_names())
    names = (n for n in names if n)
    names = logged_items(
        names,
        "[tagger] Load",
        item_name="Name",
        logger=log,
        total=aggregator.count_names,
    )
    return AhoCorasick(names, implementation=Implementation.ContiguousNFA)


class Tagger:
    def __init__(self, uri: Uri, aggregator: Aggregator) -> None:
        self.uri = uri
        self.aggregator = aggregator
        self.key_func = (
            lambda *args, **kwargs: f"aho_{self.aggregator.count_names}.pickle"
        )
        # self.cache = anycache(
        #     store=get_store(self.uri),
        #     serialization_mode="pickle",
        #     key_func=self.key_func,
        # )
        self._automation: AhoCorasick | None = None

    def get_automaton(self) -> AhoCorasick:
        if self._automation is None:
            log.info(
                "[tagger] Loading automation ...",
                uri=join_uri(self.uri, self.key_func()),
            )
            # self._automation = self.cache(build_automaton)(self.aggregator)
            self._automation = build_automaton(self.aggregator)
        return self._automation

    def tag_text(self, text: str) -> StrGenerator:
        aho = self.get_automaton()
        yield from aho.find_matches_as_strings(text, overlapping=True)
