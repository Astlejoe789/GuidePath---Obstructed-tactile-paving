from pathlib import Path
from PIL import Image
from scripts.prepare_wotr import prepare

def fixture(root,duplicate=False):
    (root/'Annotations').mkdir(parents=True);(root/'JPEGImages').mkdir();(root/'ImageSets'/'Main').mkdir(parents=True)
    for i,s in enumerate(('train','val','test')):
        name=f'image{i}'
        Image.new('RGB',(12,12),(0 if duplicate else i*40,50,100)).save(root/'JPEGImages'/f'{name}.png')
        objects=''.join(f'<object><name>{c}</name><difficult>0</difficult><bndbox><xmin>1</xmin><ymin>1</ymin><xmax>12</xmax><ymax>12</ymax></bndbox></object>' for c in ['blind_road','bicycle','motorcycle'])
        (root/'Annotations'/f'{name}.xml').write_text('<annotation><size><width>12</width><height>12</height></size>'+objects+'</annotation>')
        (root/'ImageSets'/'Main'/f'{s}.txt').write_text(name+'\n')

def test_conversion_and_voc_boundary(tmp_path):
    fixture(tmp_path/'voc');out=tmp_path/'out';r=prepare(tmp_path/'voc',out)
    assert not r['blocking_issues']
    assert r['counts']['train']['tactile_paving']==1
    assert (out/'labels/train/image0.txt').read_text().splitlines()[0]=='0 0.50000000 0.50000000 1.00000000 1.00000000'

def test_cross_split_duplicate_is_blocking(tmp_path):
    fixture(tmp_path/'voc',duplicate=True);r=prepare(tmp_path/'voc',tmp_path/'out')
    assert any('Exact duplicate pixels' in x for x in r['blocking_issues'])

def test_group_leakage_is_blocking(tmp_path):
    fixture(tmp_path/'voc');csv=tmp_path/'groups.csv'
    csv.write_text('image_id,split,group\nimage0,train,same_location\nimage1,val,same_location\nimage2,test,other\n')
    r=prepare(tmp_path/'voc',tmp_path/'out',csv)
    assert any('Group crosses splits' in x for x in r['blocking_issues'])

def test_cleanup_preserves_test_and_records_invalid_exclusions(tmp_path):
    import json, shutil
    from scripts.clean_dataset import cleanup
    root=tmp_path/'voc';fixture(root)
    shutil.copy2(root/'JPEGImages/image2.png',root/'JPEGImages/image3.png')
    shutil.copy2(root/'Annotations/image2.xml',root/'Annotations/image3.xml')
    Image.new('RGB',(12,12),(250,0,0)).save(root/'JPEGImages/image4.png')
    (root/'Annotations/image4.xml').write_text((root/'Annotations/image0.xml').read_text().replace('<xmin>1</xmin>','<xmin>0</xmin>'))
    (root/'ImageSets/Main/train.txt').write_text('image0\nimage3\nimage4\n')
    original=tmp_path/'original';prepare(root,original)
    output=tmp_path/'clean';r=cleanup(original,root,output)
    assert not r['blocking_issues']
    report=json.loads((output/'cleanup_report.json').read_text())
    assert report['before']==5 and report['after']==3
    assert {x['image_id']:x['reason'] for x in report['removed']}=={'image3':'exact_duplicate','image4':'invalid_selected_class_box'}
    assert (output/'images/test/image2.png').exists()
    assert (original/'images/train/image3.png').exists()
