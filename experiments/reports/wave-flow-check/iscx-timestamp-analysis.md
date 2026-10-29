# ISCX timestamp analysis

Inspected all 445,915 JSONL records on supermicro-devbox, including the timestamps in tcp.segs and udp.dgms. Dates below are UTC.

## Main finding

Every part is already nondecreasing by connection `ts`. There were zero backward steps and zero records more than 60 seconds behind a per-part timestamp frontier in all ten parts. The previously reported late counts arise from retaining a single watermark across parts, not disorder within a part.

| Part | Records | Earliest ts | Latest ts | Late with split-wide frontier |
| --- | ---: | --- | --- | ---: |
| testing-p01 | 119852 | 1970-01-01 00:00:06 | 2013-02-04 01:33:42 | 0 |
| testing-p02 | 68618 | 2007-10-08 13:22:16 | 2012-10-13 09:48:53 | 68618 |
| testing-p03 | 25213 | 2007-10-08 15:56:00 | 2010-02-26 13:58:57 | 25213 |
| testing-p04 | 21340 | 2010-02-26 03:12:13 | 2012-11-30 05:22:52 | 21340 |
| training-01 | 53203 | 2011-08-10 09:04:23 | 2011-08-15 15:12:51 | 0 |
| training-02 | 34478 | 2007-10-08 13:21:55 | 2011-08-19 09:45:32 | 28409 |
| training-03 | 630 | 2007-10-08 15:55:48 | 2007-10-10 00:01:42 | 630 |
| training-04 | 46475 | 2010-01-17 01:02:40 | 2010-06-12 10:07:49 | 46475 |
| training-05 | 38424 | 2010-06-12 10:07:58 | 2010-06-12 18:29:28 | 38424 |
| training-06 | 37682 | 2010-06-12 18:29:50 | 2010-06-13 03:01:05 | 37682 |

Thus all testing parts after p01 fall behind p01's February 2013 frontier. Training-02 contributes 6,069 records that catch up to the previous frontier, then advances it into August 19, 2011. All later training parts remain behind that frontier, even the mutually chronological training-04/05/06 sequence.

## Timestamp quality is a separate issue

Dataset provenance describes an overlay of captures retaining original timestamps. Parts are source-PCAP packet ranges, not disjoint chronological ranges. Shards do not align with parts; resetting at shard boundaries would therefore use the wrong unit.

All connection ts values match the first packet-array timestamp within 1 ms. They do not always equal the minimum packet timestamp: 5 such records in testing-p01 and 125 in testing-p04. There are packet-array backward steps in 9 p01 records and 125 p04 records; none were found in other parts. Thus `ts` describes the first encountered packet, and is not guaranteed to be the earliest timestamp of the grouped packets.

Example: testing-p04/udp.40 starts at 2010-06-15 03:01:31.536500, contains a packet dated 2010-06-11 09:37:19.062600, and has td=-316820.49545908 seconds. This is a real timestamp/grouping artifact in the exported data, independent of cross-part watermark loss. The source PCAP was not inspected directly in this analysis.

Eleven testing-p01 records start near epoch zero. Their position at the beginning does not cause backward event-time arrival, but their timestamps and potentially inflated durations require a separate quality policy.

## Implications

Sorting inside each part is unnecessary. Processing each part with an independent event-time frontier eliminates the measured ordering loss, but does not repair packet-level timestamp or duration artifacts. A single split-wide run would instead require a global time merge; that removes backward arrival but may combine unrelated overlay traffic into the same host/window. Choose the intended analytical scope before doing that. WAVE ingestion still needs a policy for the extra dataset annotation fields.
