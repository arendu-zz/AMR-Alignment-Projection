from AMRMetadata import *
from amr_class import *


class AmrDoc:
    def __init__(self, unparsed_document):
        self.all_amrs = {}
        for index, each_amr in enumerate(unparsed_document.strip().split("\n\n")):
            its_amr = AMRMetadata(each_amr)
            its_amr.add_attribute("amr", Amr(its_amr.graph_string))
            its_amr.attributes['amr'].code_reentrancies()
            self.all_amrs[its_amr.attributes['id']] = its_amr
            its_amr.add_attribute("original_file_order", str(index))
            
    def append_segmented_chinese(self, parallel, distributions):
        pc = parallel.split("\n")
        dist = distributions.split("\n")
        for an_amr in self.all_amrs:
            print self.all_amrs[an_amr].attributes['id']
            ind = int(self.all_amrs[an_amr].attributes['original_file_order'])
            d = {}
            ds = {}
            for term in dist[ind].strip().split(" "):
                #pass
                if not "-" in term:
                    print term
                else:
                    source= term.split("-")[0]
                    target = term.split("-")[1]
                    if not target in d:
                        d[target] = []
                    d[target].append(int(source))
                    if not source in ds:
                        ds[source] = []
                    ds[source].append(int(target))
                    
            print dist[ind]
            print pc[ind]
            for span in ds:
               print span, ds[span]
            print self.all_amrs[an_amr].attributes['caveman_alignment']
            #print index
            #print dist[index]
            #print pc[index].split("|||")[1]
        
    def concept_strings(self):
        for each_id in self.all_amrs:
            self.all_amrs[each_id].attributes['amr'].code_reentrancies()
            caveman_string, caveman_alignments=  self.all_amrs[each_id].attributes['amr'].amrtized_string(self.all_amrs[each_id].attributes["tok"], self.all_amrs[each_id].attributes["alignments"])
            self.all_amrs[each_id].add_attribute('caveman_string', caveman_string)
            self.all_amrs[each_id].add_attribute('caveman_alignment', caveman_alignments)
    def return_ulformat(self):
            output = ""
            orderable_list = []
            for a_given_id in self.all_amrs:
                if "." in a_given_id and a_given_id.split(".")[-1].isdigit():
                    orderable_list.append([int(a_given_id.split(".")[-1]), a_given_id])
                else:
                    orderable_list.append([a_given_id, a_given_id])
            orderable_list.sort()

            for __, each_id in orderable_list:
                allk =  self.all_amrs[each_id].attributes.keys()

                output += "::id "+self.all_amrs[each_id].attributes["id"].strip()+"\n"
                for each_attribute in allk:
                    if "id" == each_attribute or "amr" == each_attribute:
                        continue
                    output += "::"+each_attribute+" "+self.all_amrs[each_id].attributes[each_attribute]+"\n"
                output += self.all_amrs[each_id].graph_string+"\n\n"
                output += str(self.all_amrs[each_id].attributes["amr"])+"\n\n"
            return output


if False: #lazy testing
	test = "/home/tim/NLP_Programs/AMR-Alignment-Projection/data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned"
	y = AmrDoc(open(test).read())

	print y.concept_strings()
	print y.return_ulformat()
	test = "/home/tim/NLP_Programs/AMR-Alignment-Projection/data/Little_Prince/amr-bank-struct-v1.3.txt.en-aligned"
	segmented = "/home/tim/NLP_Programs/AMR-Alignment-Projection/data/Little_Prince/for-testing.parallel"
	distributions = "/home/tim/NLP_Programs/AMR-Alignment-Projection/data/Little_Prince/littleprince.segmented.chinese.parallel.fastalign"
	y.append_segmented_chinese(open(segmented).read(), open(distributions).read())
