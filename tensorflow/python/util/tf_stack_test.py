# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for functions used to extract and analyze stacks."""

import traceback

from tensorflow.python.platform import test
from tensorflow.python.util import tf_stack


class TFStackTest(test.TestCase):

  def testFormatStackSelfConsistency(self):
    # Both defined on the same line to produce identical stacks.
    stacks = tf_stack.extract_stack(), traceback.extract_stack()
    self.assertEqual(
        traceback.format_list(stacks[0]), traceback.format_list(stacks[1]))

  def testFrameSummaryEquality(self):
    frames1 = tf_stack.extract_stack()
    frames2 = tf_stack.extract_stack()

    self.assertNotEqual(frames1[0], frames1[1])
    self.assertEqual(frames1[0], frames1[0])
    self.assertEqual(frames1[0], frames2[0])

  def testFrameSummaryEqualityAndHash(self):
    # Both defined on the same line to produce identical stacks.
    frame1, frame2 = tf_stack.extract_stack(), tf_stack.extract_stack()
    self.assertEqual(len(frame1), len(frame2))
    for f1, f2 in zip(frame1, frame2):
      self.assertEqual(f1, f2)
      self.assertEqual(hash(f1), hash(f1))
      self.assertEqual(hash(f1), hash(f2))
    self.assertEqual(frame1, frame2)
    self.assertEqual(hash(tuple(frame1)), hash(tuple(frame2)))

  def testLastUserFrame(self):
    trace = tf_stack.extract_stack()  # COMMENT
    frame = trace.last_user_frame()
    self.assertRegex(frame.line, "# COMMENT")

  def testGetUserFrames(self):

    def func():
      trace = tf_stack.extract_stack()  # COMMENT
      frames = list(trace.get_user_frames())
      return frames

    frames = func()  # CALLSITE

    self.assertRegex(frames[-1].line, "# COMMENT")
    self.assertRegex(frames[-2].line, "# CALLSITE")

  def testDelItem(self):

    def func(n):
      if n == 0:
        return tf_stack.extract_stack()  # COMMENT
      else:
        return func(n - 1)

    trace = func(5)
    self.assertGreater(len(trace), 5)

    full_list = list(trace)
    del trace[-5:]
    head_list = list(trace)

    self.assertLen(head_list, len(full_list) - 5)
    self.assertEqual(head_list, full_list[:-5])


if __name__ == "__main__":
  test.main()
