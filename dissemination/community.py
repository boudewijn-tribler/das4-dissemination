from .conversion import Conversion
from .payload import TextPayload

from dispersy.authentication import MemberAuthentication
from dispersy.community import Community
from dispersy.conversion import DefaultConversion
from dispersy.destination import CommunityDestination
from dispersy.distribution import FullSyncDistribution
from dispersy.message import Message
from dispersy.resolution import PublicResolution

from dispersy.tool.lencoder import bz2log

class DisseminationCommunity(Community):
    def __init__(self, dispersy, master, **kargs):
        super(DisseminationCommunity, self).__init__(dispersy, master)
        self._enable_sync_cache = kargs.get("enable_sync_cache", "True") == "True"
        self._enable_sync_skip = kargs.get("enable_sync_skip", "True") == "True"
        self._sync_response_limit = int(kargs.get("sync_response_limit", 25 * 1024))
        strategies = {"largest":self._dispersy_claim_sync_bloom_filter_largest, "modulo":self._dispersy_claim_sync_bloom_filter_modulo}
        self._dispersy_sync_bloom_filter_strategy = strategies.get(kargs.get("sync_bloom_filter_strategy", "largest"))

    def initiate_meta_messages(self):
        return [Message(self, u"text", MemberAuthentication(encoding="bin"), PublicResolution(), FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"ASC", priority=128), CommunityDestination(node_count=0), TextPayload(), self.check_text, self.on_text)]

    def initiate_conversions(self):
        return [DefaultConversion(self), Conversion(self)]

    @property
    def dispersy_sync_response_limit(self):
        return self._sync_response_limit

    @property
    def dispersy_sync_bloom_filter_strategy(self):
        return self._dispersy_sync_bloom_filter_strategy

    @property
    def dispersy_sync_skip(self):
        return self._enable_sync_skip

    def dispersy_claim_sync_bloom_filter(self, request_cache):
        if not self._enable_sync_cache:
            self._sync_cache = None
        return super(DisseminationCommunity, self).dispersy_claim_sync_bloom_filter(request_cache)

    def create_text(self, text, store=True, update=True, forward=True):
        assert isinstance(text, unicode), type(text)
        assert len(text.encode("UTF-8")) < 256
        meta = self.get_meta_message(u"text")
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            payload=(text,))
        bz2log("log", "creation", mid=message.authentication.member.mid, global_time=message.distribution.global_time, text=message.payload.text)
        self._dispersy.store_update_forward([message], store, update, forward)

    def check_text(self, messages):
        return messages

    def on_text(self, messages):
        for message in messages:
            bz2log("log", "received", mid=message.authentication.member.mid, global_time=message.distribution.global_time, text=message.payload.text)
