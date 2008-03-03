from subprocess import Popen, PIPE
import unittest
import appclienttest

class Test(unittest.TestCase):
    def testNonWellFormed(self):
        """
        Non-WellFormed output should be caught
        and a log message recording the malformed
        XML should be produced.
        """
        output = Popen(["python", "appclienttest.py", "--quiet", "--playback=./rawtestdata/invalid-service/"], stdout=PIPE).communicate()[0]
        parsed = [l.split(":") for l in  output.splitlines()]
        msg_count = {}
        for code, msg in parsed:
            msg_count[code] = msg_count.get(code, 0) + 1
        self.assertTrue(["Error", appclienttest.REPRESENTATION] in parsed)
        self.assertTrue(["Log", "Response"] in parsed)        

if __name__ == "__main__":
    unittest.main()
    
