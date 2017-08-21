from __future__ import print_function
import sys
import os
import csv
import glob
import fnmatch
import re

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db import models
from api.models import GEModelReference
from api.models import GEModelSet
from api.models import GEModelSample
from api.models import GEModelFile
from api.models import GEModel

import xml.etree.ElementTree as ET
import urllib
import urllib.request

def build_ftp_path_and_dl(liste_dico_data, FTP_root, model_set):

    path_key = ['organism', 'name', 'organ_system', ['tissue', 'cell_type', 'cell_line']]
    model_data_list = []
    for i in range(len(liste_dico_data)):
        GEM_sample = {}
        GEM = {}
        dic = liste_dico_data[i]

        if 'organism' not in dic:
            print ("Error: key 'organism' is missing")
            exit()

        path = ''
        for k in path_key:
            if isinstance(k, list):
                for name in k:
                    if name in dic:
                        path = os.path.join(path, dic[name].lower().replace(',', '').replace(' ', '_'))
                        break
            else:
                if k in dic or k in model_set:
                    v = dic[k] if k in dic else model_set[k]
                    path = os.path.join(path, v.lower().replace(',', '').replace(' ', '_'))
        path = os.path.join(FTP_root, path)
        if not os.path.isdir(path):
            os.makedirs(path)

        # get the files path and format
        xml_file = None
        input_files = []
        formats = []
        if 'file' in dic:
            xml_file = dic['file']
            input_files.append(dic.pop('file'))
            if 'format' in dic:
                formats.append(dic.pop('format'))
            else:
                # default file format
                formats.append('SBML')
        else:
            for key_file, format_key in [["file%s" % k, "format%s" % k] for k in range(1,10)]:
                if not key_file in dic:
                    break
                if not format_key in dic:
                    print ("Error: key %s not in dict" % format_key)
                    exit()
                if dic[format_key] == "SBML":
                    xml_file = dic[key_file]
                input_files.append(dic.pop(key_file))
                formats.append(dic.pop(format_key))

        if not xml_file:
            print ("Error: cannot found xml file")
            print (dic)
            exit()

        output_paths = []
        for input_file in input_files:
            output_file_path = os.path.join(path, input_file.split('/')[-1])
            output_paths.append(output_file_path)
            if not os.path.isfile(output_file_path):
                print ("Downloading %s" % output_file_path)
                urllib.request.urlretrieve(xml_file, output_file_path)
            if xml_file == input_file:
                # parse the file
                count_file = "%s.cnt" % output_file_path[:-4]
                if os.path.isfile(count_file):
                    (GEM['reaction_count'], GEM['metabolite_count'], GEM['enzyme_count']) = read_count_file(count_file)
                elif os.path.isfile(output_file_path):
                    print ("Parsing xml %s" % output_file_path)
                    (GEM['reaction_count'], GEM['metabolite_count'], GEM['enzyme_count']) = parse_xml(output_file_path)
                    write_count_file(GEM['reaction_count'], GEM['metabolite_count'], GEM['enzyme_count'], count_file)
                else:
                    print ("Error: cannot find file %s" % output_file_path)
                    exit()
        if len(output_paths) != len(formats):
            print ("Error: format / path do not match")
            exit()


        for k in ['organism', 'organ_system', 'tissue', 'cell_type', 'cell_line']:
            if k not in dic:
                GEM_sample[k] = None
            else:
                GEM_sample[k] = dic[k]
        
        for k in ['description', 'label', 'maintained']:
            if k not in dic:
                GEM[k] = None
            else:
                GEM[k] = dic[k]

        a = 'reference_title' in dic
        b = 'reference_pubmed' in dic
        c = 'reference_link' in dic
        d = 'reference_year' in dic

        if len(set([a,b,c,d])) != 1:
            print ("Error: missing reference info")
            print (dic)
            exit()

        if next(iter(set([a,b,c,d]))):
            GEM['reference'] = {
                                'title': dic['reference_title'], 
                                'link': dic['reference_link'],
                                'pubmed': dic['reference_pubmed'],
                                'year': dic['reference_year'],
                                }
        elif 'reference' in dic:
            GEM['reference'] = dic['reference']
        else:
            GEM['reference'] = None

        GEM['files'] = []
        for path, formatt in zip(output_paths, formats):
            GEM['files'].append({'path': path, 'format': formatt})

        GEM['sample'] = GEM_sample
        # print (GEM)
        model_data_list.append(GEM)

    return model_data_list


def write_count_file(reaction_count, metabolite_count, enzyme_count, output_file):
    with open(output_file, 'w') as fw:
        fw.write('reaction_count\t%s\n' % reaction_count)
        fw.write('metabolite_count\t%s\n' % metabolite_count)
        fw.write('enzyme_count\t%s\n' % enzyme_count)


def read_count_file(count_file):
    with open(count_file) as fh:
        dic = {}
        for line in fh:
            if len(line) == 0:
                continue
            linearr = line.split('\t')
            dic[linearr[0]] = int(linearr[1])
        return dic['reaction_count'], dic['metabolite_count'], dic['enzyme_count']


def parse_info_file(info_file):
    # get the model_set information and Model_reference association to this set if any
    global_dict = {}
    model_set_data = {}
    with open(info_file, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) == 0 or row[0] == "#":
                continue
            global_dict[row[0]] = row[1]

        model_set_data['name'] = global_dict.pop('name')
        if 'description' in global_dict:
            model_set_data['description'] = global_dict.pop('description')
        else:
            model_set_data['description'] = None

        set_reference_data_list = []
        if 'reference_link' in global_dict:
            set_reference_data_list.append({
                'link': global_dict.pop('reference_link'),
                'title': global_dict.pop('reference_title'),
                'pubmed': global_dict.pop('reference_pubmed'),
                'year': global_dict.pop('reference_year'),})
        else:
            for key_link, key_title, key_pubmed, key_year in [["reference_link%s" % k,
                                                     "reference_title%s" % k,
                                                     "reference_pubmed%s" % k,
                                                     "reference_year%s" % k
                                                      ] for k in range(1,10)]:
                if not key_link in global_dict:
                    break
                set_reference_data_list.append({
                    'link': global_dict.pop(key_link),
                    'title': global_dict.pop(key_title),
                    'pubmed': global_dict.pop(key_pubmed),
                    'year': global_dict.pop(key_year)})

        model_set_data['reference'] = set_reference_data_list
        return global_dict, model_set_data


def parse_xml(xml_file):
    if xml_file[-4:] == ".zip":
        import zipfile
        with zipfile.ZipFile(xml_file) as z:
            #print z.namelist()
            with z.open(z.namelist()[0]) as f:
                xml_file = f.read()
    else:
        with open(xml_file) as f:
            xml_file = f.read()
    d = {}
    #ET.register_namespace('', "http://www.sbml.org/sbml/level3/version1/groups/version1")
    data = ET.fromstring(xml_file)
    #print data
    #for child in data.iter():
    #    print child.tag
    m = 0
    e = 0
    r = 0
    for s in data.iter('{http://www.sbml.org/sbml/level2/version3}species'):
        if s.get('id'):
            if s.get('id')[0] == "M":
                m += 1
            elif s.get('id')[0] == "E":
                e += 1

    for rea in data.iter('{http://www.sbml.org/sbml/level2/version3}reaction'):
        r += 1

    if 0 in [r,m,e]:
        print ("Error: parsing xml problem")
        exit()

    return r, m, e


def read_gems_data_file(parse_data_file, global_dict=None):
    res = []
    with open(parse_data_file, "r") as f:
        reader = csv.reader(f, delimiter='\t')
        # headers = reader.next()
        # types = reader.next()
        headers = next(reader)
        types = next(reader)
        glob_value = {}
        for row in reader:
            # print "Row %s " % row
            if len(row) == 0 or row[0][0] == "#":
                continue
            if row[0][0] == "@":
                if not row[1] or row[1] == "none":
                    # remove the key
                    glob_value.pop(row[0][1:], None)
                else:
                    # note: glob value are always included as string
                    glob_value[row[0][1:]] = row[1]
                continue
            d = {}
            list_key_ignore = []
            for i, col in enumerate(headers):
                if not row[i]:
                    # empty value skipped
                    continue

                if row[i][0] == ":" and row[i][:-1] != ":reference":
                    # get the value from global dict
                    gd_key = row[i][1:]
                    if types[i] == "int":
                        d[col] = int(global_dict[gd_key])
                    else:
                        d[col] = global_dict[gd_key]
                else:
                    if types[i] == "int":
                        d[col] = int(row[i])
                    else:
                        d[col] = row[i]

            if global_dict:
                for k, v in global_dict.items():
                    if not re.match('[0-9]', k[-1]):
                        # ignore the keys that have been included already in d
                        d[k] = v
            if glob_value:
                for k, v in glob_value.items():
                    d[k] = v
            if 'file' not in d and 'file1' not in d:
                print ("error")
                print (d)
                print (row)
                exit()
            res.append(d)
            # print ("d: %s" % d)

    return res

'''
    GEModelReference
    title = models.CharField(max_length=255, null=True)
    link = models.CharField(max_length=255, unique=True)
    pubmed = models.CharField(max_length=50, unique=True)
    year = models.CharField(max_length=4, null=True)
'''

'''
    GEModelSet
    name = models.CharField(max_length=200, primary_key=True)
    description = models.TextField(null=True)
    reference = models.ManyToManyField(GEModelReference, related_name='gem_references')
'''

'''
    GEModelSample
    organism = models.CharField(max_length=200)
    organ_system = models.CharField(max_length=200, null=True)
    tissue = models.CharField(max_length=200, null=True)
    cell_type = models.CharField(max_length=200, null=True)
    cell_line = models.CharField(max_length=200, null=True)
'''

'''
    GEModelFile
    path = models.CharField(max_length=200, unique=True)
    format = models.CharField(max_length=50)
'''

'''
    GEModel
    set = models.ForeignKey(GEModelSet)
    sample = models.ForeignKey(GEModelSample)
    description = models.TextField(null=True)
    label = models.CharField(max_length=200)
    reaction_count = models.IntegerField()
    metabolite_count = models.IntegerField()
    enzyme_count = models.IntegerField()
    files = models.ManyToManyField(GEModelFile, related_name='gem_files')
    maintained = models.CharField(max_length=200)
    reference = models.ForeignKey(GEModelReference, null=True)
'''

def delete_gems():
        # delete all object
    GEModelReference.objects.all().delete()
    GEModelFile.objects.all().delete()
    GEModelSet.objects.all().delete()
    GEModelSample.objects.all().delete()
    GEModel.objects.all().delete()


def insert_gems(model_set_data, model_data_list):


    # insert set references
    set_references = []
    set_references_ids = []
    for reference in model_set_data['reference']:
        try:
            gr = GEModelReference.objects.get(Q(link=reference['link']) &
                                          Q(pubmed=reference['pubmed']))
            # print ("gr1 %s" % gr)
        except GEModelReference.DoesNotExist:
            gr = GEModelReference(**reference)
            print ("gem_set_reference %s" % reference)
            # print ("gr2 %s" % gr)
            gr.save()
        set_references.append(gr)
        set_references_ids.append(gr.id)

    # print (set_references_ids)
    # print (set_references)

    # insert set if new
    try:
        gg = GEModelSet.objects.get(name=model_set_data['name'])
        # print ("gg1 %s" % gg)
    except GEModelSet.DoesNotExist:
        gg = GEModelSet(name=model_set_data['name'] , description=model_set_data['description'])
        gg.save()
        # print ("gg2 %s" % gg)
    gg.reference.add(*set_references_ids)

    i = 0
    for model_dict in model_data_list:
        # insert the gem sample if new
        model_sample = model_dict.pop('sample')
        try:
            gs = GEModelSample.objects.get(Q(organism=model_sample['organism']) &
                                       Q(organ_system=model_sample['organ_system']) &
                                       Q(tissue=model_sample['tissue']) &
                                       Q(cell_type=model_sample['cell_type']) &
                                       Q(cell_line=model_sample['cell_line']))
        except GEModelSample.DoesNotExist:
            gs = GEModelSample(**model_sample)
            gs.save()

        gem_reference = model_dict.pop('reference')
        if isinstance(gem_reference, dict):
            print ("gem_reference %s" % gem_reference)
            try:
                gr = GEModelReference.objects.get(Q(link=gem_reference['link']) &
                                              Q(pubmed=gem_reference['pubmed']))
                print ("current Gem ref year %s " % gr.year)
                # print ("gr1 %s" % gr)
            except GEModelReference.DoesNotExist:
                gr = GEModelReference(**gem_reference)
                print ("current Gem ref year %s " % gem_reference['year'])
                gr.save()
                # print ("gr2 %s" % gr)
            gem_reference = gr
        elif gem_reference:
            gem_reference = set_references[int(gem_reference[-1]) -1] # ":reference1" -> index 0 de set_reference
            print ("current Gem ref year %s " % gem_reference.year)
        elif len(set_references) == 1:
            gem_reference = set_references[0]
            print ("current Gem ref year %s " % gem_reference.year)
        else:
            gem_reference = None
            print ("current Gem ref year None")

        # save the files
        files_ids = []
        for file in model_dict.pop('files'):
            try:
                gf = GEModelFile.objects.get(path=file['path'])
                # print ("gf1 %s" % gf)
            except GEModelFile.DoesNotExist:
                gf = GEModelFile(**file)
                gf.save()
                # print ("gf2 %s" % gf)
            files_ids.append(gf.id)

        if not model_dict['maintained']:
            model_dict['maintained'] = False

        try:
            g = GEModel.objects.get(Q(gemodelset=gg) &
                                Q(sample=gs) &
                                Q(label=model_dict['label']) &
                                Q(reaction_count=model_dict['reaction_count']) &
                                Q(enzyme_count=model_dict['enzyme_count']) &
                                Q(metabolite_count=model_dict['metabolite_count']))
            # print ("g1 %s" % g)
        except GEModel.DoesNotExist:
            g = GEModel(gemodelset=gg, reference=gem_reference, sample=gs, **model_dict)
            print (model_dict)
            # print (gem_reference.year)
            g.save()
            # print ("g2 %s" % g)
        #exit()

        g.files.add(*files_ids)
        i += 1

    print ("%s models added" % i)


dir_path = os.path.dirname(os.path.realpath(__file__))
# dir_path = os.path.dirname(os.path.join(dir_path, "HMR/"))
# dir_path = os.path.dirname(os.path.join(dir_path, "INIT_cancer/"))
# dir_path = os.path.dirname(os.path.join(dir_path, "INIT_normal/"))
# dir_path = os.path.dirname(os.path.join(dir_path, "curated_model/"))
# dir_path = os.path.dirname(os.path.join(dir_path, "tissue-specific/"))
dir_path = "/project/model_files"
print ("Root dir: %s" % dir_path)

matches = []
for root, dirnames, filenames in os.walk(dir_path):
    for filename in fnmatch.filter(filenames, 'parsed_data.txt'):
        matches.append([os.path.join(root, filename), os.path.join(root, 'info.txt')])

delete_gems()
for parse_data_file, info_file in matches:
    print ("Parsing: %s" % parse_data_file)
    global_dict = None
    if os.path.isfile(info_file):
        global_dict, model_set_data = parse_info_file(info_file)

    print ("global_dict %s" % global_dict)
    print ("model_set_data %s" % model_set_data)

    results = read_gems_data_file(parse_data_file, global_dict=global_dict)
    model_data_list = build_ftp_path_and_dl(results, '/project/model_files/FTP', model_set_data)
    insert_gems(model_set_data, model_data_list)


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def handle(self, *args, **options):
        pass