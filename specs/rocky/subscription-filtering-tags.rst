..
  This template should be in ReSTructured text. The filename in the git
  repository should match the launchpad URL, for example a URL of
  https://blueprints.launchpad.net/zaqar/+spec/awesome-thing should be named
  awesome-thing.rst.

  Please do not delete any of the sections in this
  template.  If you have nothing to say for a whole section, just write: None

  For help with syntax, see http://sphinx-doc.org/rest.html
  To test out your formatting, see http://www.tele3.cz/jbar/rest/rest.html

===============================
Subscription filtering policies
===============================

https://blueprints.launchpad.net/zaqar/+spec/subscription-filtering-tags

By default, a subscriber of zaqar topic receives every message published
to the topic. To receive only a subset of the messages, a subscriber assigns
a filter policy to the topic subscription. So in this case, zaqar need to
support message filtering. This function is similar to Amazon SNS message
filtering[1].

This feature supports all subscription endpoint, including mail, webhook.

Problem description
===================

The current subscription lacks flexibility due to the fact that it does
not support message filtering. When a subscriber subscribes to a topic,
all messages which sent to the topic will be sent to this subscriber.
So, this feature is intended to solve the problem, which allows the user
to specify the filter policies when creating a subscription and publish
messages, and ultimately, the filter policies matching decides which subscriber
will receive the message.

Proposed change
===============

The filter policy is a simple JSON object. The policy contains attributes that
define which messages the subscriber receives. When you publish a message to a
topic, Zaqar compares the message attributes to the attributes in the filter
policy for each of the topic's subscriptions. If there is a match between the
attributes, Zaqar sends the message to the subscriber. Otherwise, Zaqar skips
the subscriber without sending the message to it.

With filter policies, you can simplify your message filtering criteria into
your topic subscriptions. With this consolidation, you can offload the message
filtering logic from subscribers and the message routing logic from publishers.
Therefore, you do not need to filter messages by creating a separate topic for
each filtering condition. Instead, you can use a single topic, and you can
differentiate your messages with attributes. Each subscriber receives and
processes only those messages accepted by its filter policy.

For example, you could use a single topic to publish all messages generated by
transactions from your online retail site. To each message, you could assign an
attribute that indicates the type of transaction, such as order_placed,
order_cancelled, or order_declined. With filter policies, you can route each
message to the different subscriber that is meant to process the message's
transaction type.

To do this, a new attribute named ``filter_policies`` need to be added to both
the message and subscription. Note that this property is optional and does not
affect existing functionality.

When you create a subscription, you can specify the filter policies,
just like this::

    ``{'subscriber': 'http://example.com/order_placed',
       'options':{'filter_policies': ['order_placed']}}``

Then when you send a message to the topic, you can choose to add the
attribute, just like this::

    ``{'body': 'test', 'filter_policies': ['order_placed']}``

Finally, zaqar decides which subscribers the message should be sent to
according to the following rules:

* If the subscriber does not have any filter_policies, all messages will be
  sent to the subscriber.

* If the message does not contain any filter_policies, it will not be
  sent to the subscriber which has filter_policies.

* If the message and the subscriber's filter_policies have intersecting
  collections, the message will be sent to the subscriber.

* If the message and the subscriber both have filter_policies, but
  there is no intersection set, no message will be sent to the
  subscriber.

* The relationship of the content in `order_placed` is *or*, it means
  that the message will be sent to the subscriptions that match anyone
  filters in `order_placed`.

Drawbacks
---------

N/A

Alternatives
------------

N/A

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  cdyangzhenyu <cdyangzhenyu@gmail.com>

Milestones
----------

Target Milestone for completion:
  Rocky-3

Work Items
----------

#. Change the message subscription process for applying this feature.
#. Add release note for this feature.
#. Update API reference.
#. Add user/developer document for this feature.
#. Change unit, functional and tempest tests accordingly.

Dependencies
============

None

References
==========

[1] https://docs.aws.amazon.com/sns/latest/dg/message-filtering.html
