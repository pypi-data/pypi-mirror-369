# BSD 3-Clause License
#
# Copyright (c) 2022-2025, rd2
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
from src.oslg import oslg

DBG = oslg.CN.DEBUG
INF = oslg.CN.INFO
WRN = oslg.CN.WARN
ERR = oslg.CN.ERROR
FTL = oslg.CN.FATAL

class TestOSlgModuleMethods(unittest.TestCase):
    def test_oslg_constants(self):
        self.assertEqual(DBG, 1)
        self.assertEqual(INF, 2)
        self.assertEqual(WRN, 3)
        self.assertEqual(ERR, 4)
        self.assertEqual(FTL, 5)

    def test01_oslg_initialized(self):
        self.assertEqual(len(oslg.logs()), 0)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(oslg.status(), 0)
        self.assertNotEqual(oslg.level(), DBG)
        self.assertNotEqual(oslg.status(), ERR)
        self.assertEqual(oslg.tag(), "INFO")
        self.assertEqual(oslg.msg(), "")
        self.assertEqual(oslg.tag(WRN), "WARNING")
        self.assertEqual(oslg.msg(FTL), "Failure, triggered fatal errors")
        self.assertNotEqual(oslg.msg(FTL), "Debugging ...")
        self.assertEqual(oslg.trim("   oslg  "), "oslg")
        self.assertEqual(oslg.trim("   oslg  ", 3), "osl ...")
        self.assertEqual(oslg.trim("   oslg  ", 64), "oslg")
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test02_oslg_resets(self):
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(oslg.reset(10), INF)
        self.assertEqual(oslg.reset(FTL), FTL)
        self.assertEqual(oslg.reset(), DBG)
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test03_oslg_invalid_argument_log(self):
        m1 = "Invalid 'radius' arg #2 (area)"
        m2 = "Invalid 'radius' (area)"
        self.assertEqual(oslg.level(), INF)
        self.assertFalse(oslg.logs())
        self.assertEqual(oslg.invalid("radius", "area", 2, FTL), None)
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_fatal())
        self.assertEqual(oslg.status(), FTL)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m1)
        self.assertEqual(oslg.logs()[0]["level"], FTL)
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(oslg.invalid("radius", "area", 0, WRN), None)
        self.assertFalse(oslg.is_fatal())
        self.assertTrue(oslg.is_warn())
        self.assertEqual(oslg.status(), WRN)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m2)
        self.assertEqual(oslg.logs()[0]["level"], WRN)
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

        # Longish error message, exceeding 160 chars.
        a = str([i+1 for i in range(60)])
        l1 = 3 * 9 # "1, " + "2, " + "3, " ...+ "9, "
        l2 = 4 * (59 - 9) # "10, " + "11, " + 12, ...+ "59, "
        l3 = 2 # "60"
        l4 = 2 # "[]"
        self.assertEqual(l1 + l2 + l3 + l4, 231)
        self.assertEqual(len(a), l1 + l2 + l3 + l4)
        self.assertEqual(oslg.mismatch("x", "String", list, a, FTL, None, 156), None)
        self.assertEqual(oslg.status(), FTL)
        str1 = "'x' str? expecting list "                        # 24 chars
        str2 = "([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, "   # 45 chars
        str3 = "14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, "    # 44 chars
        str4 = "25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, ..." # 47 chars
        str0 = str1 + str2 + str3 + str4
        self.assertEqual(len(str0), 160) # 156 + " ..."
        self.assertEqual(len(oslg.logs()[0]["message"]), len(str0))
        self.assertEqual(oslg.logs()[0]["message"], str0)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test04_oslg_mismatched_argument_log(self):
        m1 = "'radius' str? expecting float (area)"
        m2 = "'roster' list? expecting dict (index)"
        self.assertEqual(oslg.level(), INF)
        self.assertFalse(oslg.logs())
        self.assertEqual(oslg.mismatch("radius", "5", float, "area", ERR), None)
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_error())
        self.assertEqual(oslg.status(), ERR)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m1)
        self.assertEqual(oslg.logs()[0]["level"], oslg.status())
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(oslg.mismatch("roster", [], dict, "index", ERR), None)
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_error())
        self.assertEqual(oslg.status(), ERR)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m2)
        self.assertEqual(oslg.logs()[0]["level"], oslg.status())
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test05_oslg_missing_key_argument_log(self):
        m1 = "Missing 'r' key in argh (area)"
        self.assertEqual(oslg.level(), INF)
        self.assertFalse(oslg.logs())
        self.assertEqual(oslg.hashkey("argh", {"a":3}, "r", "area", ERR), None)
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_error())
        self.assertEqual(oslg.status(), ERR)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m1)
        self.assertEqual(oslg.logs()[0]["level"], oslg.status())
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test06_oslg_empty_argument_log(self):
        m1 = "Empty 'hash' (area)"
        self.assertEqual(oslg.level(), INF)
        self.assertFalse(oslg.logs())
        self.assertEqual(oslg.empty("hash", "area", ERR, []), [])
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_error())
        self.assertEqual(oslg.status(), ERR)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m1)
        self.assertEqual(oslg.logs()[0]["level"], oslg.status())
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test07_oslg_zero_argument_log(self):
        m1 = "Zero 'radius' (area)"
        self.assertEqual(oslg.level(), INF)
        self.assertFalse(oslg.logs())
        self.assertEqual(oslg.zero("radius", "area", ERR), None)
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_error())
        self.assertEqual(oslg.status(), ERR)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m1)
        self.assertEqual(oslg.logs()[0]["level"], oslg.status())
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

    def test07_oslg_zero_argument_log(self):
        m1 = "Negative 'radius' (area)"
        self.assertEqual(oslg.level(), INF)
        self.assertFalse(oslg.logs())
        self.assertEqual(oslg.negative("radius", "area", ERR), None)
        self.assertFalse(oslg.is_info())
        self.assertTrue(oslg.is_error())
        self.assertEqual(oslg.status(), ERR)
        self.assertEqual(oslg.level(), INF)
        self.assertEqual(len(oslg.logs()), 1)
        self.assertEqual(oslg.logs()[0]["message"], m1)
        self.assertEqual(oslg.logs()[0]["level"], oslg.status())
        self.assertEqual(oslg.reset(INF), INF)
        self.assertEqual(oslg.clean(), INF)
        self.assertEqual(oslg.level(), INF)

if __name__ == "__main__":
    unittest.main()
