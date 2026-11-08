"""Offline unit tests for provenance parsing and conservative result axes."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).with_name('20260930-clean-baseline-wrapper.py')
spec=importlib.util.spec_from_file_location('cleanup_wrapper',path)
wrapper=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)


class WrapperTests(unittest.TestCase):
    def good(self):
        return {'ok':True,'run':{'exitCode':0,'timedOut':False,'result':{
            'ok':True,'probe':{'forms':0,'submits':0,'foSeen':2,'msgHit':'interactiveEnd,complete'},
            'cookieNames':['cf_clearance']}}}

    def test_no_form_is_not_harness_failure(self):
        result=wrapper.classify(self.good(),0)
        self.assertTrue(result['harnessHealthy'])
        self.assertFalse(result['businessAccepted'])
        self.assertEqual(result['forms'],0)

    def test_disabled_probes_are_unknown_not_zero(self):
        result=wrapper.classify(self.good(),0)
        for key in ['worker','subtle','blob']:
            self.assertEqual(result[key]['status'],'probe-disabled')
            self.assertIsNone(result[key]['value'])

    def test_cookie_not_business_acceptance(self):
        result=wrapper.classify(self.good(),0)
        self.assertTrue(result['clearanceCookieNamed'])
        self.assertFalse(result['businessAccepted'])

    def test_submit_without_content_not_acceptance(self):
        value=self.good()
        value['run']['result']['probe'].update(forms=1,submits=1)
        self.assertFalse(wrapper.classify(value,0)['businessAccepted'])

    def test_timeout_fails_harness(self):
        value=self.good()
        value['run']['timedOut']=True
        self.assertFalse(wrapper.classify(value,0)['harnessHealthy'])

    def test_probe_error_is_not_measured_zero(self):
        value=self.good()
        value['run']['result']['probe']={'evalError':'synthetic'}
        result=wrapper.classify(value,0)
        self.assertFalse(result['harnessHealthy'])
        self.assertIsNone(result['forms'])

    def test_missing_output_not_success(self):
        result=wrapper.classify({},1)
        self.assertFalse(result['harnessHealthy'])
        self.assertIsNone(result['submits'])

    def test_fresh_relative_orchestrate(self):
        url=wrapper.parse_orchestrate("src='/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1?sample'",'https://example.test/cert/')
        self.assertTrue(url.startswith('https://example.test/'))

    def test_missing_orchestrate_fails_closed(self):
        with self.assertRaises(ValueError):
            wrapper.parse_orchestrate('<html>not challenge</html>','https://example.test/')


if __name__=='__main__':
    unittest.main()
