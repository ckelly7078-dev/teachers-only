import unittest
import fitz
from foundation.reconcile import count_cover, corrected, extract

class CoordinateTests(unittest.TestCase):
    def test_count(self):
        self.assertEqual(count_cover('Answer all thirty-three questions.'),33)
        self.assertEqual(count_cover('Answer all sixteen questions.'),16)
        self.assertIsNone(count_cover('No question count.'))
    def test_pinned_correction(self):
        self.assertEqual(corrected([2,2],[2,2],[2]),[2])
        with self.assertRaises(ValueError): corrected([3],[2,2],[2])
    def test_coordinate_heading_and_totals(self):
        with fitz.open() as doc:
            doc.new_page();doc.new_page();p=doc.new_page()
            p.insert_text((57,80),'1  Calculate',fontname='tibo',fontsize=12)
            p.insert_text((57,110),'2',fontname='tiro',fontsize=12) # Graph label, not a bold heading.
            p.insert_text((510,150),'[2]',fontname='tiro',fontsize=12)
            p.insert_text((57,190),'2  Calculate',fontname='tibo',fontsize=12)
            p.insert_text((510,230),'[1]',fontname='tiro',fontsize=12)
            # Synthetic fixture uses built-in font names; parser matches actual Times/Arial heading families.
            h,r,_,_=extract(doc,limit=2)
            self.assertEqual(list(h),[1,2]); self.assertEqual(r[(1,'')]['marks'],[2]);self.assertEqual(r[(2,'')]['marks'],[1])

if __name__=='__main__':unittest.main()
