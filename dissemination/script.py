from .community import DisseminationCommunity

from dispersy.logger import get_logger
from dispersy.script import ScriptBase
from dispersy.tool.lencoder import bz2log
from dispersy.tool.scenarioscript import ScenarioScript
logger = get_logger(__name__)

MASTER_MEMBER_PUBLIC_KEY = "3081a7301006072a8648ce3d020106052b810400270381920004068097a9d88022d0581ce8f9064a575f99d7907a2f1d4c865884e7445a3494484ae6f89e7c69e99697c605d066b16aeb99cb7f7f4be8b24870f88f987d52cd6279909d382cd8626606ec2944526e5bb64b936709d2c7e43b820db5e45697ea98805bcd0708a8eb2fd4377a2d8bafc5a844950e2d7bafd3072416e52b3d25710d377176ec6e1046fd99f6a9b41f816a6f".decode("HEX")

class ScenarioScript(ScenarioScript):
    def __init__(self, *args, **kargs):
        super(ScenarioScript, self).__init__(*args, **kargs)
        self._community_kargs = {}

    @property
    def my_member_security(self):
        # return u"NID_sect233k1"
        # NID_secp224r1 is approximately 2.5 times faster than NID_sect233k1
        return u"NID_secp224r1"

    @property
    def master_member_public_key(self):
        return MASTER_MEMBER_PUBLIC_KEY

    @property
    def community_class(self):
        return DisseminationCommunity

    @property
    def community_kargs(self):
        return self._community_kargs

    def log(self, _message, **kargs):
        # import sys
        # print >> sys.stderr, _message, kargs
        bz2log("log", _message, **kargs)

    def scenario_set_karg(self, key, value):
        self.community_kargs[key] = value

    def scenario_create_one(self, *message):
        community = self.has_community()
        if community:
            community.create_text(" ".join(message).decode("UTF-8"))
        else:
            logger.error("Unable to scenario_create_one (not online)")

    def scenario_create_many(self, count, *message):
        community = self.has_community()
        if community:
            community.create_text(" ".join(message).decode("UTF-8"), int(count))
        else:
            logger.error("Unable to scenario_create_many (not online)")

    def scenario_create_start(self, delay, *message):
        delay = float(delay)
        message = " ".join(message).decode("UTF-8")
        self._dispersy.callback.register(self._create_periodically, (delay, message), id_="scenario-periodically")

    def scenario_create_stop(self):
        self._dispersy.callback.unregister("scenario-periodically")

    def _create_periodically(self, delay, message):
        while True:
            community = self.has_community()
            if community:
                community.create_text(message)
            else:
                logger.error("Unable to _create_periodically (not online)")
            community = None
            yield delay

    def scenario_dissemination_success_condition(self, message_name, minimum, maximum="DEF"):
        try:
            meta_message_id, = self._dispersy.database.execute(u"SELECT id FROM meta_message WHERE name = ?",
                                                               (unicode(message_name),)).next()
            count, = self._dispersy.database.execute(u"SELECT COUNT(*) FROM sync WHERE meta_message = ?",
                                                     (meta_message_id,)).next()
        except:
            count = 0

        minimum = int(minimum)
        maximum = -1 if maximum == "DEF" else int(maximum)

        if maximum == -1:
            # there is no maximum
            self.log("success_condition",
                     type="dissemination",
                     success=minimum <= count,
                     description="%d %s messages in the database (minimum %d)" % (count, message_name, minimum))

        else:
            self.log("success-condition",
                     type="dissemination",
                     success=minimum <= count <= maximum,
                     description="%d %s messages in the database (minimum %d, maximum %d)" % (count, message_name, minimum, maximum))
            assert minimum <= maximum

class FillDatabaseScript(ScriptBase):
    @property
    def enable_wait_for_wan_address(self):
        return False

    def run(self):
        self.add_testcase(self.fill)

    def fill(self):
        community = DisseminationCommunity.join_community(self._dispersy, self._dispersy.get_member(MASTER_MEMBER_PUBLIC_KEY), self._dispersy.get_new_member(u"low"))
        community.auto_load = False

        MAX = 3000
        with self._dispersy.database:
            for i in xrange(MAX):
                community.create_text(u"Hello World! #%d" % i, forward=False)
                if i % max(1, (MAX / 100)) == 0:
                    print "progress...", i, "/", MAX, "~", round(1.0 * i / MAX, 2)
                    yield 0.0

        print self._dispersy.database.file_path
