"""Create the storage review, retaining assessed observations (codes 1/2).

Separate rendering aliases for contiguous spans preserve genuine missing
observations without changing the reference rendering engine.
"""
from pathlib import Path
import csv
import json
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
months = [f'{y}-{m:02d}' for y in range(2010, 2027) for m in range(1, 13)
          if f'{y}-{m:02d}' <= '2026-08']
names = {'AT':'Austria','AZ':'Azerbaijan','CA':'Canada','CH':'Switzerland',
         'CZ':'Czechia','DE':'Germany','DK':'Denmark','ES':'Spain','FR':'France',
         'GB':'United Kingdom','HU':'Hungary','IT':'Italy','JP':'Japan',
         'KR':'South Korea','NL':'Netherlands','NZ':'New Zealand','PL':'Poland',
         'SK':'Slovakia','TR':'Türkiye','UA':'Ukraine','US':'United States'}
names.update({'AR':'Argentina','BB':'Barbados','BD':'Bangladesh','BE':'Belgium',
    'BG':'Bulgaria','BH':'Bahrain','CL':'Chile','CO':'Colombia','DO':'Dominican Rep.',
    'EE':'Estonia','FI':'Finland','GE':'Georgia','GR':'Greece','HR':'Croatia',
    'IE':'Ireland','IN':'India','LT':'Lithuania','LU':'Luxembourg','LV':'Latvia',
    'MA':'Morocco','MD':'Moldova','MK':'North Macedonia','MM':'Myanmar','MT':'Malta',
    'NO':'Norway','PA':'Panama','PT':'Portugal','RO':'Romania','RS':'Serbia',
    'SE':'Sweden','SI':'Slovenia','TN':'Tunisia','ZA':'South Africa'})
with (ROOT/'data/raw/jodi_gas_publication28.csv').open() as handle:
    raw = [r for r in csv.DictReader(handle)
           if r['ENERGY_PRODUCT']=='NATGAS' and r['FLOW_BREAKDOWN']=='CLOSTLV'
           and r['UNIT_MEASURE']=='M3' and r['TIME_PERIOD'] in months]
accepted = [r for r in raw if r['ASSESSMENT_CODE'] in ('1','2')]
by_month = defaultdict(list)
observations = {}
assessment = {}
for r in accepted:
    val = float(r['OBS_VALUE']) / 1000.0
    assert val >= 0
    key = r['TIME_PERIOD'],r['REF_AREA']
    assert key not in observations
    observations[key] = val
    assessment[key] = r['ASSESSMENT_CODE']
    by_month[key[0]].append((key[1],val))
pool = {country for mo,country in observations}
assert pool <= names.keys(), pool-names.keys()
assert all(observations[mo,'CH']==0 for mo in months)
entities, spans, series = {}, {}, {}
for country in sorted(pool):
    runs = []
    for idx, mo in enumerate(months):
        if (mo,country) not in observations:
            continue
        if not runs or idx > runs[-1][-1]+1:
            runs.append([])
        runs[-1].append(idx)
    for number,run in enumerate(runs,1):
        code = country if len(runs)==1 else f'{country}_{number:02d}'
        entities[code]={'name':names[country]+('*' if country=='CA' else ''),'sub':'','flag':country.lower()}
        spans[code]={'country':country,'first':months[run[0]],'last':months[run[-1]]}
        for idx in run:
            series[months[idx],code] = observations[months[idx],country]
with (ROOT/'data/values.csv').open('w',newline='') as handle:
    writer=csv.writer(handle);writer.writerow(['period','code','gas'])
    for mo in months:
        for code in sorted(entities):
            writer.writerow([mo,code,series.get((mo,code),'')])
with (ROOT/'data/assessed_reported_stocks.csv').open('w',newline='') as handle:
    writer=csv.writer(handle);writer.writerow(['month','country','stocks_billion_m3','assessment_code'])
    for (mo,co),val in sorted(observations.items()):writer.writerow([mo,co,val,assessment[mo,co]])
cfg=json.loads((ROOT/'config.json').read_text())
cfg['entities']=entities
cfg['output']='output/Who_Stores_the_Most_Gas_2010-2026.mp4'
cfg['ranking'].update(top_n=6,pinned_dynamic=['max','min'],smooth_window=0)
cfg['timing']['race']=111.4
cfg['comparison']={'mode':'smallest_positive_monthly',
    'source_csv':'data/assessed_reported_stocks.csv',
    'tie_policy':'keep_current_otherwise_country_code','decimals':7}
cfg['ranking']['slot_fade_seconds']=0.25
cfg['pacing']={'year_weights':{'2011':1.25,'2013':1.4,'2021':1.25},
    'holds_at_month_indices':[23,47,143],'hold_seconds':0.25}
cfg['ranking']['swap'].update(threshold=1.000000001,hold_seconds=0.18,cooldown_seconds=0.25)
cfg['series']=[{'col':'gas','label':'Reported gas stocks · billion m³',
                'color_from':'#77BFF4','color_to':'#3D87CF'}]
cfg['value_format'].update(decimals=2,unit_suffix=' bcm')
cfg['text'].update(title='Who Stores the Most Gas?',
    subtitle='REPORTED STOCKS · JAN 2010–AUG 2026',show_month=True,
    max_label='LARGEST REPORTED GAS STOCK',min_label='SMALLEST NON-ZERO STOCK · COMPARISON',
    footer='JODI-Gas · Monthly positive minimum · Coverage varies · * Code 2: caution',
    outro_title='August 2026 · Largest reported stocks')
cfg['events']=[['2010-01','2010 · Available reporting countries'],
               ['2013-01','2013 · German reporting series begins'],
               ['2016-01','2016 · Canadian reporting series begins'],
               ['2026-08','August 2026 · Latest shared reporting month']]
cfg['sources']=['JODI-Gas · End-of-month stocks · Billion m³',
                'Assessment codes 1/2 · Unassessed data excluded',
                'Lowest positive monthly report · All eligible countries',
                '* Assessment code 2: use with caution (JODI)']
cfg['theme'].update(bg_top='#101F35',bg_bottom='#070F1D',card_top='#1B344D',
    card_bottom='#11263A',accent='#77BFF4',glows=['#478FCC','#DDB17B'],
    leader='#EDBE82',lowest='#9EBFEA',year_glow='#77BFF4')
cfg['music'].update(bpm=112,seed=201026,chords=[[50,53,57],[46,50,53],[53,57,60],[48,52,55]],
                    bass=[38,34,41,36])
(ROOT/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
summary={'start':months[0],'end':months[-1],'periods':len(months),
    'metric':'Reported end-of-month recoverable gas stocks, billion m3',
    'assessment_policy':'Codes 1/2 retained; code 2 caution recorded; code 3 unassessed excluded',
    'reporting_country_count':len({c for m,c in observations}),
    'rendering_countries':sorted(pool),'rendering_spans':spans,
    'key_months':{mo:{'reporters':len(by_month[mo]),
        'top_10':[{'country':c,'billion_m3':v} for c,v in sorted(by_month[mo],key=lambda a:(-a[1],a[0]))[:10]],
        'zero_ties':[c for c,v in sorted(by_month[mo]) if v==0]}
        for mo in ['2010-01','2010-12','2016-01','2020-12','2026-08']}}
(ROOT/'data/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='rendering_spans'},indent=2))
