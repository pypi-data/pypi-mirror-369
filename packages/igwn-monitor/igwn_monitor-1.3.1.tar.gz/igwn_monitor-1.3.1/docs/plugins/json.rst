############################
JSON Schema for `check-json`
############################

The :doc:`check_json` plugin ingests a JSON file that should follow the
schema outlined below.

==========
Parameters
==========

The JSON file should present a **single** ``object`` that presents the
following key/value information.

------------------
Author information
------------------

The author of the JSON report, or the tool that creates it, should be
provided as an ``object`` giving the ``name`` and ``email`` of the individual.

See the `Formal Schema`_ below for more details.

-------------
Creation time
-------------

The time at which the report was created should be provided using
*one* of the ``created_gps`` or ``created_unix`` parameters.

See the `Formal Schema`_ below for more details.

----------------
Status intervals
----------------

The result of the underlying check should be reported in the
``status_intervals`` key.
This should be given as an ``array`` of ``object`` types that each
specify a ``[start, stop)`` interval of time for which the contained
status is relevant.

This is mainly useful to give an 'expiry' time for the current state,
to enable problem notifications if the JSON file stops updating.

See the `Formal Schema`_ below for details of
the parameters acceptable for each status interval.

-------------------
Status explanations
-------------------

The ``ok_txt``, ``warning_txt``, ``critical_txt``, and ``unknown_txt``
parameters can be included with explantatory text for each possible
check state.

See the `Formal Schema`_ below for details of
the parameters acceptable for each status interval.

----------------
Other parameters
----------------

Other parameters are not forbidden in the JSON file, but are not parsed by
`check_json` or included in the plugin output.

=======
Example
=======

.. code-block:: json

    {
      "author": {
        "name": "Marie Curie",
        "email": "marie@science.example.com"
      },
      "creation_gps": 1234567890,
      "status_intervals": [
        {
          "start_sec": 0,
          "end_sec": 600,
          "txt_status": "Latest output file is 67 seconds old",
          "num_status": 0
        },
        {
          "start_sec": 600,
          "txt_status": "check_science status is not updating, please check the logs",
          "num_status": 3
        }
      ],
      "ok_txt": "This analysis is running fine",
      "warning_txt": "The analysis is running more than 5 minutes behind, but less than 10 minutes",
      "critical_txt": "The analysis is running more than 10 minutes behind, this is bad",
      "unknown_txt": "I couldn't check what was going on"
    }

=============
Formal Schema
=============

.. jsonschema:: igwn_monitor.plugins.check_json.SCHEMA
