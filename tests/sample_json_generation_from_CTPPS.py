Sample JSON making from PPS
=============================================================
RR_2RPGood_anyarms_ls.py
--------------------------------------


from rr_tools_18 import get_data, obtain_json_from_rr

run_class_name = "Collisions18"
dataset_name = "/Express/Collisions2018/DQM"
ls_query = "(l.CTPPS45_READY = '1' or l.CTPPS56_READY = '1')"
output_filename = "test.json"


query = "((r.RDA_CMP_RP45_210 = 'GOOD' and r.RDA_CMP_RP45_220 = 'GOOD') or \
        (r.RDA_CMP_RP45_CYL = 'GOOD' and r.RDA_CMP_RP45_210 = 'GOOD') or \
        (r.RDA_CMP_RP45_CYL = 'GOOD' and r.RDA_CMP_RP45_220 = 'GOOD')) or \
        ((r.RDA_CMP_RP56_210 = 'GOOD' and r.RDA_CMP_RP56_220 = 'GOOD') or \
        (r.RDA_CMP_RP56_220 = 'GOOD' and r.RDA_CMP_RP56_CYL = 'GOOD') or \
        (r.RDA_CMP_RP56_210 = 'GOOD' and r.RDA_CMP_RP56_CYL = 'GOOD'))"


obtain_json_from_rr(run_class_name, dataset_name, query, ls_query, output_filename)
=============================================================
rr_tools_18.py
-------------------------------------
import sys
from rhapi import DEFAULT_URL, RhApi

def get_data(q):
   api = RhApi(DEFAULT_URL, debug = False)

   p = {"class": "Collisions18"}
   qid = api.qid(q)

   return api.csv(q, p)

def obtain_json_from_rr(run_class_name, dataset_name, query, ls_query, output_filename):
   run_numbers_query = "select r.RUN_NUMBER from runreg_ctpps.datasets r where \
   r.run_class_name = '{0}' and r.RDA_NAME = '{1}' {2}".format(
   run_class_name, dataset_name, "and (" + query + ")" if query else "")

   run_numbers = [int(x) for x in [y for y in get_data(run_numbers_query).split("\n") if y and y.isdigit()]]

   with open(output_filename, 'w') as f:
       f.write("{")
       sign = ","
       for i, run_number in enumerate(run_numbers):
           lumisections_numbers = "select l.RDR_SECTION_FROM, l.RDR_SECTION_TO from runreg_ctpps.dataset_lumis l \
           where l.RDR_RUN_NUMBER = {0} {1}".format(run_number, "and (" + ls_query + ")" if ls_query else "")
           if i == len(run_numbers)-1:
               sign = "} "
           f.write("\"{0}\": [[{1}]]{2}\n".format(run_number, "], [".join([x for x in get_data(lumisections_numbers).split("\n") if x][1:]), sign))