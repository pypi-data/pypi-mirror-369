import copy
import json
import logging
import sys
import time
from sarracenia.featuredetection import features

import sarracenia

logger = logging.getLogger(__name__)

__default_options = {
    'acceptUnmatched': True,
    'batch': 100,
    'broker': None,
    'dry_run': False,
    'exchange': 'xpublic',
    'expire': 300,
    'inline': False,
    'inlineEncoding': 'guess',
    'inlineByteMax': 4096,
    'logFormat':
    '%(asctime)s [%(levelname)s] %(name)s %(funcName)s %(message)s',
    'logLevel': 'info',
    'messageDebugDump': False,
    'message_strategy': {
        'reset': True,
        'stubborn': True,
        'failure_duration': '5m'
    },
    'messageAgeMax': 0,
    'topicPrefix': ['v03'],
    'tlsRigour': 'normal'
}

def default_options() -> dict:
        """
        get default properties to override, used by client for validation. 

        """
        if (sys.version_info.major == 3) and (sys.version_info.minor < 7):
            o = {}
            for k in __default_options:
                if k == 'masks':
                    o[k] = __default_options[k]
                else:
                    o[k] = copy.deepcopy(__default_options[k])
        else:
            o = copy.deepcopy(__default_options)

        return o
          
import random

eboIntervalMaximum = 60 + random.random()*60

def ProtocolPresent(p) -> bool:
    if ( p[0:4] in ['amqp'] ) and sarracenia.features['amqp']['present']:
       return True
    if ( p[0:4] in ['mqtt'] ) and sarracenia.features['mqtt']['present']:
       return True
    if p in sarracenia.features:
        logger.critical( f"support for {p} missing, please install python packages: {' '.join(sarracenia.features[p]['modules_needed'])}" )
    else:
        logger.critical( f"Protocol scheme {p} unsupported for communications with message brokers" )

    return False


class Moth():
    r"""
        Moth ... Messages Organized by Topic Headers
        (en français: Messages organisés par thème hierarchique. )

        A multi-protocol library for use by hierarchical message passing implementations,
        (messages which have a 'topic' header that is used for routing by brokers.)
 
        - regardless of protocol, the message format returned should be the same.
        - the message is turned into a sarracenia.Message object, which acts like a python 
          dictionary, corresponding to key-value pairs in the message body, and properties.
        - topic is a special key that may end up in the message body, or some sort of property
          or metadata.
        - the protocol should support acknowledgement under user control. Such control indicated
          by the presence of an entry_point called "ack". The entry point accepts "ack_id" as
          a message identifier to be passed to the broker. Whatever protocol symbol is used
          by the protocol, it is passed through this message property. Examples:
          in rabbitmq/amqp ack takes a "delivery_tag" as an argument, in MQTT, it takes a "message-id"
          so when receiving an AMQP message, the m['ack_id'] is assigned the delivery_tag from the message. 
        - There is a special dict item:  "_DeleteOnPost",  
          to identify keys which are added only for local use.
          they will be removed from the message when publishing.
          examples:  topic (sent outside body), message-id (used for acknowledgements.)
          new_basedir, ack_id, new\_... (settings...)

        Intent is to be specialized for topic based data distribution (MQTT style.)
        API to allow pass-through of protocol specific properties, but apply templates for genericity.

        Target protocols (and corresponding libraries.): AMQP, MQTT, ?

        Things to specify:

        * broker

        * topicPrefix

        * subTopic  

        * queueName   (for amqp, used as client-id for mqtt)

        this library knows nothing about Sarracenia, the only code used from sarracenia is to interpret
        duration properties, from the root sarracenia/__init__.py, the broker argument from sarracenia.config.credentials
  
        usage::

           import sarracenia.moth
           import sarracenia.config.credentials


           props = sarracenia.moth.default_options()
           props['broker'] = sarracenia.config.credentials.Credential('amqps://anonymous:anonymous@hpfx.collab.science.gc.ca')
           props['expire'] = 300
           props['batch'] = 1
           is_subscriber=True

           c= Moth( props, is_subscriber  )

           messages = c.newMessages()

           # if there are new messages from a publisher, return them, otherwise return
           # an empty list []].
             
           p=Moth( { 'batch':1 }, False )

           p.putNewMessage()

           p.close()
           # tear down connection.     
  
        Initialize a broker connection. Connections are unidirectional.
        either for subscribing (with subFactory) or publishing (with pubFactory.)
       
        The factories return objects subclassed to match the protocol required
        by the broker argument.

        arguments to the factories are:

        * broker ... the url of the broker to connect to.

        * props is a dictionary or properties/parameters.

        * supplied as overrides to the default properties listed above.

        Some may vary among protocols::
 
          Protocol     library implementing    URL to select
          --------     --------------------    -------------

          AMQPv0.9 --> amqplib from Celery --> amqp, amqps

          AMQPv0.9 --> pika                --> pika, pikas

          MQTTv3   --> paho                --> mqtt, mqtts

          AMQPv1.0 --> qpid-proton         --> amq1, amq1s



       **messaging_strategy**

       how to manage the connection. Covers whether to treat the connection
       as new or assume it is set up. Also, If something goes wrong.  
       What should be done. 
         
       * reset: on startup... erase any state, and re-initialize.

       * stubborn: If set to True, loop forever if something bad happens.  
         Never give up. This sort of setting is desired in operations, especially unattended.
         if set to False, may give up more easily.

       * failure_duration is to advise library how to structure connection service level.
          
         * 5m - make a connection that will recover from transient errors of a few minutes,
           but not tax the broker too much for prolonged outages.

         * 5d - duration outage to striving to survive connection for five days.

       Changing recovery_strategy setting, might result in having to destroy and re-create 
       consumer queues (AMQP.)

       **Options**

       **both**

       * 'topicPrefix' : [ 'v03' ]

       * 'messageDebugDump': False, --> enable printing of raw messages.

       * 'inline': False,  - Are we inlining content within messages?

       * 'inlineEncoding': 'guess', - what encoding should we use for inlined content?

       * 'inlineByteMax': 4096,  - Maximum size of messages to inline.

       **for get**

       *  'batch'  : 100  # how many messages to get at once

       *  'broker' : an sr_broker ?

       *  'queueName'  : Mandatory, name of a queue. (only in AMQP... hmm...)

       *  'subscriptions' : [ list of config.subscription.Subscription ]

       *  'loop'

       **optional:**

       *  'message_ttl'    

       **for put:**

       *   'exchange' (only in AMQP... hmm...)
       

    """
    @staticmethod
    def subFactory(props) -> 'Moth':

        if 'subscription_index' in props:
            subIndex = props['subscription_index']
            broker = props['subscriptions'][subIndex]['broker']
        elif not props['broker'] :
            logger.error('no broker specified')
            return None
        else:
            broker = props['broker']

        if not hasattr(broker,'url'):
            logger.error('invalid broker url')
            return None

        if not ProtocolPresent(broker.url.scheme):
           logger.error('unknown broker scheme/protocol specified')
           return None

        for sc in Moth.findAllSubclasses(Moth):
            driver=sc.__name__.lower()
            # when amqp_consumer option is True, use the moth.AMQPConsumer class, not normal moth.AMQP
            if "amqp_consumer" in props and props["amqp_consumer"]:
                if driver == 'amqp':
                    continue
                if driver == 'amqpconsumer':
                    # driver needs to be amqp to match with the broker URL's scheme
                    driver = 'amqp'
            scheme=broker.url.scheme
            if (scheme == driver) or \
               ( (scheme[0:-1] == driver) and (scheme[-1] in [ 's', 'w' ])) or \
               ( (scheme[0:-2] == driver) and (scheme[-2] == 'ws')):
                return sc(props, True)
        logger.error('broker intialization failure')
        return None

    @staticmethod
    def pubFactory(props) -> 'Moth':
        if 'publisher_index' in props:
            pubIndex = props['publisher_index']
            publisher = props['publishers'][pubIndex]
            broker = publisher['broker']
            props['broker'] = broker
            props['exchange'] = publisher['exchange']
        elif not props['broker']:
            logger.error('no broker specified')
            return None
        else:
            broker = props['broker']

        if not hasattr(broker,'url'):
            logger.error( f"invalid broker url: {str(broker)} {type(broker)}")
            return None

        if not ProtocolPresent(broker.url.scheme):
            logger.error( f"unknown broker scheme/protocol specified: {broker.url.scheme}")
            return None

        scheme=broker.url.scheme
        for sc in Moth.__subclasses__():
            driver=sc.__name__.lower()
            if (scheme == driver) or \
               ( (scheme[0:-1] == driver) and (scheme[-1] in [ 's', 'w' ])) or \
               ( (scheme[0:-2] == driver) and (scheme[-2] == 'ws')):
                return sc(props, False)

        # ProtocolPresent test should ensure that we never get here...
        logger.error('broker {str(broker)} intialization failure')
        return None
    
    @staticmethod
    def findAllSubclasses(cls) -> set:
        """Recursively finds all subclasses of a class. __subclasses__() only gives direct subclasses.
        """
        cls_subclasses = set(cls.__subclasses__())
        for sc in cls_subclasses:
            cls_subclasses = cls_subclasses.union(Moth.findAllSubclasses(sc))
        return cls_subclasses

    def __init__(self, props=None, is_subscriber=True) -> None:
        """
           If is_subscriber=True, then this is a consuming instance.
           expect calls to get* routines.

           if is_subscriber=False, then expect/permit only calls to put*
        """

        self.is_subscriber = is_subscriber
        self.connected=False
        self._stop_requested = False
        self.metrics = { 'connected': False }
        self.metricsReset()

        now = time.time()
        self.next_connect_time = now
        self.next_connect_failures = 0

        self.o = default_options()

        if props is not None:
            self.o.update(props)

        me = 'sarracenia.moth.Moth'

        if is_subscriber:
            if 'subscriber_index' in self.o:
                subscription=self.o['subscriptions'][self.o['subscription_index']]
                broker = subscription['broker']
                self.o['broker'] = broker
                self.o['exchange'] = subscription['exchange']
        else:
            if 'publisher_index' in self.o:
                publisher=self.o['publishers'][self.o['publisher_index']]
                self.o['broker'] = publisher['broker']
                self.o['exchange'] = publisher['exchange']
                self.o['topicPrefix'] = publisher['topicPrefix']

        # apply settings from props.
        if 'settings' in self.o:
            if me in self.o['settings']:
                for s in self.o['settings'][me]:
                    self.o[s] = self.o['settings'][me][s]

        logging.basicConfig(format=self.o['logFormat'],
                            level=getattr(logging, self.o['logLevel'].upper()))
        logger.debug( f" Maximum interval exponential back off of connecting to broker: {eboIntervalMaximum} " )

    def ack(self, message: sarracenia.Message ) -> bool:
        """
          tell broker that a given message has been received.

          ack uses the 'ack_id' property to send an acknowledgement back to the broker.
          If there's no 'ack_id' in the message, you should return True.
        """
        logger.error("ack unimplemented")

    def getNewMessage(self) -> sarracenia.Message:
        """
        If there is one new message available, return it. Otherwise return None. Do not block.

        side effects:
            metrics.
            self.metrics['RxByteCount'] should be incremented by size of payload.
            self.metrics['RxGoodCount'] should be incremented by 1 if a good message is received.
            self.metrics['RxBadCount'] should be incremented by 1 if an invalid message is received (&discarded.)
        """
        logger.error("getNewMessage unimplemented")
        return None

    def newMessages(self) -> list:
        """
        If there are new messages available from the broker, return them, otherwise return None.

        On Success, this routine returns immediately (non-blocking) with either None, or a list of messages.

        On failure, this routine blocks, and loops reconnecting to broker, until interaction with broker is successful.
        
        """
        logger.error("NewMessages unimplemented")
        return []
    
    def please_stop(self) -> None:
        """ register a request to cleanly stop. Any long running processes should check for _stop_requested and 
            stop if it becomes True.
        """
        logger.info("asked to stop")
        self._stop_requested = True

    def putNewMessage(self, message:sarracenia.Message, content_type: str ='application/json', exchange: str = None) -> bool:
        """
           publish a message as set up to the given topic.

           return True is succeeded, False otherwise.

           side effect
            self.metrics['TxByteCount'] should be incremented by size of payload.
            self.metrics['TxGoodCount'] should be incremented by 1 if a good message is received.
            self.metrics['TxBadCount'] should be incremented by 1 if an invalid message is received (&discarded.)
        """
        logger.error("implementation missing!")
        return False

    def metricsReset(self) -> None:
        self.metrics['disconnectLast'] = 0
        self.metrics['disconnectTime'] = 0
        self.metrics['disconnectCount'] = 0
        self.metrics['rxByteCount'] = 0
        self.metrics['rxGoodCount'] = 0
        self.metrics['rxBadCount'] = 0
        self.metrics['txByteCount'] = 0
        self.metrics['txGoodCount'] = 0
        self.metrics['txBadCount'] = 0

    def metricsReport(self) -> tuple:
        if not self.metrics['connected'] and (self.metrics['disconnectLast'] > 0):
            down_time = time.time() - self.metrics['disconnectLast']
            self.metrics['disconnectTime'] += down_time

        return self.metrics

    def metricsConnect(self) -> None:
        self.metrics['connected']=True
        if self.metrics['disconnectLast'] > 0 :
            down_time = time.time() - self.metrics['disconnectLast']
            self.metrics['disconnectTime'] += down_time

    def metricsDisconnect(self) -> None:
        """
           tear down an existing connection.
        """
        self.metrics['connected']=False
        self.metrics['disconnectCount'] += 1
        self.metrics['disconnectLast'] = time.time()

    def close(self) -> None:
        logger.error("implementation missing!")

    def cleanup(self) -> None:
        """
          get rid of server-side resources associated with a client. (queues/id's, etc...)
        """
        if self.is_subscriber:
            self.getCleanUp()
        else:
            self.putCleanUp()

    def setEbo(self,start)->None:
        """  Calculate next retry time using exponential backoff
             note that it doesn't look like classic EBO because the time
             is multiplied by how long it took to fail. Long failures should not
             be retried quickly, but short failures can be variable in duration.
             If the timing of failures is variable, the "attempt_duration" will be low,
             and so the next_try might get smaller even though it hasn't succeeded yet...
             it should eventually settle down to a long period though.
        """
        now=time.time()
        # if the attempt takes a long time, do not want to try again quickly.
        # but if it fails immediately, then wait at least 1 second.
        attempt_duration = max(now - start,1)
        self.next_connect_failures += 1

        # wait a little longer after each failure. 
        ebo = 1.2**self.next_connect_failures

        # eboIntervalMaximum is something random between 1 and 4 minutes.
        # it is the ceiling. Otherwise based on the number of failures to connect and 
        # how long each attempt takes to fail.
        next_try = min(max(attempt_duration * ebo,0.1), eboIntervalMaximum)
        self.next_connect_time = now + next_try

    def splitPick(self,message) -> int:
        """
           given a message and exchangeSplit, return the number to split to.
        """

        # FIXME: assert ( len(self.o['exchange']) == self.o['post_exchangeSplit'] )
        #        if that isn't true... then there is something wrong... should we check ?
        if 'exchangeSplitOverride' in message:
            idx = int(message['exchangeSplitOverride'])%len(self.o['exchange'])
        elif 'relPath' in message:
            idx = sum( bytearray( message['relPath'], 'ascii')) % len(self.o['exchange'])
        elif 'retrievePath' in message:
            idx = sum( bytearray( message['retrievePath'], 'ascii')) % len(self.o['exchange'])
        else:
            logger.warning( f"missing fields for exchangeSplit, assigning 0")
            idx = 0
        return idx 
 

if features['amqp']['present']:
    import sarracenia.moth.amqp
    import sarracenia.moth.amqpconsumer

if features['mqtt']['present']:
    import sarracenia.moth.mqtt
