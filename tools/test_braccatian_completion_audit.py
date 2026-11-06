"""Regression guards for canonical decision labels and full-scope completion accounting."""
import copy
import unittest
from audit_braccatian_refining import assert_identity,validate_scope


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.rows=[]
        for category,count in [('buildings',23),('ships',5),('missiles',10)]:
            for i in range(count):self.rows.append(dict(id=f'{category}/{i}',name=f'{category} model {i}',category=category,decision='refined' if category=='buildings' or category=='ships' and i<3 else 'retained-after-focused-review'))
        self.canonical={r['id']:copy.deepcopy(r) for r in self.rows}

    def test_complete_exact_scope_passes(self):validate_scope(self.rows,self.canonical)

    def test_dependency_filename_cannot_become_model_name(self):
        actual=dict(id='ships/0',name='verify_rigellian_filtration.py')
        with self.assertRaises(AssertionError):assert_identity(actual,self.canonical['ships/0'])

    def test_missing_and_duplicate_definitions_are_rejected(self):
        with self.assertRaises(AssertionError):validate_scope(self.rows[:-1],self.canonical)
        altered=copy.deepcopy(self.rows);altered[-1]=copy.deepcopy(altered[0])
        with self.assertRaises(AssertionError):validate_scope(altered,self.canonical)

    def test_retained_models_cannot_be_counted_as_new(self):
        altered=copy.deepcopy(self.rows);altered[-1]['decision']='refined'
        with self.assertRaises(AssertionError):validate_scope(altered,self.canonical)

    def test_wrong_category_is_rejected(self):
        altered=copy.deepcopy(self.rows);altered[0]['category']='ships'
        with self.assertRaises(AssertionError):validate_scope(altered,self.canonical)


if __name__=='__main__':unittest.main()
